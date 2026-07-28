"""Query layer for extracting relevant world model slices."""

from src.world_model import TextWorldModel

class QueryLayer:
    def __init__(self, world_model: TextWorldModel):
        self.world_model = world_model

    def get_world_slice(self) -> str:
        """Format the agent's current knowledge into a text prompt slice."""
        curr = self.world_model.current_room
        if not curr:
            return "You have no knowledge of the world yet."
        
        room = self.world_model.map.get(curr)
        if not room:
            return "You are lost in the void."

        slice_text = [
            f"Current Location: {room.name}",
            f"Description: {room.description}"
        ]

        if room.exits:
            exits = [f"{direction} (leads to {dest})" for direction, dest in room.exits.items()]
            slice_text.append(f"Known Exits: {', '.join(exits)}")
        else:
            slice_text.append("Known Exits: None")

        if room.objects:
            slice_text.append(f"Visible Objects: {', '.join(room.objects)}")
            
        inv = self.world_model.inventory
        slice_text.append(f"Inventory: {', '.join(inv) if inv else 'Empty'}")
        
        return "\n".join(slice_text)
