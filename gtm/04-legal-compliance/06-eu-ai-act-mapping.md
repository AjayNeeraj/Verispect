# EU AI Act — Coverage Mapping

*The article-by-article story we tell buyers and auditors. Mirrors the mapping in the generated PDF report (`api.py`). Honest about what we cover vs. what remains the operator's duty.*

> Verispect supports compliance; it does not certify it. The deployer/provider remains responsible. This document explains where Verispect provides **evidence and monitoring** that helps meet each obligation.

---

## Regulatory context (state both, since the law is moving)
- The EU AI Act (Regulation 2024/1689) entered into force August 2024.
- **High-risk (Annex III) obligations are operative 2 August 2026** under the current text.
- A **Digital Omnibus** proposal may postpone standalone Annex III obligations to **2 December 2027** (and Annex I embedded AI to 2 August 2028) — **only if formally adopted and published**. Until then, treat 2 Aug 2026 as live.
- **Annex III, Section 4** classifies AI used in **employment, recruitment, worker management** as high-risk — Verispect's primary use case.

## Coverage table

| Article | Obligation (plain) | How Verispect helps | Status | Operator still must |
|---|---|---|---|---|
| **Art. 9 — Risk management** | Continuous risk management across lifecycle | Automated probe system + real-time drift flagging is a live monitoring control feeding the risk process | **Supports** | Maintain the formal risk-management system & documentation |
| **Art. 10 — Data & bias governance** | Assess data/representativeness; examine for bias on protected characteristics | 20-probe library across 8 EU-relevant protected characteristics; per-category bias evidence | **Supports** | Govern training/fine-tune data; act on findings |
| **Art. 11 / Annex IV — Technical documentation** | Maintain technical documentation | Reports retained as technical-documentation evidence; methodology documented | **Supports** | Compile full technical file |
| **Art. 12 — Record-keeping/logging** | Automatic logging of events | Timestamped audit log of calls, probes, drift scores, severities | **Supports** | Ensure logging meets retention/scope |
| **Art. 13 — Transparency & info to deployers** | Enable interpretation of output | Clear, exportable drift/bias evidence and methodology | **Supports** | Provide user-facing transparency/instructions |
| **Art. 14 — Human oversight** | Enable humans to oversee/intervene | Flagged events + dashboard + reports support human review workflows | **Partial** | Implement the human-in-the-loop decision process |
| **Art. 15 — Accuracy, robustness** | Appropriate accuracy & consistency | Consistency probes + drift tracking surface degradation | **Supports** | Engineer accuracy/robustness measures |
| **Art. 17 — Quality management** | QMS for high-risk AI | Monitoring evidence feeds the QMS | **Supports** | Operate the QMS |
| **Art. 26 — Deployer obligations** | Monitor operation, keep logs, inform | Continuous monitoring + logs + alerts | **Supports** | Assign oversight, inform affected persons |
| **Art. 72 — Post-market monitoring** | Proportionate post-market monitoring system | Core strength: continuous behavioural probing + golden-probe replay + drift timeline | **Strongly supports** | Maintain the PMM plan/system |
| **Annex III §4 — High-risk class** | Employment/recruitment AI = high-risk | Purpose-built; all probe categories target this | **Addressed** | Confirm classification with counsel |

## GDPR intersection (employment AI)
- **Art. 22 — automated decisions:** employment screening can trigger Art. 22; Verispect's bias evidence supports the fairness/oversight story but does not provide the legal basis or human-review process.
- **Art. 24/25 — accountability & data protection by design:** Verispect's privacy-by-architecture (hashes/vectors only) is itself a data-minimisation measure.
- **Art. 35 — DPIA:** Verispect provides a DPIA template (`05-dpia-template.md`) and monitoring evidence to support it.

## How to use this with a buyer/auditor
1. Lead with **Art. 72 + Art. 10** — our strongest, clearest coverage.
2. Be explicit about **"Supports" vs "Operator must"** — honesty builds the trust that closes regulated deals.
3. Hand over the **sample PDF** (renders this mapping with the customer's real data) + this doc + the DPA.

## Honesty guardrails (do not cross)
- Never claim Verispect makes a system "compliant," "certified," or "approved."
- Never claim to replace a conformity assessment (Art. 43) or Notified Body audit.
- Always attribute residual responsibility to the operator.
- Cite the **primary** source (artificialintelligenceact.eu / EUR-Lex / EU AI Act Service Desk) in customer-facing legal material.
