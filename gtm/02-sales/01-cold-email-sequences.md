# Cold Email Sequences

*All sequences are GDPR-legitimate-interest compliant: role-relevant, identified sender, one-click opt-out, business addresses only. See outreach rules in `00-sales-playbook-overview.md`.*

**Format rules:** <60 word body, 1 idea, 1 soft CTA, plain text, no images/tracking pixels that aren't disclosed, subject <5 words, send from founder@verispectai.com (real person). Personalise the first line for real — no "I came across your profile" filler.

Every email footer:
> Verispect · [address] · You're receiving this because your role relates to AI/ML in production. Not relevant? Reply "stop" and I'll remove you immediately — [unsubscribe link].

---

## SEQUENCE A — CTO / Technical Founder (HR-tech, fintech using LLM in decisions)

### Email 1 — Day 0 — "the silent change"
**Subject:** your model changed?

> Hi {First}, quick one — {Company} uses an LLM to {screen candidates / score X}. When OpenAI updates the model behind `gpt-4o-mini`, you don't get a changelog — but your scoring behaviour can shift overnight.
>
> We catch that. One line of code, zero added latency, and we never see your raw data (only hashes + vectors).
>
> Worth a 15-min look, or not on your radar yet?
> — Ajay, founder, Verispect

### Email 2 — Day 3 — proof / value-add (no ask)
**Subject:** found bias in an afternoon

> {First} — not chasing, just useful: on our first calibration run, a mainstream model rated two identical candidates differently — it cited *age* for the 54-year-old and not the identical 26-year-old. Reproducible.
>
> If you run LLM hiring/credit decisions, that's the kind of thing the EU AI Act (Art. 10/13) will want you monitoring by 2026.
> 2-page sample report if useful — want it?

### Email 3 — Day 7 — the artifact
**Subject:** the PDF your buyer will ask for

> {First}, when an enterprise prospect's security team asks "prove your AI isn't biased," most startups have nothing. Verispect outputs the exact audit-ready PDF — mapped article-by-article to the EU AI Act.
>
> Happy to generate a free one against your model so you see real numbers. Reply "snapshot" and I'll send setup (5 min, one line).

### Email 4 — Day 14 — the break-up
**Subject:** closing the loop

> {First} — I'll stop here so I'm not noise. If monitoring/compliance for your LLM ever lands on your plate, we're a one-line integration away and we never touch your data.
>
> Wishing {Company} well — Ajay. (Reply "stop" to be removed for good.)

---

## SEQUENCE B — Head of AI / Responsible AI / DPO (scale-up, regulated)

### Email 1 — Day 0
**Subject:** Art. 72 monitoring evidence

> Hi {First}, you likely own AI Act readiness at {Company}. The hard-to-evidence parts are continuous post-market monitoring (Art. 72) and bias governance (Art. 10) — most teams have the policy but not the live signal.
>
> Verispect generates that evidence automatically: active bias/drift probes → an article-mapped PDF. Privacy-first (we never receive PII).
> Open to a 20-min walkthrough?

### Email 2 — Day 4
**Subject:** closes the "unmonitored model" line

> {First} — most risk registers I see have a line like "model drift: unmonitored." We close it: continuous probing + a timestamped audit log + remediation recommendations per finding.
>
> Can send the sample report + our EU AI Act coverage mapping + DPA so your legal team can pre-clear us. Want the pack?

### Email 3 — Day 9
**Subject:** for your DPO

> {First}, the detail your DPO will like: we reduce data risk instead of adding it. We receive only SHA-256 hashes and embedding vectors — never prompts or responses. Golden probes stay encrypted on your own infra.
>
> That usually turns security review from a blocker into a green light. 20 minutes this week?

### Email 4 — Day 16 — breakup
**Subject:** last note

> {First}, I'll leave it here. When continuous AI monitoring moves up your roadmap, we're built exactly for the regulated, high-risk case. Pack's yours whenever — just reply. (Or "stop" to be removed.)

---

## SEQUENCE C — Re-engage free-snapshot users who didn't convert

### Email 1 — Day 2 after snapshot
**Subject:** your drift score

> {First}, you ran a Verispect snapshot — your avg drift was {X} with {N} flagged events in {category}. That's worth watching continuously, not once. Pro turns this into ongoing monitoring + monthly auto-reports for €99/mo. Want me to flip it on?

### Email 2 — Day 6
**Subject:** the {category} flag

> {First}, the {category} flags in your snapshot are the kind regulators and enterprise buyers probe hardest. Here's what they mean + how to remediate: {link}. Happy to walk through your specific results — 15 min?

---

## A/B subject line bank (test these)
- "your model changed?" / "silent model update" / "is your AI still fair?"
- "the PDF your buyer will ask for" / "Art. 72 evidence" / "prove your AI behaves"
- "found bias in an afternoon" / "two identical candidates, different scores"

## Personalisation tokens that actually matter
`{specific LLM use case}` > `{recent raise}` > `{enterprise customer they list}` > `{RAI claim on their site}`. The first line must prove you understand *their* product. If you can't write a true, specific first line, don't email them — they're not researched enough yet.

## Sending hygiene
- Warm the domain; <40 cold sends/day/inbox at first.
- SPF/DKIM/DMARC set. Plain text. No link-heavy first email.
- Maintain a permanent suppression list; opt-outs honoured within 24h, forever.
- Track replies, not opens-via-pixel (pixels are a consent grey area — avoid or disclose).
