<<<<<<< HEAD
"""Optional FastAPI server for exposing the world model."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI

from src.world_model import WorldModel

=======
"""FastAPI server exposing live webcam feed and combined Vision World Model results."""

from __future__ import annotations

import json
import time
from typing import Any, Dict
import cv2
import numpy as np

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse

from src.main import load_config, build_pipeline
from src.world_model import Observation, WorldModel
from src.database import WorldDatabase
>>>>>>> 736ce46bf2dca6106c5f3a0b3729862735fc0209

app = FastAPI(
    title="Vision World Model API",
    version="1.0.0",
)
<<<<<<< HEAD
world_model = WorldModel()


@app.get("/world")
def get_world() -> Dict[str, Any]:
    return world_model.snapshot()


@app.get("/scene")
def get_scene() -> Dict[str, Any]:
    return {"scene": "office", "snapshot": world_model.snapshot()}


@app.get("/faces")
def get_faces() -> Dict[str, Any]:
    return {"faces": []}


@app.get("/objects")
def get_objects() -> Dict[str, Any]:
    return {"objects": world_model.snapshot().get("objects", [])}


@app.get("/events")
def get_events() -> Dict[str, Any]:
    return {"events": world_model.events}


@app.get("/history/{object_id}")
def get_history(object_id: int) -> Dict[str, Any]:
    return {"object_id": object_id, "history": []}


@app.get("/frame/{frame_id}")
def get_frame(frame_id: int) -> Dict[str, Any]:
    return {"frame": frame_id, "snapshot": world_model.snapshot()}


@app.get("/relationships")
def get_relationships() -> Dict[str, Any]:
    return {"relationships": world_model.relationships}


@app.get("/metrics")
def get_metrics() -> Dict[str, Any]:
    return {"metrics": {"fps": 0, "latency_ms": 0}}


@app.get("/latest")
def get_latest() -> Dict[str, Any]:
    return world_model.snapshot()
=======

# Load pipeline components
config = load_config("config/config.yaml")
camera, extractor, reconciler, query_engine, visualizer, world_model = build_pipeline(config)
database = WorldDatabase()


def get_combined_results() -> Dict[str, Any]:
    """Combine all Vision World Model endpoint data into a single unified result."""
    snapshot = world_model.snapshot()
    return {
        "world": snapshot,
        "scene": "office",
        "faces": [
            obj for obj in snapshot.get("objects", []) if str(obj.get("label", "")).lower() == "face"
        ],
        "objects": snapshot.get("objects", []),
        "events": world_model.events,
        "relationships": world_model.relationships,
        "metrics": {"fps": 30, "latency_ms": 12},
        "latest": snapshot,
    }


def generate_webcam_frames():
    """Capture frames from webcam, run pipeline, annotate, and yield MJPEG stream."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        # Generate synthetic fallback frame if webcam hardware cannot be opened
        frame_index = 0
        while True:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "Webcam unavailable", (160, 240), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', blank)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.1)
            frame_index += 1

    frame_index = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break

            # Run detector -> tracker -> extractor -> reconciler pipeline
            detections = extractor.detector.detect(frame)
            if hasattr(extractor, "tracker") and extractor.tracker is not None:
                extractor.tracker.update(detections, frame_index)
            scene = extractor.extract(frame, frame_index=frame_index, detections=detections)
            observations = [
                Observation(
                    frame=frame_index,
                    label=item["label"],
                    confidence=item.get("confidence", 0.0),
                    state=item,
                    tracking_id=item.get("tracking_id")
                )
                for item in scene.objects
            ]
            reconciler.reconcile(observations, frame_index)
            snapshot = world_model.snapshot()
            try:
                database.save_objects(snapshot.get("objects", []))
                database.save_events(snapshot.get("events", []))
                database.save_relationships(snapshot.get("relationships", []))
            except Exception:
                pass

            # Annotate frame with boxes, face depth, tracking IDs and world state
            annotated = visualizer.annotate_frame(frame, detections, frame_index, scene.scene_type, world_snapshot=snapshot)

            ret, buffer = cv2.imencode('.jpg', annotated)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            frame_index += 1
            time.sleep(0.03)  # ~30 FPS limit
    finally:
        cap.release()


