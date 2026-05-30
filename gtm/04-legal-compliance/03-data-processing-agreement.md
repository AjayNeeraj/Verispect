# Data Processing Agreement (DPA)

**Between** the Customer ("Controller") **and** [LEGAL ENTITY NAME] ("Verispect", "Processor").
**Effective:** upon acceptance of the Terms of Service or signature. **Version:** [x.x]

> GDPR Article 28 template. Review by qualified counsel before signature. This DPA reflects Verispect's privacy-by-architecture design, which materially limits the personal data processed.

---

## 1. Scope & roles
This DPA governs Verispect's processing of Personal Data on the Controller's behalf in connection with the monitoring service. Verispect acts as **Processor**; the Controller is the **Controller** (or processor acting for its own controller). For Verispect's account/billing/marketing processing, Verispect is an independent **Controller** governed by its Privacy Policy, not this DPA.

## 2. Definitions
"GDPR", "Personal Data", "Processing", "Data Subject", "Sub-processor", "Supervisory Authority" as defined in the GDPR. "Monitoring Data" means the data transmitted by the SDK: SHA-256 prompt hashes, response embedding vectors, and technical metadata.

## 3. Nature of processing (Annex I summary)
- **Subject matter:** behavioural-assurance monitoring and report generation.
- **Duration:** term of the subscription + retention period per tier.
- **Nature & purpose:** computing drift/bias scores from embeddings and hashes; storing results; generating reports.
- **Type of data:** SHA-256 hashes (irreversible), embedding vectors (mathematical), technical metadata. **Raw prompts/responses and end-user content are not transmitted to Verispect by design.**
- **Categories of data subjects:** indirectly, the Controller's end users insofar as embeddings derive from content about them. No direct identifiers are received.
- **Special category data:** not knowingly processed; the architecture is designed to avoid transmitting content.

## 4. Processor obligations (Art. 28(3))
Verispect shall:
(a) process Personal Data only on documented instructions from the Controller (including this DPA and use of the service);
(b) ensure persons authorised to process are bound by confidentiality;
(c) implement appropriate technical and organisational measures (Annex II / `07-security-overview.md`);
(d) respect conditions for engaging Sub-processors (§6);
(e) assist the Controller, insofar as possible, in responding to Data Subject requests;
(f) assist the Controller with security, breach notification, DPIAs, and prior consultation (Arts. 32–36), taking into account the nature of processing and the limited data held;
(g) at the Controller's choice, delete or return Personal Data at end of services and delete existing copies unless law requires retention;
(h) make available information necessary to demonstrate compliance and allow/contribute to audits (§8).

## 5. Controller obligations
The Controller warrants it has a lawful basis and all necessary rights for the processing instructed, and that its configuration/use of the SDK complies with applicable law. The Controller is responsible for the lawfulness of the underlying AI system and its decisions.

## 6. Sub-processors
The Controller provides general authorisation for Verispect to engage Sub-processors listed at verispectai.com/subprocessors (`04-sub-processors.md`). Verispect will: impose data-protection terms equivalent to this DPA on each Sub-processor; remain liable for their performance; give the Controller [14] days' notice of additions/changes and an opportunity to object on reasonable data-protection grounds.

## 7. International transfers
Where processing involves transfer outside the EEA, the parties rely on an adequacy decision or the EU Standard Contractual Clauses (Module 2: Controller-to-Processor), incorporated by reference, with supplementary measures as needed. Sub-processor locations are disclosed in `04-sub-processors.md`.

## 8. Audits
Verispect will provide, on request, documentation (security overview, certifications when available, this DPA) to demonstrate compliance. For deeper audits, the parties agree to a reasonable, confidential audit no more than [once per year] (or after a breach), with reasonable notice, not disrupting operations, at the Controller's cost. [SOC 2 report to satisfy most audit needs once available.]

## 9. Personal data breach
Verispect will notify the Controller without undue delay (and within [48] hours where feasible) after becoming aware of a Personal Data Breach affecting the Controller's data, with available details, and assist with the Controller's notification obligations (Arts. 33–34).

## 10. Deletion/return
On termination, Verispect deletes or returns Monitoring Data per the Controller's instruction within [30] days, except where retention is legally required. Given retention tiers, the Controller controls the standing retention period.

## 11. Liability
Liability under this DPA is subject to the limitations in the Terms of Service, to the extent permitted by law.

## 12. Annexes
- **Annex I:** Processing details (see §3).
- **Annex II:** Technical & organisational measures (`07-security-overview.md`).
- **Annex III:** Sub-processors (`04-sub-processors.md`).
- **Annex IV:** EU Standard Contractual Clauses (where applicable).

Signed for the Controller: ______________  Signed for Verispect: ______________
