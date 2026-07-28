"""Camera intrinsics and camera-specific math."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CameraIntrinsics:
    """Container for pinhole camera intrinsics."""

    fx: float
    fy: float
    cx: float
    cy: float

    @property
    def focal_length_pixels(self) -> float:
        """Return a representative focal length in pixels."""
        return (self.fx + self.fy) / 2.0
