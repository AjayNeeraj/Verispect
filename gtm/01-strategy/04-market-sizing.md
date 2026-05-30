# Market Sizing — TAM / SAM / SOM

*Defensible numbers with stated assumptions. Use the conservative column when talking to investors; show the method, not just the figure.*

---

## Market context (sourced 2026-05)

- **LLM observability platform market:** ~$1.97–3.2B in 2025, projected to ~$9.26B by 2030 (CAGR ~36%) and as high as ~$24.8B by 2034 (CAGR ~25%) depending on source.
- **Agentic AI monitoring/observability subset:** ~$0.55B (2025) → ~$2.05B (2030), CAGR ~30%.
- **Primary growth driver cited by analysts:** regulatory scrutiny (EU AI Act, NIST AI RMF) pushing regulated verticals toward tamper-proof logging and continuous assurance. This is *exactly* Verispect's slice — we are positioned on the fastest-growing demand vector, not generic logging.

Sources: Mordor Intelligence (agentic observability), Dataintelo / ResearchAndMarkets (LLM observability), The Business Research Company. See `99-sources.md`.

## Method: top-down + bottom-up, then reconcile

### TAM (Total Addressable Market) — top-down
All organisations running LLMs in production that will need behavioural assurance/compliance monitoring.
- Anchor to the LLM observability market and take the **compliance/assurance-driven share**.
- Assumption: ~25–35% of observability spend is or will be compliance/governance-driven (analyst attribution of regulation as the top driver supports this).
- **TAM ≈ 30% × ~$9B (2030) ≈ $2.7B** addressable behavioural-assurance/compliance-monitoring market by 2030. (2025 equivalent ≈ 30% × ~$2.5B ≈ $750M.)

### SAM (Serviceable Available Market) — the slice we can actually serve
Filter TAM to our reachable, high-fit segment:
- **Geography:** EU/EEA + Singapore + UAE (+ UK) ≈ ~30% of global AI software spend.
- **Segment:** high-risk Annex III domains (HR, credit, insurance, legal, health) + companies facing EU procurement = a minority but the willing-to-pay core.
- **SAM ≈ 12–18% of TAM ≈ $330–490M (2030); ~$110–150M today.**

### SOM (Serviceable Obtainable Market) — bottom-up, what we can win
Bottom-up by accounts × ACV:

| Segment | Reachable accounts (EU/SG/UAE, high-risk LLM) | Realistic capture (3 yr) | Avg ACV | SOM |
|---|---|---|---|---|
| Pro self-serve (startups/scale-ups) | ~8,000 | 1.5% → 120 | €1,200/yr | €144k |
| Enterprise (regulated scale-ups/mid-market) | ~1,500 | 1.5% → 22 | €36,000/yr | €792k |
| **Total 3-yr SOM** | | **~142 accounts** | | **≈ €0.94M ARR** |

A 3-year path to ~€1M ARR from a tiny fraction of a fast-growing, regulation-driven market. The market does not need to be huge for this to be a strong solo-founder / small-team business; it needs ~150 of the right accounts.

### Bottom-up sanity check (founder-led capacity)
- Founder-led outbound realistically books ~8–12 qualified demos/month at steady state.
- ~20–25% demo→paid on Pro, ~10–15% on Enterprise pilots.
- → ~2–3 new paying logos/month achievable solo once the motion is tuned → ~30/yr → consistent with the SOM table over 3 years including churn.

## Why the SAM grows under us (tailwind, not assumption)
- **2 Aug 2026** high-risk obligations operative (Digital Omnibus may shift standalone Annex III to **2 Dec 2027** — either way the obligation arrives, and earlier preparation is rewarded).
- Enterprise procurement is *already* asking AI-governance questions today, ahead of any deadline — demand precedes the law.
- Singapore (IMDA AI Verify / Model AI Governance Framework) and UAE (national AI strategy + emerging governance) create parallel non-EU pull.

## Beachhead → expansion sequence
1. **Beachhead:** EU + Singapore HR-tech using LLM screening (probe library already built → fastest value, clearest legal trigger).
2. **Adjacent:** fintech credit/lending (extend probe library to financial-fairness scenarios).
3. **Expand:** insurance, legal, then broader "any regulated LLM decision."
4. **Platform:** become the assurance layer GRC tools and audit firms integrate (channel/OEM).

## What would make this a much bigger company
- Multi-model + agent-trace assurance (ride the agentic observability 30% CAGR).
- Becoming the *de facto* evidence format auditors accept → standards-level lock-in.
- US expansion as state-level AI laws (Colorado, etc.) mature into a second regulatory engine.
