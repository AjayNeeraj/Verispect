# Verispect — Go-To-Market Operating System

> **Verify + Inspect. Every model. Every call. Every month.**
> Active AI model drift & bias detection + EU AI Act compliance evidence, as one-line middleware.

This folder is the complete commercial operating system for Verispect — everything needed to take the product to market ethically, legally, and at speed. It is the business counterpart to the codebase in the repository root.

Owner: **Ajay** (solo founder). Last structured: 2026-05-30.

---

## How this folder is organised

| # | Folder | What's inside | Primary use |
|---|--------|---------------|-------------|
| 01 | `01-strategy/` | Business plan, vision, ICP & personas, positioning, competitive analysis, market sizing, GTM motion | Decide *who* we sell to and *why we win* |
| 02 | `02-sales/` | Cold email sequences, call scripts, LinkedIn, discovery, demo script, objection handling, follow-up cadences | Run outbound + close deals |
| 03 | `03-pricing-billing/` | Pricing tiers + rationale, billing mechanics (Stripe), unit economics, financial model | Charge money correctly |
| 04 | `04-legal-compliance/` | Privacy Policy, Terms, DPA, sub-processors, DPIA template, EU AI Act mapping, security overview, AUP | Stay legal & sell trust |
| 05 | `05-marketing-launch/` | Content/SEO plan, launch sequence (Product Hunt etc.), lead-gen funnels, web copy, nurture emails | Generate demand & leads |
| 06 | `06-collateral/` | One-pager, pitch deck, sales one-sheet, demo data scripts | Hand something to a buyer/investor |

Polished binary artifacts (PDF / PPTX / XLSX) are generated into `06-collateral/` and `03-pricing-billing/`.

---

## The 30-second pitch

LLM behaviour silently changes. Providers ship model updates, fine-tunes degrade, prompts drift — and a hiring or credit model that was fair last month quietly starts discriminating. Existing tools (Helicone, LangSmith, Braintrust) **log what already happened**. They cannot tell you the model's behaviour *shifted today*.

Verispect **actively interrogates** the model with calibrated synthetic probes on a sample of live traffic, scores behavioural drift mathematically, and produces the **audit-ready PDF an EU AI Act regulator or enterprise buyer will ask for.** One line of code to integrate. Raw prompt text never leaves the customer's machine.

## Who buys

AI-native startups and scale-ups deploying LLMs in **high-risk domains** under EU AI Act Annex III — hiring/recruitment, credit scoring, medical triage, legal review, insurance — primarily in the **EU, Singapore, and UAE**. The buyer is whoever owns "we cannot fail an audit": a technical founder/CTO at seed–Series B, or a Head of AI / DPO / Compliance lead at a scale-up.

## Why now

The EU AI Act high-risk obligations land **2 August 2026** (a Digital Omnibus proposal may move standalone Annex III to **2 December 2027** — not yet law). Either way, continuous post-market monitoring (Art. 72), logging (Art. 13), and bias governance (Art. 10) become non-optional. Verispect is the cheapest, fastest path to that evidence.

---

## Operating principles (non-negotiable)

1. **Privacy by architecture.** We never receive raw prompts or responses — only SHA-256 hashes and embedding vectors. Every sales and marketing claim must remain true to this. Never promise a capability that would require ingesting customer PII.
2. **Compliance honesty.** We provide *compliance evidence and monitoring*, not legal certification. Never imply Verispect makes a customer "certified" or replaces a Notified Body audit. The product is decision-support; the customer remains the legal operator.
3. **No dark patterns.** Transparent pricing, easy cancellation, honest benchmarks, opt-in marketing, GDPR-clean outreach.
4. **Evidence over hype.** Every drift/bias claim is backed by a reproducible cosine-similarity score against a recorded baseline.

See `01-strategy/00-vision-and-business-plan.md` to start.
