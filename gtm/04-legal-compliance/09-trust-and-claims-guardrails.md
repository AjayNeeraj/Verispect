# Trust & Claims Guardrails (Internal)

*The rules for what Verispect may and may not say — in marketing, sales, decks, ads, and the product UI. Binding on the founder and any future hire/contractor. A compliance brand dies the day it overclaims.*

---

## The one rule
**We sell evidence and monitoring. We never sell legal outcomes.** If a claim implies we make a customer "compliant," "certified," "approved," "safe," or "bias-free," it is forbidden.

## Approved claims (true, defensible)
- "Active bias and drift detection for production LLMs."
- "Audit-ready compliance *evidence*, mapped to the EU AI Act."
- "Supports your EU AI Act post-market monitoring (Art. 72) and bias governance (Art. 10) obligations."
- "We never receive your raw prompts or responses — only hashes and vectors."
- "One line of code, zero added latency."
- "Detects behavioural change relative to a recorded baseline, using deterministic semantic scoring."
- "Reduces your data-protection surface."

## Forbidden claims (legally dangerous)
- ❌ "Makes you EU AI Act compliant" / "GDPR compliant for you."
- ❌ "Certified" / "regulator-approved" / "guaranteed."
- ❌ "Eliminates / removes / prevents bias."
- ❌ "Replaces your audit / conformity assessment / DPO."
- ❌ "100% accurate drift detection."
- ❌ Any benchmark vs. a competitor we haven't actually run and can't reproduce.
- ❌ Naming a specific provider's model as "biased" as a headline without showing the reproducible method and date (defamation/accuracy risk) — present as a reproducible finding, scoped and dated.

## How to phrase the hard ones
| Want to say | Say instead |
|---|---|
| "Get compliant" | "Get the evidence your compliance needs" |
| "We make you AI Act ready" | "We help you evidence AI Act obligations" |
| "Bias-free AI" | "Continuous bias monitoring" |
| "Certified report" | "Audit-ready report in regulator-recognised format" |
| "Catches all drift" | "Catches behavioural drift against your baseline" |

## Methodology honesty (always disclose)
- Scoring is cosine similarity on `all-MiniLM-L6-v2` embeddings vs a recorded baseline — reproducible, but a *measurement*, not a verdict.
- A "pass" means consistency with the baseline; it does **not** certify the baseline itself was unbiased.
- Detection is probabilistic over sampled traffic; we don't see 100% of calls by design (sampling = privacy + cost).

## Comparative/competitive claims
- Only compare on **structural, verifiable** differences (active probing, bias library, compliance output, privacy architecture).
- Never disparage; state facts. If citing competitor pricing/features, date it and link the source.

## Customer evidence
- Use logos/testimonials/case studies **only with written consent.**
- Never publish a customer's drift/bias findings without explicit permission (it's their regulatory exposure).

## Ad-specific (paid channels)
- Fear-based hooks must be *true* (e.g. "your model may have changed" — true; "your model is broken" — not).
- Landing claims must match ad claims (no bait-and-switch — also a policy violation on most ad platforms).

## When unsure
Default to the weaker, truer claim. Ask: "Could a regulator or a burned customer quote this back at me?" If yes, soften it. The brand is trust; protect it in every sentence.
