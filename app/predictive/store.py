import hashlib
import json
import sqlite3
from pathlib import Path
from threading import RLock
from datetime import datetime, timezone


class PredictiveStore:
    """SQLite persistence for snapshots and paper orders; no live trading credentials."""
    def __init__(self, path: str):
        self.path = path
        self._lock = RLock()
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("""CREATE TABLE IF NOT EXISTS market_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT, market_id TEXT NOT NULL,
                outcome TEXT NOT NULL, probability TEXT NOT NULL, volume TEXT NOT NULL,
                liquidity TEXT NOT NULL, observed_at TEXT NOT NULL)""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_market ON market_snapshots(market_id, outcome, id)")
            db.execute("""CREATE TABLE IF NOT EXISTS paper_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT, market_id TEXT NOT NULL,
                token_id TEXT NOT NULL, side TEXT NOT NULL, limit_price TEXT NOT NULL,
                requested_size TEXT NOT NULL, filled_size TEXT NOT NULL,
                average_price TEXT, fee TEXT NOT NULL, status TEXT NOT NULL,
                created_at TEXT NOT NULL, record_hash TEXT NOT NULL)""")

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def previous_snapshot(self, market_id: str, outcome: str):
        with self._lock, self._connect() as db:
            row = db.execute("SELECT probability FROM market_snapshots WHERE market_id=? AND outcome=? ORDER BY id DESC LIMIT 1",
                             (market_id, outcome)).fetchone()
        if not row:
            return None
        from decimal import Decimal
        return Decimal(row[0])

    def record_snapshot(self, market_id: str, outcome: str, probability, volume, liquidity):
        observed_at = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO market_snapshots(market_id,outcome,probability,volume,liquidity,observed_at) VALUES(?,?,?,?,?,?)",
                       (market_id, outcome, str(probability), str(volume), str(liquidity), observed_at))

    def record_paper_order(self, order: dict) -> dict:
        created_at = datetime.now(timezone.utc).isoformat()
        canonical = json.dumps(order, sort_keys=True, separators=(",", ":"))
        previous_hash = "GENESIS"
        with self._lock, self._connect() as db:
            row = db.execute("SELECT record_hash FROM paper_orders ORDER BY id DESC LIMIT 1").fetchone()
            if row:
                previous_hash = row[0]
            digest = hashlib.sha256((previous_hash + canonical + created_at).encode()).hexdigest()
            db.execute("""INSERT INTO paper_orders(market_id,token_id,side,limit_price,requested_size,
                filled_size,average_price,fee,status,created_at,record_hash) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (order["market_id"], order["token_id"], order["side"], order["limit_price"],
                 order["requested_size"], order["filled_size"], order.get("average_price"),
                 order["fee"], order["status"], created_at, digest))
        return {**order, "created_at": created_at, "record_hash": digest, "mode": "paper"}
