import os
from databases import Database
import sqlalchemy

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///verispect.db")

# Databases needs an absolute path or special formatting for sqlite sometimes, 
# but sqlite:///verispect.db works generally.
database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

logs_table = sqlalchemy.Table(
    "logs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("model", sqlalchemy.String),
    sqlalchemy.Column("prompt", sqlalchemy.String),
    sqlalchemy.Column("response", sqlalchemy.String),
    sqlalchemy.Column("prompt_tokens", sqlalchemy.Integer),
    sqlalchemy.Column("completion_tokens", sqlalchemy.Integer),
    sqlalchemy.Column("latency_ms", sqlalchemy.Integer),
    sqlalchemy.Column("is_canary", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("drift_score", sqlalchemy.Float),
    sqlalchemy.Column("flagged", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("probe_id", sqlalchemy.String),
    sqlalchemy.Column("severity", sqlalchemy.String),
    sqlalchemy.Column("probe_category", sqlalchemy.String),
)

baselines_table = sqlalchemy.Table(
    "baselines",
    metadata,
    sqlalchemy.Column("probe_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("model", sqlalchemy.String),
    sqlalchemy.Column("response", sqlalchemy.String),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
)

# Server-side registry of golden probes.
# Stores ONLY: golden_id, client_id, prompt_hash, model, baseline_embedding (vector).
# Raw prompt text is NEVER stored here — it lives in the client's local SQLite.
golden_probe_registry = sqlalchemy.Table(
    "golden_probe_registry",
    metadata,
    sqlalchemy.Column("golden_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("client_id", sqlalchemy.String, index=True),
    sqlalchemy.Column("prompt_hash", sqlalchemy.String),
    sqlalchemy.Column("model", sqlalchemy.String),
    sqlalchemy.Column("baseline_embedding", sqlalchemy.Text),   # JSON array of floats
    sqlalchemy.Column("replay_count", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
)


async def init_db():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)

async def log_call(model, prompt, response, prompt_tokens, completion_tokens, latency_ms,
                   is_canary=0, drift_score=None, flagged=0, probe_id=None,
                   severity=None, probe_category=None):
    query = logs_table.insert().values(
        model=model,
        prompt=prompt,
        response=response,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        is_canary=is_canary,
        drift_score=drift_score,
        flagged=flagged,
        probe_id=probe_id,
        severity=severity,
        probe_category=probe_category
    )
    await database.execute(query)

async def save_baseline(probe_id: str, model: str, response: str):
    # Upsert logic depends on dialect. 
    # For a universal approach, try updating first, then insert if 0 rows matched.
    query_update = baselines_table.update().where(baselines_table.c.probe_id == probe_id).values(
        model=model, response=response
    )
    updated = await database.execute(query_update)
    if not updated:
        query_insert = baselines_table.insert().values(
            probe_id=probe_id, model=model, response=response
        )
        await database.execute(query_insert)

async def get_baseline(probe_id: str) -> str | None:
    query = sqlalchemy.select(baselines_table.c.response).where(baselines_table.c.probe_id == probe_id)
    row = await database.fetch_one(query)
    return row["response"] if row else None


# ── Golden probe registry helpers ─────────────────────────────────────────────

async def save_golden_probe(golden_id: str, client_id: str, prompt_hash: str,
                             model: str, baseline_embedding: list) -> None:
    """
    Upsert a golden probe registry entry.
    Called when the SDK reports a new golden probe via /api/sdk/ingest.
    """
    import json
    embedding_json = json.dumps(baseline_embedding)

    existing = await database.fetch_one(
        sqlalchemy.select(golden_probe_registry.c.golden_id).where(
            golden_probe_registry.c.golden_id == golden_id
        )
    )
    if existing:
        return  # Already registered — baseline is immutable once set

    await database.execute(
        golden_probe_registry.insert().values(
            golden_id=golden_id,
            client_id=client_id,
            prompt_hash=prompt_hash,
            model=model,
            baseline_embedding=embedding_json,
            replay_count=0,
        )
    )


async def get_golden_probe(golden_id: str) -> dict | None:
    """Fetch a golden probe entry by ID."""
    import json
    row = await database.fetch_one(
        sqlalchemy.select(golden_probe_registry).where(
            golden_probe_registry.c.golden_id == golden_id
        )
    )
    if not row:
        return None
    r = dict(row)
    r["baseline_embedding"] = json.loads(r["baseline_embedding"]) if r["baseline_embedding"] else []
    return r


async def get_random_golden_for_client(client_id: str) -> dict | None:
    """Return a random golden probe for a given client to replay."""
    import json
    row = await database.fetch_one(
        sqlalchemy.select(golden_probe_registry).where(
            golden_probe_registry.c.client_id == client_id
        ).order_by(sqlalchemy.func.random()).limit(1)
    )
    if not row:
        return None
    r = dict(row)
    r["baseline_embedding"] = json.loads(r["baseline_embedding"]) if r["baseline_embedding"] else []
    return r


async def increment_golden_replay_count(golden_id: str) -> None:
    await database.execute(
        golden_probe_registry.update()
        .where(golden_probe_registry.c.golden_id == golden_id)
        .values(replay_count=golden_probe_registry.c.replay_count + 1)
    )