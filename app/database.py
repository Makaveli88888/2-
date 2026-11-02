import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any


class MemoryStore:
    """Small SQLite conversation store; replaceable by Postgres/pgvector later."""

    def __init__(self, database_path: str):
        self.database_path = database_path
        self._lock = Lock()
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._lock, self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, id)")

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("Unsupported message role")
        with self._lock, self._connect() as db:
            db.execute(
                "INSERT INTO messages(conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content),
            )

    def history(self, conversation_id: str, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self._lock, self._connect() as db:
            rows = db.execute(
                "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id DESC LIMIT ?",
                (conversation_id, limit),
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def clear(self, conversation_id: str) -> None:
        with self._lock, self._connect() as db:
            db.execute("DELETE FROM messages WHERE conversation_id=?", (conversation_id,))
