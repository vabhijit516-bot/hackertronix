"""State reconciliation logic for conflicting observations."""

from __future__ import annotations

from typing import Any, Dict, List

from src.world_model import Observation, WorldModel


class StateReconciler:
    """Merge new observations into the existing world model intelligently."""

    def __init__(self, world_model: WorldModel):
        self.world_model = world_model

    def reconcile(self, observations: List[Observation], frame_index: int) -> None:
        """Add observations while preserving history and tracking uncertainty."""
        # Prefer matching by tracking_id when available; do not deduplicate solely by label
        existing_by_tracking = {
            entity.tracking_id: entity for entity in self.world_model.objects.values() if entity.tracking_id is not None
        }
        for observation in observations:
            entity = None
            if observation.tracking_id is not None:
                entity = existing_by_tracking.get(observation.tracking_id)

            # If no match by tracking id, create a new tracked object for this observation
            if entity is None:
                self.world_model.update([observation], frame_index)
                self.world_model.events.append({"frame": frame_index, "event": "created", "label": observation.label})
                continue

            if observation.confidence < 0.35:
                entity.state = "uncertain"
                entity.uncertainty = max(entity.uncertainty, 0.7)
                self.world_model.events.append({"frame": frame_index, "event": "uncertain", "label": observation.label})
                continue

            entity.state = "updated"
            entity.confidence = max(entity.confidence, observation.confidence)
            entity.uncertainty = max(0.05, entity.uncertainty - 0.03)
            self.world_model.events.append({"frame": frame_index, "event": "updated", "label": observation.label})

        # Final pass to update relationships/events based on all observations
        self.world_model.update(observations, frame_index)
