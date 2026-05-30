# Discovery Questions

*Run before any demo. Goal: surface the real pain, the trigger event, and who signs. Talk 30%, listen 70%. Use their answers to tailor the demo.*

---

## Opening frame (set context, 20 sec)
> "Before I show anything — I'd rather understand your situation so this is useful and not a generic demo. Mind if I ask a few questions about how you're using LLMs and where compliance/monitoring sits for you? Then I'll show only the relevant parts."

## 1. Situation — how they use AI
- Where are LLMs making or assisting *decisions* in your product today? (hiring? credit? triage?)
- Which providers/models? Single model or several?
- Roughly what call volume? Streaming or standard?
- Who owns the AI/ML system internally?

## 2. Pain — the gap
- How do you currently know if the model's behaviour changes over time? *(listen for "we don't")*
- Have you ever been surprised by a model update or a behaviour shift in prod?
- How would you find out today if it started treating some candidates/applicants differently?
- Have you had to answer a customer/procurement questionnaire about AI bias or governance? How did that go?

## 3. Trigger — why now
- What's driving you to look at this *now* vs six months ago? *(the most important question)*
- Any upcoming audit, certification (SOC2/ISO), enterprise deal, or board/risk review touching AI?
- How are you thinking about the EU AI Act timeline for your high-risk use case?
- Is "model monitoring / bias" an open item on a risk register or roadmap?

## 4. Impact — quantify
- If a model-drift or bias incident hit a live decision, what's the cost — legal, customer trust, a stalled deal?
- Is a deal currently stuck because you can't show AI governance evidence?
- What does *not* solving this cost you over the next two quarters?

## 5. Current alternatives
- Are you using Helicone / LangSmith / Braintrust / anything today? For what exactly?
- Considered building monitoring in-house? What's the realistic timeline/owner for that?
- What would "good enough" look like to close this gap?

## 6. Process — how a decision happens (Enterprise)
- If this is valuable, what's the path to trying it? Who else needs to be involved?
- Does anything go through security review / DPO / legal? *(→ send legal pack early)*
- What's your budget reality for a tool like this — order of magnitude?
- Any timeline you're working back from?

## 7. Privacy/security pre-empt (turn blocker to champion)
- How sensitive is the prompt data? *(then:)* "Good — relevant because we never receive it. Only hashes and vectors. Does that change who needs to approve us?"

---

## Qualify in / out fast
**Strong fit signals:** LLM in a real decision; EU/SG/UAE exposure; a concrete trigger (deal/audit/deadline); named owner; "we don't monitor this today."

**Disqualify / nurture:** no decision use case; no regulatory or procurement exposure; "just exploring," no trigger, no owner, no timeline → put on content nurture, don't burn demo time.

## End-of-discovery transition
> "That's really helpful. Based on {their trigger + pain}, the parts worth showing you are {X and Y}. Want me to run a free snapshot against your actual model first so the demo uses your real numbers — or walk the live demo now?"

## Capture (into CRM / notes)
Pain · Trigger · Impact (€) · Owner/signer · Process/blockers · Privacy stance · Timeline · Competitor incumbent · Next step + date.
