"""Lightweight webcam demo for live world-model visualization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import cv2
import yaml

from src.database import WorldDatabase
from src.extractor import VisionExtractor
from src.main import load_config, build_pipeline
from src.updater import StateReconciler
from src.visualizer import Visualizer
from src.world_model import Observation, WorldModel
from src.camera import CameraIntrinsics


def run_webcam_demo(config_path: Optional[str] = None) -> None:
    """Run a live webcam demo until the user presses 'q'."""
    config = load_config(config_path or "config/config.yaml")
    # Use build_pipeline so tracker and other components are consistent
    camera, extractor, reconciler, query_engine, visualizer, world_model = build_pipeline(config)
    database = WorldDatabase()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Unable to open webcam")

    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        # detector -> tracker -> extractor
        detections = extractor.detector.detect(frame)
        if hasattr(extractor, "tracker") and extractor.tracker is not None:
            extractor.tracker.update(detections, frame_index)
        scene = extractor.extract(frame, frame_index=frame_index, detections=detections)
        observations = [Observation(frame=frame_index, label=item["label"], confidence=item.get("confidence", 0.0), state=item, tracking_id=item.get("tracking_id")) for item in scene.objects]
        reconciler.reconcile(observations, frame_index)
        snapshot = world_model.snapshot()
        database.save_objects(snapshot.get("objects", []))
        database.save_events(snapshot.get("events", []))
        database.save_relationships(snapshot.get("relationships", []))
        # pass detections to visualizer so boxes and labels can be rendered
        annotated = visualizer.annotate_frame(frame, detections, frame_index, scene.scene_type, world_snapshot=snapshot)
        cv2.imshow("Webcam Demo", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        frame_index += 1

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_webcam_demo()
