"""Small debug harness to test object counting across the pipeline.

Usage: set environment variable FWM_DEBUG=1 to enable logging output.
"""
from pathlib import Path
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.main import build_pipeline, load_config
import numpy as np


def make_blank(width=640, height=480, channels=3):
    return np.zeros((height, width, channels), dtype=np.uint8)


def make_one_object_frame():
    frame = make_blank()
    cv2 = __import__("cv2")
    cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), -1)
    return frame


def make_many_objects_frame():
    frame = make_blank()
    cv2 = __import__("cv2")
    for i in range(5):
        x = 20 + i * 100
        cv2.rectangle(frame, (x, 50), (x + 60, 200), (255, 255, 255), -1)
    return frame


def run_rounds():
    config = load_config("config/config.yaml")
    camera, extractor, reconciler, query_engine, visualizer, world_model = build_pipeline(config)
    frames = [make_blank(), make_one_object_frame(), make_many_objects_frame()]
    for i, frame in enumerate(frames):
        scene = extractor.extract(frame, frame_index=i)
        observations = [__import__("src.world_model", fromlist=["Observation"]).Observation(frame=i, label=item["label"], confidence=item.get("confidence", 0.0), state=item, tracking_id=item.get("tracking_id")) for item in scene.objects]
        reconciler.reconcile(observations, i)
        snapshot = world_model.snapshot()
        print(f"Round {i}: detector={len(scene.objects)} faces={len(scene.faces)} world_objects={len(snapshot.get('objects', []))}")


if __name__ == "__main__":
    run_rounds()
