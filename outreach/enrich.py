"""
enrich.py — find + verify business emails for leads, automatically.

Uses legitimate B2B data providers (Hunter.io primary, Apollo optional) that carry
their own lawful-basis/compliance — NOT scraping LinkedIn/IG (banned + GDPR breach).

Set ONE of:
  HUNTER_API_KEY   (hunter.io — domain-search + email-finder + verifier)
  APOLLO_API_KEY   (apollo.io — people match) [secondary]

No key set -> enrichment is a no-op (pipeline still produces LinkedIn-ready copy).
Only emails that VERIFY as deliverable are written back, to protect domain reputation.
"""
import os, json, time, urllib.request, urllib.parse

HUNTER = "https://api.hunter.io/v2"
APOLLO = "https://api.apollo.io/v1"

# Prefer decision-makers
WANT_TITLES = ["cto", "chief technology", "head of ai", "head of data", "founder",
               "co-founder", "vp engineering", "head of engineering", "ml lead",
               "head of compliance", "dpo", "data protection"]


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"  [enrich] request error: {e}")
        return None


def _post(url, payload, headers):
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"  [enrich] apollo error: {e}")
        return None


def hunter_key():
    return os.getenv("HUNTER_API_KEY", "").strip()


def hunter_domain_search(company):
    """Find domain + best-fit email for a company name via Hunter domain-search."""
    key = hunter_key()
    if not key:
        return None
    q = urllib.parse.urlencode({"company": company, "api_key": key, "limit": 10})
    data = _get(f"{HUNTER}/domain-search?{q}")
    if not data or "data" not in data:
        return None
    d = data["data"]
    emails = d.get("emails", [])
    # rank by wanted titles, then seniority, then confidence
    def score(e):
        pos = (e.get("position") or "").lower()
        title_hit = any(t in pos for t in WANT_TITLES)
        sen = {"executive": 2, "senior": 1}.get((e.get("seniority") or ""), 0)
        return (title_hit, sen, e.get("confidence") or 0)
    emails.sort(key=score, reverse=True)
    best = emails[0] if emails else None
    return {
        "domain": d.get("domain"),
        "email": best.get("value") if best else None,
        "first": (best.get("first_name") if best else None),
        "last": (best.get("last_name") if best else None),
        "position": (best.get("position") if best else None),
        "confidence": (best.get("confidence") if best else None),
    }


def hunter_verify(email):
    """Return True only if Hunter says deliverable (protects sender reputation)."""
    key = hunter_key()
    if not key or not email:
        return False
    q = urllib.parse.urlencode({"email": email, "api_key": key})
    data = _get(f"{HUNTER}/email-verifier?{q}")
    if not data or "data" not in data:
        return False
    status = (data["data"].get("status") or "").lower()
    return status in ("valid", "deliverable", "accept_all")  # accept_all = risky-ok


def apollo_find(company):
    """Secondary: Apollo people search by org + title."""
    key = os.getenv("APOLLO_API_KEY", "").strip()
    if not key:
        return None
    payload = {"q_organization_domains": company, "person_titles": WANT_TITLES[:6],
               "page": 1, "per_page": 5}
    headers = {"Content-Type": "application/json", "Cache-Control": "no-cache",
               "X-Api-Key": key}
    data = _post(f"{APOLLO}/mixed_people/search", payload, headers)
    if not data:
        return None
    people = data.get("people") or []
    if not people:
        return None
    p = people[0]
    return {"email": p.get("email"), "first": p.get("first_name"),
            "last": p.get("last_name"), "position": p.get("title")}


def enrich_lead(lead):
    """Fill lead['email'] + contact if found AND verified. Returns True if enriched."""
    company = (lead.get("Company") or lead.get("company") or "").strip()
    if not company:
        return False
    res = hunter_domain_search(company) or apollo_find(company)
    if not res or not res.get("email"):
        return False
    email = res["email"]
    if not hunter_verify(email):
        print(f"  [enrich] {company}: found {email} but not verified -> skip")
        return False
    lead["email"] = email
    if res.get("first"):
        lead["Contact (RESEARCH)"] = f"{res.get('first','')} {res.get('last','')}".strip()
    if res.get("position"):
        lead["Title"] = res["position"]
    print(f"  [enrich] {company}: {email} ({res.get('position') or 'contact'}) [verified]")
    return True


def enrich_leads(leads, throttle=1.5):
    if not (hunter_key() or os.getenv("APOLLO_API_KEY")):
        print("[enrich] no HUNTER_API_KEY / APOLLO_API_KEY set -> skipping (LinkedIn copy still produced)")
        return leads, 0
    n = 0
    for lead in leads:
        has = (lead.get("email") or "").strip()
        if has:
            continue
        if enrich_lead(lead):
            n += 1
            time.sleep(throttle)
    print(f"[enrich] verified emails found for {n} leads")
    return leads, n
