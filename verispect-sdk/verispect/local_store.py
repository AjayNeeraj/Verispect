"""
local_store.py
SQLite database stored on the CLIENT'S machine (under ~/.verispect/).

Stores golden probe prompts — raw text that NEVER leaves this machine.
The server only ever sees a hash + embedding, never the prompt text itself.

Thread-safe: SQLite uses file-level locking; check_same_thread=False is safe
for concurrent reads from multiple threads in the same process.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("verispect")

_DEFAULT_DIR = Path.home() / ".verispect"
_DEFAULT_DB = _DEFAULT_DIR / "golden_probes.db"

# Maximum number of golden probes to keep locally.
# Oldest are pruned when this limit is exceeded.
_MAX_GOLDEN_PROBES = 500


class LocalStore:
    def __init__(self, db_path: Optional[str] = None):
        path = Path(db_path) if db_path else _DEFAULT_DB
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = str(path)
        self._init_db()

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        try:
            with self._connect() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS golden_probes (
                        golden_id    TEXT PRIMARY KEY,
                        prompt_hash  TEXT NOT NULL,
                        prompt_text  TEXT NOT NULL,
                        model        TEXT NOT NULL,
                        embedding    TEXT,
                        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_prompt_hash
                    ON golden_probes (prompt_hash)
                """)
                conn.commit()
        except Exception as e:
            logger.debug(f"LocalStore init error: {e}")

    # ── Write ─────────────────────────────────────────────────────────────────

    def save_golden(
        self,
        golden_id: str,
        prompt_hash: str,
        prompt_text: str,
        model: str,
        embedding: list,
    ) -> bool:
        """
        Persist a golden probe locally.
        Returns True if inserted, False if this prompt_hash already exists.
        Silently prunes oldest entries if _MAX_GOLDEN_PROBES is exceeded.
        """
        try:
            with self._connect() as conn:
                # Deduplicate by prompt_hash — don't store the same prompt twice
                existing = conn.execute(
                    "SELECT golden_id FROM golden_probes WHERE prompt_hash = ?",
                    (prompt_hash,),
                ).fetchone()
                if existing:
                    return False

                conn.execute(
                    """
                    INSERT INTO golden_probes
                        (golden_id, prompt_hash, prompt_text, model, embedding)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (golden_id, prompt_hash, prompt_text, model, json.dumps(embedding)),
                )
                conn.commit()

                # Prune if over limit
                count = conn.execute(
                    "SELECT COUNT(*) FROM golden_probes"
                ).fetchone()[0]
                if count > _MAX_GOLDEN_PROBES:
                    conn.execute("""
                        DELETE FROM golden_probes
                        WHERE golden_id IN (
                            SELECT golden_id FROM golden_probes
                            ORDER BY created_at ASC
                            LIMIT ?
                        )
                    """, (count - _MAX_GOLDEN_PROBES,))
                    conn.commit()

                return True
        except Exception as e:
            logger.debug(f"LocalStore save error: {e}")
            return False

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_by_hash(self, prompt_hash: str) -> Optional[str]:
        """Return raw prompt text for replay, or None if not found."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT prompt_text FROM golden_probes WHERE prompt_hash = ?",
                    (prompt_hash,),
                ).fetchone()
                return row["prompt_text"] if row else None
        except Exception as e:
            logger.debug(f"LocalStore get_by_hash error: {e}")
            return None

    def get_random(self) -> Optional[dict]:
        """Return a random golden probe record for local replay decisions."""
        try:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT golden_id, prompt_hash, prompt_text, model, embedding
                    FROM golden_probes
                    ORDER BY RANDOM()
                    LIMIT 1
                    """
                ).fetchone()
                if row:
                    return {
                        "golden_id": row["golden_id"],
                        "prompt_hash": row["prompt_hash"],
                        "prompt_text": row["prompt_text"],
                        "model": row["model"],
                        "embedding": json.loads(row["embedding"]) if row["embedding"] else [],
                    }
        except Exception as e:
            logger.debug(f"LocalStore get_random error: {e}")
        return None

    def count(self) -> int:
        try:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT COUNT(*) FROM golden_probes"
                ).fetchone()[0]
        except Exception:
            return 0
