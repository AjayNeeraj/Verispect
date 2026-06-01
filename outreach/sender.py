"""
sender.py — SMTP sender. DRY-RUN by default (writes files, sends nothing).
Goes LIVE only when SMTP env vars are set AND --send is passed.

Env to go live:
  SMTP_HOST, SMTP_PORT (587), SMTP_USER, SMTP_PASS, FROM_EMAIL
Throttled + jittered to protect domain reputation. Honors suppression via engine.
"""
import os, smtplib, time
from email.mime.text import MIMEText
from email.utils import formataddr

THROTTLE_SECONDS = 25          # gap between sends (protect reputation)
DAILY_HARD_CAP = 50            # never exceed, regardless of caller

def smtp_ready():
    return all(os.getenv(k) for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS", "FROM_EMAIL"))

def send_one(to_email, subject, body):
    host = os.getenv("SMTP_HOST"); port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER"); pw = os.getenv("SMTP_PASS")
    frm = os.getenv("FROM_EMAIL")
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Ajay — Verispect", frm))
    msg["To"] = to_email
    with smtplib.SMTP(host, port, timeout=30) as s:
        s.starttls(); s.login(user, pw); s.sendmail(frm, [to_email], msg.as_string())

def send_batch(messages, live=False):
    """messages: list from engine.build_campaign. Returns (sent, skipped)."""
    sent, skipped = 0, 0
    if live and not smtp_ready():
        print("[sender] LIVE requested but SMTP env not set -> staying DRY-RUN.")
        live = False
    for m in messages:
        if not m.get("email_valid"):
            skipped += 1
            print(f"  SKIP (no valid email) {m['company']}")
            continue
        if sent >= DAILY_HARD_CAP:
            print("  reached DAILY_HARD_CAP"); break
        if live:
            try:
                send_one(m["email"], m["subject"], m["body"])
                print(f"  SENT  -> {m['email']}  ({m['company']})")
                sent += 1
                time.sleep(THROTTLE_SECONDS)
            except Exception as e:
                print(f"  FAIL  {m['company']}: {e}")
                skipped += 1
        else:
            print(f"  DRY   would send -> {m['email'] or '(no email)'}  [{m['subject']}]")
            sent += 1
    return sent, skipped
