from src.camera_calibration import CameraCalibrator
from src.database import WorldDatabase
from src.events import EventDetector
from src.performance import PerformanceProfiler
from src.scene_graph import SceneGraph
from src.world_model import Observation, WorldModel


def test_scene_graph_updates_and_queries():
    graph = SceneGraph()
    graph.add_edge("person", "using", "laptop", confidence=0.9, frame=1)
    result = graph.query(source="person")
    assert result[0]["target"] == "laptop"


def test_event_detector_emits_events():
    detector = EventDetector()
    events = detector.detect(previous_objects=[{"label": "chair"}], current_objects=[{"label": "chair"}, {"label": "laptop"}], frame=2)
    assert len(events) >= 1


def test_database_persists_state():
    database = WorldDatabase(db_path="results/test.sqlite3")
    database.save_objects([{"id": 1, "label": "chair", "tracking_id": 1, "confidence": 0.8, "uncertainty": 0.2, "first_seen": 0, "last_seen": 1, "observation_count": 1, "state": "updated"}])
    database.save_events([{"event_id": "e1", "timestamp": 1, "frame": 1, "confidence": 0.8, "related_objects": ["chair"], "description": "chair appeared"}])
    database.save_relationships([{"source": "person", "relation": "using", "target": "laptop", "confidence": 0.8, "frame": 1}])
    state = database.load_state()
    assert state["objects"][0]["label"] == "chair"


def test_calibration_module_builds_config():
    calibrator = CameraCalibrator()
    assert calibrator.checkerboard_size == (9, 6)


def test_performance_profiler_metrics():
    profiler = PerformanceProfiler()
    profiler.measure("noop", lambda: 1 + 1)
    metrics = profiler.metrics()
    assert metrics["fps"] >= 0
