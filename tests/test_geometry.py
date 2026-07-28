import math

from src.camera import CameraIntrinsics
from src.geometry import compute_uncertainty, estimate_angle, estimate_depth, pixel_to_camera_ray


def test_estimate_depth_basic():
    depth = estimate_depth(focal_length=600.0, face_width_m=0.16, face_width_px=120.0)
    assert math.isclose(depth, 0.8, rel_tol=1e-9)


def test_estimate_angle_basic():
    angle_deg, angle_rad = estimate_angle(x=320.0, cx=320.0, focal_length=600.0)
    assert angle_deg == 0.0
    assert angle_rad == 0.0


def test_pixel_to_camera_ray():
    ray = pixel_to_camera_ray(320.0, 240.0, CameraIntrinsics(600.0, 600.0, 320.0, 240.0))
    assert ray[0] == 0.0
    assert ray[1] == 0.0


def test_compute_uncertainty():
    uncertainty = compute_uncertainty(face_size=0.8, blur=0.2, detector_confidence=0.9, occlusion=0.1, motion=0.0, visibility=0.95)
    assert uncertainty["depth_uncertainty"] > 0
    assert uncertainty["angle_uncertainty"] > 0
    assert uncertainty["classification_uncertainty"] > 0
