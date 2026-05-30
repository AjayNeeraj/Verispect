# Verispect — Vision & Business Plan

*Version 1.0 · 2026-05-30 · Founder: Ajay*

---

## 1. One-sentence company

Verispect is privacy-first middleware that actively probes any LLM for behavioural drift and bias and turns the result into audit-ready EU AI Act compliance evidence — integrated with one line of code.

## 2. The problem (sharp version)

Companies put LLMs into decisions that change people's lives — who gets hired, who gets a loan, who gets triaged first. Three things then go wrong, silently:

1. **Provider drift.** OpenAI/Anthropic/Google update models behind a stable API name. Behaviour shifts overnight. The customer is never told.
2. **Fine-tune / prompt degradation.** Internal changes erode fairness without anyone noticing.
3. **Latent bias activation.** A model that scored Sarah and James equally last quarter starts docking points for a "parental leave" gap this quarter.

None of this is visible in a normal dashboard, because **logs only record what was asked and answered — not whether the answer would have been different yesterday.** The first time most teams find out is when a regulator, an enterprise procurement team, or a journalist asks "prove your model isn't biased." They have no evidence. Building the evidence pipeline in-house is a multi-month ML + compliance project nobody has time for.

## 3. The insight / wedge

> You cannot detect drift by watching. You have to *interrogate*.

Verispect fires **calibrated synthetic probes** — paired candidate profiles identical except for one protected characteristic (gender, age, race, nationality, disability, parental status, socioeconomic origin) plus consistency probes — at the live model on a small sample of traffic. It measures the semantic distance between today's answer and a recorded baseline, and between paired demographic answers. Divergence = a number you can put in a report.

This is a category Helicone/LangSmith/Braintrust structurally do not occupy: they are **passive observability**. Verispect is **active assurance**.

## 4. Product (what exists today)

- **One-line middleware / SDK.** `wrap(OpenAI(...), verispect_key=...)` or change the `base_url`. Zero added latency — all probe work is async/background.
- **Privacy-by-architecture.** Raw prompts/responses never leave the customer. Server receives only SHA-256 hashes + 384-dim embedding vectors. Golden probes (replays of the customer's own traffic) are stored encrypted on the *customer's* machine.
- **Two probe layers.** (1) 20 regulatory bias/consistency probes mapped to EU-protected characteristics; (2) golden probes sampled from real production traffic to catch drift on the customer's actual use case.
- **Deterministic drift scoring.** `all-MiniLM-L6-v2` cosine similarity → severity (none/low/medium/high). No LLM in the scoring loop, so results are reproducible.
- **The paid artifact: a branded multi-page PDF compliance report** mapping findings to EU AI Act Articles 9, 10, 13, 14, 72 and Annex III §4, plus GDPR Art. 22/24 considerations, methodology, drift-event log, and remediation recommendations.
- **Dashboard** (React): compliance ring, drift timeline, per-category bias breakdown, call log, on-demand report export.
- **Accounts, JWT auth, API key management.** Multi-tenant ready.

### Not yet built (roadmap, see strategy/04)
Multi-model native scoring beyond OpenAI-compatible, Slack/email alerting, SOC 2, scheduled report delivery, probe library expansion to 50+, self-serve billing.

## 5. Why we win (durable moat)

1. **Probe library as IP.** Domain-specific, calibrated, EU-protected-characteristic probes are the encoded knowledge. Competitors can copy the proxy in a weekend; they cannot copy a year of calibrated, regulation-mapped probes overnight.
2. **Compliance output as lock-in.** The customer's audit trail accumulates inside Verispect. Switching means losing historical evidence — painful right before an audit.
3. **Privacy architecture as trust wedge.** "We literally cannot see your data" closes security review faster than any competitor that ingests prompts.
4. **Regulatory tailwind.** The EU AI Act makes the buying trigger a legal deadline, not a nice-to-have.

## 6. Business model

Recurring SaaS subscription + usage. Free wedge → Pro self-serve → Enterprise sales-assisted. The PDF report is the value crystallisation; the middleware is the distribution mechanism. Detail in `03-pricing-billing/`.

## 7. Market (summary — full sizing in `04-market-sizing.md`)

LLM observability is a **$2–3.2B (2025) market growing 25–36% CAGR toward $9–24B by 2030–2034.** Verispect targets the **compliance-driven, high-risk slice** — smaller but higher willingness-to-pay and far less competitive than generic logging.

## 8. Go-to-market motion (summary — full in `05-gtm-motion.md`)

Founder-led outbound to a tight ICP in EU/SG/UAE, plus compliance-led content/SEO that ranks for "EU AI Act monitoring," plus a free drift-audit lead magnet. Land via a free bias snapshot report, expand to Pro, graduate the best logos to Enterprise.

## 9. 12-month objectives (illustrative, solo-founder realistic)

| Horizon | Goal |
|---|---|
| Month 0–3 | Ship multi-model + alerts + self-serve billing. 5 design-partner logos (free→Pro). Public launch. |
| Month 3–6 | 15 paying Pro accounts. First 1–2 Enterprise pilots. €3–5k MRR. |
| Month 6–12 | 40+ Pro, 3–5 Enterprise. €15–25k MRR. SOC 2 Type I in progress. First hire (DevRel or founding AE). |

## 10. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Omnibus delays AI Act → buyers relax | Lead with *enterprise procurement* demand + Singapore/UAE frameworks, not only EU deadline. Drift is a real engineering problem regardless of law. |
| Incumbents add a "drift" checkbox | Move fast on probe-library depth + compliance output; that's the hard, defensible part, not the feature label. |
| "Synthetic probes aren't real audits" objection | Position honestly as monitoring + evidence, never certification. Partner with law/audit firms for the certification layer. |
| Solo-founder bandwidth | Productise onboarding (self-serve), automate report generation, use design partners as references not custom builds. |
| Embedding-only scoring misses nuanced bias | Roadmap: add LLM-judge optional layer + statistical significance over many probe runs; document methodology limits transparently. |

## 11. Founder

Ajay — BSCS, FAST NUCES Karachi. Solo technical founder. Built the full stack: FastAPI proxy, privacy-preserving SDK, embedding drift engine, compliance PDF generator, React dashboard, auth. Distribution advantage: ships fast, speaks the buyer's technical language.

---
*Next: read `01-ideation-and-narrative.md` for the origin story used in fundraising and PR, then `02-icp-and-personas.md`.*
