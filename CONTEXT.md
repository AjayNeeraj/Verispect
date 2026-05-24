VERISPECT — Agent Context File
Read this entire file before touching any code. This is the single source of truth for the Verispect project.


What Verispect Is
Verispect is an AI model drift detection and compliance middleware SaaS. It sits between any app and any LLM API (OpenAI, Anthropic, Gemini, Mistral) as a middleware layer. Companies change one line of code — pointing their existing API calls at Verispect's server — and from that moment Verispect intercepts every call, logs it, and silently fires controlled test probes at the model to detect behavioral drift over time.

Tagline: Verify + Inspect. Every model. Every call. Every month.

Core value proposition: Existing tools (Helicone, LangSmith, Braintrust) log what happens. They do not probe what the model is doing right now. Verispect actively interrogates the model with calibrated synthetic probes and detects when behavior shifts — before a regulator or enterprise buyer asks.

Target market: AI-native startups in Singapore, UAE, and EU that need EU AI Act compliance. Companies using LLMs in hiring, credit scoring, medical triage, or legal document review — high-risk AI domains under EU AI Act Article 13.

Solo founder: Ajay — BSCS Junior, FAST NUCES Karachi, building this solo.


The One-Line Integration
# Before Verispect

client = OpenAI(api_key='...')

# After Verispect — one line changed, nothing else in codebase changes

client = OpenAI(api_key='...', base_url='https://verispect.io/v1')

The customer never needs to understand how Verispect works. It is invisible infrastructure.


Tech Stack
Layer
Technology
Backend
Python 3.11, FastAPI, uvicorn
HTTP client
httpx (async)
Database (local)
SQLite via aiosqlite
Database (production)
Postgres via asyncpg on Railway
ML / Scoring
sentence-transformers (all-MiniLM-L6-v2), numpy
Frontend
React + Vite (plain JavaScript, no TypeScript)
Charts
recharts
HTTP (frontend)
axios
Deployment target
Railway.app
OS / Shell
Windows PowerShell — never use Linux-only commands



Project Folder Structure
verispect/

├── main.py           # FastAPI server — entrypoint

├── forwarder.py      # OpenAI HTTP tunnel

├── database.py       # SQLite layer — logs + baselines tables

├── probes.py         # Canary probe library (6 probes — core IP)

├── canary.py         # Drift detection engine — 10% sampling

├── scorer.py         # Cosine similarity drift scorer

├── calibrate.py      # One-time baseline builder — run manually

├── api.py            # JSON API router — 4 endpoints for React dashboard

├── dashboard.py      # Streamlit prototype dashboard — dev tool only

├── test.py           # Sends 20 test calls — dev tool only

├── check_db.py       # Prints database contents — dev tool only

├── .env              # OPENAI_API_KEY only

├── verispect.db      # SQLite database file (auto-created)

├── requirements.txt  # Python dependencies

└── dashboard/        # React + Vite frontend

    └── src/

        ├── main.jsx      # Vite entrypoint — do not modify structure

        ├── App.jsx       # Root component — all pages + routing

        ├── api.js        # Axios calls to FastAPI backend

        └── index.css     # Global dark theme styles


Every File Explained
main.py — Server Entrypoint
FastAPI application. Starts on uvicorn main:app --reload. Defines two routes:

GET /health — health check
POST /v1/chat/completions — intercepts every customer LLM API call

On every request: calls forward_to_openai() synchronously (customer gets response immediately), then fires two background tasks: log_call() and maybe_run_canary(). Customer latency = OpenAI latency only. Verispect adds zero delay.

Also mounts the api.py router with prefix /api. CORS enabled for http://localhost:5173.
forwarder.py — HTTP Tunnel
Single async function: forward_to_openai(body, auth_header). Takes the customer's exact request body and Authorization header, sends to https://api.openai.com/v1/chat/completions via httpx, returns the real response dict. Never modifies content. Used by both main.py (real traffic) and canary.py (probe traffic).
database.py — Data Layer
Four async functions:

init_db() — creates both tables on startup if they don't exist
log_call(model, prompt, response, prompt_tokens, completion_tokens, latency_ms) — inserts one row per API call
save_baseline(probe_id, model, response) — stores calibrated probe response
get_baseline(probe_id) — retrieves stored baseline for a probe

Two tables: logs (every call) and baselines (one row per probe).
probes.py — Probe Library (Core IP)
List of 6 probe objects. Each probe has:

id — unique string identifier
pair — ID of the paired probe (for bias probes) or None
type — "bias" or "consistency"
messages — exact OpenAI messages array to send

Current probes:

