"""Structured world model representing the agent's beliefs about the game state."""

from typing import Dict, List, Optional

class RoomNode:
    def __init__(self, name: str):
        self.name = name
        self.description: str = ""
        self.exits: Dict[str, str] = {}  # direction -> room_name
        self.objects: List[str] = []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "objects": self.objects
        }

class TextWorldModel:
    def __init__(self):
        self.current_room: Optional[str] = None
        self.inventory: List[str] = []
        self.map: Dict[str, RoomNode] = {}

    def get_or_create_room(self, name: str) -> RoomNode:
        if name not in self.map:
            self.map[name] = RoomNode(name)
        return self.map[name]

    def update_room(self, name: str, description: str, exits: List[str], objects: List[str]):
        room = self.get_or_create_room(name)
        room.description = description
        
        for ex in exits:
            if ex not in room.exits:
                room.exits[ex] = "unknown"
                
        room.objects = objects

    def add_connection(self, from_room: str, direction: str, to_room: str):
        fr = self.get_or_create_room(from_room)
        fr.exits[direction] = to_room

    def snapshot(self) -> dict:
        return {
            "current_room": self.current_room,
            "inventory": self.inventory,
            "map": {name: room.to_dict() for name, room in self.map.items()}
        }
