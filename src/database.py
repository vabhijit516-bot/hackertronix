"""SQLite-backed persistence for the world model."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class WorldDatabase:
    """Persist world model state into SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or "results/world_model.sqlite3")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connect()
        self._initialize_schema()

    def _connect(self) -> None:
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def _initialize_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS objects (
                id INTEGER PRIMARY KEY,
                label TEXT NOT NULL,
                tracking_id INTEGER,
                confidence REAL,
                uncertainty REAL,
                first_seen INTEGER,
                last_seen INTEGER,
                observation_count INTEGER,
                state TEXT,
                payload TEXT
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                event_id TEXT,
                timestamp INTEGER,
                frame INTEGER,
                confidence REAL,
                related_objects TEXT,
                description TEXT
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY,
                source TEXT,
                relation TEXT,
                target TEXT,
                confidence REAL,
                frame INTEGER
            )
            """
        )
        self.connection.commit()

    def save_objects(self, objects: List[Dict[str, Any]]) -> None:
        """Persist objects to the database."""
        self.connection.execute("DELETE FROM objects")
        for obj in objects:
            self.connection.execute(
                "INSERT INTO objects (id, label, tracking_id, confidence, uncertainty, first_seen, last_seen, observation_count, state, payload) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    obj.get("id"),
                    obj.get("label"),
                    obj.get("tracking_id"),
                    obj.get("confidence"),
                    obj.get("uncertainty"),
                    obj.get("first_seen"),
                    obj.get("last_seen"),
                    obj.get("observation_count"),
                    obj.get("state"),
                    json.dumps(obj),
                ),
            )
        self.connection.commit()

    def save_events(self, events: List[Dict[str, Any]]) -> None:
        """Persist events."""
        self.connection.execute("DELETE FROM events")
        for event in events:
            self.connection.execute(
                "INSERT INTO events (event_id, timestamp, frame, confidence, related_objects, description) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event.get("event_id"),
                    event.get("timestamp"),
                    event.get("frame"),
                    event.get("confidence"),
                    json.dumps(event.get("related_objects", [])),
                    event.get("description"),
                ),
            )
        self.connection.commit()

    def save_relationships(self, relationships: List[Dict[str, Any]]) -> None:
        """Persist relationships."""
        self.connection.execute("DELETE FROM relationships")
        for relationship in relationships:
            self.connection.execute(
                "INSERT INTO relationships (source, relation, target, confidence, frame) VALUES (?, ?, ?, ?, ?)",
                (
                    relationship.get("source"),
                    relationship.get("relation"),
                    relationship.get("target"),
                    relationship.get("confidence"),
                    relationship.get("frame"),
                ),
            )
        self.connection.commit()

    def load_state(self) -> Dict[str, Any]:
        """Load the persisted state."""
        objects = [dict(row) for row in self.connection.execute("SELECT * FROM objects")]
        events = [dict(row) for row in self.connection.execute("SELECT * FROM events")]
        relationships = [dict(row) for row in self.connection.execute("SELECT * FROM relationships")]
        return {"objects": objects, "events": events, "relationships": relationships}
