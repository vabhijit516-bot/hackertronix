"""Face estimation pipeline for monocular depth and angle estimation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from src.camera import CameraIntrinsics
from src.geometry import compute_uncertainty, estimate_angle, estimate_depth


@dataclass
class FaceEstimate:
    """Structured estimate for one detected face."""

    id: str
    depth_m: float
    angle_deg: float
    angle_rad: float
    confidence: float
    bbox: Tuple[float, float, float, float]
    center: Tuple[float, float]
    face_width_px: float
    uncertainty: dict


class FaceEstimator:
    """Estimate face depth and angle from a face bounding box."""

    def __init__(self, camera: CameraIntrinsics, average_face_width_m: float, detector_confidence: float = 0.5):
        self.camera = camera
        self.average_face_width_m = average_face_width_m
        self.detector_confidence = detector_confidence
        self._face_counter = 0

    def estimate(
        self,
        bbox: Tuple[float, float, float, float],
        *,
        confidence: float,
        blur: float = 0.0,
        occlusion: float = 0.0,
        motion: float = 0.0,
        visibility: float = 1.0,
    ) -> FaceEstimate:
        """Estimate depth and angle from a face bounding box."""
        x_min, y_min, x_max, y_max = bbox
        width = max(1.0, x_max - x_min)
        height = max(1.0, y_max - y_min)
        face_width_px = max(width, height)
        center_x = (x_min + x_max) / 2.0
        center_y = (y_min + y_max) / 2.0
        depth = estimate_depth(
            focal_length=self.camera.focal_length_pixels,
            face_width_m=self.average_face_width_m,
            face_width_px=face_width_px,
        )
        angle_deg, angle_rad = estimate_angle(center_x, self.camera.cx, self.camera.focal_length_pixels)
        uncertainty = compute_uncertainty(
            face_size=min(1.0, face_width_px / 200.0),
            blur=blur,
            detector_confidence=confidence,
            occlusion=occlusion,
            motion=motion,
            visibility=visibility,
        )
        confidence_score = max(0.0, min(1.0, (confidence * 0.6) + (visibility * 0.25) + (max(0.0, 1.0 - blur) * 0.15)))
        self._face_counter += 1
        return FaceEstimate(
            id=f"face-{self._face_counter}",
            depth_m=depth,
            angle_deg=angle_deg,
            angle_rad=angle_rad,
            confidence=confidence_score,
            bbox=bbox,
            center=(center_x, center_y),
            face_width_px=face_width_px,
            uncertainty=uncertainty,
        )
