"""Updates the World Model based on text parsing of the environment response."""

import re
from typing import List, Tuple

from src.world_model import TextWorldModel

class Updater:
    def __init__(self, world_model: TextWorldModel):
        self.world_model = world_model

    def update(self, action: str, response: str, previous_room: str = None):
        """Parse game text and update the world model."""
        action = action.lower().strip()
        
        # 1. Update Inventory if we picked something up
        if action.startswith("take "):
            obj = action.replace("take ", "").strip()
            if "You take the" in response:
                if obj not in self.world_model.inventory:
                    self.world_model.inventory.append(obj)
        
        # 2. Extract Room info if we looked or moved
        if "===" in response:
            room_name, desc, exits, objects = self._parse_room(response)
            if room_name:
                self.world_model.current_room = room_name
                self.world_model.update_room(room_name, desc, exits, objects)

                # Link previous room if we just moved
                if action.startswith("go ") and previous_room:
                    direction = action.replace("go ", "").strip()
                    self.world_model.add_connection(previous_room, direction, room_name)

    def _parse_room(self, response: str) -> Tuple[str, str, List[str], List[str]]:
        lines = response.split("\n")
        room_name = ""
        desc_lines = []
        exits = []
        objects = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("===") and line.endswith("==="):
                room_name = line.replace("===", "").strip()
            elif line.startswith("Exits:"):
                ex_str = line.replace("Exits:", "").strip()
                exits = [e.strip() for e in ex_str.split(",") if e.strip()]
            elif line.startswith("You see:"):
                ob_str = line.replace("You see:", "").strip()
                objects = [o.strip() for o in ob_str.split(",") if o.strip()]
            elif not line.startswith("You head") and not line.startswith("==="):
                desc_lines.append(line)
                
        return room_name, " ".join(desc_lines), exits, objects
