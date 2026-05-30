# DPIA Template — AI System Using Verispect

*A Data Protection Impact Assessment template customers can use for their LLM-based high-risk system. Doubles as a high-value lead magnet ("Free EU AI Act DPIA template"). Customer completes; Verispect monitoring evidence supports several sections.*

> Not legal advice. A DPIA is the controller's responsibility under GDPR Art. 35. This template helps structure it for an LLM decision system and shows where Verispect provides supporting evidence.

---

## 0. Document control
- System name: __________  · Owner/DPO: __________ · Date: __________ · Version: ____
- Reviewers: __________ · Next review: __________

## 1. Describe the processing
- **What the AI system does:** [e.g. ranks job candidates from CVs using an LLM]
- **Purpose & necessity:** [why AI; why necessary/proportionate]
- **Data flows:** [inputs → model → outputs → human decision]
- **LLM provider/model:** [e.g. OpenAI gpt-4o-mini]
- **Volume & frequency:** [e.g. 100k decisions/month]
- **Is it Annex III high-risk?** [yes/no + reasoning]

## 2. Necessity & proportionality
- Lawful basis (Art. 6): __________
- If special category data (Art. 9): basis __________
- Data minimisation measures: __________
- Note: *Verispect itself processes only hashes/vectors/metadata — it does not increase the personal-data footprint.*

## 3. Stakeholders & consultation
- Data subjects (e.g. candidates): __________
- DPO advice: __________
- Consultation undertaken: __________

## 4. Risks to individuals (assess each: likelihood × severity)
| Risk | Likelihood | Severity | Notes |
|---|---|---|---|
| Discriminatory/biased outcomes (protected characteristics) | | | *Verispect provides continuous bias evidence across 8 categories* |
| Model drift causing unfair/inconsistent decisions | | | *Verispect drift detection + alerts mitigate* |
| Lack of transparency / unexplained decisions | | | |
| Over-reliance on automated output (Art. 22) | | | |
| Inaccurate outputs | | | *Consistency probes surface degradation* |
| Data breach of inputs | | | *Verispect never receives raw inputs* |

## 5. Measures to address risks
| Risk | Measure | Residual risk | Owner |
|---|---|---|---|
| Bias | Continuous monitoring via Verispect + human review + prompt audit | | |
| Drift | Verispect drift alerts + re-baseline process | | |
| Transparency | Candidate notice + explanation process | | |
| Automated decision | Human-in-the-loop per Art. 22 | | |
| Accuracy | Eval suite + Verispect consistency probes | | |

## 6. Monitoring & review (Art. 72 link)
- Continuous monitoring tool: **Verispect** — describe cadence, who reviews alerts, escalation.
- Report retention: [tier] — recommended ≥10 years as AI-system technical documentation.
- Review trigger: model/prompt change, drift alert, periodic ([quarterly]).

## 7. Sign-off
- DPO opinion: __________
- Decision (proceed / proceed with measures / do not proceed): __________
- Approver & date: __________

---

### How Verispect supports this DPIA
| DPIA section | Verispect evidence |
|---|---|
| §4 Bias risk | Per-category bias probe results |
| §4 Drift/accuracy risk | Drift timeline + consistency probes |
| §5 Measures | Continuous monitoring control with audit log |
| §6 Monitoring & review | Automated post-market monitoring + monthly reports |
| Data minimisation | Verispect receives no raw content (hashes/vectors only) |

*Want this as a fillable PDF/Word file? It's offered free at verispectai.com/dpia — also a lead-capture asset.*
