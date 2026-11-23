from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, MetaData, String, Table, Text, create_engine, func, select, delete
from sqlalchemy.engine import Engine


metadata = MetaData()
conversations = Table(
    "conversations", metadata,
    Column("id", String(100), primary_key=True),
    Column("owner_id", String(128), nullable=False, index=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("conversation_id", String(100), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("role", String(16), nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)


class MemoryStore:
    """SQLAlchemy conversation store with mandatory user ownership."""

    def __init__(self, database_url: str):
        self.engine: Engine = create_engine(database_url, pool_pre_ping=True, future=True)
        metadata.create_all(self.engine)

    def _ensure_owner(self, db, conversation_id: str, owner_id: str) -> None:
        row = db.execute(
            select(conversations.c.owner_id).where(conversations.c.id == conversation_id)
        ).first()
        if row is None:
            db.execute(conversations.insert().values(id=conversation_id, owner_id=owner_id))
        elif row.owner_id != owner_id:
            raise PermissionError("Conversation not found")

    def add_message(self, conversation_id: str, owner_id: str, role: str, content: str) -> None:
        if role not in {"user", "assistant"}:
            raise ValueError("Unsupported message role")
        with self.engine.begin() as db:
            self._ensure_owner(db, conversation_id, owner_id)
            db.execute(messages.insert().values(conversation_id=conversation_id, role=role, content=content))

    def history(self, conversation_id: str, owner_id: str, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self.engine.begin() as db:
            self._ensure_owner(db, conversation_id, owner_id)
            rows = db.execute(
                select(messages.c.role, messages.c.content)
                .where(messages.c.conversation_id == conversation_id)
                .order_by(messages.c.id.desc()).limit(limit)
            ).mappings().all()
        return [dict(row) for row in reversed(rows)]

    def clear(self, conversation_id: str, owner_id: str) -> None:
        with self.engine.begin() as db:
            self._ensure_owner(db, conversation_id, owner_id)
            db.execute(delete(messages).where(messages.c.conversation_id == conversation_id))

    def close(self) -> None:
        self.engine.dispose()
