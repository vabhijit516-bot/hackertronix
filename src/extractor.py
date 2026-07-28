"""Vision extractor with rich structured scene output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.camera import CameraIntrinsics
from src.detector import Detector
from src.face_estimator import FaceEstimator


@dataclass
class StructuredScene:
    """Structured scene description emitted by the extractor."""

    scene_type: str
    objects: List[Dict[str, Any]] = field(default_factory=list)
    faces: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[int] = None

    @property
    def scene(self) -> str:
        """Compatibility accessor for scene labels."""
        return self.scene_type

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the structured scene to JSON-compatible data."""
        return {
            "scene": self.scene_type,
            "objects": self.objects,
            "faces": self.faces,
            "relationships": self.relationships,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class VisionExtractor:
    """Extract a structured scene description from a single frame."""

    def __init__(self, camera: CameraIntrinsics, average_face_width_m: float, detector: Optional[Detector] = None):
        self.camera = camera
        self.average_face_width_m = average_face_width_m
        self.detector = detector or Detector()
        self.face_estimator = FaceEstimator(camera, average_face_width_m)

    def extract(self, frame, frame_index: int = 0, detections: Optional[List[Any]] = None) -> StructuredScene:
        """Return a scene description with entities, relationships, and metadata."""
        detections = detections or self.detector.detect(frame)
        face_payloads: List[Dict[str, Any]] = []
        object_payloads: List[Dict[str, Any]] = []
        for detection in detections:
            if detection.label.lower() == "face":
                estimate = self.face_estimator.estimate(detection.bbox, confidence=detection.confidence)
                face_payloads.append(
                    {
                        "id": estimate.id,
                        "depth_m": round(estimate.depth_m, 3),
                        "angle_deg": round(estimate.angle_deg, 3),
                        "angle_rad": round(estimate.angle_rad, 3),
                        "confidence": round(estimate.confidence, 3),
                        "uncertainty": estimate.uncertainty,
                        "bbox": detection.bbox,
                        "center": detection.center,
                        "tracking_id": detection.tracking_id,
                    }
                )
            else:
                object_payloads.append(
                    {
                        "label": detection.label,
                        "confidence": round(detection.confidence, 3),
                        "bbox": detection.bbox,
                        "center": detection.center,
                        "position": detection.position,
                        "tracking_id": detection.tracking_id,
                    }
                )

        scene_type = self.infer_scene_type(object_payloads + face_payloads)
        relationships = self.build_relationships(object_payloads, face_payloads)
        brightness = self.estimate_brightness(frame) if frame is not None else 0.5
        metadata = {
            "lighting": "bright" if brightness > 120 else "dim",
            "confidence": round(max((item.get("confidence", 0.0) for item in object_payloads + face_payloads), default=0.0), 3),
            "entity_count": len(object_payloads) + len(face_payloads),
        }
        return StructuredScene(
            scene_type=scene_type.lower(),
            objects=object_payloads,
            faces=face_payloads,
            relationships=relationships,
            metadata=metadata,
            timestamp=frame_index,
        )

    def infer_scene_type(self, objects: List[Dict[str, Any]]) -> str:
        """Infer room classification dynamically based on all detected objects."""
        labels = {str(item.get("label", "")).lower() for item in objects}

        if any(l in labels for l in {"bed", "pillow", "blanket"}):
            return "Bedroom"
        if any(l in labels for l in {"couch", "sofa", "tv", "television", "remote"}):
            return "Living Room"
        if any(l in labels for l in {"sink", "stove", "refrigerator", "microwave", "bottle", "cup", "bowl", "wine glass"}):
            return "Kitchen"
        if any(l in labels for l in {"monitor", "laptop", "keyboard", "mouse"}):
            return "Office"
        if any(l in labels for l in {"desk", "book", "backpack"}):
            return "Meeting Room"
        if any(l in labels for l in {"door", "window"}):
            return "Hallway"

        return "Office"

    def build_relationships(self, objects: List[Dict[str, Any]], faces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create simple relationships between detected entities."""
        relationships: List[Dict[str, Any]] = []
        if faces and any(item.get("label") == "laptop" for item in objects):
            relationships.append({"person": "Person 1", "using": "Laptop"})
        if any(item.get("label") == "chair" for item in objects):
            relationships.append({"person": "Person 1", "on": "Chair"})
        return relationships

    def estimate_brightness(self, frame) -> float:
        """Estimate image brightness using the mean intensity."""
        if frame is None:
            return 0.5
        gray = frame.mean(axis=2)
        return float(gray.mean())
