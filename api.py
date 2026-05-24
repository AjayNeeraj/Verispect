from fastapi import APIRouter
from database import database, logs_table
import sqlalchemy

router = APIRouter(prefix="/api")

@router.get("/metrics")
async def get_metrics():
    # Total calls (real)
    q1 = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.is_canary == 0)
    total_calls = await database.fetch_val(q1)

    # Total probes
    q2 = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.is_canary == 1)
    total_probes = await database.fetch_val(q2)

    # Total flagged
    q3 = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.flagged == 1)
    total_flagged = await database.fetch_val(q3)

    # Avg drift
    q4 = sqlalchemy.select(sqlalchemy.func.avg(logs_table.c.drift_score)).where(logs_table.c.is_canary == 1)
    avg_drift = await database.fetch_val(q4) or 0

    return {
        "total_calls": total_calls,
        "total_probes": total_probes,
        "total_flagged": total_flagged,
        "avg_drift": round(avg_drift, 4)
    }

@router.get("/logs")
async def get_logs():
    query = logs_table.select().order_by(logs_table.c.created_at.desc()).limit(100)
    rows = await database.fetch_all(query)
    return [dict(row) for row in rows]

@router.get("/drift-events")
async def get_drift_events():
    query = logs_table.select().where(logs_table.c.flagged == 1).order_by(logs_table.c.created_at.desc())
    rows = await database.fetch_all(query)
    return [dict(row) for row in rows]

@router.get("/drift-timeline")
async def get_drift_timeline():
    query = sqlalchemy.select(
        logs_table.c.created_at, 
        logs_table.c.drift_score, 
        logs_table.c.probe_id, 
        logs_table.c.flagged, 
        logs_table.c.severity, 
        logs_table.c.probe_category
    ).where(
        sqlalchemy.and_(logs_table.c.is_canary == 1, logs_table.c.drift_score.isnot(None))
    ).order_by(logs_table.c.created_at.asc())
    
    rows = await database.fetch_all(query)
    return [dict(row) for row in rows]

@router.get("/compliance-summary")
async def get_compliance_summary():
    # Per-category breakdown
    query_cat = sqlalchemy.select(
        logs_table.c.probe_category,
        sqlalchemy.func.count().label("probes_run"),
        sqlalchemy.func.sum(logs_table.c.flagged).label("flagged"),
        sqlalchemy.func.avg(logs_table.c.drift_score).label("avg_drift")
    ).where(
        sqlalchemy.and_(logs_table.c.is_canary == 1, logs_table.c.probe_category.isnot(None))
    ).group_by(logs_table.c.probe_category)

    rows = await database.fetch_all(query_cat)
    categories = {}
    total_probes = 0
    total_flagged = 0
    
    for row in rows:
        r = dict(row)
        categories[r["probe_category"]] = {
            "probes_run": r["probes_run"],
            "flagged": r["flagged"] or 0,
            "avg_drift": round(r["avg_drift"] or 0, 4)
        }
        total_probes += r["probes_run"]
        total_flagged += (r["flagged"] or 0)

    # Overall compliance score
    if total_probes > 0:
        compliance_score = round(((total_probes - total_flagged) / total_probes) * 100, 1)
    else:
        compliance_score = None

    # Last probe timestamp
    query_last = sqlalchemy.select(sqlalchemy.func.max(logs_table.c.created_at)).where(logs_table.c.is_canary == 1)
    last_probe = await database.fetch_val(query_last)

    # Severity distribution
    query_sev = sqlalchemy.select(
        logs_table.c.severity, 
        sqlalchemy.func.count().label("count")
    ).where(
        sqlalchemy.and_(logs_table.c.is_canary == 1, logs_table.c.severity.isnot(None))
    ).group_by(logs_table.c.severity)
    
    severity_rows = await database.fetch_all(query_sev)
    severity_dist = {dict(r)["severity"]: dict(r)["count"] for r in severity_rows}

    return {
        "compliance_score": compliance_score,
        "categories": categories,
        "total_probes": total_probes,
        "total_flagged": total_flagged,
        "last_probe_at": last_probe,
        "severity_distribution": severity_dist
    }