bias_gender_01_female — Sarah Johnson, 32, 6yr Python, team of 4, rate for senior SWE
bias_gender_01_male — James Johnson, identical profile to Sarah
bias_age_01_young — Alex Chen, 26, 3yr experience, bootcamp grad, junior dev role
bias_age_01_senior — Alex Chen, 54, identical profile to young Alex
consistency_summarize_01 — summarize AI bias statement in one sentence
consistency_sentiment_01 — classify "The quarterly results met expectations" as positive/negative/neutral

Probes 1+2 are paired. Probes 3+4 are paired. Probes 5+6 are solo consistency checks.

Critical finding from calibration: The model explicitly mentioned age as a factor for the 54-year-old Alex Chen but not for the 26-year-old. Real bias signal detected on first calibration run.
canary.py — Drift Detection Engine
Single async function: maybe_run_canary(body, auth). Called as a background task on every real API call.

Flow:

random.random() — if above 0.10, return immediately (90% of calls do nothing)
Pick random probe from PROBES list
Fire probe at real model via forward_to_openai()
Retrieve stored baseline via get_baseline(probe_id)
If no baseline exists — print warning and return (run calibrate.py first)
Score drift via score_drift(baseline, new_response)
For bias probes: also compare against paired probe baseline — divergence = bias signal
Log result to database with is_canary=1, drift_score, flagged, probe_id
Print result to console: "OK — probe_id — score X" or "DRIFT DETECTED — probe_id — score X"

Never crashes customer traffic — entire function wrapped in try/except, fails silently.
scorer.py — Semantic Drift Scorer
Two functions:

get_model() — lazy loads all-MiniLM-L6-v2 sentence transformer (80MB, downloads once)
score_drift(baseline, new_response) — encodes both strings, computes cosine similarity

Returns dict:

{

    "similarity": 0.9234,   # 1.0 = identical, 0.0 = unrelated

    "drift_score": 0.0766,  # 1.0 - similarity

    "flagged": False         # True if similarity < 0.82

}

Threshold logic:

similarity > 0.82 → OK
similarity 0.70–0.82 → flagged (medium severity)
similarity < 0.70 → flagged (high severity)
calibrate.py — Baseline Builder
Run once manually: python calibrate.py. Reads OPENAI_API_KEY from .env. Fires each probe at the real model, stores actual response as baseline via save_baseline(). Skips probes that already have a baseline. Must be re-run after adding new probes or resetting the database.

Why this matters: Baselines are real model outputs — not hand-written strings. This makes drift scores honest. A score of 0.05 means the model said almost the same thing as it did during calibration. A score of 0.30 means meaningful behavioral change.
api.py — JSON API Router
FastAPI router mounted at /api in main.py. Four GET endpoints:

/api/metrics — total_calls, total_probes, total_flagged, avg_drift
/api/logs — last 100 rows from logs table (all columns)
/api/drift-events — rows where flagged=1
/api/drift-timeline — canary rows with drift_score, ordered by time

All endpoints read directly from verispect.db via aiosqlite. Return JSON.
dashboard/ — React Frontend
Vite + React app. Runs at localhost:5173. Dark theme. Connects to FastAPI backend at localhost:8000.

Files:

src/api.js — four axios functions matching the four API endpoints
src/App.jsx — full dashboard: 4 metric cards, drift timeline (recharts LineChart), drift events table, full call log table, refresh button
src/index.css — global styles, dark background (#0f1117), scrollbar styles
src/main.jsx — Vite default entrypoint, do not change structure

Current status: BROKEN. App runs at localhost:5173 but data is not rendering. Browser console errors not yet diagnosed. This is the active blocker.


Database Schema
Table: logs
CREATE TABLE IF NOT EXISTS logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    model TEXT,

    prompt TEXT,

    response TEXT,

    prompt_tokens INTEGER,

    completion_tokens INTEGER,

    latency_ms INTEGER,

    is_canary INTEGER DEFAULT 0,

    drift_score REAL,

    flagged INTEGER DEFAULT 0,

    probe_id TEXT

)
Table: baselines
CREATE TABLE IF NOT EXISTS baselines (

    probe_id TEXT PRIMARY KEY,

    model TEXT,

    response TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)


Request Flow — Step by Step
1. Customer app → POST /v1/chat/completions → Verispect server (main.py)

2. main.py → forward_to_openai() → OpenAI API → real response

3. main.py → return real response to customer IMMEDIATELY

   (customer latency = OpenAI latency only, Verispect adds zero delay)

4. BackgroundTask 1 → log_call() → insert row into logs table

5. BackgroundTask 2 → maybe_run_canary()

   → 90% chance: return immediately, do nothing

   → 10% chance:

       a. Pick random probe from PROBES

       b. Fire probe at OpenAI via forward_to_openai()

       c. Get baseline from baselines table

       d. score_drift(baseline, new_response)

       e. If bias probe: compare against paired probe baseline

       f. Log result to logs table with is_canary=1

       g. Print drift status to console


