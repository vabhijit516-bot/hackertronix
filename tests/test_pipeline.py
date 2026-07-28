from src.camera import CameraIntrinsics
from src.extractor import VisionExtractor
from src.query import QueryEngine
from src.updater import StateReconciler
from src.world_model import Observation, WorldModel


def test_world_model_and_query():
    world_model = WorldModel()
    reconciler = StateReconciler(world_model)
    query_engine = QueryEngine(world_model)
    reconciler.reconcile([Observation(frame=0, label="chair", confidence=0.8)], 0)
    result = query_engine.query("current world state")
    assert result["frame"] == 0
    assert len(result["objects"]) >= 1


def test_extractor_structure():
    camera = CameraIntrinsics(600.0, 600.0, 320.0, 240.0)
    extractor = VisionExtractor(camera, 0.16)
    scene = extractor.extract(None, frame_index=3)
    assert scene.scene_type == "office"
    assert scene.timestamp == 3
