import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import cv2
import numpy as np
from collections import Counter, deque
import threading
import time

from src.environment import TextEnvironment
from src.world_model import TextWorldModel
from src.database import WorldDatabase
from src.updater import Updater
from src.query import QueryLayer
from src.agent import HeuristicAgent

app = FastAPI(title="Text World Agent - Vision Edition")

# ── Game State ──
env = TextEnvironment()
db = WorldDatabase()
world_model = TextWorldModel()
updater = Updater(world_model)
query_layer = QueryLayer(world_model)
agent = HeuristicAgent(objective="Find the treasure")

# Initialize game
response = env.reset()
updater.update("look", response, None)

# ── Webcam ──
cap = cv2.VideoCapture(0)

# ── YOLO Model (loaded lazily) ──
yolo_model = None

def get_yolo_model():
    global yolo_model
    if yolo_model is None:
        from ultralytics import YOLO
        yolo_model = YOLO("yolov8n.pt")
    return yolo_model

# ── Room Classification Heuristic ──
ROOM_RULES = {
    "Kitchen": {"microwave", "oven", "refrigerator", "toaster", "sink", "knife", "fork", "spoon", "bowl", "cup"},
    "Bedroom": {"bed", "clock", "teddy bear", "pillow"},
    "Living Room": {"tv", "remote", "couch", "sofa"},
    "Office / Study": {"laptop", "keyboard", "mouse", "monitor", "book", "cell phone"},
    "Dining Room": {"dining table", "wine glass", "bottle", "cup", "fork", "knife", "spoon"},
    "Bathroom": {"toilet", "toothbrush", "hair drier", "sink"},
    "Outdoor": {"car", "truck", "bus", "bicycle", "motorcycle", "traffic light", "stop sign", "fire hydrant", "bench", "bird", "dog", "cat", "horse"},
}

def classify_room(detected_labels: list[str]) -> str:
    if not detected_labels:
        return "Unknown"
    label_set = set(detected_labels)
    scores = {}
    for room, keywords in ROOM_RULES.items():
        overlap = label_set & keywords
        if overlap:
            scores[room] = len(overlap)
    if scores:
        return max(scores, key=scores.get)
    return "Unknown"

# ── Room smoothing buffer (keeps last 15 classifications) ──
room_history = deque(maxlen=15)

# ── Shared vision state (thread-safe) ──
vision_lock = threading.Lock()
vision_state = {
    "room": "Scanning...",
    "objects": {},
    "total_count": 0,
}

# ── Neon Colors ──
NEON_CYAN = (244, 233, 3)      # BGR for #03e9f4
NEON_MAGENTA = (233, 3, 244)   # BGR for #f403e9
NEON_GREEN = (20, 255, 57)     # BGR for #39ff14
NEON_YELLOW = (59, 235, 255)   # BGR for #ffeb3b
BG_DARK = (16, 12, 11)        # BGR for #0b0c10

def draw_neon_text(frame, text, pos, color, scale=0.6, thickness=2):
    """Draw text with a neon glow effect."""
    x, y = pos
    # Glow (larger, blurred text behind)
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness + 2, cv2.LINE_AA)
    # Sharp text on top
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), thickness, cv2.LINE_AA)

def generate_frames():
    model = get_yolo_model()
    frame_count = 0
    
    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.03)
            continue
        
        frame_count += 1
        
        # Run YOLO detection every 3rd frame to save CPU
        if frame_count % 3 == 0:
            results = model(frame, verbose=False, conf=0.35)
            
            detected_labels = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    detected_labels.append(label)
                    
                    # Draw neon bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), NEON_MAGENTA, 2)
                    
                    # Label background
                    label_text = f"{label} {conf:.0%}"
                    (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 10, y1), NEON_MAGENTA, -1)
                    cv2.putText(frame, label_text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            
            # Classify room with temporal smoothing
            instant_room = classify_room(detected_labels)
            room_history.append(instant_room)
            # Pick the most frequent room from the last N frames
            room_counts = Counter(room_history)
            stable_room = room_counts.most_common(1)[0][0]
            obj_counts = dict(Counter(detected_labels))
            
            with vision_lock:
                vision_state["room"] = stable_room
                vision_state["objects"] = obj_counts
                vision_state["total_count"] = len(detected_labels)
        
        # ── Draw HUD Overlay ──
        h, w = frame.shape[:2]
        
        # Semi-transparent top bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 70), BG_DARK, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        with vision_lock:
            room_text = vision_state["room"]
            obj_counts = vision_state["objects"]
            total = vision_state["total_count"]
        
        # Room classification (top-left)
        draw_neon_text(frame, f"ROOM: {room_text}", (15, 30), NEON_CYAN, 0.8, 2)
        
        # Object count (top-right)
        count_text = f"OBJECTS: {total}"
        (tw, _), _ = cv2.getTextSize(count_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        draw_neon_text(frame, count_text, (w - tw - 30, 30), NEON_GREEN, 0.8, 2)
        
        # Object breakdown (top bar, second line)
        if obj_counts:
            breakdown = " | ".join([f"{k}: {v}" for k, v in sorted(obj_counts.items(), key=lambda x: -x[1])[:5]])
            draw_neon_text(frame, breakdown, (15, 58), NEON_YELLOW, 0.5, 1)
        
        # Neon border around entire frame
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), NEON_CYAN, 2)
        
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.on_event("shutdown")
def shutdown_event():
    if cap.isOpened():
        cap.release()

