# Positioning & Messaging

*The words. Use these verbatim across web, sales, decks, and ads so the story is consistent.*

---

## Positioning statement (internal)

For **AI-native companies running LLMs in high-stakes, regulated decisions**, who **must prove their models aren't drifting or discriminating**, Verispect is **active AI assurance middleware** that **interrogates the model with calibrated probes and produces audit-ready EU AI Act evidence** — unlike **passive observability tools (Helicone, LangSmith, Braintrust) that only log what already happened.** Our difference is that we **actively test behaviour and never see your data.**

## Category

We are not "LLM observability." We deliberately name a new category:

> **AI Behavioural Assurance** — continuous, active verification that a production model still behaves as it should.

Observability watches. Assurance verifies. This reframes the comparison so we're not feature-vs-feature against logging incumbents.

## Tagline system

- **Master tagline:** *Verify + Inspect. Every model. Every call. Every month.*
- **Punchy:** *Your model changed. We're the only ones who noticed.*
- **Compliance angle:** *The audit-ready proof your AI behaves — in one line of code.*
- **Privacy angle:** *AI compliance monitoring that never sees your data.*
- **Fear angle (ads):* *Logging tells you what your AI said. Verispect tells you when it started lying.*

## The one-liner (use everywhere)

**Verispect actively probes your production LLM for bias and drift, and turns the result into the EU AI Act compliance evidence enterprises and regulators demand — integrated in one line, with zero access to your data.**

## Value pillars (the three things we always say)

### 1. Active, not passive
Everyone else logs. We *test*. Calibrated synthetic probes + golden replays of your own traffic catch behavioural change the moment it happens — including silent provider-side model updates.

### 2. Audit-ready by default
The output is the artifact a regulator or enterprise buyer accepts: a branded PDF mapped article-by-article to EU AI Act 9/10/13/14/72 + Annex III, with GDPR considerations, methodology, and remediation steps. Not a dashboard you have to translate — the document itself.

### 3. Privacy by architecture
We never receive raw prompts or responses. Only SHA-256 hashes and embedding vectors. Golden probes live encrypted on your machine. We *reduce* your data-protection surface instead of adding to it. This closes security review faster than any competitor.

## Proof points (back every claim)

| Claim | Proof |
|---|---|
| Zero added latency | Real call returns immediately; all probe/logging work is async background thread/task. Show the code. |
| We never see your data | SDK sends only `sha256(prompt)` + 384-float embedding. Golden probes in `~/.verispect/golden_probes.db` on the client. Show the wrapper source. |
| Real bias is detectable | First calibration run flagged explicit age mention for a 54-yr-old vs identical 26-yr-old. Reproducible. |
| Deterministic scoring | `all-MiniLM-L6-v2` cosine similarity, no LLM in scoring loop → same inputs, same score. |
| One-line integration | `wrap(OpenAI(...), verispect_key=...)` or change `base_url`. |
| Maps to the law | Report renders Articles 9/10/13/14/72 + Annex III §4 with coverage status. |

## Messaging hierarchy by funnel stage

- **Ad / cold open (pattern interrupt):** "Your hiring model passed a fairness test in January. Has anyone checked it since?"
- **Landing hero (clarity):** the one-liner above.
- **Demo / consideration (proof):** the three pillars + sample PDF + live drift detection.
- **Close (risk reversal):** free bias snapshot, no card; cancel anytime; DPA on request; we never see your data.

## Words we use / words we avoid

| Use | Avoid | Why |
|---|---|---|
| assurance, monitoring, evidence, detect, interrogate, probe | certify, guarantee compliant, make you safe, eliminate bias | Overclaiming compliance is legally dangerous and brand-suicidal |
| audit-ready, regulator-accepted format | "regulator-approved" | We're not approved by any regulator |
| reduces your data risk | "fully GDPR compliant for you" | Customer remains the controller |
| catches drift | "prevents drift" | We detect, we don't control the provider's model |

## Competitive one-liners (the dagger sentences)

- vs **Helicone:** "Helicone tells you what your model said. Verispect tells you when it started saying it differently."
- vs **LangSmith:** "LangSmith is for debugging your chains. Verispect is for proving your model to a regulator."
- vs **Braintrust:** "Braintrust evals run when you remember to run them. Verispect probes automatically, forever, in production."
- vs **build-it-yourself:** "You could build the proxy in a weekend. The calibrated probe library and the article-by-article report are the year you don't have."
- vs **doing nothing:** "Doing nothing is a choice you'll defend in front of an auditor."

## Elevator pitches by length

**10 words:** Active bias & drift detection for production AI, audit-ready, one line.

**30 words:** Verispect probes your live LLM for bias and drift and generates the EU AI Act compliance report enterprises demand. One line to integrate. We never see your raw data.

**60 words:** AI logging tools tell you what your model said. They can't tell you it started behaving differently today. Verispect actively interrogates your production model with calibrated bias and consistency probes, scores the drift mathematically, and produces an audit-ready PDF mapped to the EU AI Act. It integrates in one line and, by design, never receives your raw prompts or responses — only hashes and vectors.
