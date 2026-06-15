# Path to €15k MRR — the operating model

*Owned plan. €15k MRR ≈ 11 customers at $1,500, or a blended ladder that gets there with more logos and faster proof.*

---

## The number, three ways
| Mix | MRR | Notes |
|---|---|---|
| 11 × Founding ($1,500) | €14.7k | fewest logos, hardest cold close, slowest |
| **6 Founding + 12 Starter (€490) + 1 Enterprise (€4k)** | **~€18k** | **recommended** — diversified, faster logos |
| 20 Founding (full cohort) | €27k | stretch; the cohort cap |

## The ladder (the one strategic change)
- **Starter — €490/mo** · 1 model, self-serve, the reports, no white-glove. The *easy yes* that creates logos + case studies.
- **Founding — $1,500/mo** (hero, locked-for-life → public $2,500) · everything + white-glove. The margin engine.
- **Enterprise — €4k+/mo** · multi-entity, SSO, SLA, custom probes.
- **Readiness Report — $2,900 one-time** · for "just need the document now" buyers; upsell to monitoring.

Starter doesn't cheapen the brand — it's a capability tier (1 model, self-serve). It exists to win logos fast, which makes the Founding sells believable.

## The funnel to get there (from the 86-company list)
86 real prospects loaded (33 Tier-A). To net ~15 customers:
- 86 → expand to ~200 with contacts (Hunter/Apollo enrichment).
- ~200 touches × ~12% reply (warm, surgical, real ICP) → ~24 conversations.
- ~24 → ~16 snapshots → ~12 demos → **~12–15 closes** across Starter+Founding.
The list quality (every row a real high-risk ICP with a why-now signal) is what makes 12% reply realistic instead of 3%.

## The 4 blockers and their fixes (status)
1. **Take money** → invoice generator built (`build_invoice.py`), Payoneer rail. *Fill your Payoneer details in the script.* ← only you.
2. **Pipeline** → 86 real prospects loaded + outreach generated. *Add contacts via Hunter key.* ← only you (the key).
3. **Proof** → demo recorded tomorrow + sample PDFs done. First 2 logos become the case study.
4. **Backend live** → deploy to Render post-demo (white-glove covers the gap meanwhile).

## Sequence (own it day by day)
- **Today/tonight:** record demo (script ready), fill Payoneer details in `build_invoice.py`, re-drag landing to Netlify.
- **June 12:** drop Hunter key → `python outreach/run.py --leads gtm/07-sprint/prospects-master.csv --enrich --send`. Wave one fires to Tier-A.
- **Daily:** morning outbound block, run snapshots, demos, close → invoice on the spot (`build_invoice.py --company ... --plan founding-monthly`).
- **Weekly gate:** if Founding closes are slow, lead Starter to bank logos + MRR, upsell later.

## What I can still do for you (say the word)
- Enrich the 86 → real emails (needs your Hunter/Apollo key in `.env`).
- Build the Starter tier into the landing + pricing (currently $1,500-only).
- Draft the Render deploy so the backend is live for real customers.