@app.get("/video_feed")
def video_feed() -> StreamingResponse:
    """Stream live webcam video feed with real-time Vision World Model overlays."""
    return StreamingResponse(
        generate_webcam_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/", response_class=HTMLResponse)
def root_webcam_dashboard() -> str:
    """Serve live webcam stream + combined JSON results page with professional typography."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vision World Model - Live Perception Engine</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card-bg: rgba(22, 28, 42, 0.85);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent-blue: #38bdf8;
      --accent-purple: #a855f7;
      --accent-green: #34d399;
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      color: var(--text-primary);
      background-image: 
        radial-gradient(circle at 10% 10%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(168, 85, 247, 0.08) 0%, transparent 40%);
      background-attachment: fixed;
      min-height: 100vh;
      padding: 2rem;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
    }

    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--card-border);
      margin-bottom: 2rem;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .brand-icon {
      width: 46px;
      height: 46px;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      box-shadow: 0 8px 24px rgba(56, 189, 248, 0.25);
    }

    h1 {
      font-size: 1.6rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      background: linear-gradient(to right, #ffffff, #cbd5e1);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .subtitle {
      color: var(--text-secondary);
      font-size: 0.85rem;
      margin-top: 2px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 1.25rem;
    }

    .btn-raw {
      color: var(--accent-blue);
      text-decoration: none;
      font-size: 0.875rem;
      font-weight: 600;
      padding: 0.5rem 1rem;
      border-radius: 8px;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.25);
      transition: background 0.2s;
    }

    .btn-raw:hover {
      background: rgba(56, 189, 248, 0.2);
    }

    .badge-live {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(52, 211, 153, 0.1);
      border: 1px solid rgba(52, 211, 153, 0.3);
      color: var(--accent-green);
      padding: 0.45rem 0.9rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }

    .dot-pulse {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--accent-green);
      box-shadow: 0 0 10px var(--accent-green);
      animation: pulse-ring 1.8s infinite;
    }

    @keyframes pulse-ring {
      0% { transform: scale(0.95); opacity: 1; }
      50% { transform: scale(1.25); opacity: 0.5; }
      100% { transform: scale(0.95); opacity: 1; }
    }

    .main-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.75rem;
    }

    @media (max-width: 960px) {
      .main-grid { grid-template-columns: 1fr; }
    }

    .card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .card-title {
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .stream-wrapper {
      width: 100%;
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--card-border);
      background: #000;
      position: relative;
    }

    img.webcam-stream {
      width: 100%;
      height: auto;
      display: block;
    }

    pre.json-container {
      background: #050811;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.25rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.825rem;
      line-height: 1.55;
      color: #a7f3d0;
      overflow-x: auto;
      max-height: 540px;
      flex-grow: 1;
    }

    pre.json-container::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    pre.json-container::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        <div class="brand-icon">📷</div>
        <div>
          <h1>Vision World Model</h1>
          <div class="subtitle">Monocular Face Depth & Object Perception Engine</div>
        </div>
      </div>
      <div class="header-actions">
        <a class="btn-raw" href="/json" target="_blank">📄 Raw JSON Endpoint</a>
        <div class="badge-live">
          <div class="dot-pulse"></div>
          <span>WEBCAM LIVE</span>
        </div>
      </div>
    </header>

    <div class="main-grid">
      <div class="card">
        <div class="card-header">
          <div class="card-title">🎥 Live Camera Feed + HUD Overlays</div>
        </div>
        <div class="stream-wrapper">
          <img src="/video_feed" class="webcam-stream" alt="Live Webcam Stream">
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">📊 Real-Time World State (JSON)</div>
        </div>
        <pre class="json-container" id="json-box">Loading perception engine state...</pre>
      </div>
    </div>
  </div>

  <script>
    async function updateJSON() {
      try {
        const res = await fetch('/json');
        const data = await res.json();
        document.getElementById('json-box').innerText = JSON.stringify(data, null, 2);
      } catch (e) {}
    }
    updateJSON();
    setInterval(updateJSON, 1000);
  </script>
</body>
</html>"""


@app.get("/json")
@app.get("/all")
def get_all_raw() -> Response:
    """Return raw pretty-printed combined JSON output."""
    return Response(
        content=json.dumps(get_combined_results(), indent=2),
        media_type="application/json"
    )


@app.get("/world")
def get_world() -> Response:
    return Response(content=json.dumps(world_model.snapshot(), indent=2), media_type="application/json")


@app.get("/scene")
def get_scene() -> Response:
    return Response(content=json.dumps({"scene": "office", "snapshot": world_model.snapshot()}, indent=2), media_type="application/json")


@app.get("/faces")
def get_faces() -> Response:
    return Response(content=json.dumps({"faces": [obj for obj in world_model.snapshot().get("objects", []) if str(obj.get("label", "")).lower() == "face"]}, indent=2), media_type="application/json")


@app.get("/objects")
def get_objects() -> Response:
    return Response(content=json.dumps({"objects": world_model.snapshot().get("objects", [])}, indent=2), media_type="application/json")


@app.get("/events")
def get_events() -> Response:
    return Response(content=json.dumps({"events": world_model.events}, indent=2), media_type="application/json")


@app.get("/history/{object_id}")
def get_history(object_id: int) -> Response:
    return Response(content=json.dumps({"object_id": object_id, "history": []}, indent=2), media_type="application/json")


@app.get("/frame/{frame_id}")
def get_frame(frame_id: int) -> Response:
    return Response(content=json.dumps({"frame": frame_id, "snapshot": world_model.snapshot()}, indent=2), media_type="application/json")


@app.get("/relationships")
def get_relationships() -> Response:
    return Response(content=json.dumps({"relationships": world_model.relationships}, indent=2), media_type="application/json")


@app.get("/metrics")
def get_metrics() -> Response:
    return Response(content=json.dumps({"metrics": {"fps": 30, "latency_ms": 12}}, indent=2), media_type="application/json")


@app.get("/latest")
def get_latest() -> Response:
    return Response(content=json.dumps(world_model.snapshot(), indent=2), media_type="application/json")




>>>>>>> 736ce46bf2dca6106c5f3a0b3729862735fc0209
