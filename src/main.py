"""Entry point for the Text World Agent Loop."""

import time

from src.environment import TextEnvironment
from src.world_model import TextWorldModel
from src.database import WorldDatabase
from src.updater import Updater
from src.query import QueryLayer
from src.agent import HeuristicAgent

def main():
    print("Initializing Text World Agent...")
    env = TextEnvironment()
    db = WorldDatabase()
    
    world_model = TextWorldModel()
    updater = Updater(world_model)
    query_layer = QueryLayer(world_model)
    agent = HeuristicAgent(objective="Find the treasure")

    # Start game
    response = env.reset()
    updater.update("look", response)
    
    # Agent Loop
    step = 0
    while step < 15:
        print(f"\n--- Step {step} ---")
        
        # 1. Query Layer extracts slice
        world_slice = query_layer.get_world_slice()
        print(f"[Query Layer Output]\n{world_slice}\n")
        
        # 2. Agent decides action
        action = agent.decide_action(world_slice)
        print(f"[*] Agent decides to: {action}")
        
        # Check win condition
        if "treasure" in world_model.inventory:
            print("\n>>> The agent has found the treasure! Objective complete. <<<")
            break

        # 3. Environment responds
        previous_room = world_model.current_room
        response = env.step(action)
        print(f"\n[Environment Output]\n{response}\n")
        
        # 4. Updater updates world model
        updater.update(action, response, previous_room)
        
        # Save state
        db.save_state(world_model.snapshot())
        
        step += 1

    print("\nFinal World Model Snapshot:")
    import json
    print(json.dumps(world_model.snapshot(), indent=2))

if __name__ == "__main__":
    main()
