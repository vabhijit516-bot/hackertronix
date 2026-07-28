"""Optional FastAPI server for exposing the world model."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI

from src.world_model import WorldModel


app = FastAPI(
    title="Vision World Model API",
    version="1.0.0",
)
world_model = WorldModel()


@app.get("/world")
def get_world() -> Dict[str, Any]:
    return world_model.snapshot()


@app.get("/scene")
def get_scene() -> Dict[str, Any]:
    return {"scene": "office", "snapshot": world_model.snapshot()}


@app.get("/faces")
def get_faces() -> Dict[str, Any]:
    return {"faces": []}


@app.get("/objects")
def get_objects() -> Dict[str, Any]:
    return {"objects": world_model.snapshot().get("objects", [])}


@app.get("/events")
def get_events() -> Dict[str, Any]:
    return {"events": world_model.events}


@app.get("/history/{object_id}")
def get_history(object_id: int) -> Dict[str, Any]:
    return {"object_id": object_id, "history": []}


@app.get("/frame/{frame_id}")
def get_frame(frame_id: int) -> Dict[str, Any]:
    return {"frame": frame_id, "snapshot": world_model.snapshot()}


@app.get("/relationships")
def get_relationships() -> Dict[str, Any]:
    return {"relationships": world_model.relationships}


@app.get("/metrics")
def get_metrics() -> Dict[str, Any]:
    return {"metrics": {"fps": 0, "latency_ms": 0}}


@app.get("/latest")
def get_latest() -> Dict[str, Any]:
    return world_model.snapshot()
