# Unit Economics

*The numbers under the model. Conservative assumptions; update with real data. Costs are low because the architecture is light (no LLM in the scoring loop, embeddings are cheap, we never store raw data).*

---

## Cost to serve (per account/month) — estimates

| Cost item | Free | Pro | Business | Enterprise |
|---|---|---|---|---|
| Hosting/compute (Railway/cloud, shared) | ~€0.30 | ~€1.50 | ~€6 | ~€25 |
| DB / storage (hashes + vectors only — tiny) | ~€0.10 | ~€0.50 | ~€2 | ~€10 |
| Embedding compute (MiniLM, self-hosted) | ~€0.05 | ~€0.40 | ~€3 | ~€15 |
| Stripe/MoR fees (~3–5%) | €0 | ~€4 | ~€16 | ~€150 |
| Email/infra (transactional) | ~€0.05 | ~€0.20 | ~€0.50 | ~€2 |
| Support (founder time, allocated) | ~€0 | ~€3 | ~€15 | ~€300 |
| **Est. total COGS/mo** | **~€0.55** | **~€10** | **~€42** | **~€500** |
| **Price/mo** | €0 | €99 | €399 | ~€4,000 (avg) |
| **Gross margin** | n/a | **~90%** | **~89%** | **~88%** |

> Note: probe traffic uses the *customer's own* OpenAI key (SDK fires probes client-side), so we don't pay for probe LLM calls — a structural cost advantage. Our compute is embeddings + API, both cheap.

Margins ~88–90% — characteristic of a software-only, no-LLM-inference-cost SaaS. Healthy.

## SaaS metrics targets

| Metric | Target | Notes |
|---|---|---|
| Gross margin | 85%+ | architecture supports it |
| CAC (Pro, founder-led + content) | < €150 | mostly time; low cash cost |
| CAC (Enterprise) | < €2,000 | founder time + travel/events |
| LTV (Pro) | ~€1,800 | €99 × ~18 mo avg life × ~90% margin ≈ €1,600–1,900 |
| LTV:CAC (Pro) | > 10:1 | strong (content/founder-led is cash-cheap) |
| LTV (Enterprise) | ~€100k+ | €4k/mo × 24+ mo × 88% |
| CAC payback (Pro) | < 2 mo | €99 covers low CAC fast |
| CAC payback (Enterprise) | < 6 mo | |
| Logo churn (Pro) | < 4%/mo target | compliance stickiness + audit history lock-in |
| Net revenue retention | > 110% | expansion via Pro→Business→Enterprise |

## Why churn should be low
- The accumulating **audit history** is lost on cancellation — high switching cost right before any audit.
- **Monthly auto-report** = recurring felt value.
- **Compliance is not discretionary** for the ICP — it's a standing obligation, not a project that ends.
- Risk: churn spikes if a customer's *use case* sunsets or they get acquired — outside our control; mitigate with multi-use-case expansion.

## Contribution by tier (illustrative monthly)
- Pro: €99 − €10 = **€89 contribution** (90%).
- Business: €399 − €42 = **€357 contribution** (89%).
- Enterprise: €4,000 − €500 = **€3,500 contribution** (88%).

→ One Enterprise account ≈ 40 Pro accounts in contribution. But Pro/Business volume funds discovery, references, and word-of-mouth that source Enterprise. Need both.

## Break-even (solo founder)
Assume founder living/ops cost ~€3,000/mo (lean, student/early). Break-even ≈ **34 Pro** OR **9 Business** OR **~1 Enterprise** account. Realistically a blend: ~10 Pro + 3 Business + 1 Enterprise ≈ €5,900 MRR clears costs comfortably. Achievable within the 12-month plan.

## Sensitivity / watch-items
- If forced to use a managed embedding API instead of self-hosted MiniLM, embedding cost rises — keep MiniLM self-hosted to protect margin.
- MoR (Paddle/Lemon Squeezy) fee ~5% + % vs Stripe ~2.9% — worth it early to kill VAT admin; revisit at scale.
- Enterprise support time is the real cost — productise onboarding to keep it bounded.
