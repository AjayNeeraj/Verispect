# Billing Mechanics

*How money actually moves. Built on Stripe. Designed for solo-founder operability and EU tax compliance.*

---

## Stack
- **Stripe Billing** — subscriptions, invoices, proration, tax, customer portal.
- **Stripe Checkout** — hosted, PCI-compliant payment page (we never touch card data).
- **Stripe Customer Portal** — self-serve upgrade/downgrade/cancel/invoice history (no support ticket needed).
- **Stripe Tax** — automatic EU VAT / reverse-charge / GST handling.
- We store only a `stripe_customer_id` + `stripe_subscription_id` + plan + status against each `client` in our DB. No card data ever.

## Plan model in Stripe
- One **Product** per tier (Free, Pro, Business, Enterprise).
- Each with a **monthly** and **annual** Price (annual = ~2 months free).
- Free = no Stripe subscription (just an app-level flag).
- Enterprise = custom invoice or negotiated Stripe subscription (manual).

## Metering & usage enforcement
Monitored API calls are the metered dimension. Approach: **soft caps with alerts, not hard cut-offs** (never break a customer's monitoring silently).

1. App counts monitored calls per `client_id` per billing period (from the `logs` table, `is_canary=0`).
2. At 80% / 100% of tier limit → in-app banner + email: "You're approaching your plan limit. Upgrade or you'll keep running but we'll prompt to upgrade."
3. Over limit → keep monitoring (never lose audit data), show persistent upgrade prompt; for sustained overage, prompt tier upgrade or metered overage (Business+). **Never silently drop probes** — losing audit evidence is the one thing we must never do to a compliance customer.
4. Optional Stripe **metered/usage-based** price component for overages on Business+ (report usage to Stripe via usage records).

## Signup → paid flow
1. Register (existing `/auth/register`) → Free plan, API key auto-issued.
2. Upgrade click → Stripe Checkout session (server creates session with `client_id` in metadata).
3. Stripe webhook `checkout.session.completed` → set plan = Pro/Business, store IDs, raise limits.
4. `invoice.paid` / `invoice.payment_failed` / `customer.subscription.updated|deleted` webhooks → keep plan + status in sync.
5. Downgrade/cancel via Customer Portal → webhook → adjust limits at period end (no mid-period punishment).

## Webhooks to implement (minimum)
- `checkout.session.completed` → activate plan.
- `invoice.paid` → extend access.
- `invoice.payment_failed` → dunning state, email, grace period.
- `customer.subscription.updated` → plan/seat changes.
- `customer.subscription.deleted` → downgrade to Free at period end (keep their data per retention tier).

## Dunning (failed payments)
Stripe Smart Retries + email sequence: T+0 "card failed, update here," T+3 reminder, T+7 final notice, T+10 downgrade to Free (data retained per Free retention; not deleted abruptly — they may be mid-audit). Honest, gentle, no service-cutoff shock.

## Invoicing & tax (EU-critical)
- **VAT:** Stripe Tax auto-calculates. B2B EU cross-border → reverse charge (collect + validate customer VAT ID via Stripe). Domestic → local VAT.
- **VAT ID validation:** require business VAT ID at checkout for EU B2B; Stripe validates against VIES.
- **Invoices:** Stripe issues compliant invoices automatically; customer portal has full history.
- **Currency:** price in EUR primary; offer USD for non-EU. Consider SGD/AED display for SG/UAE later.
- **Entity/registration:** founder must register a business entity + VAT as required by domicile and EU OSS thresholds before charging EU customers. (Action item — not optional.)

## Enterprise billing
- Custom order form / MSA → invoice (NET 30) or annual prepay.
- Stripe Invoicing for one-off/annual; or a manually-created subscription.
- PO support, custom payment terms, multi-year discount on request.

## Refunds & cancellation policy
- Cancel anytime, effective end of billing period (no lock-in).
- Pro-rated refund on annual within 14 days of purchase (consumer-fair, builds trust).
- Data retained per tier after downgrade; export available on request (no hostage data).

## Financial ops hygiene (solo founder)
- Reconcile Stripe payout vs bank monthly.
- Track MRR/ARR/churn from Stripe dashboard + the financial model.
- Keep VAT filings current (or use an EU merchant-of-record like Paddle/Lemon Squeezy if VAT admin becomes too heavy — trade higher fee for zero tax overhead; strongly consider for a solo founder).

## Build note
Existing code has auth + API keys + `plan` field on client. To go live on billing: add Stripe SDK, a `/billing/checkout` + `/billing/portal` endpoint, webhook handler, and a usage-counter against `logs`. ~1–2 days of work. Or start with **Lemon Squeezy / Paddle (merchant of record)** to offload all EU VAT — faster path for a solo founder, recommended for v1.
