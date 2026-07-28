"""Modular detector layer with local CPU-friendly backends."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import logging
import os


@dataclass
class Detection:
    """A single detection produced by the detector stack."""

    label: str
    bbox: Tuple[float, float, float, float]
    confidence: float
    center: Tuple[float, float]
    position: Dict[str, float] = field(default_factory=dict)
    tracking_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Detector:
    """Local detector with a pluggable face/object backend."""

    def __init__(self, labels: Optional[List[str]] = None, face_backend: str = "auto", object_backend: str = "auto"):
        self.labels = labels or ["person", "chair", "bottle", "laptop", "monitor", "keyboard", "table", "door", "window"]
        self.face_backend = face_backend
        self.object_backend = object_backend
        self._face_cascade = None
        self._hog = None
        self._mediapipe = None
        self._yolo_model = None
        self._init_backends()

    def _init_backends(self) -> None:
        """Initialize whichever local backend is available."""
        try:
            import mediapipe as mp

            self._mediapipe = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)
        except Exception:
            self._mediapipe = None

        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception:
            self._face_cascade = None

        try:
            self._hog = cv2.HOGDescriptor()
            self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        except Exception:
            self._hog = None

    def detect(self, frame: Optional[np.ndarray]) -> List[Detection]:
        """Return face and object detections for a frame."""
        if frame is None:
            return []
        if not isinstance(frame, np.ndarray):
            frame = np.array(frame, dtype=np.uint8)
        if frame.size == 0:
            return []

        detections: List[Detection] = []
        detections.extend(self._detect_faces(frame))
        detections.extend(self._detect_objects(frame))
        # optional debug logging when enabled via environment
        try:
            if os.environ.get("FWM_DEBUG", "0") == "1":
                logger = logging.getLogger("fwmodel.detector")
                logger.setLevel(logging.DEBUG)
                logger.debug("Detector output count=%d", len(detections))
        except Exception:
            pass
        return detections

    def _detect_faces(self, frame: np.ndarray) -> List[Detection]:
        """Detect faces using MediaPipe when available, else Haar cascades."""
        if self.face_backend == "mediapipe" and self._mediapipe is not None:
            return self._detect_faces_mediapipe(frame)
        if self._mediapipe is not None and self.face_backend != "cascade":
            return self._detect_faces_mediapipe(frame)
        if self._face_cascade is not None:
            return self._detect_faces_cascade(frame)
        return []

    def _detect_faces_mediapipe(self, frame: np.ndarray) -> List[Detection]:
        """Detect faces through MediaPipe face detection."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._mediapipe.process(rgb)
        detections: List[Detection] = []
        if not results.detections:
            return detections
        height, width = frame.shape[:2]
        for result in results.detections:
            box = result.location_data.relative_bounding_box
            x = int(box.xmin * width)
            y = int(box.ymin * height)
            w = int(box.width * width)
            h = int(box.height * height)
            bbox = (float(x), float(y), float(x + w), float(y + h))
            center = ((x + x + w) / 2.0, (y + y + h) / 2.0)
            confidence = float(result.score[0]) if result.score else 0.5
            detections.append(
                Detection(
                    label="face",
                    bbox=bbox,
                    confidence=confidence,
                    center=center,
                    position={"x": center[0] / max(1.0, width), "y": center[1] / max(1.0, height)},
                    metadata={"backend": "mediapipe"},
                )
            )
        return detections

    def _detect_faces_cascade(self, frame: np.ndarray) -> List[Detection]:
        """Use OpenCV Haar cascade as a robust fallback for faces."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        detections: List[Detection] = []
        height, width = frame.shape[:2]
        for (x, y, w, h) in faces:
            bbox = (float(x), float(y), float(x + w), float(y + h))
            center = (x + w / 2.0, y + h / 2.0)
            detections.append(
                Detection(
                    label="face",
                    bbox=bbox,
                    confidence=0.7,
                    center=center,
                    position={"x": center[0] / max(1.0, width), "y": center[1] / max(1.0, height)},
                    metadata={"backend": "cascade"},
                )
            )
        return detections

    def _detect_objects(self, frame: np.ndarray) -> List[Detection]:
        """Detect common objects using YOLO if installed, or local heuristics."""
        if self.object_backend != "heuristic":
            yolo_detections = self._detect_with_yolo(frame)
            if yolo_detections:
                return yolo_detections
        return self._detect_with_heuristics(frame)

    def _detect_with_yolo(self, frame: np.ndarray) -> List[Detection]:
        """Attempt to use Ultralytics YOLO if available."""
        try:
            from ultralytics import YOLO
        except Exception:
            return []

        if self._yolo_model is None:
            try:
                self._yolo_model = YOLO("yolov8n.pt")
            except Exception:
                try:
                    self._yolo_model = YOLO("yolov11n.pt")
                except Exception:
                    return []

        height, width = frame.shape[:2]
        try:
            results = self._yolo_model(frame, stream=False, conf=0.25, imgsz=320)
        except Exception:
            return []

        detections: List[Detection] = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                label = result.names.get(int(box.cls[0]), "object") if hasattr(result, "names") else "object"
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
                confidence = float(box.conf[0])
                detections.append(
                    Detection(
                        label=label.lower(),
                        bbox=(x1, y1, x2, y2),
                        confidence=confidence,
                        center=center,
                        position={"x": center[0] / max(1.0, width), "y": center[1] / max(1.0, height)},
                        metadata={"backend": "yolo"},
                    )
                )
        return detections

    def _detect_with_heuristics(self, frame: np.ndarray) -> List[Detection]:
        """Fallback heuristics for common objects on CPU."""
        detections: List[Detection] = []
        height, width = frame.shape[:2]
        if self._hog is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, found_w = self._hog.detectMultiScale(gray, winStride=(8, 8), padding=(4, 4), scale=1.05)
            for (x, y, w, h) in found:
                bbox = (float(x), float(y), float(x + w), float(y + h))
                center = (x + w / 2.0, y + h / 2.0)
                detections.append(
                    Detection(
                        label="person",
                        bbox=bbox,
                        confidence=0.6,
                        center=center,
                        position={"x": center[0] / max(1.0, width), "y": center[1] / max(1.0, height)},
                        metadata={"backend": "hog"},
                    )
                )
        if len(frame.shape) == 2:
            gray = frame
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # process contours sorted by area (largest first) and collect all sufficiently large contours
        contour_areas = [(cv2.contourArea(c), c) for c in contours]
        contour_areas.sort(key=lambda t: t[0], reverse=True)
        for area, contour in contour_areas:
            if area < 1000:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            bbox = (float(x), float(y), float(x + w), float(y + h))
            center = (x + w / 2.0, y + h / 2.0)
            label = "monitor" if w > 40 and h > 40 else "table"
            detections.append(
                Detection(
                    label=label,
                    bbox=bbox,
                    confidence=0.55,
                    center=center,
                    position={"x": center[0] / max(1.0, width), "y": center[1] / max(1.0, height)},
                    metadata={"backend": "heuristic"},
                )
            )
        return detections
