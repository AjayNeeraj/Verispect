# Deploy Stack — Netlify + Supabase + Spaceship (demo June 11, launch June 12)

*Your chosen stack, wired. Architecture truth up top so nothing breaks.*

```
  Spaceship (domain + Spacemail email)
        │ DNS
        ▼
  Netlify ──────────►  landing page (landing/)  +  static React dashboard build
        │                         │ API calls
        │                         ▼
        │              FastAPI backend  ── Render (launch)  /  LOCAL (demo)
        │                         │
        │                         ▼
        └────────────────►  Supabase (Postgres DB)
```

**Why backend isn't on Netlify:** Netlify runs static files + JS serverless only — it cannot run a long-lived Python/uvicorn server with sentence-transformers. So the backend goes to **Render** (simplest Railway-alternative) for launch, or just runs **locally** for the recorded demo.

---

## 1. Landing → Netlify (15 min)
- Easiest: drag the `landing/` folder to **app.netlify.com/drop** → instant URL.
- Or connect the GitHub repo → Netlify reads `netlify.toml` (publishes `landing/`). Auto-deploys on push.

## 2. Domain (Spaceship) → Netlify
- Netlify → Domain settings → Add custom domain → enter your Spaceship domain.
- In **Spaceship → domain → DNS**, add what Netlify shows:
  - `A` record `@` → Netlify's load-balancer IP `75.2.60.5`, **or**
  - `CNAME` `www` → `<your-site>.netlify.app`
  - (Easiest: set Spaceship nameservers to Netlify DNS, then Netlify manages it.)
- SSL is automatic on Netlify (Let's Encrypt).

## 3. Email (Spacemail) → outreach sending
Spacemail SMTP (confirmed):
```
SMTP_HOST = mail.spacemail.com
SMTP_PORT = 587          # STARTTLS  (or 465 for SSL)
SMTP_USER = you@yourdomain.com      # full Spacemail address
SMTP_PASS = your mailbox password
FROM_EMAIL = you@yourdomain.com
```
Put these in `.env` → `python outreach/run.py --enrich --send` works. **Set SPF + DKIM + DMARC** in Spaceship DNS (Spacemail gives the records) before sending cold, or you land in spam. Warm the inbox a few days first.

## 4. Database → Supabase
`database.py` already reads `DATABASE_URL` (defaults to SQLite). To use Supabase:
- Supabase → Project → Settings → Database → Connection string (URI).
- Use the **Session pooler** or direct connection. Set:
```
DATABASE_URL = postgresql://postgres:[PASSWORD]@db.[ref].supabase.co:5432/postgres?ssl=require
```
- Ensure `asyncpg` is installed (it's in requirements). Tables auto-create on startup via `init_db()`.
- Migrate seed data: run `python seed_demo.py` with `DATABASE_URL` set to Supabase → demo data lands in Postgres for the demo.
- (Supabase MCP is connected — I can create the project/tables for you on request.)

## 5. Backend
- **Demo (June 11):** run locally — `uvicorn main:app --reload` + `cd dashboard && npm run dev`. Screen-record. No deploy needed.
- **Launch:** deploy to **Render** — New Web Service → connect repo → build `pip install -r requirements.txt && cd dashboard && npm install && npm run build` → start `uvicorn main:app --host 0.0.0.0 --port $PORT` → add env `DATABASE_URL` (Supabase), `OPENAI_API_KEY`. (Same shape as the old Railway guide in `DEPLOY.md`.)

## Demo-day minimum (June 11) — fastest path
1. Landing live on Netlify + Spaceship domain. ✅ legit public presence.
2. Backend + dashboard **local**, seeded data. ✅ demo looks real.
3. Record the 3-min demo (`LAUNCH-CHECKLIST.md` §C).
That's enough to shoot. Render + Supabase can go live right after, for the launch wave.
```
