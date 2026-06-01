"""
engine.py — the brain of the outreach robot.
Loads leads, dedups, checks suppression, personalizes per-lead email + LinkedIn copy,
renders send-ready files, and tracks status. No human edits needed per lead.
"""
import csv, os, json, hashlib, datetime, re
import templates as T

HERE = os.path.dirname(__file__)
OUTBOX = os.path.join(HERE, "outbox")
SUPPRESSION = os.path.join(HERE, "suppression.csv")
STATE = os.path.join(HERE, "state.json")
SENT_LOG = os.path.join(HERE, "sent_log.csv")

# Campaign constants (update SPOTS honestly as founders join)
SPOTS_LEFT = 14
DEADLINE = datetime.date(2026, 8, 2)


def days_to_deadline(today=None):
    today = today or datetime.date.today()
    return max(0, (DEADLINE - today).days)


def _norm(s):
    return (s or "").strip()


def first_name(person, company):
    p = _norm(person)
    if p:
        return p.split()[0]
    return "there"  # fallback when contact not yet researched


def load_suppression():
    s = set()
    if os.path.exists(SUPPRESSION):
        for row in csv.DictReader(open(SUPPRESSION, encoding="utf-8")):
            for k in ("email", "Email", "company", "Company"):
                if row.get(k):
                    s.add(row[k].strip().lower())
    return s


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {}


def save_state(state):
    json.dump(state, open(STATE, "w", encoding="utf-8"), indent=2)


def lead_id(lead):
    key = (lead.get("email") or lead.get("Company") or lead.get("company") or "").strip().lower()
    return hashlib.sha1(key.encode()).hexdigest()[:10]


def tokens(lead):
    company = _norm(lead.get("Company") or lead.get("company"))
    vertical = _norm(lead.get("Vertical") or lead.get("vertical"))
    usecase = _norm(lead.get("Likely LLM use case (personalization hook)")
                    or lead.get("usecase") or "your LLM-driven decisions")
    person = _norm(lead.get("Contact (RESEARCH)") or lead.get("Person") or lead.get("person"))
    return {
        "first": first_name(person, company),
        "company": company or "your team",
        "usecase": usecase,
        "vertical": vertical,
        "spots": SPOTS_LEFT,
        "days": days_to_deadline(),
        "snapshot": T.SNAPSHOT_LINK,
        "cal": T.CAL_LINK,
    }


def segment_for(vertical):
    return T.VERTICAL_SEGMENT.get(vertical, "head_ai")


def _tidy(text):
    """Clean up when contact name is unknown (fallback 'there'), so copy reads natural."""
    text = text.replace("thanks there!", "thanks!").replace("thanks !", "thanks!")
    for lead_in in ("there — ", "there —", "there - "):
        if text.startswith(lead_in):
            text = text[len(lead_in):].lstrip()
            break
    if text.startswith("— "):
        text = text[2:]
    return text


def render_email(lead, step=1):
    tk = tokens(lead)
    seg = segment_for(tk["vertical"])
    if step == 1:
        tpl = T.EMAIL[seg]
    else:
        tpl = T.EMAIL_FOLLOWUP[step]
    subject = tpl["subject"].format(**tk)
    body = _tidy(tpl["body"].format(**tk))
    unsub = f"{T.SNAPSHOT_LINK}?unsub={lead_id(lead)}"
    footer = T.FOOTER.format(sender=T.SENDER_NAME, title=T.SENDER_TITLE,
                             addr=T.COMPANY_ADDR, unsub=unsub)
    return subject, body + footer


def render_linkedin(lead, kind="connect"):
    tk = tokens(lead)
    return _tidy(T.LINKEDIN[kind].format(**tk))


def email_ok(lead):
    e = _norm(lead.get("email") or lead.get("LinkedIn/Email (RESEARCH)") or "")
    return bool(re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", e)), e


def build_campaign(leads, step=1, daily_cap=60):
    """Returns list of message dicts ready to send/queue. Respects suppression, dedup, cap."""
    sup = load_suppression()
    state = load_state()
    out = []
    sent_today = 0
    for lead in leads:
        lid = lead_id(lead)
        company = _norm(lead.get("Company") or lead.get("company")).lower()
        valid_email, email = email_ok(lead)
        # suppression
        if company in sup or (email and email.lower() in sup):
            continue
        # dedup / already at/over this step
        st = state.get(lid, {})
        if st.get("email_step", 0) >= step:
            continue
        if sent_today >= daily_cap:
            break
        subject, body = render_email(lead, step)
        li_connect = render_linkedin(lead, "connect")
        li_dm = render_linkedin(lead, "dm1")
        out.append({
            "lead_id": lid,
            "company": _norm(lead.get("Company") or lead.get("company")),
            "person": _norm(lead.get("Contact (RESEARCH)") or lead.get("Person") or ""),
            "email": email,
            "email_valid": valid_email,
            "vertical": _norm(lead.get("Vertical") or lead.get("vertical")),
            "step": step,
            "subject": subject,
            "body": body,
            "linkedin_connect": li_connect,
            "linkedin_dm": li_dm,
        })
        sent_today += 1
    return out


def write_outbox(messages):
    """Write per-lead send-ready files + a combined outbox.csv (mail-merge friendly)."""
    os.makedirs(OUTBOX, exist_ok=True)
    csv_path = os.path.join(OUTBOX, "outbox.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lead_id", "company", "person", "email", "email_valid",
                    "vertical", "step", "subject", "body", "linkedin_connect", "linkedin_dm"])
        for m in messages:
            w.writerow([m["lead_id"], m["company"], m["person"], m["email"], m["email_valid"],
                        m["vertical"], m["step"], m["subject"], m["body"],
                        m["linkedin_connect"], m["linkedin_dm"]])
    for m in messages:
        safe = re.sub(r"[^A-Za-z0-9_-]", "_", m["company"])[:40] or m["lead_id"]
        path = os.path.join(OUTBOX, f"{safe}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {m['company']}  ·  {m['vertical']}  ·  step {m['step']}\n\n")
            f.write(f"**Email valid:** {m['email_valid']}  ·  **To:** {m['email'] or '(research email)'}\n\n")
            f.write("## EMAIL\n\n")
            f.write(f"**Subject:** {m['subject']}\n\n{m['body']}\n\n")
            f.write("## LINKEDIN — connect note\n\n" + m["linkedin_connect"] + "\n\n")
            f.write("## LINKEDIN — DM after accept\n\n" + m["linkedin_dm"] + "\n")
    return csv_path


def mark_sent(messages, channel="email"):
    """Advance state + append to sent_log. Call after a real send (or queued handoff)."""
    state = load_state()
    new = not os.path.exists(SENT_LOG)
    with open(SENT_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "lead_id", "company", "channel", "step", "subject", "status"])
        for m in messages:
            st = state.setdefault(m["lead_id"], {})
            if channel == "email":
                st["email_step"] = m["step"]
            st["last_touch"] = datetime.datetime.utcnow().isoformat()
            w.writerow([st["last_touch"], m["lead_id"], m["company"], channel,
                        m["step"], m["subject"], "sent"])
    save_state(state)
