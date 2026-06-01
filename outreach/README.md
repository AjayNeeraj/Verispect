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

## Daily, hands-off
Cron it, or it's wired into the project scheduler to run once/day and auto-advance waves. Update `SPOTS_LEFT` in `engine.py` as founders join.

## Honest boundaries
- LinkedIn/IG have no compliant send API for cold DMs — the robot writes the copy; you paste-send from your account (or a throttled, ToS-safe assistant). Mass-DM bots = ban + GDPR breach.
- Email sending is fully automatable here once SMTP creds + verified addresses exist.
- Social posts (launch, content) **can** be fully auto-scheduled to LinkedIn/Reddit/X via Postiz — ask to switch that on.
