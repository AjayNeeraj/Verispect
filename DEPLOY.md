# Railway Deployment Guide — Verispect

## Architecture

Verispect runs as a **single Railway service**. The FastAPI backend serves:
- `/v1/chat/completions` — LLM middleware proxy
- `/api/*` — Dashboard API endpoints
- `/` — React dashboard (static files from `dashboard/dist/`)

No separate Vercel deployment needed.

---

## Step 1: Push Code to GitHub

Already done. Repo: `github.com/AjayNeeraj/verispect`

```powershell
git add -A
git commit -m "Production-ready: add db lifecycle, static serving, Railway build"
git push origin main
```

## Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. **New Project** → **Deploy from GitHub Repo**
4. Select `AjayNeeraj/verispect`
5. Railway detects `railway.json` and starts building automatically

## Step 3: Add PostgreSQL Database

1. In your Railway project, click **+ New**
2. Select **Database → PostgreSQL**
3. Railway auto-generates `DATABASE_URL` and links it to your service
4. Verify: click your service → Variables → `DATABASE_URL` should be present

## Step 4: Set Environment Variables

In Railway → your service → **Variables** tab:

| Variable | Value |
|---|---|
| `OPENAI_API_KEY` | Your actual OpenAI API key |
| `VERISPECT_API_KEY` | *(optional — leave blank for no dashboard auth)* |

> `PORT` and `DATABASE_URL` are auto-set by Railway — don't touch them.

## Step 5: Deploy

Railway deploys automatically on:
- Every push to `main` branch
- Every environment variable change

The build command (from `railway.json`) will:
1. `pip install -r requirements.txt` — Python deps
2. `cd dashboard && npm install && npm run build` — React build

Watch **Deployments** tab for build logs.

## Step 6: Get Railway URL

1. Service → **Settings** → **Networking**
2. Click **Generate Domain** → get a URL like `verispect-production.up.railway.app`
3. Test: `https://verispect-production.up.railway.app/health` → `{"status": "alive"}`

## Step 7: Add Custom Domain — verispectai.com

1. Service → **Settings** → **Networking** → **Custom Domain**
2. Click **Add Custom Domain** → enter `verispectai.com`
3. Railway shows a CNAME record value

## Step 8: Configure DNS

At your domain registrar, add:

| Type | Host | Value | TTL |
|---|---|---|---|
| **CNAME** | `@` (root) | Railway's CNAME value | 300 |
| **CNAME** | `www` | `verispectai.com` | 300 |

> **Note:** If your registrar doesn't support root CNAME, use Cloudflare (free) for CNAME flattening.

Railway provides **automatic HTTPS/SSL** — no extra setup.

## Step 9: Verify

```powershell
# DNS propagation (wait 5-30 min)
nslookup verispectai.com

# Health check
curl https://verispectai.com/health

# API
curl https://verispectai.com/api/metrics

# Dashboard — open in browser
start https://verispectai.com
```

## Step 10: Seed Production Database

Run calibration against the live server:

```powershell
# Set DATABASE_URL to your Railway Postgres connection string locally
$env:DATABASE_URL = "postgresql://..."
python calibrate.py
```

Or send test calls through the middleware:
```python
from openai import OpenAI
client = OpenAI(api_key="sk-...", base_url="https://verispectai.com/v1")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response)
```

---

## Troubleshooting

**Build fails:**
- Check Railway build logs (Deployments → View Logs)
- Ensure Node.js is available (Railway's Nixpacks detects `package.json`)

**Database errors:**
- Verify `DATABASE_URL` is set in Variables
- The `databases` library auto-detects PostgreSQL from the URL prefix

**CORS errors:**
- Already configured for `https://verispectai.com` and `https://www.verispectai.com`
- Not needed in production (same origin) but kept for API consumers

**Domain not resolving:**
- DNS propagation: 5-30 min
- Verify: `nslookup verispectai.com`
- Check Railway domain settings for green checkmark
