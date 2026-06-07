# Getting Paid from Pakistan — the plan

*Stripe is NOT available in Pakistan. But selling $1,500/mo B2B to EU/Gulf customers is fully doable. Ranked, sourced (2026). Don't over-optimize fees early — speed + legitimacy win.*

> Key truth: at **$1,500/mo B2B**, you do NOT need a slick self-serve checkout. You need to **invoice and receive USD/EUR**. That unblocks launch today; add a checkout later.

---

## DO THIS — 3 layers, in order

### Layer 1 — TODAY (zero wait, unblocks June 12 launch): Payoneer + invoice
- Open a **Payoneer** business account (Pakistan-supported; gives you USD/EUR receiving accounts).
- For each Founding customer: send a **payment request / invoice** → they pay by card or bank → you withdraw to your PK bank.
- Manual, but perfect for 10–20 high-ticket customers. No approval delay, no code. **Start now.**
- **Wise Business** = alternative for holding multi-currency, but Payoneer is more reliable for *receiving* into Pakistan.

### Layer 2 — PARALLEL (1–2 wk): Merchant of Record for a real checkout + EU VAT
A MoR sells on your behalf and **handles EU VAT automatically** — which matters because we sell compliance into the EU. Gives a checkout button + subscriptions.
- **Dodo Payments** — built for Pakistani/Indian SaaS founders. Pays out via **Payoneer + Wise + local PK bank**, reviews bank details in 1–2 days. **Best first MoR — PK-native payouts.** (Note: MoRs run strict risk/KYC; keep your product + site legit.)
- **Paddle** — gold standard for SaaS; pays out worldwide except sanctioned countries (Pakistan OK). Stricter approval, wants a live product + site. ~5% + 50¢. Apply in parallel.
- **Lemon Squeezy / Polar** — LS payout leans on PayPal (dead in Pakistan) → weaker fit. Polar is newer.
- Wire the chosen MoR's checkout link into the landing page `PAY_LINK`.

### Layer 3 — SCALE (2–3 wk): US LLC + Mercury + Stripe (max legitimacy)
The durable foundation. A **US company** also makes you look far more serious to EU enterprise buyers at $1,500/mo.
- Form a **Wyoming/Delaware LLC** via **doola** ($297/yr Starter + state fee) or **Stripe Atlas** → get **EIN** → open **Mercury** (no US address needed for the holder) → activate **full Stripe**.
- First-year cost ~$300–800. Then `billing.py` (already written) works as-is with real Stripe keys.

---

## Recommended sequence
1. **This week:** Payoneer → invoice the first Founding customers. Launch is unblocked.
2. **Parallel:** apply to **Dodo Payments** (PK-friendly MoR) for a checkout + automatic EU VAT.
3. **Next 2–3 wk:** **doola → US LLC → Mercury → Stripe** as the long-term base.

## Fees (rough, 2026)
- MoR (Dodo/Paddle): ~5% (they handle VAT + global cards + payout).
- Stripe via US LLC: ~2.9% + 30¢ (you handle VAT — but US LLC selling to EU B2B often reverse-charge).
- Payoneer: ~1–3% + withdrawal fee.
→ At $1,500/mo the fee gap is small. Optimize for **fast + legit**, not lowest fee.

## What to change in the assets
- `billing.py` (Stripe) = keep — it's the Layer-3 path once the US LLC + Stripe exist.
- Landing `PAY_LINK` = point at the **MoR checkout** (Layer 2) when live; until then the "Claim" button routes to the snapshot/contact so you can **invoice via Payoneer** (Layer 1).
- Never block a hot lead on infra: take the verbal yes → send a Payoneer invoice → onboard.

## Sources (verify before acting — fast-moving)
- Stripe gap / PK alternatives: xpezia.com.pk, doola.com, dodopayments.com (sell-software-from-pakistan)
- MoR payout countries: paddle.com (worldwide ex-sanctioned), lemonsqueezy docs, dodopayments.com
- US LLC route: doola.com/pricing ($297 Starter), Stripe Atlas, Mercury (non-resident accounts)
