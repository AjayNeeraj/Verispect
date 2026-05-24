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