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
    scene = extractor.extract(None, frame_index=1)
    reconciler.reconcile([Observation(frame=1, label="chair", confidence=0.82)], 1)
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
