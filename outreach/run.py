"""
run.py — ONE command runs the whole outreach robot.

Usage:
  python outreach/run.py                      # build step-1 campaign, DRY-RUN (writes outbox/)
  python outreach/run.py --step 2             # build follow-up #2 for leads already at step 1
  python outreach/run.py --send               # actually send via SMTP (needs env vars)
  python outreach/run.py --leads path.csv     # use a different lead file
  python outreach/run.py --cap 40             # daily cap

What it does, no human per-lead work:
  load leads -> dedup -> drop suppressed -> personalize email+LinkedIn -> write send-ready
  files to outbox/ -> (optionally) send via SMTP -> log + advance each lead's state.

Daily loop: run it once/day (cron or the scheduler). It auto-advances steps & respects caps.
"""
import argparse, csv, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import engine, sender, enrich

DEFAULT_LEADS = os.path.join(os.path.dirname(__file__), "..", "gtm", "07-sprint", "starter-target-list.csv")

def load_leads(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _persist_emails(path, leads):
    """Write enriched emails/contacts back to the lead CSV so we never re-pay to enrich."""
    if not leads:
        return
    fields = list(leads[0].keys())
    if "email" not in fields:
        fields.append("email")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for ld in leads:
            w.writerow({k: ld.get(k, "") for k in fields})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leads", default=DEFAULT_LEADS)
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--cap", type=int, default=60)
    ap.add_argument("--send", action="store_true", help="actually send via SMTP (else dry-run)")
    ap.add_argument("--enrich", action="store_true", help="find+verify emails via Hunter/Apollo (needs API key)")
    args = ap.parse_args()

    leads = load_leads(args.leads)
    print(f"[run] loaded {len(leads)} leads from {os.path.abspath(args.leads)}")

    if args.enrich:
        leads, found = enrich.enrich_leads(leads)
        if found:
            _persist_emails(args.leads, leads)
            print(f"[run] wrote {found} verified emails back to {args.leads}")
    print(f"[run] {engine.SPOTS_LEFT} founding spots left · {engine.days_to_deadline()} days to deadline")

    msgs = engine.build_campaign(leads, step=args.step, daily_cap=args.cap)
    print(f"[run] built {len(msgs)} personalized messages (step {args.step}, after dedup/suppression/cap)")

    csv_path = engine.write_outbox(msgs)
    print(f"[run] wrote send-ready files -> {os.path.abspath(engine.OUTBOX)}")
    print(f"[run] mail-merge file        -> {os.path.abspath(csv_path)}")

    valid = sum(1 for m in msgs if m["email_valid"])
    print(f"[run] {valid}/{len(msgs)} have a valid email (rest = LinkedIn-only until email researched)")

    if args.send:
        print("[run] SENDING (live if SMTP env set)...")
        s, sk = sender.send_batch(msgs, live=True)
        engine.mark_sent([m for m in msgs if m["email_valid"]], channel="email")
        print(f"[run] sent={s} skipped={sk}")
    else:
        # dry-run still demonstrates the send path + marks LinkedIn queue, does NOT advance email state
        sender.send_batch(msgs, live=False)
        print("[run] DRY-RUN complete. Review outbox/. To go live: set SMTP_* env + rerun with --send")

    print("\nNEXT:")
    print("  • Review outbox/ (one .md per lead) or outbox.csv (import into any mail-merge / CRM).")
    print("  • LinkedIn: copy linkedin_connect / linkedin_dm per lead (send from your account).")
    print("  • Go live email: export SMTP_HOST SMTP_USER SMTP_PASS FROM_EMAIL ; rerun with --send.")
    print("  • Tomorrow: rerun (same cmd) for new leads, or --step 2 for follow-ups.")

if __name__ == "__main__":
    main()
