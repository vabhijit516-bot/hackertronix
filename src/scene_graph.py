"""Simple scene graph for representing relationships between entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Edge:
    """A relationship edge between two entities."""

    source: str
    relation: str
    target: str
    confidence: float = 0.5
    frame: int = 0


@dataclass
class SceneGraph:
    """Mutable scene graph for the world model."""

    edges: List[Edge] = field(default_factory=list)

    def add_edge(self, source: str, relation: str, target: str, confidence: float = 0.5, frame: int = 0) -> None:
        """Add or update a relationship edge."""
        for edge in self.edges:
            if edge.source == source and edge.relation == relation and edge.target == target:
                edge.confidence = confidence
                edge.frame = frame
                return
        self.edges.append(Edge(source=source, relation=relation, target=target, confidence=confidence, frame=frame))

    def query(self, source: Optional[str] = None, relation: Optional[str] = None, target: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query edges by optional filters."""
        result = []
        for edge in self.edges:
            if source and edge.source != source:
                continue
            if relation and edge.relation != relation:
                continue
            if target and edge.target != target:
                continue
            result.append({"source": edge.source, "relation": edge.relation, "target": edge.target, "confidence": edge.confidence, "frame": edge.frame})
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the graph to JSON-friendly data."""
        return {"edges": self.query()}
