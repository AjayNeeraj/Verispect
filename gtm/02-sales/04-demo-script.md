# Demo Script

*20–25 minutes. Goal: one "oh, that's the thing" moment, then a clear next step. Best demo uses the prospect's own free-snapshot data — show *their* model drifting, not ours.*

---

## Pre-demo checklist
- [ ] Ran their free snapshot? (ideal — demo on their numbers)
- [ ] Know their use case + trigger from discovery
- [ ] Sample PDF ready to screen-share / send
- [ ] Demo account seeded with realistic drift data (`seed_demo.py`)
- [ ] Legal pack link ready if DPO/security in the room

## Structure (the arc)

### 0. Recap & frame (2 min)
> "From our chat: you're running {LLM use case}, the trigger is {audit/deal/deadline}, and today you have no way to know if the model's behaviour shifts. I'll show three things: (1) how we catch that, (2) the report it produces, (3) how it's literally one line and never sees your data. Stop me anytime."

### 1. The problem, made real (3 min)
- Show the paired-probe concept live: "Sarah Johnson" vs "James Johnson," identical except the name. Or age 26 vs 54.
- Run them. Show the model's two answers side by side. Highlight divergence.
- > "Same qualifications. Different output. No code of yours changed. This is what's invisible in a logging tool — and it's exactly what an auditor or your enterprise buyer asks about."

### 2. Continuous detection (5 min) — the core "aha"
- Open the dashboard. Walk the **drift timeline**: "Each point is a probe fired automatically on a sample of live traffic. This dip is the day behaviour shifted."
- Show **per-category bias breakdown** (gender, age, race, nationality, disability, parental, socioeconomic, consistency).
- Show a **flagged drift event** with its severity + score.
- > "You don't run this. It runs forever, on 2% of real traffic, and flags the moment something moves."

### 3. The artifact they pay for (5 min)
- Generate / open the **EU AI Act compliance PDF**. Scroll it on screen.
- Land on: cover compliance score → **EU AI Act article mapping (9/10/13/14/72 + Annex III)** → methodology → bias-by-category → drift-event log → remediation recommendations → legal declaration.
- > "This is the document. When procurement or a regulator asks 'prove your AI behaves,' you send this — generated automatically, mapped to the law, branded to you."

### 4. Integration + privacy (4 min) — disarm the blocker
- Show the one line: `client = wrap(OpenAI(...), verispect_key="vs_live_...")` (or `base_url`).
- Show the wrapper sends only `sha256(prompt)` + embedding vector. Open the source if they're technical.
- > "Zero added latency — your call returns immediately, all our work is background. And we never receive your prompts or responses. Your DPO usually likes that more than anything else."

### 5. Close to next step (3 min)
- > "Two ways forward: start a free Pro trial today on your real traffic, or set up a 2-week pilot with success criteria we agree now. Which fits how you decide?"
- Agree pilot success criteria explicitly (e.g. "Verispect surfaces ≥1 real drift/bias signal + produces a report your DPO accepts").
- Book the next meeting *in the room*. Send legal pack + sample PDF same day.

---

## Demo do's and don'ts
- **Do** narrate in their language (their use case, their regulator, their buyer).
- **Do** let silence sit after the "aha" — let them react.
- **Do** show real code; technical buyers trust what they can read.
- **Don't** feature-dump. Three things, well.
- **Don't** overclaim: it's "audit-ready evidence," never "makes you certified/compliant."
- **Don't** demo a broken thing live — if unsure, screen-record a backup.

## If a DPO/security person is in the room
Pivot weight to Section 4 + the legal pack. Their yes is often the gate. "We never see your data" + DPA + sub-processor list usually converts them to internal champion.

## Leave-behind (send within 1 hour)
- Sample EU AI Act PDF
- One-pager (`06-collateral`)
- Legal pack link (DPA, privacy, security overview)
- Their snapshot results (if run)
- Clear next step + calendar invite
