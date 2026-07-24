"""Simple online tracker with stable IDs and IoU-based matching."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import logging
import os


@dataclass
class Track:
    """A tracked entity."""

    track_id: int
    label: str
    bbox: Tuple[float, float, float, float]
    confidence: float
    last_seen: int = 0
    hits: int = 1
    age: int = 0


class Tracker:
    """Minimal tracker with stable IDs and simple hit counting."""

    def __init__(self, max_age: int = 8, min_hits: int = 2):
        self.max_age = max_age
        self.min_hits = min_hits
        self.next_id = 1
        self.tracks: Dict[int, Track] = {}
        self.frame_index = 0

    def update(self, detections: List[object], frame_index: int) -> List[Track]:
        """Associate detections to existing tracks and create new ones."""
        self.frame_index = frame_index
        matched_ids = set()
        for detection in detections:
            best_track = None
            best_iou = 0.0
            for track_id, track in self.tracks.items():
                if track.label != detection.label:
                    continue
                iou = self._iou(track.bbox, detection.bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_track = track_id
            if best_track is not None and best_iou > 0.1:
                track = self.tracks[best_track]
                track.bbox = detection.bbox
                track.confidence = max(track.confidence, detection.confidence)
                track.last_seen = frame_index
                track.age = 0
                track.hits += 1
                detection.tracking_id = best_track
                matched_ids.add(best_track)
            else:
                new_id = self.next_id
                self.next_id += 1
                detection.tracking_id = new_id
                self.tracks[new_id] = Track(
                    track_id=new_id,
                    label=detection.label,
                    bbox=detection.bbox,
                    confidence=detection.confidence,
                    last_seen=frame_index,
                    hits=1,
                    age=0,
                )
                matched_ids.add(new_id)

        for track_id, track in list(self.tracks.items()):
            if track_id not in matched_ids:
                track.age += 1
                if track.age > self.max_age:
                    del self.tracks[track_id]

        active_tracks = [track for track in self.tracks.values() if frame_index - track.last_seen <= self.max_age]
        # optional debug logging
        try:
            if os.environ.get("FWM_DEBUG", "0") == "1":
                logger = logging.getLogger("fwmodel.tracker")
                logger.setLevel(logging.DEBUG)
                logger.debug("Tracker output count=%d", len(active_tracks))
        except Exception:
            pass
        return sorted(active_tracks, key=lambda track: track.track_id)

    def _iou(self, bbox_a: Tuple[float, float, float, float], bbox_b: Tuple[float, float, float, float]) -> float:
        """Compute intersection-over-union for two boxes."""
        x1 = max(bbox_a[0], bbox_b[0])
        y1 = max(bbox_a[1], bbox_b[1])
        x2 = min(bbox_a[2], bbox_b[2])
        y2 = min(bbox_a[3], bbox_b[3])
        inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        area_a = max(0.0, bbox_a[2] - bbox_a[0]) * max(0.0, bbox_a[3] - bbox_a[1])
        area_b = max(0.0, bbox_b[2] - bbox_b[0]) * max(0.0, bbox_b[3] - bbox_b[1])
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0
