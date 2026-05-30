# Verispect Privacy Policy

**Effective date:** [DATE] · **Last updated:** [DATE]

> Template — review by qualified counsel before publishing. `[BRACKETS]` = complete before use.

Verispect ("Verispect", "we", "us") operates verispectai.com and the Verispect AI behavioural-assurance service. This policy explains what personal data we process, why, and your rights under the GDPR (Regulation 2016/679) and other applicable laws. We are committed to processing the minimum data necessary.

**Data controller:** [LEGAL ENTITY NAME], [REGISTERED ADDRESS]. Contact: privacy@verispectai.com. [DPO/representative details if applicable.]

---

## 1. Summary (the honest version)
- For the **monitoring service**, we are designed *not* to receive your or your end-users' raw content. We receive only irreversible hashes, mathematical embedding vectors, and technical metadata.
- For **running our business** (your account, billing, support, marketing to you), we process your **business contact details** as a controller.
- We never sell personal data. We never use your data to train models for other customers.

## 2. Data we process

### 2.1 Account & billing data (we are controller)
- Identity/contact: name, work email, company name.
- Authentication: hashed password, session/JWT tokens, API key identifiers.
- Billing: handled by our payment processor; we store only a customer/subscription identifier and plan status (no card data).
- Usage/support: log-in events, support correspondence.

**Purpose:** provide and secure the service, bill you, support you, comply with law.
**Legal basis:** performance of contract (Art. 6(1)(b)); legitimate interests (Art. 6(1)(f)) for security/product improvement; legal obligation (Art. 6(1)(c)) for tax/accounting.

### 2.2 Monitoring data (we are processor on your behalf)
Transmitted by the Verispect SDK from your systems:
- SHA-256 hashes of prompts (irreversible).
- Response embedding vectors (384 floating-point numbers).
- Metadata: model name, token counts, latency, timestamps, probe results, drift scores.

We do **not** receive raw prompt text, raw response text, or your end-users' personal data in the standard flow. Golden-probe source prompts remain stored **on your infrastructure**, encrypted, and are not uploaded to us.

**Purpose:** detect model drift/bias and generate compliance reports for *you*.
**Legal basis / role:** processed under your instructions per the Data Processing Agreement; you are the controller.

### 2.3 Website data
- Cookies/analytics: [privacy-friendly analytics, e.g. Plausible — no cross-site tracking]. Cookie banner where required; non-essential cookies set only with consent.
- Marketing contacts: see §5.

## 3. How we use data
Provide, secure, and improve the service; authenticate users; bill; support; communicate service notices; (with basis) market our own similar services to business contacts; meet legal obligations.

We do **not** use your monitoring data to train models benefiting other customers. Embeddings are used solely to compute *your* drift scores.

## 4. Sharing & sub-processors
We share data only with vetted sub-processors (hosting, database, payments, email, analytics) under GDPR-compliant terms. Current list: see `04-sub-processors.md` / verispectai.com/subprocessors. We notify customers of material changes. We disclose to authorities only where legally required.

## 5. Marketing & outreach
We contact business prospects on a **legitimate-interest** basis only where role-relevant, always with a clear, immediate opt-out, and we honour opt-outs permanently. You can unsubscribe from any marketing email at any time. We do not use purchased consumer lists.

## 6. International transfers
Where data is transferred outside the EEA, we rely on adequacy decisions or EU Standard Contractual Clauses with supplementary measures. Sub-processor locations are listed in `04-sub-processors.md`.

## 7. Retention
- Account data: for the life of the account + [period] for legal/tax.
- Monitoring data: per your subscription tier (7 days / 90 days / 1 year / custom) and your instructions; deleted/returned on termination per the DPA.
- Marketing contacts: until opt-out or [period] of inactivity.

## 8. Security
Encryption in transit and at rest, access controls, least-privilege, secure development practices. Details: `07-security-overview.md`. Our architecture minimises sensitive data by design.

## 9. Your rights (GDPR)
Access, rectification, erasure, restriction, portability, objection, and the right not to be subject to solely automated decisions with legal/significant effect. To exercise: privacy@verispectai.com. You may complain to your supervisory authority. For monitoring data, direct requests to the relevant controller (your vendor/customer); we assist them per the DPA.

## 10. Children
The service is for businesses; not directed at children. We do not knowingly process children's data.

## 11. Changes
We update this policy as needed and post the new effective date; material changes notified to account holders.

## 12. Contact
privacy@verispectai.com · [LEGAL ENTITY, ADDRESS] · [supervisory authority details].
