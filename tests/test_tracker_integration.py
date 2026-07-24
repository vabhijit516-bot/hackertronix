import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.main import build_pipeline, load_config
from src.camera import CameraIntrinsics
import numpy as np


def make_one_object_frame():
    import cv2
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame, (100, 100), (200, 200), (255, 255, 255), -1)
    return frame


def test_tracking_id_persistence():
    config = load_config("config/config.yaml")
    camera, extractor, reconciler, query_engine, visualizer, world_model = build_pipeline(config)
    assert hasattr(extractor, "tracker"), "Extractor must have tracker attached"
    frame0 = make_one_object_frame()
    frame1 = make_one_object_frame()

    # Frame 0
    detections0 = extractor.detector.detect(frame0)
    extractor.tracker.update(detections0, 0)
    scene0 = extractor.extract(frame0, frame_index=0, detections=detections0)
    observations0 = [__import__("src.world_model", fromlist=["Observation"]).Observation(frame=0, label=item["label"], confidence=item.get("confidence", 0.0), state=item, tracking_id=item.get("tracking_id")) for item in scene0.objects]
    reconciler.reconcile(observations0, 0)
    snap0 = world_model.snapshot()
    ids0 = [obj.get("tracking_id") for obj in snap0.get("objects", [])]

    # Frame 1
    detections1 = extractor.detector.detect(frame1)
    extractor.tracker.update(detections1, 1)
    scene1 = extractor.extract(frame1, frame_index=1, detections=detections1)
    observations1 = [__import__("src.world_model", fromlist=["Observation"]).Observation(frame=1, label=item["label"], confidence=item.get("confidence", 0.0), state=item, tracking_id=item.get("tracking_id")) for item in scene1.objects]
    reconciler.reconcile(observations1, 1)
    snap1 = world_model.snapshot()
    ids1 = [obj.get("tracking_id") for obj in snap1.get("objects", [])]

    # There should be at least one object and its tracking_id should persist across frames
    assert len(ids0) >= 1
    assert len(ids1) >= 1
    # Compare first tracking ids (if multiple objects exist, at least one should match)
    assert any(i in ids1 for i in ids0), f"No persistent tracking_id across frames: {ids0} vs {ids1}"
