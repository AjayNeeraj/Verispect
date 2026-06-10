# Website Copy — verispectai.com

*Ready-to-ship copy for the marketing site. Matches positioning (`01-strategy/03`) and respects claims guardrails (`04-legal-compliance/09`). Visual: purple #7c6eff + dark, clean, technical.*

---

## HOME

### Hero
**H1:** Your AI model changed. We're the only ones who noticed.
**Sub:** Verispect actively probes your production LLM for bias and drift and turns the result into the EU AI Act compliance evidence enterprises and regulators demand — in one line of code, with zero access to your data.
**Primary CTA:** Run a free snapshot → · **Secondary:** See a sample report
**Trust line:** We never receive your raw prompts or responses. Only hashes and vectors.

### Logo / social proof strip
"Trusted by AI teams building in high-risk domains" + [design-partner logos when available].

### Problem section
**Heading:** Logging tells you what your model said. Not that it started saying it differently.
> Providers update models behind a stable name. Fine-tunes degrade. Prompts drift. A hiring or credit model that was fair last month can quietly start discriminating — and nothing in your code changed. Observability tools can't catch it, because the inputs and outputs still look normal.

### Solution section (3 pillars)
**1. Active, not passive.** Calibrated synthetic probes + replays of your own traffic test behaviour continuously — catching change the moment it happens, including silent provider updates.
**2. Audit-ready by default.** Get the document a regulator or enterprise buyer accepts: a branded report mapped article-by-article to EU AI Act 9/10/13/14/72 and Annex III.
**3. Privacy by architecture.** We never receive your prompts or responses — only SHA-256 hashes and embedding vectors. Your sensitive data never leaves your machine.

### How it works (3 steps)
1. **Add one line.** `client = wrap(OpenAI(...), verispect_key="vs_live_...")`. Zero added latency.
2. **We probe & score.** On a sample of live traffic, Verispect fires bias/consistency probes and scores drift against your baseline — deterministically.
3. **You get the report.** A continuously-updated, audit-ready PDF mapped to the EU AI Act. Send it to your buyer or your auditor.

### Differentiator band
> **Observability watches. Assurance verifies.** Verispect is AI Behavioural Assurance — the layer Helicone, LangSmith, and Braintrust don't have. Keep your logger; add the proof.

### Compliance band
> Built for the EU AI Act high-risk deadline (2 Aug 2026; standalone Annex III may move to 2 Dec 2027 if the Digital Omnibus is adopted). Supports your obligations under Articles 10, 13, 14, and 72. *Verispect provides compliance evidence and monitoring — you remain the operator.*

### Final CTA
**H:** See if your model is drifting — in 5 minutes.
**CTA:** Run a free snapshot · No card. One line of code. We never see your data.

---

## FEATURES PAGE (sections)
- **Active probing** — 8 protected-characteristic bias categories + consistency probes.
- **Golden probes** — replay your own traffic to catch drift on your real use case; stored encrypted on your machine.
- **Deterministic scoring** — semantic similarity, no LLM in the loop, reproducible.
- **Compliance reports** — branded PDF, EU AI Act article mapping, drift log, remediation.
- **Dashboard** — compliance ring, drift timeline, per-category breakdown.
- **Alerts** — Slack/email when behaviour shifts. *(roadmap badge if not shipped)*
- **Privacy-first** — hashes + vectors only; DPA on request; we reduce your data risk.
- **One-line integration** — SDK or base-url swap; zero added latency.

---

## PRICING PAGE
*(pull tiers from `03-pricing-billing/00`)*
- Headline: **Compliance evidence, priced for startups.**
- Sub: Start free. Upgrade when it earns it. Cancel anytime.
- 3 cards: Free snapshot / **Verispect $1,500/mo** (Founding — most popular) / Enterprise (talk to us).
- FAQ: "Does this make me compliant?" → "No tool can — and we won't pretend. Verispect generates the monitoring and bias evidence the law asks for, mapped to the articles, so your team can stand behind it." · "Do you see our data?" → "No. Only hashes and vectors." · "Latency?" → "Zero added." · "Multi-model?" → "OpenAI-compatible today; more on the roadmap — talk to us about design-partner access."

---

## SECURITY / TRUST PAGE
- Lead: "Our biggest security control is that we don't hold your sensitive data."
- Sections from `04-legal-compliance/07`: data handling, encryption, access, privacy-by-design, sub-processors, SOC 2 (planned), responsible disclosure.
- Downloads: Security Overview, DPA, Sub-processor list.

---

## ABOUT PAGE
- The origin story (`01-strategy/01`), condensed: the silent-change insight + the afternoon bias finding + the mission. Founder bio (Ajay). Values (privacy, honesty, evidence). "Built solo, in public."

---

## MICROCOPY BANK
- Snapshot CTA: "Run a free snapshot" / "See your drift score in 5 min"
- Empty dashboard: "No drift detected yet — your model is behaving. We'll flag the moment that changes."
- Footer tagline: "Verify + Inspect. Every model. Every call. Every month."
- 404: "This page drifted. The rest of Verispect is stable."
- Cookie banner: minimal, honest, consent for non-essential only.

## SEO meta (examples)
- Home title: "Verispect — Active AI Bias & Drift Detection | EU AI Act Compliance Evidence"
- Home description: "Monitor your production LLM for bias and drift. Audit-ready EU AI Act reports. One line of code. We never see your data."
