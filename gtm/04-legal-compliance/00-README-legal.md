# Legal & Compliance Pack

> **IMPORTANT — READ FIRST.** These documents are professionally-structured **templates** drafted to be accurate to Verispect's privacy-by-architecture design. They are **not legal advice** and must be reviewed by a qualified lawyer (EU data protection + AI Act) before publication or signature. Placeholders in `[BRACKETS]` must be completed (legal entity name, registered address, jurisdiction, DPO/contact, effective dates). Verispect is a *compliance* brand — our own paperwork must be impeccable.

## What's in here

| File | Purpose | Audience |
|---|---|---|
| `01-privacy-policy.md` | How we handle personal data | Public (website) |
| `02-terms-of-service.md` | Contract for using Verispect | Public (website) |
| `03-data-processing-agreement.md` | GDPR Art. 28 processor terms | Customers' DPO/legal |
| `04-sub-processors.md` | Third parties we use | Public + DPA annex |
| `05-dpia-template.md` | Helps customers do their DPIA | Customers (lead magnet) |
| `06-eu-ai-act-mapping.md` | Article-by-article coverage | Buyers, auditors |
| `07-security-overview.md` | Security posture | Security reviewers |
| `08-acceptable-use-policy.md` | What customers may/may not do | Public |
| `09-trust-and-claims-guardrails.md` | What we may/may not claim | Internal (sales/marketing) |

## The core legal posture (the thing that makes all of this easier)

**Verispect is architected to minimise its own data-protection footprint.** We receive only:
- SHA-256 hashes of prompts (irreversible identifiers), and
- mathematical embedding vectors (384 floats),
plus operational metadata (model name, token counts, latency, timestamps).

We do **not** receive raw prompts, raw responses, or end-user personal data in the normal product flow. Golden probes (replays of the customer's own traffic) are stored **on the customer's own machine**, encrypted, never uploaded.

This means: for the *monitoring data path*, Verispect is largely a processor of pseudonymous/technical data, which dramatically simplifies the DPA and the customer's DPIA. The personal data we *do* process is **account data** (customer's business contact details) — for which we are a controller.

> A lawyer must confirm whether SHA-256 hashes/embeddings constitute personal data in a given context (they can, if re-identification is feasible). We treat them cautiously as potentially personal and apply GDPR safeguards regardless — this is the conservative, brand-safe stance.

## Two controller/processor relationships (keep them straight)
1. **Account data** (name, email, company, billing) → Verispect is **controller** → governed by Privacy Policy.
2. **Monitoring data** (hashes, vectors, metadata about the customer's AI usage) → Verispect is **processor** acting on the customer's instructions → governed by the DPA.
