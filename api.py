from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from database import (
    database, logs_table,
    golden_probe_registry,
    save_golden_probe, get_golden_probe,
    get_random_golden_for_client, increment_golden_replay_count,
    get_baseline,
)
from probes import PROBES
import sqlalchemy
import io
import json
import random
from datetime import datetime

router = APIRouter(prefix="/api")

# ── SDK router — no VERISPECT_API_KEY check, uses X-Verispect-Key as client_id ──
sdk_router = APIRouter(prefix="/api/sdk")

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


@router.get("/report")
async def generate_report():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    # ── Fetch data ────────────────────────────────────────────────────────────
    q_total = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.is_canary == 0)
    total_calls = await database.fetch_val(q_total) or 0

    q_probes = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.is_canary == 1)
    total_probes = await database.fetch_val(q_probes) or 0

    q_flagged = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.flagged == 1)
    total_flagged = await database.fetch_val(q_flagged) or 0

    q_avg = sqlalchemy.select(sqlalchemy.func.avg(logs_table.c.drift_score)).where(logs_table.c.is_canary == 1)
    avg_drift = await database.fetch_val(q_avg) or 0

    compliance_score = round(((total_probes - total_flagged) / total_probes) * 100, 1) if total_probes > 0 else None

    q_cat = sqlalchemy.select(
        logs_table.c.probe_category,
        sqlalchemy.func.count().label("probes_run"),
        sqlalchemy.func.sum(logs_table.c.flagged).label("flagged"),
        sqlalchemy.func.avg(logs_table.c.drift_score).label("avg_drift")
    ).where(
        sqlalchemy.and_(logs_table.c.is_canary == 1, logs_table.c.probe_category.isnot(None))
    ).group_by(logs_table.c.probe_category)
    cat_rows = await database.fetch_all(q_cat)

    q_events = logs_table.select().where(logs_table.c.flagged == 1).order_by(logs_table.c.created_at.desc()).limit(10)
    drift_events = await database.fetch_all(q_events)

    CATEGORY_LABELS = {
        "gender": "Gender Bias",
        "age": "Age Bias",
        "race_ethnicity": "Race / Ethnicity Bias",
        "nationality": "Nationality Bias",
        "disability": "Disability Bias",
        "parental": "Parental Status Bias",
        "socioeconomic": "Socioeconomic Bias",
        "consistency": "Consistency",
    }

    # ── Build PDF ─────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    PURPLE = colors.HexColor("#7c6eff")
    DARK   = colors.HexColor("#0f1119")
    GRAY   = colors.HexColor("#6b7280")
    RED    = colors.HexColor("#ef4444")
    GREEN  = colors.HexColor("#10b981")
    AMBER  = colors.HexColor("#f59e0b")

    styles = getSampleStyleSheet()
    title_style   = ParagraphStyle("title",   parent=styles["Normal"], fontSize=24, textColor=PURPLE,  spaceAfter=4,  fontName="Helvetica-Bold")
    sub_style     = ParagraphStyle("sub",     parent=styles["Normal"], fontSize=11, textColor=GRAY,    spaceAfter=2)
    h2_style      = ParagraphStyle("h2",      parent=styles["Normal"], fontSize=14, textColor=DARK,    spaceBefore=16, spaceAfter=6, fontName="Helvetica-Bold")
    body_style    = ParagraphStyle("body",    parent=styles["Normal"], fontSize=10, textColor=DARK,    spaceAfter=4)
    caption_style = ParagraphStyle("caption", parent=styles["Normal"], fontSize=8,  textColor=GRAY)

    story = []

    # Header
    story.append(Paragraph("Verispect", title_style))
    story.append(Paragraph("AI Compliance &amp; Drift Detection Report", sub_style))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}", caption_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PURPLE, spaceAfter=16))

    # Compliance Score
    score_color = GREEN if (compliance_score or 0) >= 90 else (AMBER if (compliance_score or 0) >= 75 else RED)
    score_text = f"{compliance_score}%" if compliance_score is not None else "N/A"
    story.append(Paragraph("Overall Compliance Score", h2_style))
    score_data = [
        [Paragraph(f'<font size="36" color="{score_color.hexval()}">{score_text}</font>', ParagraphStyle("sc", fontName="Helvetica-Bold", alignment=TA_CENTER)),
         Paragraph(
            f"<b>Total API Calls:</b> {total_calls}<br/>"
            f"<b>Canary Probes Fired:</b> {total_probes}<br/>"
            f"<b>Drift Events Detected:</b> {total_flagged}<br/>"
            f"<b>Average Drift Score:</b> {round(avg_drift, 4)}<br/>"
            f"<b>Assessment Period:</b> Last 30 days",
            body_style
        )]
    ]
    score_table = Table(score_data, colWidths=[5*cm, None])
    score_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (0,0), colors.HexColor("#f5f3ff")),
        ("ROUNDEDCORNERS", [8]),
        ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
        ("PADDING", (0,0), (-1,-1), 12),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    # EU AI Act note
    story.append(Paragraph("Regulatory Context", h2_style))
    story.append(Paragraph(
        "This report supports compliance with the <b>EU AI Act (Regulation 2024/1689)</b>, "
        "which classifies AI systems used in recruitment and employment as <b>high-risk</b> under Annex III. "
        "High-risk systems are required to implement continuous monitoring, bias testing across protected "
        "characteristics, and maintain audit logs. Verispect automates this monitoring layer.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Category Breakdown
    story.append(Paragraph("Bias &amp; Consistency Analysis by Category", h2_style))
    cat_table_data = [["Category", "Probes Run", "Drift Events", "Avg Drift Score", "Status"]]
    for row in cat_rows:
        r = dict(row)
        cat = CATEGORY_LABELS.get(r["probe_category"], r["probe_category"])
        flagged_count = r["flagged"] or 0
        avg = round(r["avg_drift"] or 0, 4)
        status = "PASS" if flagged_count == 0 else ("WARN" if avg < 0.25 else "FAIL")
        cat_table_data.append([cat, str(r["probes_run"]), str(flagged_count), str(avg), status])

    if len(cat_table_data) > 1:
        ct = Table(cat_table_data, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 3*cm, 2*cm])
        ct_style = [
            ("BACKGROUND",  (0,0), (-1,0), PURPLE),
            ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
            ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",    (0,0), (-1,-1), 9),
            ("ALIGN",       (1,0), (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9fafb")]),
            ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
            ("PADDING",     (0,0), (-1,-1), 7),
        ]
        # Color status cells
        for i, row in enumerate(cat_table_data[1:], start=1):
            status_val = row[4]
            if status_val == "PASS":
                ct_style.append(("TEXTCOLOR", (4,i), (4,i), GREEN))
            elif status_val == "WARN":
                ct_style.append(("TEXTCOLOR", (4,i), (4,i), AMBER))
            else:
                ct_style.append(("TEXTCOLOR", (4,i), (4,i), RED))
        ct.setStyle(TableStyle(ct_style))
        story.append(ct)
    else:
        story.append(Paragraph("No probe data available yet.", body_style))

    story.append(Spacer(1, 12))

    # Drift Events
    story.append(Paragraph("Recent Drift Events", h2_style))
    if drift_events:
        ev_data = [["Timestamp", "Category", "Probe ID", "Drift Score", "Severity"]]
        for ev in drift_events:
            e = dict(ev)
            ts = e["created_at"].strftime("%Y-%m-%d %H:%M") if e["created_at"] else "—"
            cat = CATEGORY_LABELS.get(e["probe_category"], e["probe_category"] or "—")
            ev_data.append([ts, cat, e["probe_id"] or "—", str(e["drift_score"] or "—"), (e["severity"] or "—").upper()])

        et = Table(ev_data, colWidths=[3.5*cm, 4*cm, 4.5*cm, 2.5*cm, 2*cm])
        et.setStyle(TableStyle([
            ("BACKGROUND",     (0,0), (-1,0), colors.HexColor("#374151")),
            ("TEXTCOLOR",      (0,0), (-1,0), colors.white),
            ("FONTNAME",       (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",       (0,0), (-1,-1), 8),
            ("ALIGN",          (3,0), (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fef2f2")]),
            ("GRID",           (0,0), (-1,-1), 0.3, colors.HexColor("#e5e7eb")),
            ("PADDING",        (0,0), (-1,-1), 6),
        ]))
        story.append(et)
    else:
        story.append(Paragraph("No drift events detected. Model is behaving consistently.", body_style))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This report was automatically generated by Verispect — AI Drift Detection &amp; Compliance Middleware. "
        "For questions contact support@verispectai.com",
        caption_style
    ))

    doc.build(story)
    buf.seek(0)

    filename = f"verispect-compliance-report-{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SDK ENDPOINTS  (/api/sdk/*)
# Auth: X-Verispect-Key header is used as client_id (no dashboard key required)
# ═══════════════════════════════════════════════════════════════════════════════

def _get_client_id(request: Request) -> str:
    """Extract client_id from the SDK key header."""
    key = request.headers.get("X-Verispect-Key", "").strip()
    if not key:
        raise HTTPException(status_code=401, detail="Missing X-Verispect-Key header")
    return key


@sdk_router.post("/ingest")
async def sdk_ingest(request: Request):
    """
    Receives a log entry from the SDK after every real API call.
    Payload contains prompt_hash, response_embedding, model, tokens, latency.
    If is_golden=True, also registers the golden probe baseline on the server.

    Raw prompt text is NEVER sent here — only hashes and embedding vectors.
    """
    client_id = _get_client_id(request)
    body = await request.json()

    prompt_hash = body.get("prompt_hash", "")
    response_embedding = body.get("response_embedding", [])
    model = body.get("model", "unknown")
    latency_ms = int(body.get("latency_ms", 0))
    prompt_tokens = int(body.get("prompt_tokens", 0))
    completion_tokens = int(body.get("completion_tokens", 0))
    is_golden = bool(body.get("is_golden", False))

    if not prompt_hash or not response_embedding:
        raise HTTPException(status_code=422, detail="prompt_hash and response_embedding are required")

    # Log the real call (is_canary=0, no drift score for real calls)
    await database.execute(logs_table.insert().values(
        model=model,
        prompt=prompt_hash,          # Store hash — not raw text
        response=None,               # Never store raw response text from SDK
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        is_canary=0,
        drift_score=None,
        flagged=0,
        probe_id=None,
        severity=None,
        probe_category=None,
    ))

    # Register golden probe baseline if applicable
    if is_golden:
        golden_id = body.get("golden_id")
        golden_embedding = body.get("golden_embedding", response_embedding)
        if golden_id and golden_embedding:
            await save_golden_probe(
                golden_id=golden_id,
                client_id=client_id,
                prompt_hash=prompt_hash,
                model=model,
                baseline_embedding=golden_embedding,
            )

    return {"status": "ok"}


@sdk_router.get("/probe")
async def sdk_get_probe(request: Request, model: str = "unknown"):
    """
    Returns a probe for the SDK to fire using the client's own OpenAI key.
    70% chance: regulatory probe (bias/consistency from PROBES library).
    30% chance: golden probe (client's own historical prompt to replay).
    Falls back to regulatory if no golden probes exist for this client.
    """
    client_id = _get_client_id(request)

    # Decide probe type
    use_golden = random.random() < 0.30
    if use_golden:
        golden = await get_random_golden_for_client(client_id)
        if golden:
            await increment_golden_replay_count(golden["golden_id"])
            return {
                "type": "golden",
                "probe_id": golden["golden_id"],
                "prompt_hash": golden["prompt_hash"],
            }
        # No golden probes yet — fall through to regulatory

    # Pick a regulatory probe that has a stored baseline
    probes_with_baseline = []
    for p in PROBES:
        baseline = await get_baseline(p["id"])
        if baseline:
            probes_with_baseline.append(p)

    if not probes_with_baseline:
        return {"type": "none", "reason": "no baselines calibrated yet"}

    probe = random.choice(probes_with_baseline)
    return {
        "type": "regulatory",
        "probe_id": probe["id"],
        "messages": probe["messages"],
        "category": probe.get("category", "unknown"),
    }


@sdk_router.post("/probe-result")
async def sdk_probe_result(request: Request):
    """
    Receives the result of a probe fired by the SDK.

    Regulatory probes: response_text is provided → server scores via text comparison.
    Golden probes:     response_embedding is provided → server scores via vector comparison.
    Raw prompt text is never present in either case.
    """
    from scorer import score_drift, score_drift_from_embeddings

    client_id = _get_client_id(request)
    body = await request.json()

    probe_id = body.get("probe_id", "")
    probe_type = body.get("probe_type", "regulatory")
    response_text = body.get("response_text", "")
    response_embedding = body.get("response_embedding", [])
    model = body.get("model", "unknown")
    category = body.get("category", "unknown")

    if not probe_id:
        raise HTTPException(status_code=422, detail="probe_id is required")

    drift_result = None

    if probe_type == "regulatory":
        # Score against stored text baseline
        baseline_text = await get_baseline(probe_id)
        if baseline_text and response_text:
            drift_result = score_drift(baseline_text, response_text)
        else:
            # No baseline yet — store this as the new baseline
            if response_text:
                from database import save_baseline
                await save_baseline(probe_id, model, response_text)
            return {"status": "baseline_stored"}

    elif probe_type == "golden":
        # Score against stored embedding baseline
        golden = await get_golden_probe(probe_id)
        if golden and response_embedding:
            drift_result = score_drift_from_embeddings(
                golden["baseline_embedding"], response_embedding
            )
        else:
            return {"status": "golden_not_found"}

    if not drift_result or drift_result.get("drift_score") is None:
        return {"status": "scoring_failed"}

    # Log probe result to the main logs table (same as canary probes)
    await database.execute(logs_table.insert().values(
        model=model,
        prompt=f"[sdk_probe:{probe_id}]",
        response=response_text if probe_type == "regulatory" else None,
        prompt_tokens=0,
        completion_tokens=0,
        latency_ms=0,
        is_canary=1,
        drift_score=drift_result["drift_score"],
        flagged=int(drift_result["flagged"]),
        probe_id=probe_id,
        severity=drift_result["severity"],
        probe_category=category,
    ))

    status = "DRIFT_DETECTED" if drift_result["flagged"] else "OK"
    return {
        "status": status,
        "drift_score": drift_result["drift_score"],
        "severity": drift_result["severity"],
        "flagged": drift_result["flagged"],
    }