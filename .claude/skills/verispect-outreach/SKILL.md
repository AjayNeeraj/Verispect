---
name: verispect-outreach
description: Run the Verispect outbound sales machine — find/verify leads, generate short 3-liner personalized email + LinkedIn copy, send via SMTP, schedule daily, track the 15-day Founding-20 sprint. Use when the user says "run outreach", "send the emails", "do a wave", "verispect outreach", "new leads", "follow up", "/verispect-outreach", or asks to contact prospects for Verispect.
---

# Verispect Outreach Machine

Operate the outbound engine in `outreach/`. Goal: book free snapshots → demos → Founding-20 closes before the EU AI Act deadline (2 Aug 2026). Floor 10 sales, target 15-20 in the 15-day sprint.

## Run a wave (the one command)
```bash
python outreach/run.py                     # dry-run: build + write send-ready copy to outbox/
python outreach/run.py --enrich            # + find/verify emails via Hunter/Apollo (needs HUNTER_API_KEY)
python outreach/run.py --enrich --send     # FULL autopilot: find → verify → personalize → send → log
python outreach/run.py --step 2            # follow-up wave for already-contacted leads
python outreach/run.py --step 3            # final scarcity/breakup wave
```
Live send needs env: `HUNTER_API_KEY`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL` (the user's custom domain email). Windows hands-off: fill + schedule `outreach/autopilot.bat` via `schtasks`.

## Copy rules (NON-NEGOTIABLE — modern outbound)
- **3 lines max.** No 200-word emails. 1 line context (their pain), 1 line value+proof, 1 line easy CTA.
- Subject: 2-4 words, lowercase ok (e.g. "ai act · {company}").
- Conversational, human, specific to THEIR use case. Edit copy in `outreach/templates.py`.
- Lead with their world + the deadline; close with the free 5-min snapshot.

## Compliance guardrails (we ARE the compliance brand — never break)
- Claims: "audit-ready / evidence / proves", NEVER "compliant/certified/guaranteed". Badge = "Monitoring Active".
- Emails come from Hunter/Apollo (lawful B2B data) — NEVER scrape LinkedIn/IG or auto-DM bots (ban + GDPR breach).
- Every email: identified sender + one-click opt-out. Honor STOP instantly → add to `outreach/suppression.csv` (never emailed again).
- LinkedIn = the user's own account + the robot's copy (paste-send or browser-assisted), human-paced.

## After a wave
- Review `outreach/outbox/` (one .md per lead) or `outbox.csv` (mail-merge).
- Log results in `gtm/07-sprint/Verispect-Sprint-Tracker.xlsx` (5 numbers: touches, snapshots, demos, closes, spots left).
- Update `SPOTS_LEFT` in `outreach/engine.py` + the landing page as founders join (keep scarcity honest).
- New replies → send free snapshot → demo → close. Price = $1,500/mo (Founding 20 locks $1,500 for life before it rises to $2,500). Never quote price in cold copy — sell the free snapshot; price on the call, anchored to AI Act fines (up to €15M / 3% turnover) vs €50k+ manual projects.

## Context
Full reshape/offer: `gtm/07-sprint/00-reshape-and-offer.md`. Battle plan + funnel math: `gtm/07-sprint/01-15-day-battle-plan.md`. Day-0 setup: `gtm/07-sprint/06-day0-setup-checklist.md`.
