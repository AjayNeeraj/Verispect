# DEMO DAY RUNBOOK — June 11

*Exact commands + click path. Record with OBS/Loom, 1080p, mic on. Total: ~3 min footage.*

---

## ⚠️ FIRST: re-publish the landing (2 min)
The live verispectai.com still runs the **old** landing. The new one (Supabase-wired lead form) is in the repo. **Re-drag `landing/` folder to Netlify** (Deploys → drag-drop), or if the site is repo-connected it deploys itself on push. Then submit the form once on the live site — the lead must appear in Supabase → Table Editor → `leads`.

## Start the demo stack (local, seeded)
```powershell
cd C:\Users\akmad\OneDrive\Desktop\Verispect
.venv\Scripts\activate          # if venv exists; else plain python
uvicorn main:app --port 8000
```
Open: `http://localhost:8000` → React dashboard (seeded: 500 calls, 80 probes, drift timeline, categories).
Open second tab: `http://localhost:8000/docs` → Swagger UI (the "engine room" — looks credible, is real).

## Shot list (3 min)
1. **Hook (15s)** — face/voice over landing page (verispectai.com): "EU AI Act hits Aug 2026. Most AI teams can't prove their model is fair. Watch."
2. **Risk Classifier (40s)** — in `/docs`: POST `/api/risk/classify` body:
   `{"hiring": true, "uses_llm_decision": true, "eu_market": true}`
   → response shows **HIGH-RISK, Annex III §4, 8 obligations**. Say: "Step one — classified and documented in seconds."
   Show `gtm/06-collateral/Verispect-SAMPLE-Risk-Classification.pdf`.
3. **The catch (45s)** — dashboard: drift timeline + a flagged event. "Two identical CVs — the model docked the 54-year-old. Logging tools can't see this. We caught it automatically."
4. **The audit pack (45s)** — `/docs`: POST `/api/docs/dpia` body:
   `{"company":"Acme HR GmbH","system_name":"CandidateRank AI","purpose":"automated candidate screening","model":"gpt-4o-mini"}`
   → downloads the DPIA filled with live evidence. Also show the full compliance report (GET `/api/report`). "The €15k consultant deliverable. One click."
5. **Integration + privacy (25s)** — show the one line: `client = wrap(OpenAI(...), verispect_key="vs_live_...")` + "We only ever receive hashes and vectors. Your data never leaves your machine."
6. **Close (10s)** — landing page CTA on screen: "Your autonomous AI compliance department. Founding 20 open — verispectai.com."

## If something breaks live
- Dashboard empty → `python seed_demo.py` (reseeds local SQLite).
- Report errors → it reads the same DB; reseed fixes both.
- Record sections separately + stitch — nobody needs one perfect take.

## Pre-flight checks (tick before recording)
- [ ] verispectai.com shows NEW landing (shield logo, $1,500, countdown)
- [ ] Form on live site → row in Supabase `leads`
- [ ] `uvicorn main:app` boots, dashboard shows data
- [ ] `/api/risk/classify` + `/api/docs/dpia` respond in /docs
- [ ] 3 sample PDFs open clean (`gtm/06-collateral/`)
- [ ] Mic + screen recorder tested

## After recording (same day)
Upload video (YouTube unlisted/Loom) → embed link on landing → post clip to LinkedIn page → **June 12: fire `python outreach/run.py --enrich --send`** (needs `.env`: Hunter + Spacemail SMTP).
