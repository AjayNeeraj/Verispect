# Ideal Customer Profile & Buyer Personas

*Who we sell to, who we ignore, and the human on the other end of the email.*

---

## Tiered ICP

### Tier 1 — Best fit (spend 80% of outbound here)
**AI-native startups & scale-ups (15–200 employees, seed–Series B) deploying LLMs in an EU AI Act Annex III high-risk domain, with EU/EEA, Singapore, or UAE exposure.**

High-risk domains we target, in priority order:
1. **HR-tech / recruitment** — résumé screening, candidate ranking, interview scoring. (Our probe library is *already built* for this — fastest time-to-value.)
2. **Fintech / credit & lending** — creditworthiness, fraud-adjacent scoring, underwriting assistants.
3. **Insurtech** — claims triage, risk pricing assistance.
4. **Legal-tech** — document review, contract risk, eligibility decisions.
5. **Health-tech / triage** — symptom triage, prioritisation (sell carefully; medical = Annex I, longer cycle).

**Qualifying signals (the "why them, why now"):**
- Uses OpenAI/Anthropic/Gemini/Mistral in a *decision* (not just content generation).
- Sells to EU enterprises (so procurement security/compliance reviews already hurt them).
- Has hit, or fears, a procurement questionnaire asking about AI bias/monitoring.
- Public about "responsible AI" but has no monitoring infrastructure (hypocrisy gap = pain).
- Recently raised — has budget and a board asking about regulatory risk.

### Tier 2 — Good fit (opportunistic)
Mid-market enterprises with an internal AI/platform team building LLM features in regulated functions; AI consultancies/agencies who can resell or embed Verispect for their clients; MLOps/platform teams at companies 200–1000 employees.

### Tier 3 — Channel / future
Law firms & compliance consultancies (referral partners, not direct users); Big-4-style audit practices needing a monitoring tool to back their AI assurance engagements; GRC platforms (integration/OEM).

### Explicit anti-ICP (do NOT chase)
- Hobbyists / pre-product solo devs (no budget, no compliance pain).
- Pure content-generation use cases with no decision risk (marketing copy, chatbots for fun).
- US-only companies with zero EU/regulated exposure (the deadline lever doesn't apply — revisit when US state AI laws mature).
- Enterprises that want a fully on-prem, air-gapped build in month one (revisit post-SOC 2).

---

## Firmographic filter (for list building)

| Attribute | Target |
|---|---|
| Headcount | 15–200 (Tier 1), up to 1000 (Tier 2) |
| Funding stage | Pre-seed (design partner) → Series B |
| Geography | EU/EEA, Singapore, UAE; secondary UK, broader GCC |
| Tech signal | Hiring "ML/AI engineer," uses OpenAI/Anthropic, job posts mention "LLM in production" |
| Domain | Annex III high-risk (HR, credit, insurance, legal, health) |
| Trigger | Recent raise, new "Head of AI/Responsible AI/DPO" hire, public RAI commitment, SOC2/ISO in progress |

**Where to find them:** LinkedIn Sales Navigator (title + industry + geo filters), Crunchbase/Dealroom (recent EU AI raises), YC/Antler/Entrepreneur First/Techstars batches with EU founders, AI Act-focused LinkedIn communities, GitHub orgs depending on `openai`/`anthropic` SDKs, conference attendee lists (see marketing).

---

## Personas

### Persona A — "Maya," Technical Co-founder / CTO (PRIMARY, Tier 1)
- **Company:** 25-person Series A HR-tech in Berlin. Screens 100k+ candidates/month with an LLM.
- **Reports to:** the board / her co-founder CEO.
- **Goals:** ship fast, don't get sued, close enterprise deals stuck in security review.
- **Pains:** Enterprise prospects send 200-line security/AI questionnaires she can't answer for "bias monitoring." She knows the model could drift but has no time to build detection. The Aug 2026 deadline is a board agenda item.
- **What she believes:** "I could build this myself" (she could — in 3 months she doesn't have).
- **Trigger to buy:** a lost or stalled deal blamed on inability to show AI governance.
- **Winning message:** *"One line of code. We never see your data. You get the audit PDF your enterprise buyer is demanding — this week, not in Q4."*
- **How she evaluates:** reads the SDK code, checks latency claim, tests the free report. Sell to the engineer in her.

### Persona B — "Daniel," Head of AI / Responsible AI Lead (PRIMARY, Tier 1/2)
- **Company:** 120-person fintech, Series B, Amsterdam + Singapore.
- **Goals:** stand up an AI governance program that survives audit; be the person who "had it covered."
- **Pains:** owns AI Act readiness but has no continuous monitoring; risk register has a glaring "model drift — unmonitored" line; legal keeps asking for evidence.
- **Trigger:** internal audit / board risk review / a near-miss bias incident.
- **Winning message:** *"Continuous post-market monitoring (Art. 72) and bias governance (Art. 10) evidence, generated automatically, mapped article-by-article. Close the open item on your risk register."*
- **How he evaluates:** wants the sample PDF, the EU AI Act mapping, the DPA, the security overview. Sell trust + paper.

### Persona C — "Priya," DPO / Compliance / Legal Counsel (INFLUENCER / BLOCKER)
- **Goals:** no new data-protection liability; defensible documentation.
- **Pains:** every new SaaS vendor is a new sub-processor risk. AI bias is a GDPR Art. 22 + AI Act exposure she's accountable for.
- **Winning message:** *"Verispect is the rare vendor that reduces your data risk: we never receive PII — only hashes and vectors. Here's the DPA, sub-processor list, and DPIA template."*
- **Role in deal:** can kill a deal on data grounds; our privacy architecture turns her from blocker to champion. Always send her the legal pack early.

### Persona D — "Tom," Solo Technical Founder (design-partner / free-tier wedge)
- **Goals:** look credible to enterprise buyers despite tiny team.
- **Winning message:** *"Free tier. Ship the trust badge + a real compliance report without hiring a compliance person."*
- **Role:** early logos, references, product feedback, word-of-mouth in founder communities. Low revenue, high strategic value early.

---

## Jobs-to-be-done (what they're really hiring us for)

1. *"When an enterprise buyer asks me to prove my AI isn't biased, give me the document — fast."*
2. *"Tell me the moment my model's behaviour changes, before a customer or regulator does."*
3. *"Let me close the 'unmonitored AI' line on my risk register without a 3-month build."*
4. *"Make my responsible-AI claims true and provable, not just marketing."*

## Messaging map (persona → lead value)

| Persona | Lead with | Proof to send |
|---|---|---|
| Maya (CTO) | Speed + zero latency + one line | SDK snippet, latency note, free report |
| Daniel (Head of AI) | Article-by-article evidence, automated | Sample PDF, EU AI Act mapping doc |
| Priya (DPO) | We never see your data | DPA, sub-processor list, security overview |
| Tom (solo founder) | Free credibility | Free tier signup, trust badge |
