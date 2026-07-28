"""SQLite-backed persistence for the text world model."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

class WorldDatabase:
    """Persist text world model state into SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "results/text_world_model.sqlite3")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connect()
        self._initialize_schema()

    def _connect(self) -> None:
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def _initialize_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY,
                current_room TEXT,
                inventory TEXT,
                map_json TEXT
            )
            """
        )
        self.connection.commit()

    def save_state(self, snapshot: Dict[str, Any]) -> None:
        """Persist snapshot to the database."""
        self.connection.execute("DELETE FROM game_state")
        self.connection.execute(
            "INSERT INTO game_state (id, current_room, inventory, map_json) VALUES (1, ?, ?, ?)",
            (
                snapshot.get("current_room"),
                json.dumps(snapshot.get("inventory", [])),
                json.dumps(snapshot.get("map", {})),
            ),
        )
        self.connection.commit()

    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load the persisted state."""
        row = self.connection.execute("SELECT * FROM game_state WHERE id=1").fetchone()
        if not row:
            return None
        return {
            "current_room": row["current_room"],
            "inventory": json.loads(row["inventory"]),
            "map": json.loads(row["map_json"])
        }