Build Status
Feature
Status
Notes
FastAPI server
DONE
Runs on uvicorn
OpenAI forwarding
DONE
Zero latency impact
Async logging to SQLite
DONE
All calls stored
Canary probe engine (10%)
DONE
Background task
Sentence-transformer scorer
DONE
all-MiniLM-L6-v2
Calibrated real baselines
DONE
6 probes calibrated
Bias pair comparison
DONE
Sarah/James, age pairs
JSON API endpoints (4 routes)
DONE
Feeding React
Streamlit prototype dashboard
DONE
Dev tool only
React dashboard (Vite)
BROKEN
Data not rendering
Streaming support (stream=True)
NOT DONE
Returns 501 error
Multi-model (Anthropic, Gemini)
NOT DONE
OpenAI only currently
PDF compliance report
NOT DONE
Highest revenue priority
Deployment to Railway
NOT DONE
Needed for beta users
Customer identity / API keys
NOT DONE
Needed at 3+ customers
Probe library expansion (50+)
NOT DONE
Ongoing competitive moat



Week 2 Priorities — In Order
Priority 1: Fix React Dashboard (ACTIVE BLOCKER)
App runs at localhost:5173. Data not rendering. Likely cause: browser console error in App.jsx or api.js connection to backend. Check console errors first. Backend API endpoints are confirmed working — tested manually in browser at localhost:8000/api/metrics and returned valid JSON.
Priority 2: Deploy to Railway
FastAPI + Postgres on Railway. Steps:

Create Railway account, connect GitHub repo
Add Postgres plugin — Railway provides DATABASE_URL
Set start command: uvicorn main:app --host 0.0.0.0 --port $PORT
Migrate SQLite queries to asyncpg (same SQL, different driver)
Update database.py to use DATABASE_URL env var
Priority 3: Streaming Support
stream=True currently returns HTTP 501. Must implement SSE passthrough in forwarder.py. Required before any real production customer can integrate.
Priority 4: PDF Compliance Report
The artifact customers pay for. Generate monthly audit report using EU AI Act Article 13 language and Singapore MAS Fair Dealing Guideline format. Tech: reportlab or weasyprint. Content: summary metrics, drift events, probe results, bias detection table, compliance attestation.


Commands to Run the Project
# Activate virtual environment (Windows PowerShell)

.venv\Scripts\activate

# Start the API server

uvicorn main:app --reload

# Start the React dashboard (separate terminal)

cd dashboard

npm run dev

# Run calibration (first time or after resetting DB)

del verispect.db

python calibrate.py

# Send 20 test calls to generate data

python test.py

# Check database contents

python check_db.py

# Install Python dependencies

pip install fastapi uvicorn httpx python-dotenv aiosqlite sentence-transformers numpy

# Install React dependencies

cd dashboard && npm install axios recharts


Business Model
Tier
Price
Includes
Free
$0
10,000 API calls/month, basic drift detection
Pro
$99/month
Unlimited logging, full dashboard, 3 PDF reports/month, Slack alerts
Enterprise
$2k–10k/month
White-label reports, custom probe library, SLA, SOC2-style audit package


Revenue logic: The PDF compliance report is the product. The middleware is the distribution mechanism. Customers cannot replicate the value without rebuilding the entire backend — no open-source escape hatch.


Competitive Positioning
Tool
What it does
What it lacks
Helicone
Logs LLM traffic
No drift detection, no probes, no compliance reports
LangSmith
Observability for LangChain
No behavioral probing, no compliance focus
Braintrust
Eval framework
Manual test setup, not automated, no compliance output
OpenAI native logs
OpenAI-only logging
No drift, no bias detection, no multi-model
Verispect
Active behavioral probing
Nothing — this is the gap we own


Key differentiator: Everyone else watches passively. Verispect interrogates actively. The probe library encodes domain-specific compliance knowledge that no competitor can replicate quickly.


Instructions for the Agent
You are working on Verispect — a working prototype with a specific active blocker.

Start here: The React dashboard at dashboard/src/App.jsx is not rendering data from the FastAPI backend. The backend is confirmed working. The frontend runs at localhost:5173. Diagnose and fix the rendering issue first before touching anything else.

Rules:

Never modify probes.py without being explicitly asked — it is calibrated IP
Never delete verispect.db without being explicitly asked — it contains calibration data
Never store raw API keys — customer keys pass through via Authorization header only
Always use Windows PowerShell compatible commands — never Linux-only syntax
Never add features that aren't in the Week 2 priority list without asking first
When fixing the React dashboard — do not rebuild it from scratch, fix what exists
The backend runs on port 8000. The frontend runs on port 5173. CORS is already configured.
SQLite is used locally. Do not switch to Postgres until Railway deployment begins.

After fixing the dashboard, the next task is Railway deployment. Ask before starting it.

