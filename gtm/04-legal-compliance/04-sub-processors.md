# Sub-Processors

**Last updated:** [DATE] · Published at verispectai.com/subprocessors

Verispect engages the following sub-processors to deliver the service. Each is bound by data-protection terms equivalent to our DPA. We notify customers of material changes ([14] days' notice; objection rights per DPA §6).

> Complete this table with your *actual* vendors before publishing. Example/likely set below based on the current stack.

| Sub-processor | Purpose | Data processed | Location | Safeguard |
|---|---|---|---|---|
| Railway (or chosen cloud) | Application hosting / compute | Hashes, vectors, metadata, account data | [region] | DPA + SCCs if outside EEA |
| [Postgres provider / Railway PG] | Database | Same as above | [region] | DPA + SCCs |
| [Payment processor — Stripe / Paddle / Lemon Squeezy] | Billing & payments (merchant of record if Paddle/LS) | Billing identity, payment metadata (no card data held by us) | [region] | DPA + SCCs; PCI-DSS |
| [Transactional email — e.g. Postmark / Resend] | Service & lifecycle emails | Name, email | [region] | DPA + SCCs |
| [Analytics — e.g. Plausible (EU)] | Privacy-friendly website analytics | Aggregated/pseudonymous web data | EU | EU-hosted, no cross-site tracking |
| [Error monitoring — e.g. Sentry] | Application error tracking | Technical logs (scrub PII) | [region] | DPA + SCCs |
| [Support/CRM — e.g. email or HubSpot] | Customer support & sales | Business contact data | [region] | DPA + SCCs |

## Notes
- The architecture means most sub-processors only ever touch **hashes, vectors, and metadata** — not raw customer content. This narrows transfer risk significantly.
- Golden-probe source prompts are **never** sent to any sub-processor; they remain on the customer's own infrastructure.
- Prefer EU-hosted vendors where practical to minimise transfer complexity (e.g. EU region for hosting/DB, EU analytics).
- Keep this list current — it is both a legal artifact (DPA Annex III) and a trust signal in security reviews.

## Change log
| Date | Change | Notice given |
|---|---|---|
| [DATE] | Initial publication | n/a |
