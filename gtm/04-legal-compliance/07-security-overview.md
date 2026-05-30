# Security Overview

*The document you hand a prospect's security team. Designed to pass review fast by leading with the architectural truth: we don't hold the sensitive data.* Serves as DPA Annex II (technical & organisational measures).

> Keep this honest and current. Mark roadmap items clearly as "planned," not "done." A compliance brand must never overstate its own security posture.

---

## 1. Security model in one line
Verispect's biggest security control is **architectural**: we are designed never to receive raw prompts, raw responses, or end-user content — only SHA-256 hashes and mathematical embedding vectors. The most sensitive data never reaches us, so it cannot be breached at us.

## 2. Data handling
- **What we receive:** SHA-256 prompt hashes (irreversible), 384-dim response embeddings, model name, token counts, latency, timestamps, probe/drift results.
- **What we never receive:** raw prompt text, raw response text, end-user PII, API keys for the customer's LLM provider (those stay client-side; the SDK fires probes using the customer's own key locally).
- **Golden probes:** stored encrypted on the **customer's** machine (`~/.verispect/golden_probes.db`); never uploaded.
- **Data minimisation:** we store the minimum needed to compute drift and produce reports.

## 3. Encryption
- **In transit:** TLS 1.2+ for all API and dashboard traffic; HTTPS enforced.
- **At rest:** database encryption at rest via the hosting provider; secrets stored in environment/secret management, never in code or the repo.

## 4. Access control
- Multi-tenant isolation by `client_id`; dashboard data scoped per authenticated account.
- Authentication: hashed passwords (bcrypt/argon2 — confirm), JWT session tokens, scoped API keys (`vs_live_*`) validated against the database; keys shown once, revocable; max active keys per account.
- Least-privilege internal access; production access limited to the founder [and future staff under policy].

## 5. Application security
- Input validation on API endpoints; parameterised queries (SQLAlchemy) — no string-built SQL.
- Probe execution wrapped in try/except — monitoring never disrupts customer traffic.
- CORS restricted to known origins.
- Dependency hygiene: [pin versions, monitor advisories — e.g. Dependabot].

## 6. Infrastructure
- Hosting: [Railway / cloud], [EU region preferred].
- Backups: [frequency, retention] of the metadata/results database.
- Monitoring/logging: application logs with PII scrubbing; error tracking [Sentry] configured to avoid capturing sensitive data.

## 7. Organisational measures
- Confidentiality obligations for anyone with access.
- Secure development practices; code review before deploy.
- Incident response process (§9).
- Vendor management: sub-processors under DPAs (`04-sub-processors.md`).

## 8. Privacy by design
- Architecture chosen specifically to avoid processing personal content.
- Customer-controlled retention (tiered).
- Data deletion/return on termination.

## 9. Incident response
- Detection → triage → contain → notify. Customer notification of any breach affecting their data without undue delay (target [48h]) per DPA §9.
- Post-incident review and remediation.

## 10. Compliance & certifications
- GDPR: DPA available; privacy-by-architecture posture.
- **SOC 2 Type I/II: planned** — [target date]. Enterprise tier includes the report when available.
- Penetration test: [planned/last date].

## 11. Roadmap (clearly marked planned)
- [ ] SOC 2 Type I → II
- [ ] SSO/SAML for Enterprise
- [ ] Independent penetration test
- [ ] Audit logging export to customer SIEM
- [ ] Region pinning options

## 12. Contact
security@verispectai.com · responsible disclosure: we welcome reports and will not pursue good-faith researchers. [Policy link.]

---
*Security questionnaire shortcut: most buyer questionnaires are answered by §2 — "you don't receive our prompts or responses?" Correct. That single fact resolves the majority of concerns.*
