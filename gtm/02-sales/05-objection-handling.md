# Objection Handling

*Acknowledge → reframe → prove → advance. Never argue. Every rebuttal stays honest.*

---

### "We already use Helicone / LangSmith / Langfuse."
> "Great — keep it. Those log what your model *said*. They can't tell you it started behaving *differently* today, and they don't produce bias-by-protected-characteristic evidence or an AI Act report. Verispect is the assurance layer on top — it coexists. You don't rip anything out."
*Proof:* show the comparison table; offer a snapshot alongside their existing tool.

### "We can build this ourselves."
> "You absolutely could build the proxy — it's a weekend. The part that isn't a weekend is a calibrated probe library across 8 protected characteristics, deterministic scoring, the privacy architecture, and a report an auditor actually accepts — kept current as the law and models change. And there's an independence problem: 'we graded our own homework' is a weak audit answer."
*Proof:* show the probe library + report; ask "who owns that build and ships it by your deadline?"

### "We're not in scope for the EU AI Act / the deadline got delayed."
> "Maybe — and the Digital Omnibus may push standalone Annex III to Dec 2027. But two things are already true: your enterprise buyers' procurement teams are asking AI-governance questions *now*, ahead of any law; and drift/bias is a real engineering risk regardless of regulation. The deadline is the calendar reason; the stalled deal is the business reason."
*Proof:* the procurement-questionnaire angle usually lands harder than the law.

### "We don't want to send our prompt data to a third party." (the big one)
> "Completely agree — so we designed it so you can't. We never receive prompts or responses. Only a SHA-256 hash and a 384-number embedding vector. Your golden probes stay encrypted on your own machine. We *reduce* your data-protection surface."
*Proof:* open the SDK source live; send the security overview + DPA.

### "Will this add latency to our API calls?"
> "No. Your call goes straight through and returns immediately. Every bit of our work — logging, embedding, probing — happens in a background thread/task after your user already has their answer. Zero added latency on the critical path."
*Proof:* show the async background code path.

### "How accurate is the bias/drift detection? Embeddings feel fuzzy."
> "Fair. We're honest about the method: deterministic cosine similarity on sentence embeddings, scored against a recorded baseline — same input, same score, reproducible. It detects *behavioural change relative to baseline*, and we document that limitation in every report. For stronger signal we run many probes over time and (roadmap) an optional LLM-judge layer. It's monitoring evidence, not a certified verdict — and we never pretend otherwise."
*Proof:* methodology section of the PDF; the reproducibility point.

### "This is just compliance theatre / does it actually make us compliant?"
> "It doesn't make you compliant — no tool can, and anyone who says so is lying. *You* remain the operator. What it does is produce the continuous-monitoring and bias evidence the Act asks for, mapped article-by-article, so a human can stand behind it. It's the evidence engine under your governance, not a rubber stamp."

### "Too expensive / no budget."
> "What's the cost of the deal currently stuck in security review? Pro is €99/mo — less than an hour of an ML engineer's time, and it replaces a multi-month internal build. Start free, prove value on your real traffic, upgrade only if it earns it."
*Proof:* free tier; ROI framed against the stalled deal, not against a logging tool's price.

### "Now isn't the right time."
> "Understood. The free snapshot takes 5 minutes and one line — run it now, see if your model is actually drifting, and decide later with data instead of a guess. If it's clean, great, you've got a report for your file. If it's not, you'll want to know before your buyer does."

### "We only use {Anthropic/Gemini/Mistral}, not OpenAI."
> "Multi-model is on the near-term roadmap; the architecture is provider-agnostic (OpenAI-compatible today). If you're a fit, you're exactly who I want as a design partner for {provider} — free Pro and you shape the integration." *(Be honest about current state.)*

### "Send me some info." (the brush-off)
> "Happy to — and so it's not generic, can I send the sample report plus a free snapshot of *your* model? Five minutes to set up. That way the info is about you, not us. Fair?"

---

## Objection patterns by persona
- **CTO:** latency, build-it-ourselves, accuracy → answer with code + reproducibility.
- **Head of AI:** scope/deadline, "theatre" → answer with article mapping + procurement reality.
- **DPO:** data privacy → answer with architecture + legal pack (usually flips to champion).
- **Founder/budget owner:** price → answer with stalled-deal ROI + free tier.

## Golden rule
If an objection is *true* (e.g. "you're OpenAI-only today"), agree, scope it honestly, and convert it into a design-partner opportunity. Honesty is the brand.
