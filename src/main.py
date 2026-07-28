<<<<<<< HEAD
"""Entry point for the Text World Agent Loop."""

import time

from src.environment import TextEnvironment
from src.world_model import TextWorldModel
from src.database import WorldDatabase
from src.updater import Updater
from src.query import QueryLayer
from src.agent import HeuristicAgent

def main():
    print("Initializing Text World Agent...")
    env = TextEnvironment()
    db = WorldDatabase()
    
    world_model = TextWorldModel()
    updater = Updater(world_model)
    query_layer = QueryLayer(world_model)
    agent = HeuristicAgent(objective="Find the treasure")

    # Start game
    response = env.reset()
    updater.update("look", response)
    
    # Agent Loop
    step = 0
    while step < 15:
        print(f"\n--- Step {step} ---")
        
        # 1. Query Layer extracts slice
        world_slice = query_layer.get_world_slice()
        print(f"[Query Layer Output]\n{world_slice}\n")
        
        # 2. Agent decides action
        action = agent.decide_action(world_slice)
        print(f"[*] Agent decides to: {action}")
        
        # Check win condition
        if "treasure" in world_model.inventory:
            print("\n>>> The agent has found the treasure! Objective complete. <<<")
            break

        # 3. Environment responds
        previous_room = world_model.current_room
        response = env.step(action)
        print(f"\n[Environment Output]\n{response}\n")
        
        # 4. Updater updates world model
        updater.update(action, response, previous_room)
        
        # Save state
        db.save_state(world_model.snapshot())
        
        step += 1

    print("\nFinal World Model Snapshot:")
    import json
    print(json.dumps(world_model.snapshot(), indent=2))
=======
"""Entry point for the face-depth/world-model demo pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import cv2
import yaml

from src.database import WorldDatabase
from src.extractor import VisionExtractor
from src.query import QueryEngine
from src.updater import StateReconciler
from src.visualizer import Visualizer
from src.world_model import Observation, WorldModel
from src.camera import CameraIntrinsics
from src.tracker import Tracker


def load_config(path: Optional[str] = None) -> dict:
    """Load YAML configuration from disk."""
    config_path = Path(path or "config/config.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_pipeline(config: dict):
    """Construct the application pipeline from configuration."""
    camera = CameraIntrinsics(
        fx=config["camera"]["fx"],
        fy=config["camera"]["fy"],
        cx=config["camera"]["cx"],
        cy=config["camera"]["cy"],
    )
    world_model = WorldModel()
    database = WorldDatabase()
    extractor = VisionExtractor(camera, config["camera"]["average_face_width_m"])
    # attach a Tracker to the extractor to assign persistent tracking IDs
    tracker = Tracker()
    extractor.tracker = tracker
    reconciler = StateReconciler(world_model)
    query_engine = QueryEngine(world_model)
    visualizer = Visualizer(
        font_scale=config["visualization"].get("font_scale", 0.6),
        line_thickness=config["visualization"].get("line_thickness", 2),
    )
    return camera, extractor, reconciler, query_engine, visualizer, world_model


def run_demo(config: dict, video_path: Optional[str] = None) -> dict:
    """Run the demo pipeline against a video file or camera stream."""
    _, extractor, reconciler, query_engine, visualizer, world_model = build_pipeline(config)
    cap = cv2.VideoCapture(0 if video_path is None else video_path)
    if not cap.isOpened():
        raise RuntimeError("Unable to open video source")

    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        # optional per-frame debug logging for the full pipeline
        try:
            import os, logging

            if os.environ.get("FWM_DEBUG", "0") == "1":
                logger = logging.getLogger("fwmodel.pipeline")
                logger.setLevel(logging.DEBUG)
                logger.debug("Frame %d: read ok=%s frame_shape=%s", frame_index, ok, getattr(frame, "shape", None))
        except Exception:
            pass
        # run detector -> tracker -> extractor so detections receive stable tracking IDs
        detections = extractor.detector.detect(frame)
        if hasattr(extractor, "tracker") and extractor.tracker is not None:
            extractor.tracker.update(detections, frame_index)
        scene = extractor.extract(frame, frame_index=frame_index, detections=detections)
        observations = [Observation(frame=frame_index, label=item["label"], confidence=item.get("confidence", 0.0), state=item, tracking_id=item.get("tracking_id")) for item in scene.objects]
        try:
            import os, logging
            if os.environ.get("FWM_DEBUG", "0") == "1":
                logger = logging.getLogger("fwmodel.pipeline")
                logger.debug("Frame %d: detector->observations=%d", frame_index, len(observations))
        except Exception:
            pass
        reconciler.reconcile(observations, frame_index)
        snapshot = world_model.snapshot()
        try:
            import os, logging
            if os.environ.get("FWM_DEBUG", "0") == "1":
                logger = logging.getLogger("fwmodel.pipeline")
                logger.debug("Frame %d: snapshot.objects=%d", frame_index, len(snapshot.get("objects", [])))
        except Exception:
            pass
        database.save_objects(snapshot.get("objects", []))
        database.save_events(snapshot.get("events", []))
        database.save_relationships(snapshot.get("relationships", []))
        annotated = visualizer.annotate_frame(frame, [], frame_index, scene.scene_type, world_snapshot=snapshot)
        cv2.imshow("FaceDepthWorldModel", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        frame_index += 1
    cap.release()
    cv2.destroyAllWindows()
    return query_engine.query("current world state")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run the monocular face depth and world model demo")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--video", default=None)
    args = parser.parse_args()
    config = load_config(args.config)
    result = run_demo(config, args.video)
    print(json.dumps(result, indent=2))

>>>>>>> 736ce46bf2dca6106c5f3a0b3729862735fc0209

if __name__ == "__main__":
    main()
