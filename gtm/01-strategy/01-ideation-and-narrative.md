# Ideation & Founding Narrative

*The story behind Verispect — for PR, fundraising, About page, and podcast/founder interviews. Keep it true.*

---

## The origin (the version you tell on a podcast)

Every AI company ships an LLM into production behind a model name like `gpt-4o-mini` and treats it as a fixed dependency. It isn't. The provider can change what sits behind that name at any time, and your "stable" hiring filter or credit model can start behaving differently overnight — with no changelog, no alert, no diff.

The realisation that became Verispect: **the most dangerous bug in an AI product is the one where nothing in your code changed.** You can't catch it by reading logs, because the inputs and outputs still look normal. The only way to catch it is to ask the model the *same controlled question* over and over and watch the answer move.

So I built a small experiment — fire two identical candidate profiles at a model, one named "Sarah," one named "James," and measure the gap. On the very first calibration run, the model explicitly mentioned age as a factor for a 54-year-old candidate but not for an identical 26-year-old. That wasn't a hypothetical. That was a measurable bias signal, in a model thousands of companies use for hiring, found in an afternoon.

If one probe found that in an afternoon, what is running undetected in production hiring and lending systems across Europe right now? And who is going to have to answer for it when the EU AI Act's high-risk rules bite in 2026–2027?

That's Verispect: the instrument that asks the question continuously, and writes down the answer in a form a regulator accepts.

## The naming

**Veri**fy + In**spect** → Verispect. Verify that the model still behaves as recorded; inspect it actively rather than watching passively.

## The values (and why they constrain the product)

- **We refuse to see your data.** The privacy architecture (hashes + embeddings only, golden probes stored on the customer's own machine) wasn't a feature decision — it's a moral and strategic one. A compliance product that itself creates a data-protection liability is a contradiction. This constraint is the trust wedge.
- **We sell evidence, not absolution.** Verispect will never tell a customer they're "certified" or "safe." It tells them what their model is doing, mapped to the law, so a human can decide. Overclaiming compliance is the fastest way to destroy a compliance brand.
- **The probe library is a public good we happen to monetise.** Encoding what "fair" looks like across protected characteristics is genuinely useful work. We keep it honest and keep expanding it.

## The three sentences for press

1. *Verispect is the first tool that actively interrogates production AI models for bias and drift, instead of just logging what they already did.*
2. *It integrates in one line, never sees the customer's raw data, and outputs the audit-ready evidence the EU AI Act requires.*
3. *Built solo by a CS student who found measurable hiring bias in a mainstream model in an afternoon — and decided someone should be watching continuously.*

## Mission

To make continuous, privacy-preserving AI behaviour assurance the default for every high-stakes model in production — so that "we didn't know it changed" stops being an acceptable answer.

## Vision (5-year)

Verispect becomes the standard layer between regulated companies and their AI providers: the independent instrument of record for model behaviour. When a board, an auditor, or a regulator asks "how do you know your AI is behaving?", the answer is "we run Verispect."
