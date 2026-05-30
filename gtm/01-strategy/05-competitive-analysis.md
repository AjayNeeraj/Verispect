# Competitive Analysis

*Honest, specific, and built for sales enablement. Know the real strengths of incumbents — don't strawman them.*

---

## The map

| | Logs traffic | Manual evals | **Active probing in prod** | Bias/protected-attr probes | **Compliance report output** | Never sees raw data |
|---|---|---|---|---|---|---|
| **Verispect** | ✅ (hashes) | — | ✅ | ✅ (8 categories) | ✅ (EU AI Act PDF) | ✅ |
| Helicone | ✅ | partial | ❌ | ❌ | ❌ | ❌ |
| LangSmith | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Braintrust | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Langfuse | ✅ | ✅ | ❌ | ❌ | ❌ | self-host option |
| Arize / Fiddler (ML monitoring) | ✅ | ✅ | partial | partial | partial | ❌ |
| Credo AI / Holistic AI (GRC) | ❌ | ❌ | ❌ | questionnaire-based | ✅ (governance) | ❌ |
| DIY in-house | ✅ | ✅ | possible | possible | manual | depends |

## Player-by-player

### Helicone
- **What it is:** popular, developer-loved LLM logging/observability proxy. Free to 10k req/mo (7-day retention); Pro ~$79/mo (30-day); Team ~$799/mo (SOC 2, HIPAA).
- **Real strengths:** dead-simple proxy integration, great DX, caching, cost tracking, large mindshare.
- **Where it stops:** passive only — no active probing, no bias testing, no drift-vs-baseline, no compliance artifact. Ingests prompts/responses (data-surface).
- **Our wedge:** "Keep Helicone for cost/logging if you like — Verispect adds the *assurance* layer they don't have, without sending us your data." We can coexist, not just compete.

### LangSmith
- **What it is:** LangChain's official observability + eval platform. Developer free (5k traces/mo); Plus ~$39/user/mo; Enterprise custom.
- **Strengths:** best-in-class for LangChain/LangGraph tracing and dataset-driven evals; strong with teams already in that ecosystem.
- **Where it stops:** debugging/eval tool for builders, not a continuous in-prod bias/drift assurance or compliance-evidence tool. Evals are manual/CI, not automatic production probing.
- **Our wedge:** "LangSmith helps you build it. Verispect proves it to a regulator — automatically, in production, forever."

### Braintrust
- **What it is:** eval-first platform; free AI proxy with logging, caching, retries.
- **Strengths:** strong eval framework, cost-effective proxy, growing adoption.
- **Where it stops:** evals run when *you* run them; no autonomous production probing, no protected-characteristic bias library, no EU AI Act output.
- **Our wedge:** "Evals you remember to run vs probes that never stop. Compliance can't depend on someone remembering."

### Langfuse
- **What it is:** open-source observability + evals, self-hostable.
- **Strengths:** OSS, self-host (data-control story), active community.
- **Where it stops:** same passive/eval category; no active bias probing or regulation-mapped reporting out of the box.
- **Our wedge:** privacy parity (we don't see data either) *plus* the active probing + report they lack. Against OSS, sell the calibrated probe library + done-for-you compliance output as the thing not worth self-building.

### Arize / Fiddler (ML observability + some bias)
- **Strengths:** mature ML monitoring, drift on features/embeddings, some fairness metrics; enterprise credibility.
- **Where it stops:** built for classic ML pipelines/feature drift; heavier, enterprise-priced, not LLM-prompt-native one-line integration, not packaged as EU AI Act evidence for LLM apps; ingests data.
- **Our wedge:** lightweight, LLM-native, one line, privacy-first, regulation-output-first, startup-priced.

### GRC / AI governance platforms (Credo AI, Holistic AI, etc.)
- **Strengths:** policy, governance workflows, risk registers, exec/legal buyer relationships.
- **Where it stops:** largely *questionnaire- and process-based* — they document that you *say* you monitor; they don't provide the live technical signal.
- **Our wedge / partnership:** we are the *technical evidence engine* under their governance layer. Strong **integration/partner** candidates, not pure competitors. "They hold the binder; we generate the page that proves the binder is true."

### DIY in-house
- **Reality:** any good team *can* build a proxy + a few probes.
- **Why they don't / shouldn't:** calibrated, regulation-mapped probe library across 8 protected characteristics; deterministic scoring; privacy architecture; and an auditor-credible report format = months of focused work + ongoing maintenance as the law and models change. Build-vs-buy math favours buy for everyone except the few with a dedicated RAI team — and even they value an *independent* instrument.
- **Our wedge:** "Independence matters. 'We graded our own homework' is not a good audit answer."

## Positioning takeaways for sellers
1. **Reframe the category.** Don't get dragged into "logging feature parity." We're *assurance*, they're *observability*. Different job.
2. **Coexistence is a sales tool, not a weakness.** "Keep your logger; add the assurance layer" lowers switching friction and disarms the incumbent-loyalty objection.
3. **Two moats they can't quickly copy:** the calibrated protected-characteristic probe library and the regulator-credible report. Lead demos with both.
4. **Privacy is the tie-breaker in security review.** When two vendors look similar to a DPO, "we never receive your data" wins.

## Win/loss watch-list (update as we sell)
- Track: which competitor was incumbent, why we won/lost, which objection decided it. Feed back into `02-sales/05-objection-handling.md`.
