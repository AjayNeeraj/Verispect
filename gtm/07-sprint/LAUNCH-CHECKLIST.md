# Launch Checklist — Demo June 11, Launch June 12

*Everything to exist + look legit before we shoot the demo and go cold. ✅ = built/ready in repo. 🔑 = needs you (accounts/login). One page. Tick down.*

---

## A. The product (the "department") — ✅ built
- ✅ **8 Fairness Auditors** + Drift Sentinel + Evidence Clerk (core monitoring, probes, scoring)
- ✅ **Module 1 — Risk Classifier** (`/api/risk/classify`, `/api/risk/questions`) → Annex III classification + Risk Classification Record PDF
- ✅ **Module 2 — Evidence Clerk / DPIA Generator** (`/api/docs/dpia`) → auto DPIA + Annex IV tech-doc, populated with live evidence
- ✅ **Compliance report** (`/api/report`) → branded AI Act audit pack
- ✅ One-line SDK · privacy-by-architecture (hashes + vectors only)
- ✅ Sample PDFs in `gtm/06-collateral/`: compliance report, risk classification, (DPIA sample on next push)

→ Roster is now genuinely a **monitoring + evidence department**, not a single tool. Claim matches capability.

## B. What the customer GETS, HOW, how EASY, the IMPACT (say this on every call)
| They get | How they get it | Effort | Impact |
|---|---|---|---|
| AI Act Risk Classification | 6-Q wizard in dashboard | 2 min | "Am I high-risk?" answered + documented (Art. 9) |
| Live bias & drift monitoring | one-line SDK connect | 5 min, once | catches discrimination/drift the moment it happens |
| Auto DPIA + tech-doc | one click (auto-filled) | 0 | the €5-15k consultant deliverable, instant |
| Monthly audit pack | emailed automatically | 0 | the document a regulator/buyer asks for |
| Real-time alerts | Slack/email | 0 | "your model started docking age — here's proof" |
| "Monitoring Active" trust badge | paste on their site | 2 min | sells THEIR trust to THEIR buyers |
**The line:** "Connect once. We deliver compliance to you. We never see your data."

## C. Demo to shoot (June 11) — 3-minute screen recording
1. **Hook (15s):** "EU AI Act hits Aug 2026. Most AI teams can't prove their model is fair. Watch this." 
2. **Risk Classifier (30s):** answer 6 questions → "HIGH-RISK, Annex III §4" + record PDF. "Step one, documented."
3. **The catch (45s):** show drift timeline + a flagged bias event ("age docked for identical CV"). "This is what logging tools miss."
4. **The audit pack (45s):** click → DPIA + compliance PDF, filled with live evidence. "The €15k consultant deliverable, in one click."
5. **Integration + privacy (30s):** the one line of code + "we only ever get hashes and vectors."
6. **Close (15s):** "Your autonomous AI compliance department. $1,500/mo. Founding 20 open → verispectai.com." 
*Record with seeded data (already in DB) so numbers look real. Tool: Loom / OBS.*

## D. Legitimacy pack (the "we exist + we're real" signals)
- ✅ **Logo** — `landing/assets/logo-mark.svg` + `logo-full.svg` (use as LinkedIn avatar, favicon, deck, badge). Favicon wired into landing.
- 🔑 **Domain live** — point verispectai.com at the landing (`landing/`) via Netlify/Vercel/your host.
- 🔑 **Custom domain email** — you have it → set as FROM_EMAIL.
- 🔑 **LinkedIn Company Page** — content below; create it, set logo as avatar.
- ✅ **Trust badge** ("Monitoring Active") — concept ready; render from logo for customers.
- ✅ **Real sample PDFs** to attach in outreach (collateral folder).

## E. The 6 buttons only you can press before June 11 (~half a day)
1. 🔑 Deploy `landing/` → public URL on verispectai.com (Netlify Drop = 15 min).
2. 🔑 Stripe Payment Links: $1,500/mo + $15,000/yr → paste into landing `PAY_LINK`.
3. 🔑 Lead capture: set `LEAD_ENDPOINT` (Formspree/Tally) in landing.
4. 🔑 `.env`: HUNTER_API_KEY + SMTP + FROM_EMAIL (your domain) → email autopilot live.
5. 🔑 Create LinkedIn Company Page (content below) + set logo.
6. 🔑 Record the 3-min demo (section C) → host on the landing + LinkedIn.

## F. Launch (June 12) — fire the machine
- Email: `python outreach/run.py --enrich --send` (autopilot) — list in `starter-target-list.csv` (expand to 300 via playbook).
- LinkedIn: founder launch post (in `02-outbound-dm-kit.md`) + per-lead connect/DM copy from `outreach/outbox/`.
- Reddit/communities: value-first, follow each sub's rules (see `05-marketing-launch/02-launch-plan.md`).
- Track every touch in `Verispect-Sprint-Tracker.xlsx`. Goal: 10-20 Founding 20 closes.

---

## LinkedIn Company Page — ready to paste
- **Name:** Verispect
- **Tagline (260 char):** Automated EU AI Act compliance for AI products. We monitor your model for bias & drift and deliver your always-current audit pack — in one line of code. We never see your data. Audit-ready before 2 Aug 2026.
- **Industry:** Software Development · **Specialties:** EU AI Act, AI compliance, bias detection, model drift, GDPR, responsible AI, LLMOps
- **About:**
> The EU AI Act makes high-risk AI — hiring, credit, insurance, legal — prove it isn't drifting or discriminating. Most teams have a policy; almost none have the proof.
> Verispect is your autonomous AI compliance department. Eight fairness auditors and a drift sentinel interrogate your production model 24/7, an evidence engine auto-builds your DPIA and audit pack from live results, and you get the regulator-ready report — in one line of code. We never see your raw data; only hashes and vectors.
> Audit-ready in a day. Stay ready automatically. From $1,500/mo.
> Founding 20 open → verispectai.com

### First 3 posts (schedule via Postiz/manually)
1. **Launch:** the origin story (the "two identical CVs, different scores" find) + "we built the fix" + Founding 20 CTA. (Full text in `02-outbound-dm-kit.md`.)
2. **Education:** "EU AI Act Art. 72 in plain English — the obligation you can't fake." → free snapshot CTA.
3. **Proof:** a 20-sec clip of the demo (risk classify → drift catch → audit pack). "This is compliance in one click."

> Honesty guardrail (LinkedIn + everywhere): "audit-ready / evidence", never "certified/compliant". Agents are AI agents, never humans. Badge = "Monitoring Active".
