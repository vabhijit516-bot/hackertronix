"""Basic camera calibration helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import yaml


class CameraCalibrator:
    """Estimate camera intrinsics from a checkerboard image set."""

    def __init__(self, checkerboard_size: Tuple[int, int] = (9, 6), square_size: float = 0.025):
        self.checkerboard_size = checkerboard_size
        self.square_size = square_size

    def calibrate(self, image_paths: list[Path]) -> Tuple[np.ndarray, np.ndarray, dict]:
        """Estimate camera matrix and distortion coefficients."""
        object_points = []
        image_points = []
        objp = np.zeros((self.checkerboard_size[0] * self.checkerboard_size[1], 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:self.checkerboard_size[0], 0:self.checkerboard_size[1]].T.reshape(-1, 2)
        objp *= self.square_size

        for path in image_paths:
            image = cv2.imread(str(path))
            if image is None:
                continue
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, self.checkerboard_size, None)
            if ret:
                object_points.append(objp)
                image_points.append(corners)

        if len(image_points) < 3:
            raise ValueError("At least 3 calibration images are required")

        ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(object_points, image_points, gray.shape[::-1], None, None)
        calibration = {"camera_matrix": camera_matrix.tolist(), "dist_coeffs": dist_coeffs.tolist()}
        return camera_matrix, dist_coeffs, calibration

    def save(self, calibration: dict, output_path: Optional[str] = None) -> None:
        """Persist calibration data to YAML."""
        path = Path(output_path or "camera.yaml")
        path.write_text(yaml.safe_dump(calibration), encoding="utf-8")