@app.get("/")
def index():
    return HTMLResponse('''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Text World Agent - Neon Vision</title>
            <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Share Tech Mono', monospace; 
                    background-color: #0b0c10; 
                    background-image: linear-gradient(0deg, transparent 24%, rgba(0,255,255,0.03) 25%, rgba(0,255,255,0.03) 26%, transparent 27%, transparent 74%, rgba(0,255,255,0.03) 75%, rgba(0,255,255,0.03) 76%, transparent 77%, transparent), linear-gradient(90deg, transparent 24%, rgba(0,255,255,0.03) 25%, rgba(0,255,255,0.03) 26%, transparent 27%, transparent 74%, rgba(0,255,255,0.03) 75%, rgba(0,255,255,0.03) 76%, transparent 77%, transparent);
                    background-size: 50px 50px;
                    color: #45f3ff; 
                    padding: 25px; 
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    min-height: 100vh;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .header h1 { 
                    font-family: 'Orbitron', sans-serif;
                    color: #fff; 
                    font-size: 2.4em;
                    text-shadow: 0 0 5px #03e9f4, 0 0 25px #03e9f4, 0 0 50px #03e9f4, 0 0 100px #03e9f4;
                    letter-spacing: 4px;
                    margin-bottom: 5px;
                }
                .header p { color: #666; font-size: 0.95em; }
                
                .main-layout {
                    display: flex;
                    flex-direction: row;
                    gap: 30px;
                    width: 100%;
                    max-width: 1400px;
                }
                .panel {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                }
                .panel-title { 
                    font-family: 'Orbitron', sans-serif;
                    color: #fff; 
                    font-size: 1.1em;
                    text-shadow: 0 0 5px #03e9f4, 0 0 25px #03e9f4;
                    text-align: center;
                    margin-bottom: 15px;
                    letter-spacing: 2px;
                }
                
                /* ── Agent Log Panel ── */
                #log { 
                    flex-grow: 1;
                    white-space: pre-wrap; 
                    margin-bottom: 20px; 
                    border: 1px solid #03e9f4; 
                    border-radius: 10px;
                    padding: 18px; 
                    height: 480px; 
                    overflow-y: auto; 
                    background: rgba(11, 12, 16, 0.9); 
                    line-height: 1.6;
                    box-shadow: 0 0 10px rgba(3, 233, 244, 0.2), inset 0 0 15px rgba(3, 233, 244, 0.05);
                    scrollbar-width: thin;
                    scrollbar-color: #03e9f4 #1f2833;
                }
                #log::-webkit-scrollbar { width: 6px; }
                #log::-webkit-scrollbar-track { background: #1f2833; border-radius: 4px; }
                #log::-webkit-scrollbar-thumb { background: #03e9f4; border-radius: 4px; }
                
                button { 
                    padding: 14px 28px; 
                    background: transparent; 
                    color: #03e9f4; 
                    border: 2px solid #03e9f4; 
                    border-radius: 30px;
                    cursor: pointer; 
                    font-family: 'Orbitron', sans-serif;
                    font-size: 15px;
                    font-weight: bold;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    transition: 0.2s;
                    box-shadow: 0 0 10px rgba(3, 233, 244, 0.3);
                    align-self: center;
                }
                button:hover { 
                    background: #03e9f4; 
                    color: #050801;
                    box-shadow: 0 0 10px #03e9f4, 0 0 40px #03e9f4, 0 0 80px #03e9f4;
                }
                
                /* ── Webcam Panel ── */
                .webcam-wrap {
                    position: relative;
                    border: 2px solid #f403e9;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 0 15px rgba(244, 3, 233, 0.4), 0 0 30px rgba(244, 3, 233, 0.15);
                }
                img.webcam {
                    width: 100%;
                    display: block;
                }
                
                /* ── Vision Stats Panel ── */
                .vision-stats {
                    margin-top: 15px;
                    border: 1px solid #39ff14;
                    border-radius: 10px;
                    padding: 15px;
                    background: rgba(11, 12, 16, 0.9);
                    box-shadow: 0 0 10px rgba(57, 255, 20, 0.15);
                }
                .stat-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                    padding-bottom: 8px;
                    border-bottom: 1px solid rgba(57, 255, 20, 0.15);
                }
                .stat-row:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
                .stat-label { color: #888; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px; }
                .stat-value { color: #39ff14; font-size: 1.1em; font-weight: bold; text-shadow: 0 0 5px rgba(57, 255, 20, 0.5); }
                .stat-value.room { color: #f403e9; text-shadow: 0 0 5px rgba(244, 3, 233, 0.5); }
                #obj-list {
                    color: #45f3ff;
                    font-size: 0.9em;
                    margin-top: 8px;
                    line-height: 1.8;
                }
                .obj-badge {
                    display: inline-block;
                    background: rgba(3, 233, 244, 0.1);
                    border: 1px solid rgba(3, 233, 244, 0.3);
                    border-radius: 15px;
                    padding: 3px 12px;
                    margin: 3px 4px;
                    font-size: 0.85em;
                }
                
                .action { color: #f403e9; font-weight: bold; text-shadow: 0 0 5px rgba(244, 3, 233, 0.5); }
                .win { color: #39ff14; font-weight: bold; font-size: 1.2em; margin-top: 12px; display: block; text-shadow: 0 0 10px rgba(57, 255, 20, 0.8); text-align: center; }
                .section { margin-bottom: 10px; }
                hr { border-color: rgba(3, 233, 244, 0.2); margin: 15px 0; }
                .sys-tag { color: #ffeb3b; text-shadow: 0 0 5px rgba(255, 235, 59, 0.5); }
                .query-tag { color: #03e9f4; text-shadow: 0 0 5px rgba(3, 233, 244, 0.5); }
                .agent-tag { color: #f403e9; text-shadow: 0 0 5px rgba(244, 3, 233, 0.5); }
                .env-tag { color: #39ff14; text-shadow: 0 0 5px rgba(57, 255, 20, 0.5); }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>TEXT WORLD AGENT</h1>
                <p>Vision-Augmented Exploration System</p>
            </div>
            <div class="main-layout">
                <div class="panel">
                    <div class="panel-title">AGENT TERMINAL</div>
                    <div id="log"><span class="sys-tag">[System]</span> Agent initialized in the Kitchen.\n<span class="sys-tag">[System]</span> Vision module active. Scanning environment...</div>
                    <button onclick="step()" id="stepBtn">EXECUTE STEP</button>
                </div>
                <div class="panel">
                    <div class="panel-title">LIVE VISION FEED</div>
                    <div class="webcam-wrap">
                        <img class="webcam" src="/webcam" alt="Webcam Stream">
                    </div>
                    <div class="vision-stats">
                        <div class="stat-row">
                            <span class="stat-label">Detected Room</span>
                            <span class="stat-value room" id="room-label">Scanning...</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Total Objects</span>
                            <span class="stat-value" id="obj-count">0</span>
                        </div>
                        <div id="obj-list"></div>
                    </div>
                </div>
            </div>
            <script>
                // Poll vision stats every second
                setInterval(async () => {
                    try {
                        const res = await fetch('/vision_stats');
                        const data = await res.json();
                        document.getElementById('room-label').textContent = data.room;
                        document.getElementById('obj-count').textContent = data.total_count;
                        
                        const objList = document.getElementById('obj-list');
                        if (Object.keys(data.objects).length > 0) {
                            objList.innerHTML = Object.entries(data.objects)
                                .sort((a,b) => b[1] - a[1])
                                .map(([k, v]) => `<span class="obj-badge">${k}: ${v}</span>`)
                                .join('');
                        } else {
                            objList.innerHTML = '<span style="color:#555">No objects detected</span>';
                        }
                    } catch(e) {}
                }, 1000);
                
                async function step() {
                    const btn = document.getElementById('stepBtn');
                    btn.disabled = true;
                    btn.innerText = "PROCESSING...";
                    
                    try {
                        const res = await fetch('/step');
                        const data = await res.json();
                        const log = document.getElementById('log');
                        
                        let newEntry = `\\n\\n<hr>\\n`;
                        newEntry += `<div class="section"><span class="query-tag">[Query Layer]</span>\\n${data.query}</div>`;
                        newEntry += `<div class="section"><span class="agent-tag">[Agent Decision]</span> <span class="action">${data.action}</span></div>`;
                        newEntry += `<div class="section"><span class="env-tag">[Environment Response]</span>\\n${data.response}</div>`;
                        
                        if (data.won) {
                            newEntry += `<span class="win">>>> OBJECTIVE COMPLETE: TREASURE SECURED <<<</span>`;
                            btn.style.display = 'none';
                        }
                        
                        log.innerHTML += newEntry;
                        log.scrollTop = log.scrollHeight;
                    } catch (e) {
                        alert("Error communicating with mainframe.");
                    } finally {
                        btn.disabled = false;
                        if (btn.style.display !== 'none') {
                            btn.innerText = "EXECUTE STEP";
                        }
                    }
                }
            </script>
        </body>
    </html>
    ''')

@app.get("/webcam")
def webcam_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/vision_stats")
def get_vision_stats():
    with vision_lock:
        return JSONResponse(content={
            "room": vision_state["room"],
            "objects": vision_state["objects"],
            "total_count": vision_state["total_count"],
        })

@app.get("/step")
def step():
    world_slice = query_layer.get_world_slice()
    
    if "treasure" in world_model.inventory:
        return {"query": world_slice, "action": "None", "response": "Game over.", "won": True}
        
    action = agent.decide_action(world_slice)

    previous_room = world_model.current_room
    response = env.step(action)
    updater.update(action, response, previous_room)
    db.save_state(world_model.snapshot())
    
    won = "treasure" in world_model.inventory
    return {
        "query": world_slice,
        "action": action,
        "response": response,
        "won": won
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
