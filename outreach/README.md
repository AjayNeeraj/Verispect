# Verispect Outreach Robot

Runs the outbound machine. **One command. No per-lead work.**

```bash
python outreach/run.py            # build + personalize + write send-ready files (dry-run)
python outreach/run.py --send     # actually email (needs SMTP env, see below)
python outreach/run.py --step 2   # follow-up wave for leads already contacted
```

## What it does automatically
load leads → dedup → drop suppressed/opt-outs → personalize **email + LinkedIn** per lead (company, use case, correct segment) → write `outbox/<company>.md` + `outbox/outbox.csv` → (optional) send via SMTP, throttled → log to `sent_log.csv` → advance each lead's step in `state.json`.

## The only inputs it needs from you (one-time)
1. **Verified emails** in the lead CSV (`gtm/07-sprint/starter-target-list.csv`, column `LinkedIn/Email (RESEARCH)` or add an `email` column). Without them, email is skipped and you get LinkedIn-ready copy instead.
2. **To send email live**, set env vars then `--send`:
   ```bash
   export SMTP_HOST=smtp.yourhost.com SMTP_PORT=587 \
          SMTP_USER=ajay@verispectai.com SMTP_PASS=*** FROM_EMAIL=ajay@verispectai.com
   python outreach/run.py --send
   ```
   Throttled (25s gap), hard cap 50/day, GDPR footer + unsubscribe on every message.

## Files
- `run.py` — CLI orchestrator · `engine.py` — personalize/dedup/state · `sender.py` — SMTP (dry-run default) · `templates.py` — message copy (edit here)
- `suppression.csv` — opt-outs (add anyone who says STOP; never emailed again)
- `outbox/` — send-ready output · `sent_log.csv` + `state.json` — auto-tracking

## FULL EMAIL AUTOPILOT (find → verify → personalize → send → log → follow-up)
Two keys + one login and it's hands-off:
```bash
export HUNTER_API_KEY=...            # hunter.io — finds + verifies business emails (legit B2B data)
export SMTP_HOST=... SMTP_PORT=587 SMTP_USER=ajay@verispectai.com SMTP_PASS=... FROM_EMAIL=ajay@verispectai.com
python outreach/run.py --enrich --send --cap 40
```
`--enrich` auto-finds the right contact (CTO/Head of AI/DPO) per company via Hunter/Apollo, verifies deliverability (only verified emails are used — protects your domain), writes them back to the lead CSV so you never re-pay. Then personalizes + sends, throttled, GDPR footer + unsubscribe, logs, advances each lead's wave.

**Windows:** fill `outreach/autopilot.bat`, then schedule daily:
```
schtasks /create /tn "Verispect Outreach" /tr "%CD%\outreach\autopilot.bat" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:30
```
Now it runs itself every weekday. Update `SPOTS_LEFT` in `engine.py` as founders join.

## Why emails come from Hunter/Apollo, NOT a LinkedIn/IG scraper
Scraping LinkedIn/IG for emails or auto-DMing = account ban + GDPR breach + ToS/computer-misuse exposure. Fatal for a compliance brand. Hunter/Apollo are B2B data providers that carry their own lawful basis and honor opt-outs — the compliant way to get the same reach. LinkedIn outreach itself = your account + the robot's pre-written copy (paste-send or browser-assisted), never a bot farm.

## Honest boundaries
- LinkedIn/IG have no compliant send API for cold DMs — the robot writes the copy; you paste-send from your account (or a throttled, ToS-safe assistant). Mass-DM bots = ban + GDPR breach.
- Email sending is fully automatable here once SMTP creds + verified addresses exist.
- Social posts (launch, content) **can** be fully auto-scheduled to LinkedIn/Reddit/X via Postiz — ask to switch that on.
