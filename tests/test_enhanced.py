from src.detector import Detection, Detector
from src.extractor import VisionExtractor
from src.query import QueryEngine
from src.tracker import Tracker
from src.updater import StateReconciler
from src.world_model import Observation, WorldModel
from src.camera import CameraIntrinsics


def test_detector_returns_detections_for_placeholder_frame():
    detector = Detector()
    frame = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    detections = detector.detect(frame)
    assert isinstance(detections, list)


def test_extractor_builds_rich_scene_output():
    camera = CameraIntrinsics(600.0, 600.0, 320.0, 240.0)
    extractor = VisionExtractor(camera, 0.16)
    scene = extractor.extract(None, frame_index=3)
    assert scene.scene_type.lower() in {"office", "bedroom", "kitchen", "meeting room", "hallway"}
    assert isinstance(scene.relationships, list)


def test_tracker_assigns_stable_ids():
    tracker = Tracker(max_age=3, min_hits=1)
    detections = [Detection(label="chair", bbox=(0, 0, 10, 10), confidence=0.8, center=(5, 5))]
    tracks = tracker.update(detections, 0)
    assert tracks[0].track_id == 1


def test_world_model_and_reconciliation():
    world_model = WorldModel()
    reconciler = StateReconciler(world_model)
    reconciler.reconcile([Observation(frame=1, label="chair", confidence=0.8)], 1)
    assert any(obj.label == "chair" for obj in world_model.objects.values())


def test_query_engine_supports_world_queries():
    world_model = WorldModel()
    query_engine = QueryEngine(world_model)
    result = query_engine.query("current world state")
    assert "frame" in result
