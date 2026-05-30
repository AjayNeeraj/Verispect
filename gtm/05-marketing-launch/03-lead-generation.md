# Lead Generation System

*Where leads come from, how they're captured, and how they move toward revenue. Three sources: outbound (sales folder), inbound (content), and magnets (here).*

---

## The lead-gen map

```
                ┌─────────────── OUTBOUND (sales/01,02,08) ───────────────┐
                │  cold email · LinkedIn · (warm) calls → reply → snapshot │
                └──────────────────────────────────────────────────────────┘
                                          │
  INBOUND (content/SEO) ──► site ──►  FREE SNAPSHOT  ──► email captured ──► NURTURE ──► DEMO ──► PAID
                                          ▲   (DPIA, checklist, quiz also capture here)
  MAGNETS (this file) ────────────────────┘
```

The **free snapshot** is the central conversion event — it both delivers value and qualifies (they have an LLM in prod + cared enough to integrate one line).

## Lead magnets (capture assets)

| Magnet | Audience | Capture | Follow-up |
|---|---|---|---|
| **Free Drift/Bias Snapshot** | engineers/CTO | email + (optional) account | nurture A → demo |
| **DPIA template** (Word/PDF) | compliance/DPO | email | nurture B (compliance) |
| **EU AI Act readiness checklist** | AI/compliance lead | email | nurture B |
| **"Is your AI high-risk?" quiz** | mixed | email + result | segmented nurture |
| **Sample compliance report** (download) | buyer/auditor | email | sales sequence B |
| **Methodology whitepaper** | technical/skeptic | email | nurture A |

## Capture mechanics
- Every blog post ends with a relevant magnet CTA + inline email capture.
- LinkedIn posts use "comment 'report'/'DPIA'" → DM the asset (native, high-converting).
- Site: sticky "Run free snapshot" CTA; exit-intent for the checklist; pricing page demo CTA.
- All captures are **consent-based** with clear purpose + easy unsubscribe (GDPR).

## Lead scoring (simple, solo-founder-runnable)
| Signal | Points |
|---|---|
| Ran a snapshot | +30 |
| Snapshot showed flagged drift | +15 (real pain) |
| ICP-fit firmographics | +20 |
| Downloaded DPIA/checklist (compliance intent) | +15 |
| Visited pricing | +10 |
| Title = CTO/Head of AI/DPO | +15 |
| Replied to outreach | +20 |
≥50 points → personal outreach / book demo. <50 → stay in nurture.

## List building (outbound source)
- LinkedIn Sales Navigator: title + industry (HR-tech/fintech/insurtech/legal-tech) + geo (EU/SG/UAE) + headcount.
- Crunchbase/Dealroom: recent EU AI raises (budget + board pressure signal).
- Accelerator batches (YC/EF/Antler/Techstars) with EU founders.
- GitHub orgs depending on `openai`/`anthropic` SDKs in target geos.
- Conference/event attendee lists (RAI/AI Act/HR-tech events).
- **All list-building respects GDPR legitimate-interest rules** (sales/00) — role-relevant business contacts only, documented basis, suppression honoured.

## CRM (keep it light)
A simple CRM (HubSpot free / Notion / Airtable) tracking: source, score, stage, last touch, next step+date, persona, snapshot result. One source of truth so no lead is dropped.

## Conversion targets (steady state)
- Snapshot → demo: 30–40%.
- Magnet (non-snapshot) → demo (via nurture): 5–10%.
- Demo → paid: 25% Pro / 10–15% Enterprise.
- Goal: enough top-of-funnel for ~8–12 qualified demos/month.

## The compounding loop
Content → magnet → snapshot → (some convert) → case study → more content/credibility → more inbound. Every customer win becomes fuel. Protect the loop by being honest and useful at every step.
