import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.api import app
from src.database import WorldDatabase
from src.extractor import VisionExtractor
from src.main import build_pipeline, load_config
from src.world_model import Observation, WorldModel
from src.camera import CameraIntrinsics


def test_end_to_end_pipeline_smoke():
    config = load_config("config/config.yaml")
    camera = CameraIntrinsics(600.0, 600.0, 320.0, 240.0)
    extractor = VisionExtractor(camera, 0.16)
    scene = extractor.extract(None, frame_index=3)
    assert scene.scene_type.lower() in {"office", "bedroom", "kitchen", "meeting room", "hallway"}


def test_api_app_exists():
    assert app is not None


def test_database_persistence_round_trip():
    db = WorldDatabase(db_path="results/test_end_to_end.sqlite3")
    db.save_objects([{"id": 1, "label": "chair", "tracking_id": 1, "confidence": 0.9, "uncertainty": 0.1, "first_seen": 1, "last_seen": 2, "observation_count": 2, "state": "updated"}])
    db.save_events([{"event_id": "e1", "timestamp": 2, "frame": 2, "confidence": 0.95, "related_objects": ["chair"], "description": "chair observed"}])
    state = db.load_state()
    assert state["objects"][0]["label"] == "chair"
    assert state["events"][0]["event_id"] == "e1"


def test_world_model_snapshot_is_json_serializable():
    world_model = WorldModel()
    world_model.update([Observation(frame=0, label="chair", confidence=0.8, state={"position": {"x": 0.1, "y": 0.2}})], 0)
    payload = json.dumps(world_model.snapshot())
    assert "chair" in payload
