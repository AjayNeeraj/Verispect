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

# Compact 2-line footer (GDPR needs identity + opt-out, kept minimal so the email stays short)
FOOTER = (
    "\n\n— {sender}, Verispect · {unsub} to opt out"
)

# ── EMAIL: step 1 by segment — SHORT 3-LINERS ───────────────────────────────
# Modern cold style: 1 line context, 1 line value+proof, 1 line easy CTA. No fluff.
EMAIL = {
    "cto": {
        "subject": "ai act · {company}",
        "body": (
            "{first} — {company}'s LLM for {usecase} is high-risk under the EU AI Act (live Aug 2026), "
            "and providers change models with no changelog.\n"
            "Verispect proves yours isn't drifting/biased in 1 line of code — we never see your data.\n"
            "Free 5-min snapshot of your model? {snapshot}"
        ),
    },
    "head_ai": {
        "subject": "art. 72 proof · {company}",
        "body": (
            "{first} — Art. 72 + 10 of the AI Act (Aug 2026) need {company} to *evidence* bias + drift "
            "monitoring for {usecase}. Policy's easy; live proof isn't.\n"
            "Verispect auto-generates it, article-mapped — and never sees your data (hashes + vectors only).\n"
            "Want the sample report + a free snapshot? {snapshot}"
        ),
    },
}

# ── EMAIL follow-ups — even shorter ──────────────────────────────────────────
EMAIL_FOLLOWUP = {
    2: {  # day +3
        "subject": "2 identical CVs, different scores",
        "body": (
            "{first} — proof, not a chase: a mainstream model docked the 54-yr-old vs an identical "
            "26-yr-old. Reproducible. That's the AI Act risk.\n"
            "Free snapshot of {company}'s model: {snapshot}"
        ),
    },
    3: {  # day +7  (breakup + scarcity)
        "subject": "{spots} founding spots left",
        "body": (
            "{first} — closing the Founding 20 ({spots} left). €79/mo locked for life, I set it up, "
            "free snapshot first.\n"
            "Want a spot before Aug 2026, or should I close the loop?"
        ),
    },
}

# ── LinkedIn — short, human, no corporate ────────────────────────────────────
LINKEDIN = {
    "connect": (
        "{first} — {company} runs LLMs in {usecase}; that's high-risk under the EU AI Act from Aug 2026. "
        "Built Verispect to prove a model isn't biased/drifting in 1 line (we never see your data). Worth connecting?"
    ),
    "dm1": (
        "thanks {first}! quick + real: Aug 2026 the AI Act needs your {usecase} model to prove no bias/drift. "
        "Verispect does it in one line, we never see your data.\n"
        "free 5-min snapshot of {company}'s model? just your real numbers, no pitch."
    ),
    "dm_followup": (
        "{first} — no rush, the Art. 72 monitoring bit is the one most teams can't evidence yet. "
        "free snapshot whenever ({spots}/20 founding spots left): {snapshot}"
    ),
}
