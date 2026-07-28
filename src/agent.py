"""Agent decision logic for Text World."""

import random

class HeuristicAgent:
    def __init__(self, objective: str):
        self.objective = objective

    def decide_action(self, world_slice: str) -> str:
        """Decide the next action based on the current world slice."""
        lines = world_slice.split("\n")
        
        objects = []
        exits = []
        
        for line in lines:
            if line.startswith("Visible Objects:"):
                ob_str = line.replace("Visible Objects:", "").strip()
                if ob_str and ob_str != "None":
                    objects = [o.strip() for o in ob_str.split(",")]
            elif line.startswith("Known Exits:"):
                ex_str = line.replace("Known Exits:", "").strip()
                if ex_str and ex_str != "None":
                    exits = [e.split(" (")[0].strip() for e in ex_str.split(",")]

        # Simple heuristic logic:
        # 1. If we see the treasure, take it
        if "treasure" in objects:
            return "take treasure"
            
        # 2. If we see anything else, take it
        if objects:
            return f"take {objects[0]}"
            
        # 3. Go through random exit
        if exits:
            return f"go {random.choice(exits)}"
            
        return "look"
