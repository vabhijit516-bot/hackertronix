"""Custom Text Adventure Environment."""

from typing import Dict, List

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[str, str] = {}
        self.objects: List[str] = []

class TextEnvironment:
    """Minimal text adventure engine."""
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.current_room: str = ""
        self.inventory: List[str] = []
        self._build_world()

    def _build_world(self):
        kitchen = Room("Kitchen", "You are in a dark, dirty kitchen. A faint smell of rot lingers.")
        kitchen.objects.append("knife")
        kitchen.exits["north"] = "Hallway"

        hallway = Room("Hallway", "A long hallway with flickering lights.")
        hallway.exits["south"] = "Kitchen"
        hallway.exits["east"] = "Library"

        library = Room("Library", "Dusty shelves full of old books.")
        library.objects.append("book")
        library.exits["west"] = "Hallway"
        library.exits["north"] = "Secret Room"

        secret = Room("Secret Room", "A small hidden room. It feels very cold.")
        secret.objects.append("treasure")
        secret.exits["south"] = "Library"

        self.rooms = {
            "Kitchen": kitchen,
            "Hallway": hallway,
            "Library": library,
            "Secret Room": secret
        }
        self.current_room = "Kitchen"

    def reset(self) -> str:
        """Resets the environment and returns the initial observation."""
        self._build_world()
        self.inventory = []
        return self._look()

    def step(self, action: str) -> str:
        """Executes an action and returns the game's response."""
        action = action.lower().strip()
        parts = action.split(" ")
        verb = parts[0]
        noun = " ".join(parts[1:]) if len(parts) > 1 else ""

        if verb == "look":
            return self._look()
        elif verb == "go":
            if not noun:
                return "Go where?"
            return self._go(noun)
        elif verb == "take":
            if not noun:
                return "Take what?"
            return self._take(noun)
        elif verb == "inventory":
            return f"You are carrying: {', '.join(self.inventory) if self.inventory else 'nothing'}."
        else:
            return "I don't understand that command. Available commands: look, go [direction], take [object], inventory."

    def _look(self) -> str:
        room = self.rooms[self.current_room]
        desc = [f"=== {room.name} ===", room.description]
        if room.exits:
            exits = ", ".join(room.exits.keys())
            desc.append(f"Exits: {exits}")
        if room.objects:
            objs = ", ".join(room.objects)
            desc.append(f"You see: {objs}")
        return "\n".join(desc)

    def _go(self, direction: str) -> str:
        room = self.rooms[self.current_room]
        if direction in room.exits:
            self.current_room = room.exits[direction]
            return f"You head {direction}.\n\n" + self._look()
        return "You can't go that way."

    def _take(self, obj: str) -> str:
        room = self.rooms[self.current_room]
        if obj in room.objects:
            room.objects.remove(obj)
            self.inventory.append(obj)
            return f"You take the {obj}.\n\n" + self._look()
        return "You don't see that here."
