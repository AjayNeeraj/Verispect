"""
billing.py — Verispect billing (Stripe Checkout + webhooks).

Fast path for the 15-day sprint:
  - For the Founding 20 you can sell with ZERO code using Stripe Payment Links
    (create them in the Stripe dashboard for $15,000/yr and $1,500/mo, paste into the
    landing page PAY_LINK + the offer PDF). Take a verbal yes -> send the link.
  - This module adds proper in-app Checkout + webhooks for when you want
    self-serve upgrades from the dashboard.

Env vars required (set in Railway / .env):
  STRIPE_SECRET_KEY        = sk_live_... (or sk_test_...)
  STRIPE_WEBHOOK_SECRET    = whsec_...
  STRIPE_PRICE_PRO_MONTH   = price_...   ($1,500/mo — Founding rate, locked for life)
  STRIPE_PRICE_PRO_YEAR    = price_...   ($15,000/yr — Founding annual)
  BILLING_SUCCESS_URL      = https://verispectai.com/dashboard?upgraded=1
  BILLING_CANCEL_URL       = https://verispectai.com/founding

Install:  pip install stripe
Wire in main.py:  from billing import billing_router ; app.include_router(billing_router)

NOTE (solo-founder VAT): if EU VAT admin is a burden, use a Merchant-of-Record
(Paddle / Lemon Squeezy) instead of raw Stripe — they handle all EU VAT. The
endpoint shape below is the same idea; swap the SDK calls.
"""
import os
from fastapi import APIRouter, Request, HTTPException, Depends

billing_router = APIRouter(prefix="/api/billing")

# Lazy import so the app still boots without stripe installed during the sprint.
def _stripe():
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
    if not stripe.api_key:
        raise HTTPException(status_code=503, detail="Billing not configured (STRIPE_SECRET_KEY missing)")
    return stripe

PRICE_MAP = {
    "pro_month": "STRIPE_PRICE_PRO_MONTH",
    "pro_year":  "STRIPE_PRICE_PRO_YEAR",
}


@billing_router.post("/checkout")
async def create_checkout(request: Request):
    """
    Body: { "plan": "pro_year" | "pro_month", "client_id": "...", "email": "..." }
    Returns: { "url": "<stripe checkout url>" } — redirect the user there.
    """
    stripe = _stripe()
    body = await request.json()
    plan = body.get("plan", "pro_year")
    client_id = body.get("client_id", "")
    email = body.get("email", "")

    price_env = PRICE_MAP.get(plan)
    if not price_env:
        raise HTTPException(status_code=400, detail="Unknown plan")
    price_id = os.getenv(price_env, "")
    if not price_id:
        raise HTTPException(status_code=503, detail=f"Price not configured ({price_env})")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        customer_email=email or None,
        client_reference_id=client_id or None,
        allow_promotion_codes=True,
        automatic_tax={"enabled": True},          # Stripe Tax handles EU VAT
        tax_id_collection={"enabled": True},      # collect + validate VAT IDs (B2B)
        metadata={"client_id": client_id, "plan": plan, "cohort": "founding20"},
        success_url=os.getenv("BILLING_SUCCESS_URL", "https://verispectai.com/dashboard?upgraded=1"),
        cancel_url=os.getenv("BILLING_CANCEL_URL", "https://verispectai.com/founding"),
    )
    return {"url": session.url, "id": session.id}


@billing_router.post("/portal")
async def customer_portal(request: Request):
    """Body: { "stripe_customer_id": "cus_..." } -> { "url": ... } self-serve manage/cancel."""
    stripe = _stripe()
    body = await request.json()
    cust = body.get("stripe_customer_id", "")
    if not cust:
        raise HTTPException(status_code=400, detail="stripe_customer_id required")
    portal = stripe.billing_portal.Session.create(
        customer=cust,
        return_url=os.getenv("BILLING_SUCCESS_URL", "https://verispectai.com/dashboard"),
    )
    return {"url": portal.url}


@billing_router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Stripe events -> update the client's plan/status.
    Configure in Stripe dashboard: send checkout.session.completed, invoice.paid,
    invoice.payment_failed, customer.subscription.updated/deleted to /api/billing/webhook.
    """
    stripe = _stripe()
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook signature failed: {e}")

    etype = event["type"]
    obj = event["data"]["object"]

    # Map events -> plan changes. Persist via database helpers (see TODO).
    if etype == "checkout.session.completed":
        client_id = (obj.get("metadata") or {}).get("client_id") or obj.get("client_reference_id")
        plan = (obj.get("metadata") or {}).get("plan", "pro_year")
        customer = obj.get("customer")
        subscription = obj.get("subscription")
        await _set_plan(client_id, plan="pro", status="active",
                        stripe_customer_id=customer, stripe_subscription_id=subscription)
    elif etype == "invoice.paid":
        await _set_status_by_customer(obj.get("customer"), "active")
    elif etype == "invoice.payment_failed":
        await _set_status_by_customer(obj.get("customer"), "past_due")
    elif etype in ("customer.subscription.deleted",):
        await _set_status_by_customer(obj.get("customer"), "canceled")  # downgrade to free at period end
    # else: ignore

    return {"received": True}


# ── Persistence hooks ────────────────────────────────────────────────────────
# TODO: wire to database.py. The clients table already has a `plan` column.
# Add columns if missing: stripe_customer_id TEXT, stripe_subscription_id TEXT, status TEXT.
async def _set_plan(client_id, plan, status, stripe_customer_id=None, stripe_subscription_id=None):
    if not client_id:
        return
    try:
        from database import database, clients_table  # clients_table must exist in database.py
        import sqlalchemy
        vals = {"plan": plan}
        # Only set columns that exist; guard with try/except per project schema.
        await database.execute(
            sqlalchemy.update(clients_table).where(clients_table.c.id == client_id).values(**vals)
        )
    except Exception as e:
        print(f"[billing] _set_plan skipped ({e}) — wire clients_table in database.py")


async def _set_status_by_customer(stripe_customer_id, status):
    if not stripe_customer_id:
        return
    print(f"[billing] customer {stripe_customer_id} -> {status} (wire to clients_table to persist)")
