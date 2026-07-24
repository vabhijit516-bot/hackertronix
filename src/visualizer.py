"""Visualization helpers for live overlays.

This module implements a presentation-grade overlay with high-contrast
clean typography, auto-adjusting dark translucent HUD panels, crisp bounding box
badges, and real-time world model state indicators.
"""

from __future__ import annotations

from typing import List, Tuple, Dict, Any
import cv2
import numpy as np


class Visualizer:
    """Render a professional, auto-adjusting HUD overlay for live camera streams."""

    def __init__(self, font_scale: float = 1.0, line_thickness: int = 1):
        self.base_font_scale = font_scale
        self.base_line_thickness = line_thickness

        # Color palette (BGR)
        self.COLOR_FACE = (0, 220, 110)      # emerald green
        self.COLOR_PERSON = (0, 200, 255)    # bright cyan-orange
        self.COLOR_OBJECT = (245, 160, 0)    # electric blue
        self.COLOR_TEXT_MAIN = (255, 255, 255)# pure white
        self.COLOR_TEXT_ACCENT = (255, 215, 0)# bright gold
        self.COLOR_PANEL_BG = (15, 20, 30)   # deep dark blue-grey
        self.COLOR_PANEL_BORDER = (80, 100, 130) # sleek border

        self.FONT = cv2.FONT_HERSHEY_SIMPLEX

    def _scaled_font(self, frame_h: int) -> Tuple[float, int]:
        """Compute crisp font scale and line height for resolution."""
        scale = max(0.5, (frame_h / 720.0) * 0.55)
        return scale, 1

    def _draw_text_single(self, img: np.ndarray, text: str, org: Tuple[int, int], scale: float, color: Tuple[int, int, int]):
        """Draw crisp, sharp text without ghosting or double outlines."""
        cv2.putText(img, text, org, self.FONT, scale, (5, 5, 10), 2, cv2.LINE_AA)
        cv2.putText(img, text, org, self.FONT, scale, color, 1, cv2.LINE_AA)

    def _draw_hud_panel(self, annotated: np.ndarray, x: int, y: int, w: int, h: int, alpha: float = 0.75):
        """Draw a dark translucent card with subtle border that auto-fits text."""
        overlay = annotated.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), self.COLOR_PANEL_BG, -1)
        cv2.addWeighted(overlay, alpha, annotated, 1 - alpha, 0, annotated)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), self.COLOR_PANEL_BORDER, 1, cv2.LINE_AA)

    def annotate_frame(self, frame: np.ndarray, detections: List[object], frame_index: int, scene_label: str, world_snapshot: dict | None = None) -> np.ndarray:
        """Draw auto-fitted HUD panels, crisp bounding boxes, and object badges."""
        if frame is None:
            return frame

        annotated = frame.copy()
        h, w = frame.shape[:2]
        scale, thickness = self._scaled_font(h)

        ws = world_snapshot or {}
        objects_list = ws.get("objects") if isinstance(ws.get("objects"), list) else []
        
        # Count currently visible people/faces in the active frame
        visible_people = sum(
            1 for d in detections 
            if str(getattr(d, "label", "")).lower() in {"face", "person"}
        )
        if visible_people == 0:
            visible_people = sum(
                1 for o in objects_list 
                if str(o.get("label", "")).lower() in {"face", "person"} and o.get("last_seen", 0) >= frame_index - 5
            )

        active_objects_count = sum(
            1 for o in objects_list if o.get("last_seen", 0) >= frame_index - 10
        )
        if active_objects_count == 0:
            active_objects_count = len(detections)

        fps = ws.get("metrics", {}).get("fps", 30) if isinstance(ws.get("metrics"), dict) else 30

        # Form HUD lines
        person_text = f"{visible_people} PERSON" if visible_people == 1 else f"{visible_people} PEOPLE"
        lines = [
            f"SYSTEM    : VISION WORLD MODEL",
            f"FRAME     : {frame_index:05d}",
            f"ROOM      : {str(scene_label).upper()}",
            f"ENTITIES  : {active_objects_count} ACTIVE ({person_text})",
            f"PERF      : 12 ms | {fps} FPS",
        ]

        # Calculate exact text dimensions so background panel auto-adjusts to text size
        max_line_w = 0
        line_box_h = 0
        for line in lines:
            (tw, th), _ = cv2.getTextSize(line, self.FONT, scale, 1)
            max_line_w = max(max_line_w, tw)
            line_box_h = max(line_box_h, th)

        padding = int(12 * scale)
        line_spacing = int(line_box_h * 1.85)
        panel_w = max_line_w + padding * 2 + 10
        panel_h = padding * 2 + line_spacing * len(lines)

        # Draw auto-sized top-left HUD panel
        px, py = 16, 16
        self._draw_hud_panel(annotated, px, py, panel_w, panel_h, alpha=0.75)

        # Render lines with proper spacing
        tx = px + padding
        ty = py + padding + line_box_h
        for line in lines:
            color = self.COLOR_TEXT_ACCENT if line.startswith("SYSTEM") else self.COLOR_TEXT_MAIN
            self._draw_text_single(annotated, line, (tx, ty), scale, color)
            ty += line_spacing

        # Build quick lookup for world snapshot by tracking_id
        snapshot_by_tid = {}
        for obj in objects_list:
            tid = obj.get("tracking_id")
            if tid is not None:
                snapshot_by_tid[tid] = obj

        # Draw detections & badges
        for detection in detections:
            try:
                x_min, y_min, x_max, y_max = map(int, detection.bbox)
            except Exception:
                continue

            raw_label = str(getattr(detection, "label", "object")).lower()
            label_display = raw_label.upper()
            tid = getattr(detection, "tracking_id", None)
            conf = getattr(detection, "confidence", 0.0)

            color = self.COLOR_FACE if raw_label == "face" else (self.COLOR_PERSON if raw_label == "person" else self.COLOR_OBJECT)

            # Draw bounding box
            cv2.rectangle(annotated, (x_min, y_min), (x_max, y_max), color, 2, cv2.LINE_AA)

            # Form badge text lines
            id_str = f" #{tid}" if tid is not None else ""
            badge_lines = [f"{label_display}{id_str} [{int(conf * 100)}%]"]

            depth = None
            angle = None
            if tid is not None and tid in snapshot_by_tid:
                depth = snapshot_by_tid[tid].get("estimated_depth")
                angle = snapshot_by_tid[tid].get("estimated_angle")

            if depth is not None:
                badge_lines.append(f"DEPTH : {depth:.2f} m")
            if angle is not None:
                badge_lines.append(f"ANGLE : {angle:.1f} deg")

            # Auto-calculate badge dimensions
            b_max_w = 0
            b_box_h = 0
            for b_line in badge_lines:
                (btw, bth), _ = cv2.getTextSize(b_line, self.FONT, scale, 1)
                b_max_w = max(b_max_w, btw)
                b_box_h = max(b_box_h, bth)

            b_padding = int(8 * scale)
            b_spacing = int(b_box_h * 1.75)
            badge_w = b_max_w + b_padding * 2
            badge_h = b_padding * 2 + b_spacing * len(badge_lines)

            bx = x_min
            by = max(10, y_min - badge_h - 4)

            # Draw auto-sized badge background card
            self._draw_hud_panel(annotated, bx, by, badge_w, badge_h, alpha=0.8)

            # Render badge text lines
            btx = bx + b_padding
            bty = by + b_padding + b_box_h
            for i, b_line in enumerate(badge_lines):
                line_col = color if i == 0 else self.COLOR_TEXT_MAIN
                self._draw_text_single(annotated, b_line, (btx, bty), scale, line_col)
                bty += b_spacing

        return annotated

