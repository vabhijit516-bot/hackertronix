"""Query engine for inspecting the world state."""

from __future__ import annotations

from typing import Any, Dict, List

from src.world_model import WorldModel


class QueryEngine:
    """Simple JSON-oriented query interface over the world model."""

    def __init__(self, world_model: WorldModel):
        self.world_model = world_model

    def query(self, query_text: str) -> Dict[str, Any]:
        """Return structured JSON for common queries."""
        query_text = query_text.lower().strip()
        if query_text in {"current world", "current world state", "world state"}:
            return self.world_model.snapshot()
        if query_text.startswith("frame "):
            frame_id = int(query_text.split()[-1])
            return {"frame": frame_id, "status": "requested", "snapshot": self.world_model.snapshot()}
        if query_text.startswith("history of object"):
            object_id = query_text.split()[-3]
            return {"object_id": object_id, "history": []}
        if query_text in {"scene summary", "summary"}:
            return {"scene": "office", "objects": len(self.world_model.objects)}
        if query_text in {"current people", "people"}:
            return {"people": []}
        if query_text in {"current faces", "faces"}:
            return {"faces": []}
        if query_text in {"current chairs", "chairs"}:
            return {"chairs": [obj for obj in self.world_model.objects.values() if obj.label == "chair"]}
        if query_text in {"current laptops", "laptops"}:
            return {"laptops": [obj for obj in self.world_model.objects.values() if obj.label == "laptop"]}
        return {"query": query_text, "status": "unsupported"}
