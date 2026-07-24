"""Geometry helpers for monocular depth and angle estimation."""

from __future__ import annotations

import math
from typing import Dict, Tuple

from src.camera import CameraIntrinsics


def estimate_depth(focal_length: float, face_width_m: float, face_width_px: float) -> float:
    """Estimate depth from face width using the pinhole camera model.

    The relation is derived from similar triangles:
    Z = (f * W) / w_px
    where Z is depth, f is focal length in pixels, W is the real face width,
    and w_px is the observed face width in pixels.
    """
    if face_width_px <= 0:
        raise ValueError("face_width_px must be positive")
    return (focal_length * face_width_m) / face_width_px


def estimate_angle(x: float, cx: float, focal_length: float) -> Tuple[float, float]:
    """Estimate horizontal angle from pixel position.

    theta = arctan((x - cx) / f)
    """
    if focal_length <= 0:
        raise ValueError("focal_length must be positive")
    angle_rad = math.atan2(x - cx, focal_length)
    angle_deg = math.degrees(angle_rad)
    return angle_deg, angle_rad


def pixel_to_camera_ray(x: float, y: float, camera: CameraIntrinsics) -> Tuple[float, float]:
    """Map image coordinates to a normalized camera ray in image plane coordinates."""
    dx = (x - camera.cx) / camera.focal_length_pixels
    dy = (y - camera.cy) / camera.focal_length_pixels
    return dx, dy


def compute_uncertainty(
    *,
    face_size: float,
    blur: float,
    detector_confidence: float,
    occlusion: float,
    motion: float,
    visibility: float,
) -> Dict[str, float]:
    """Compute uncertainty metrics for depth, angle, and classification."""
    depth_uncertainty = 0.2 + (1.0 - face_size) * 0.8 + blur * 0.5 + occlusion * 0.4 + motion * 0.3
    angle_uncertainty = 0.3 + (1.0 - detector_confidence) * 1.0 + occlusion * 0.3 + motion * 0.2
    classification_uncertainty = 0.1 + (1.0 - visibility) * 0.5 + blur * 0.2 + occlusion * 0.2
    return {
        "depth_uncertainty": max(0.0, min(2.0, depth_uncertainty)),
        "angle_uncertainty": max(0.0, min(10.0, angle_uncertainty)),
        "classification_uncertainty": max(0.0, min(1.0, classification_uncertainty)),
    }
