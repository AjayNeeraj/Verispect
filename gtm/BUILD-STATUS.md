# GTM Package — Build Status

*What exists, what's a template, what needs a human before going live. Generated 2026-05-30.*

## ✅ Complete (29 docs + 3 binaries)

**01-strategy/** — vision/business plan, ideation/narrative, ICP & personas, positioning & messaging, market sizing, competitive analysis, GTM motion, sources.
**02-sales/** — playbook overview, cold email sequences, LinkedIn, discovery, demo script, objection handling, qualification/deal mgmt, onboarding/expansion, cold-call scripts.
**03-pricing-billing/** — pricing strategy, billing mechanics, unit economics, + **Verispect-Financial-Model.xlsx** (24-mo live model).
**04-legal-compliance/** — README, privacy policy, ToS, DPA, sub-processors, DPIA template, EU AI Act mapping, security overview, AUP, claims guardrails.
**05-marketing-launch/** — marketing strategy, content/SEO, launch plan, lead gen, email nurture, website copy.
**06-collateral/** — collateral index, + **Verispect-One-Pager.pdf**, **Verispect-Pitch-Deck.pptx** (15 slides).

## ⚠️ Needs a human before go-live (non-negotiable)
1. **Legal review** of all `04-legal-compliance/` docs by a qualified EU data-protection + AI Act lawyer. These are accurate templates, not legal advice.
2. **Register the business entity + VAT**, fill every `[BRACKET]` placeholder (entity, address, jurisdiction, DPO contact, dates).
3. **Verify competitor pricing & EU AI Act dates** before publishing any customer-facing claim (law is moving — Digital Omnibus pending).
4. **Wire billing** (Stripe or — recommended for solo founder — a merchant-of-record like Paddle/Lemon Squeezy to offload EU VAT). See billing-mechanics.
5. **Get written consent** before using any customer logo/testimonial/finding.

## 🔭 Product gaps that GTM assumes (from CONTEXT.md roadmap)
- Multi-model native support (currently OpenAI-compatible).
- Slack/email drift alerts.
- Self-serve billing endpoints.
- Probe library expansion (toward 50+).
These are referenced honestly in sales/marketing (roadmap badges, design-partner framing) — keep claims matched to reality.

## How to regenerate binaries
```powershell
python gtm/03-pricing-billing/build_financial_model.py
python gtm/06-collateral/build_one_pager.py
python gtm/06-collateral/build_pitch_deck.py
```

## The throughline
Every document enforces the same three principles: **active assurance (not passive logging)**, **honest compliance claims (evidence, never certification)**, and **privacy by architecture (we never see raw data)**. That consistency is the brand. Protect it in every email, slide, and contract.
