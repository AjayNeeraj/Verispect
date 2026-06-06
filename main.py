import os
import pathlib
import time

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from forwarder import forward_to_openai, stream_openai
from database import init_db, log_call, database
from canary import maybe_run_canary
from auth import require_auth
from api import router, auth_router, keys_router, sdk_router
from risk_classifier import risk_router
from doc_generator import doc_router

load_dotenv()

app = FastAPI(
    title="Verispect",
    description="AI Model Drift Detection & Compliance Middleware",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://verispectai.com",
        "https://www.verispectai.com",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
# Dashboard API — protected by JWT (require_auth dependency on each endpoint)
app.include_router(router)

# Auth — public (register, login)
app.include_router(auth_router)

# API key management — protected by JWT per endpoint
app.include_router(keys_router)

# SDK ingest/probe — protected by vs_live_xxx key validated against DB
app.include_router(sdk_router)

# Risk Classifier agent (Module 1) — Annex III classification + record PDF
app.include_router(risk_router)

# Evidence Clerk agent (Module 2) — auto DPIA + Annex IV tech-doc from live evidence
app.include_router(doc_router)

# ── Lifecycle ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await init_db()
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "alive"}

# ── LLM Proxy endpoint ────────────────────────────────────────────────────────
@app.post("/v1/chat/completions")
async def intercept(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    auth = request.headers.get("Authorization", "")

    if body.get("stream", False):
        stream_gen = await stream_openai(body, auth)

        async def proxy_and_collect():
            start = time.time()
            async for chunk in stream_gen:
                yield chunk
            fragments = getattr(stream_gen, "parsed_fragments", []) or []
            full_text = "".join(fragments)
            latency   = int((time.time() - start) * 1000)
            prompt    = str(body.get("messages", ""))
            model     = body.get("model", "unknown")
            background_tasks.add_task(log_call, model, prompt, full_text, 0, 0, latency)
            background_tasks.add_task(maybe_run_canary, body, auth)

        return StreamingResponse(proxy_and_collect(), media_type="text/event-stream")

    start  = time.time()
    result = await forward_to_openai(body, auth)
    latency = int((time.time() - start) * 1000)

    prompt         = str(body.get("messages", ""))
    response_text  = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    model          = body.get("model", "unknown")
    usage          = result.get("usage", {})

    background_tasks.add_task(
        log_call, model, prompt, response_text,
        usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), latency,
    )
    background_tasks.add_task(maybe_run_canary, body, auth)
    return JSONResponse(result)

# ── Serve React frontend ──────────────────────────────────────────────────────
dashboard_dist = pathlib.Path(__file__).parent / "dashboard" / "dist"
if dashboard_dist.exists():
    app.mount("/", StaticFiles(directory=str(dashboard_dist), html=True), name="dashboard")
