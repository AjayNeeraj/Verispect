# Railway Deployment Guide — Verispect

## Step 1: Prepare GitHub Repository

1. Initialize git (if not already done):
   ```powershell
   git init
   git add .
   git commit -m "Initial Verispect commit — streaming support + dashboard"
   ```

2. Push to GitHub:
   ```powershell
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/verispect.git
   git push -u origin main
   ```

## Step 2: Create Railway Account & Project

1. Go to https://railway.app
2. Sign up (GitHub auth recommended)
3. Create a new project → "Deploy from GitHub repo"
4. Select your verispect repository
5. Authorize Railway to access your GitHub

## Step 3: Configure Environment Variables in Railway

Once the project is created in Railway, go to **Variables** tab and add:

```
OPENAI_API_KEY=sk-proj-xxxx...  (your actual OpenAI key)
VERISPECT_API_KEY=your-secret-key-here  (optional, for dashboard auth)
DATABASE_URL=postgresql://...  (Railway will auto-populate this after Postgres is added)
```

## Step 4: Add PostgreSQL Database to Railway

1. In your Railway project, click **+ New**
2. Select **Add Database → PostgreSQL**
3. Railway will auto-generate a `DATABASE_URL` environment variable
4. This replaces SQLite for production

## Step 5: Deploy the Application

Railway will automatically:
1. Detect `Procfile`
2. Run `pip install -r requirements.txt`
3. Start the server with the command in `Procfile`
4. Expose your app at a Railway-generated URL (e.g., `verispect-prod.up.railway.app`)

## Step 6: Point Custom Domain

1. In Railway project settings, go to **Domains**
2. Add custom domain: `verispectai.com`
3. Follow Railway's DNS instructions to point your domain registrar to Railway's nameservers
4. Within 10-30 minutes, your app will be live at `https://verispectai.com`

## Step 7: Verify Deployment

Test endpoints:

```powershell
# Health check
curl https://verispectai.com/health

# Metrics endpoint
curl https://verispectai.com/api/metrics
```

## Step 8: Deploy Frontend to Vercel (Optional but Recommended)

The React dashboard should be deployed separately to Vercel for speed:

1. Go to https://vercel.com
2. Sign up with GitHub
3. Import your verispect repository
4. Configure build:
   - Root: `dashboard`
   - Build command: `npm run build`
   - Output: `dist`
5. Add environment variable:
   - `VITE_API_URL=https://verispectai.com/api` (optional if using smart detection in api.js)
6. Deploy

Your dashboard will then live at `verispect.vercel.app` or a custom domain.

## Notes

- Railway handles HTTPS automatically with free SSL
- Database backups are automatic on Railway Postgres
- Logs are viewable in Railway dashboard (Deployments tab)
- Environment variables are encrypted at rest
- The `DATABASE_URL` format will be PostgreSQL, so the app already handles both SQLite (dev) and Postgres (prod) via the `databases` library

## Troubleshooting

**App won't start:**
- Check Railway logs: Deployments → View Logs
- Ensure all dependencies in `requirements.txt` are correct
- Verify `Procfile` syntax

**Database errors:**
- Ensure `DATABASE_URL` environment variable is set
- Railway Postgres is accessible from the app by default

**CORS errors:**
- Already configured in `main.py` to allow `https://verispectai.com`
- If using Vercel for frontend, also add that origin to CORS in `main.py`

**Domain not resolving:**
- DNS propagation takes 10-30 min. Check Railway's DNS records in domain settings.
- Use `nslookup verispectai.com` to verify.
