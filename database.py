import os
from databases import Database
import sqlalchemy

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///verispect.db")

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# ── Client accounts ───────────────────────────────────────────────────────────
clients_table = sqlalchemy.Table(
    "clients",
    metadata,
    sqlalchemy.Column("id",           sqlalchemy.String,   primary_key=True),   # UUID
    sqlalchemy.Column("company_name", sqlalchemy.String,   nullable=False),
    sqlalchemy.Column("email",        sqlalchemy.String,   nullable=False, unique=True),
    sqlalchemy.Column("password_hash",sqlalchemy.String,   nullable=False),
    sqlalchemy.Column("plan",         sqlalchemy.String,   default="free"),      # free | pro | enterprise
    sqlalchemy.Column("created_at",   sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
)

# ── API keys (vs_live_xxx) ────────────────────────────────────────────────────
api_keys_table = sqlalchemy.Table(
    "api_keys",
    metadata,
    sqlalchemy.Column("id",           sqlalchemy.String,   primary_key=True),   # UUID
    sqlalchemy.Column("client_id",    sqlalchemy.String,   sqlalchemy.ForeignKey("clients.id"), nullable=False),
    sqlalchemy.Column("key_value",    sqlalchemy.String,   nullable=False, unique=True),  # vs_live_xxx
    sqlalchemy.Column("name",         sqlalchemy.String,   default="Default"),
    sqlalchemy.Column("is_active",    sqlalchemy.Integer,  default=1),
    sqlalchemy.Column("last_used_at", sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column("created_at",   sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
)

logs_table = sqlalchemy.Table(
    "logs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("client_id", sqlalchemy.String, index=True),   # tenant isolation — every read filters on this
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

leads_table = sqlalchemy.Table(
    "leads",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("company", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String),
    sqlalchemy.Column("usecase", sqlalchemy.String),
    sqlalchemy.Column("source", sqlalchemy.String),
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
                   severity=None, probe_category=None, client_id=None):
    query = logs_table.insert().values(
        client_id=client_id,
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


# ── Client auth helpers ───────────────────────────────────────────────────────

async def create_client(client_id: str, company_name: str, email: str, password_hash: str) -> None:
    await database.execute(clients_table.insert().values(
        id=client_id,
        company_name=company_name,
        email=email,
        password_hash=password_hash,
        plan="free",
    ))


async def get_client_by_email(email: str) -> dict | None:
    row = await database.fetch_one(
        clients_table.select().where(clients_table.c.email == email)
    )
    return dict(row) if row else None


async def get_client_by_id(client_id: str) -> dict | None:
    row = await database.fetch_one(
        clients_table.select().where(clients_table.c.id == client_id)
    )
    return dict(row) if row else None


# ── API key helpers ───────────────────────────────────────────────────────────

async def create_api_key(key_id: str, client_id: str, key_value: str, name: str) -> None:
    await database.execute(api_keys_table.insert().values(
        id=key_id,
        client_id=client_id,
        key_value=key_value,
        name=name,
        is_active=1,
    ))


async def get_client_id_from_key(key_value: str) -> str | None:
    """Validate an SDK key and return the client_id. Returns None if invalid/revoked."""
    row = await database.fetch_one(
        sqlalchemy.select(api_keys_table.c.client_id, api_keys_table.c.id)
        .where(
            sqlalchemy.and_(
                api_keys_table.c.key_value == key_value,
                api_keys_table.c.is_active == 1,
            )
        )
    )
    if row:
        # Update last_used_at asynchronously
        from datetime import datetime
        await database.execute(
            api_keys_table.update()
            .where(api_keys_table.c.id == row["id"])
            .values(last_used_at=datetime.utcnow())
        )
        return row["client_id"]
    return None


async def list_api_keys(client_id: str) -> list:
    rows = await database.fetch_all(
        api_keys_table.select()
        .where(api_keys_table.c.client_id == client_id)
        .order_by(api_keys_table.c.created_at.desc())
    )
    return [dict(r) for r in rows]


async def revoke_api_key(key_id: str, client_id: str) -> bool:
    """Revoke a key. Verifies it belongs to this client."""
    result = await database.execute(
        api_keys_table.update()
        .where(sqlalchemy.and_(
            api_keys_table.c.id == key_id,
            api_keys_table.c.client_id == client_id,
        ))
        .values(is_active=0)
    )
    return result > 0