"""Event detection engine for the vision world model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Event:
    """A world event emitted by the system."""

    event_id: str
    timestamp: int
    frame: int
    confidence: float
    related_objects: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the event to a JSON-friendly structure."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "frame": self.frame,
            "confidence": self.confidence,
            "related_objects": self.related_objects,
            "description": self.description,
        }


class EventDetector:
    """Simple heuristics-based event detector."""

    def __init__(self) -> None:
        self.events: List[Event] = []
        self._counter = 0

    def detect(self, previous_objects: Optional[List[Dict[str, Any]]] = None, current_objects: Optional[List[Dict[str, Any]]] = None, frame: int = 0) -> List[Event]:
        """Generate events from object transitions."""
        previous_labels = {item.get("label", "") for item in previous_objects or []}
        current_labels = {item.get("label", "") for item in current_objects or []}
        detected: List[Event] = []
        for label in sorted(current_labels - previous_labels):
            self._counter += 1
            detected.append(Event(event_id=f"event-{self._counter}", timestamp=frame, frame=frame, confidence=0.8, related_objects=[label], description=f"{label.title()} appeared"))
        for label in sorted(previous_labels - current_labels):
            self._counter += 1
            detected.append(Event(event_id=f"event-{self._counter}", timestamp=frame, frame=frame, confidence=0.8, related_objects=[label], description=f"{label.title()} removed"))
        self.events.extend(detected)
        return detected
