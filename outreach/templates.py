"""
templates.py — message bank for the Verispect outreach robot.
Segment chosen from the lead's vertical. Tokens: {first} {company} {usecase} {vertical} {spots} {days}
All copy is GDPR-safe: identified sender, role-relevant, honest claims, unsubscribe in footer.
Edit copy here; the engine renders per-lead.
"""

SENDER_NAME = "Ajay"
SENDER_TITLE = "Founder, Verispect"
SENDER_EMAIL = "ajay@verispectai.com"
COMPANY_ADDR = "Verispect, [registered address]"
SNAPSHOT_LINK = "https://verispectai.com/founding"
CAL_LINK = "https://cal.com/verispect/15min"

# vertical -> segment key
VERTICAL_SEGMENT = {
    "HR-tech": "cto",
    "Fintech": "cto",
    "Insurtech": "head_ai",
    "Legal-tech": "head_ai",
    "AI/Enterprise": "head_ai",
}

FOOTER = (
    "\n\n—\n{sender}, {title}\nVerispect · {addr}\n"
    "You're receiving this because your role relates to AI in production and the EU AI Act. "
    "Not relevant? Reply STOP and I'll remove you immediately. Unsubscribe: {unsub}"
)

# ── EMAIL: step 1 by segment ────────────────────────────────────────────────
EMAIL = {
    "cto": {
        "subject": "{company}'s AI + Aug 2026",
        "body": (
            "Hi {first},\n\n"
            "{company} uses an LLM for {usecase}. From 2 Aug 2026 the EU AI Act needs that to "
            "prove it isn't drifting or biased — and providers change models behind a stable name "
            "with no changelog.\n\n"
            "Verispect generates that proof in one line of code. Zero added latency, and we never "
            "see your data (only hashes + vectors).\n\n"
            "Want a free 5-minute snapshot of your model's real drift? {snapshot}\n"
            "(Opening founding pricing to 20 EU/SG/UAE teams — {spots} spots left.)"
        ),
    },
    "head_ai": {
        "subject": "Art. 72 evidence before the deadline",
        "body": (
            "Hi {first},\n\n"
            "You likely own AI Act readiness at {company}. The hard part is evidencing continuous "
            "monitoring (Art. 72) and bias (Art. 10) for {usecase} — policy is easy, live proof isn't.\n\n"
            "Verispect auto-generates it: active probes → an article-mapped readiness report. "
            "Privacy-first — we receive only hashes and vectors, never prompts or PII.\n\n"
            "Want the sample report + a free snapshot of your model? {snapshot}"
        ),
    },
}

# ── EMAIL follow-ups (same for both segments; sent on cadence) ───────────────
EMAIL_FOLLOWUP = {
    2: {  # day +3
        "subject": "found bias in an afternoon",
        "body": (
            "{first} — quick proof, not a chase: on our first run a mainstream model rated two "
            "identical candidates differently — citing age for the 54-year-old, not the 26-year-old. "
            "Reproducible. That's the exact risk the Act targets.\n\n"
            "Free snapshot of {company}'s model whenever it's useful: {snapshot}"
        ),
    },
    3: {  # day +7  (breakup + scarcity)
        "subject": "founding spots ({spots} left)",
        "body": (
            "{first}, closing the Founding 20 soon — {spots} spots left, then public pricing.\n\n"
            "If getting {company} audit-ready before Aug 2026 is on your list, this is the cheapest "
            "and fastest it'll be: €79/mo locked for life, I set it up with you, free snapshot first.\n\n"
            "Want a spot, or should I close the loop? Reply STOP and I'll leave you be."
        ),
    },
}

# ── LinkedIn ────────────────────────────────────────────────────────────────
LINKEDIN = {
    "connect": (
        "Hi {first} — building Verispect: active bias/drift detection for production LLMs, EU AI Act "
        "focus. Saw {company} uses an LLM for {usecase} — exactly what the Act covers from Aug 2026. "
        "Opening 20 founding spots for EU AI teams; thought you'd want to know. Connect?"
    ),
    "dm1": (
        "Thanks for connecting! Relevant + quick: from 2 Aug 2026 the EU AI Act needs high-risk "
        "AI ({usecase} qualifies) to evidence bias monitoring + drift. Most teams have the policy, not "
        "the live proof.\n\nI built the tool that generates it — one line, zero latency, we never see "
        "your data. Want a free 5-min snapshot of {company}'s model? No pitch, just your real numbers."
    ),
    "dm_followup": (
        "No rush {first} — sharing in case useful: the Art. 72 monitoring obligation is the one most "
        "teams can't evidence yet. Free snapshot's there whenever; founding spots filling ({spots}/20 left). {snapshot}"
    ),
}
