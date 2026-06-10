# Day-0 Setup Checklist — Go-Live in a Few Hours

*What's built for you vs. the 5 buttons only you can press (accounts/keys/DNS). Do these top to bottom; you can be selling by tonight.*

---

## ✅ Built and ready in the repo (done by the AI team)
- **Landing page** — `landing/index.html`. Self-contained, deployable anywhere. Countdown to 2 Aug 2026, live spot counter, free-snapshot capture modal, founding offer, comparison, FAQ, payment-link hook. Open it in a browser right now to see it.
- **Sample compliance report** — `gtm/06-collateral/Verispect-SAMPLE-Compliance-Report.pdf`. Generated from the real product on seeded data. Attach in outreach.
- **Founding offer sheet** — `gtm/07-sprint/Verispect-Founding-20-Offer.pdf`. The close-the-deal leave-behind.
- **Billing code** — `billing.py`. Stripe Checkout + portal + webhooks. (Payment Links need no code — see below.)
- **Sprint tracker** — `gtm/07-sprint/Verispect-Sprint-Tracker.xlsx`. Funnel math + daily log + prospects + pipeline.
- **All outbound copy** — `gtm/07-sprint/02-outbound-dm-kit.md`.
- **Target-list method + starter list** — `gtm/07-sprint/03-target-list-playbook.md` + `gtm/07-sprint/starter-target-list.csv`.

## 🔑 The 5 buttons only you can press (need your accounts — ~2–3 hours total)

### 1. Deploy the landing page (15 min)
- Easiest: drag `landing/` folder to **Netlify Drop** (netlify.com/drop) or **Vercel** — instant public URL. Or point `verispectai.com/founding` at it.
- Or fold it into the existing dashboard build under `/founding`.

### 2. Billing — Stripe Payment Links (NO code, 20 min)
- Create a Stripe account → **Products** → add "Verispect Founding" with two prices: **$15,000/yr** and **$1,500/mo**.
- **Payment Links** → create a link for each price → copy the URLs.
- Paste the annual link into `landing/index.html` → `PAY_LINK` (and into the offer PDF / DMs).
- That's it — you can take money today. The `billing.py` Checkout/webhook flow is for later self-serve.

### 3. Free-snapshot capture (15 min)
- In `landing/index.html` set `LEAD_ENDPOINT` to a capture URL: a free **Formspree**/**Tally**/**Google Form** webhook, or your own `/api/lead`. Until then, submissions log to console — fine for a soft test.
- When a lead comes in: email them the one-line SDK setup + run their snapshot with them on the white-glove call.

### 4. Sending infra (30 min)
- Email: a domain inbox (founder@verispectai.com) with **SPF + DKIM + DMARC** set (your DNS / Google Workspace). Warm it — start <40 sends/day.
- LinkedIn: your account, ready. Calendar: a **Cal.com**/Calendly link for "15-min Verispect demo." Put it in every message.

### 5. Build the prospect list (2–4 hrs, or have the AI continue)
- `starter-target-list.csv` gives you a seeded set + the exact queries to expand to 300 (`03-target-list-playbook.md`). Fill the tracker's Prospects tab.

---

## Honest status of "fully automated outreach"
A bot that mass-DMs LinkedIn/IG/Reddit = account ban + GDPR breach + brand damage for a *compliance* company. The safe, fast pipeline that actually works:
1. **AI builds the list + writes every personalized message** (done / continuing).
2. Messages are **queued per prospect** in the tracker.
3. **You (or a warmed, ToS-compliant tool)** send from your own account — LinkedIn manually or via a careful, throttled assistant; email via your warmed inbox.
4. Replies → snapshot → demo → close, tracked in the sheet.

The AI can also **drive your browser with you watching** (open LinkedIn, pre-fill a connect note, queue it) via the Chrome/computer-use tools — you approve each app, then it sets things up. That's the compliant middle ground: AI does the typing-and-finding, you keep the account safe and press send.

---

## Definition of "Day-0 done"
- [ ] Landing page live at a public URL
- [ ] Two Stripe Payment Links created + pasted in
- [ ] Lead capture wired (or Google Form fallback)
- [ ] Email domain warmed + calendar link ready
- [ ] 300 prospects in the tracker
- [ ] Sample report + offer PDF on hand
Then → Day 1 in `01-15-day-battle-plan.md`. Fire.
