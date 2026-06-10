# Demo Script — Word for Word

*Say exactly this. Practice twice out loud before recording. Total ≈ 3:00. Screen actions in [brackets]. Tone: calm, technical, certain. You are showing facts, not selling.*

---

## 0:00–0:15 — THE HOOK
**[Screen: verispectai.com hero. Voice over.]**

> "On the second of August 2026, the EU AI Act starts requiring companies that use AI for hiring, credit, or insurance to *prove* their AI isn't discriminating. Most teams have a policy document. Almost none have actual proof. In the next three minutes, I'll show you what proof looks like."

*(Why: a date + a legal verb + a gap they recognize. "Prove" is the keyword of the demo. Repeat it.)*

## 0:15–0:55 — RISK CLASSIFIER (Module 1)
**[Screen: localhost:8000/docs. POST /api/risk/classify. Paste body. Execute.]**
```json
{"hiring": true, "uses_llm_decision": true, "eu_market": true}
```

> "Step one: do you even fall under the law? Six questions about your AI system. Does it screen candidates? Does it influence the decision? Do you operate in the EU?"

**[Response appears. Point at HIGH-RISK.]**

> "There's the answer: high-risk. Annex III, section four, employment. With every article that now applies to you, mapped automatically. That classification used to be a consultant engagement. It's now a form."

**[Flash the Risk Classification Record PDF: cover, then obligations table.]**

> "And it's documented, because Article 9 requires this on file."

*(Why: starts with THEIR situation, not your product. The instant HIGH-RISK verdict is the "oh, that's me" moment.)*

## 0:55–1:40 — THE CATCH (the emotional core)
**[Screen: localhost:8000 dashboard. Drift timeline. Click a flagged event.]**

> "Step two. The part nobody else does. Verispect doesn't just log your AI. It *interrogates* it, continuously. We send the model pairs of identical candidates. Same résumé. Same experience. One is 26 years old, one is 54."

**[Pause one beat. Point at the flagged event.]**

> "Here's what we caught: the model brought up *age* for the older candidate. Not for the younger one. Identical CVs. Nothing in this company's code changed. The provider updated the model behind the scenes, and behavior shifted."

> "Your logging tools can't see this, because the inputs and outputs still look normal. The only way to catch it is to keep asking the same controlled question and measure when the answer moves. That's what runs here, twenty-four seven, on a sample of live traffic."

*(Why: this is the fear made concrete. One specific, visual, true example beats any feature list. Slow down on "identical CVs.")*

## 1:40–2:25 — THE AUDIT PACK (the value)
**[Screen: /docs. POST /api/docs/dpia. Paste body. Execute. Open the PDF.]**
```json
{"company":"Acme HR GmbH","system_name":"CandidateRank AI","purpose":"automated candidate screening","model":"gpt-4o-mini"}
```

> "Step three: the paperwork. The Act wants a DPIA, technical documentation, risk logs, monitoring evidence. Consultants charge five to fifteen thousand euros for this document. Watch."

**[PDF opens. Scroll slowly: cover → risk table → live evidence section → Annex IV index.]**

> "One click. A full Data Protection Impact Assessment plus the Annex IV technical file, and look — it's filled with this company's *real* monitoring numbers. Five hundred calls. Eighty probes. Eleven flagged events, each one already in the risk log with a remediation owner. This document updates itself every month, automatically."

**[Flash the Monitoring Report PDF cover for two seconds.]**

> "Same for the full monitoring report. This is what you hand an auditor, or an enterprise customer's procurement team, when they ask: prove it."

*(Why: "watch" then silence while the PDF renders is the money shot. Let the document speak.)*

## 2:25–2:50 — INTEGRATION + PRIVACY (kill the two objections)
**[Screen: code editor with the one line, big font.]**
```python
client = wrap(OpenAI(api_key="..."), verispect_key="vs_live_...")
```

> "Setup? One line of code. Your API calls don't slow down, everything runs in the background. And here's the part your security team will like: we never see your data. Not your prompts, not your responses. Only cryptographic hashes and number vectors ever leave your machine. We can't leak what we never receive."

*(Why: the two killer objections in cold outreach are "effort" and "data risk." Twenty-five seconds, both dead.)*

## 2:50–3:00 — THE CLOSE
**[Screen: back to verispectai.com, Founding 20 section visible, spot counter on screen.]**

> "Verispect. Your AI compliance department, running on autopilot. We're taking twenty founding companies before the deadline, at a rate locked for life. The free snapshot takes five minutes, and you only join if it shows you something worth fixing. verispectai dot com."

**[End card: logo + verispectai.com + "Founding 20 — {N} spots left."]**

---

## Delivery rules
- **Pace:** slower than feels natural. Pause after "identical CVs" and after "watch."
- **Never say:** "compliant", "certified", "guaranteed". Always: "proof", "evidence", "audit-ready".
- **Energy curve:** calm (hook) → curious (classifier) → grave (the catch) → confident (audit pack) → warm (close).
- **If you flub a line:** keep rolling, re-record that section only, stitch later. Nobody ships one perfect take.
- **Length discipline:** if over 3:20 total, cut from section 2 (classifier), never from section 3 (the catch).

## The three sentences to memorize cold (use everywhere: calls, DMs, hallways)
1. "The EU AI Act makes you *prove* your AI isn't discriminating. We generate that proof automatically."
2. "We caught a mainstream model treating two identical CVs differently because of age. Yours could be doing it right now."
3. "One line of code, we never see your data, and the audit pack writes itself."
