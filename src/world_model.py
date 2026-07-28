<<<<<<< HEAD
"""Structured world model representing the agent's beliefs about the game state."""

from typing import Dict, List, Optional

class RoomNode:
    def __init__(self, name: str):
        self.name = name
        self.description: str = ""
        self.exits: Dict[str, str] = {}  # direction -> room_name
        self.objects: List[str] = []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "objects": self.objects
        }

class TextWorldModel:
    def __init__(self):
        self.current_room: Optional[str] = None
        self.inventory: List[str] = []
        self.map: Dict[str, RoomNode] = {}

    def get_or_create_room(self, name: str) -> RoomNode:
        if name not in self.map:
            self.map[name] = RoomNode(name)
        return self.map[name]

    def update_room(self, name: str, description: str, exits: List[str], objects: List[str]):
        room = self.get_or_create_room(name)
        room.description = description
        
        for ex in exits:
            if ex not in room.exits:
                room.exits[ex] = "unknown"
                
        room.objects = objects

    def add_connection(self, from_room: str, direction: str, to_room: str):
        fr = self.get_or_create_room(from_room)
        fr.exits[direction] = to_room

    def snapshot(self) -> dict:
        return {
            "current_room": self.current_room,
            "inventory": self.inventory,
            "map": {name: room.to_dict() for name, room in self.map.items()}
=======
"""Persistent world model for tracking entities and scene state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.events import EventDetector
from src.scene_graph import SceneGraph


@dataclass
class Observation:
    """Single observation of an entity."""

    frame: int
    label: str
    confidence: float
    state: Dict[str, Any] = field(default_factory=dict)
    tracking_id: Optional[int] = None


@dataclass
class TrackedObject:
    """Tracked object with history and uncertainty."""

    object_id: int
    label: str
    tracking_id: Optional[int]
    first_seen: int
    last_seen: int
    history: List[Observation] = field(default_factory=list)
    estimated_depth: Optional[float] = None
    estimated_angle: Optional[float] = None
    state: str = "created"
    confidence: float = 0.0
    uncertainty: float = 0.5
    observation_count: int = 0
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0})


@dataclass
class WorldModel:
    """Structured persistent world model."""

    objects: Dict[int, TrackedObject] = field(default_factory=dict)
    frame_index: int = 0
    events: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    scene_graph: SceneGraph = field(default_factory=SceneGraph)
    event_detector: EventDetector = field(default_factory=EventDetector)

    def update(self, observations: List[Observation], frame_index: int) -> None:
        """Add observations to the persistent model."""
        self.frame_index = frame_index
        previous_objects = [{"label": obj.label} for obj in self.objects.values()]
        for observation in observations:
            object_id = self._find_or_create(observation)
            entity = self.objects[object_id]
            entity.last_seen = frame_index
            entity.observation_count += 1
            entity.history.append(observation)
            entity.confidence = max(entity.confidence, observation.confidence)
            entity.uncertainty = max(0.05, entity.uncertainty - 0.02)
            entity.state = "updated"
            entity.position = observation.state.get("position", entity.position)
            entity.estimated_depth = observation.state.get("depth_m")
            entity.estimated_angle = observation.state.get("angle_deg")
        current_objects = [{"label": obj.label} for obj in self.objects.values()]
        detected_events = self.event_detector.detect(previous_objects, current_objects, frame_index)
        for event in detected_events:
            self.events.append(event.to_dict())
        self._update_relationships(observations, frame_index)
        # optional debug logging
        try:
            import os, logging

            if os.environ.get("FWM_DEBUG", "0") == "1":
                logger = logging.getLogger("fwmodel.world_model")
                logger.setLevel(logging.DEBUG)
                logger.debug("Frame %d: world_model.objects=%d", frame_index, len(self.objects))
        except Exception:
            pass

    def _find_or_create(self, observation: Observation) -> int:
        """Find an existing object or create a new tracked object."""
        # First, try to match by tracking_id when available
        for object_id, entity in self.objects.items():
            if observation.tracking_id is not None and entity.tracking_id == observation.tracking_id:
                return object_id

        # If no tracking_id, attempt spatial proximity-based matching to avoid merging all same-label detections
        obs_pos = observation.state.get("position") if isinstance(observation.state, dict) else None
        for object_id, entity in self.objects.items():
            if entity.label != observation.label:
                continue
            if obs_pos and entity.position:
                try:
                    dx = entity.position.get("x", 0.0) - obs_pos.get("x", 0.0)
                    dy = entity.position.get("y", 0.0) - obs_pos.get("y", 0.0)
                    dist = (dx * dx + dy * dy) ** 0.5
                except Exception:
                    dist = None
                # consider it the same object if within a small normalized distance
                if dist is not None and dist < 0.12:
                    return object_id

        object_id = len(self.objects) + 1
        self.objects[object_id] = TrackedObject(
            object_id=object_id,
            label=observation.label,
            tracking_id=observation.tracking_id,
            first_seen=self.frame_index,
            last_seen=self.frame_index,
            history=[observation],
            confidence=observation.confidence,
            uncertainty=0.5,
            observation_count=1,
            state="created",
        )
        return object_id

    def _update_relationships(self, observations: List[Observation], frame_index: int) -> None:
        """Update scene-graph relationships from current observations."""
        if not observations:
            return
        for observation in observations:
            if observation.label == "chair":
                self.scene_graph.add_edge(observation.label, "near", "person", confidence=0.5, frame=frame_index)
            if observation.label == "laptop":
                self.scene_graph.add_edge("person", "using", observation.label, confidence=0.5, frame=frame_index)
        self.relationships = self.scene_graph.query()

    def snapshot(self) -> Dict[str, Any]:
        """Return a JSON-friendly snapshot of the current world model."""
        return {
            "frame": self.frame_index,
            "objects": [
                {
                    "id": obj.object_id,
                    "label": obj.label,
                    "tracking_id": obj.tracking_id,
                    "confidence": round(obj.confidence, 3),
                    "uncertainty": round(obj.uncertainty, 3),
                    "first_seen": obj.first_seen,
                    "last_seen": obj.last_seen,
                    "observation_count": obj.observation_count,
                    "state": obj.state,
                    "history": [obs.frame for obs in obj.history[-5:]],
                    "estimated_depth": obj.estimated_depth,
                    "estimated_angle": obj.estimated_angle,
                }
                for obj in self.objects.values()
            ],
            "events": self.events,
            "relationships": self.relationships,
>>>>>>> 736ce46bf2dca6106c5f3a0b3729862735fc0209
        }
