import os
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from forwarder import forward_to_openai, stream_openai
from database import init_db, log_call
from canary import maybe_run_canary
from api import router, sdk_router
import time

load_dotenv()

VERISPECT_API_KEY = os.getenv("VERISPECT_API_KEY")

app = FastAPI(title="Verispect", description="AI Model Drift Detection & Compliance Middleware")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "http://localhost:3000",  # Alt dev port
        "https://verispectai.com",
        "https://www.verispectai.com"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple API key auth for dashboard endpoints
# If VERISPECT_API_KEY is not set (dev mode), skip auth entirely
async def verify_api_key(request: Request):
    if not VERISPECT_API_KEY:
        return  # Dev mode — no auth required
    key = request.headers.get("X-Verispect-Key", "")
    if key != VERISPECT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

app.include_router(router, dependencies=[Depends(verify_api_key)])   # Dashboard — protected
app.include_router(sdk_router)                                          # SDK endpoints — own auth

# Serve built React frontend — only if the dist folder exists (production)
DIST_DIR = os.path.join(os.path.dirname(__file__), "dashboard", "dist")
if os.path.isdir(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        # Don't intercept API or proxy routes
        if full_path.startswith("api/") or full_path.startswith("v1/"):
            raise HTTPException(status_code=404)
        index = os.path.join(DIST_DIR, "index.html")
        return FileResponse(index)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
def health():
    return {"status": "alive"}

@app.post("/v1/chat/completions")
async def intercept(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    auth = request.headers.get("Authorization", "")

    # If client requested streaming, proxy OpenAI SSE stream to client while
    # reassembling content fragments for later logging and canary probes.
    if body.get("stream", False):
        # Obtain an async generator that yields raw bytes and accumulates parsed fragments
        stream_gen = await stream_openai(body, auth)

        async def proxy_and_collect():
            start = time.time()
            # stream chunks through to the client as they arrive
            async for chunk in stream_gen:
                yield chunk
            # after stream ends, assemble full text from parsed fragments
            fragments = getattr(stream_gen, "parsed_fragments", []) or []
            full_text = "".join(fragments)

            latency = int((time.time() - start) * 1000)
            prompt = str(body.get("messages", ""))
            model = body.get("model", "unknown")

            # schedule background logging and canary run once we have full response
            background_tasks.add_task(
                log_call,
                model,
                prompt,
                full_text,
                0,
                0,
                latency
            )
            background_tasks.add_task(maybe_run_canary, body, auth)

        return StreamingResponse(proxy_and_collect(), media_type="text/event-stream")

    # Non-streaming (existing behaviour)
    start = time.time()
    result = await forward_to_openai(body, auth)
    latency = int((time.time() - start) * 1000)

    prompt = str(body.get("messages", ""))
    response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    model = body.get("model", "unknown")
    usage = result.get("usage", {})

    background_tasks.add_task(
        log_call,
        model,
        prompt,
        response_text,
        usage.get("prompt_tokens", 0),
        usage.get("completion_tokens", 0),
        latency
    )
    background_tasks.add_task(maybe_run_canary, body, auth)
    
    return JSONResponse(result)