"""Simple demo script for narrating the project in a live presentation."""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.main import build_pipeline, load_config
from src.world_model import Observation


def run_demo_script() -> None:
    config = load_config(Path("config/config.yaml"))
    _, extractor, reconciler, query_engine, visualizer, world_model = build_pipeline(config)
    # Run detector -> tracker -> extractor sequence for a single demo frame (None = synthetic / no-op)
    detections = extractor.detector.detect(None)
    if hasattr(extractor, "tracker") and extractor.tracker is not None:
        extractor.tracker.update(detections, 1)
    scene = extractor.extract(None, frame_index=1, detections=detections)
    # reconcile using any observed items (keeps behavior compatible)
    observations = [Observation(frame=1, label=item.get("label", "object"), confidence=item.get("confidence", 0.0), state=item, tracking_id=item.get("tracking_id")) for item in scene.objects]
    reconciler.reconcile(observations, 1)
    print(json.dumps({
        "scene": scene.scene_type,
        "faces": scene.faces,
        "world_state": query_engine.query("current world state"),
    }, indent=2))


def main() -> None:
    """Compatibility wrapper for automation and validation scripts."""
    run_demo_script()


if __name__ == "__main__":
    main()
