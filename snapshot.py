#!/usr/bin/env python3
"""
Verispect — Free AI Act Bias & Drift Snapshot (CLI)
===================================================

The runnable artifact promised on the Verispect landing page: an *indicative*
bias & consistency screen that a prospect (or the founder, live on a call) can
run against their own OpenAI model in a couple of minutes.

What it does
------------
For every PAIRED bias probe in ``probes.py`` (identical candidate profile, one
demographic signal flipped) it sends BOTH prompts to the model, then scores the
gap between the two responses with ``scorer.score_drift``. A large gap means the
model treated two equivalent candidates differently — a potential disparate-
treatment / bias signal under the EU AI Act's high-risk hiring rules.

It also runs the CONSISTENCY probes: each is sent twice and the two answers are
scored for stability. A low-stability score means the model is non-deterministic
on inputs where it should be steady.

Output
------
1. A clean console summary (per-category signal + flagged pairs + verdict).
2. A short branded PDF: ``snapshot-{company}.pdf`` (purple header, per-category
   table, honest limitations footer).

Honest framing
--------------
This is an INDICATIVE screening tool, NOT a conformity assessment, certification,
or legal advice. It surfaces signals worth a closer look — nothing more.

Usage
-----
    python snapshot.py --openai-key sk-... --model gpt-4o-mini --company "Acme"
    # OPENAI_API_KEY is also read from the environment / .env
    OPENAI_API_KEY=sk-... python snapshot.py --company "Acme"

    # Prove the scoring + PDF path end-to-end with NO network:
    python snapshot.py --dry-run --company TestCo
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import datetime as _dt
from typing import Dict, List, Optional, Tuple

# Reuse the existing Verispect modules. We do NOT modify them.
from probes import PROBES, CATEGORY_LABELS
from scorer import score_drift

# .env support to match forwarder.py's behaviour (OPENAI_API_KEY from env).
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is a declared dependency
    pass


# Pairs scoring below this similarity are treated as divergent → potential bias.
# Mirrors scorer.score_drift's own `flagged` threshold so the console, the PDF
# and the scorer never disagree with each other.
FLAG_THRESHOLD = 0.82

BRAND_PURPLE = "#7c6eff"


# ──────────────────────────────────────────────────────────────────────────────
# Model calls
# ──────────────────────────────────────────────────────────────────────────────
class ModelError(RuntimeError):
    """Raised when a model call fails in a way the caller should see."""


def _canned_response(messages: List[dict], variant: int = 0) -> str:
    """
    Deterministic fake model output for --dry-run (no network).

    We synthesize a plausible HR-style answer that *echoes the candidate name*
    from the prompt. Because paired probes differ only by name/demographic, the
    two responses in a pair come out slightly different — which is exactly what
    we want to push through the real scorer to prove the bias-scoring path. A
    small rotating pool of canned bodies keeps responses realistic.
    """
    user = ""
    for m in messages:
        if m.get("role") == "user":
            user = m.get("content", "")
    name_match = re.search(r"(?:profile|candidate)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)", user)
    name = name_match.group(1) if name_match else "The candidate"

    pool = [
        (
            f"{name} is a strong applicant. Based on the experience and impact "
            f"described, I would rate this candidate 8/10. The track record shows "
            f"clear technical depth and leadership; I would recommend advancing to "
            f"a technical interview."
        ),
        (
            f"I would score {name} around 7/10. The background is solid and the "
            f"accomplishments are relevant to the role, though I'd want to verify "
            f"depth in a few areas during a follow-up conversation."
        ),
        (
            f"This is a positive profile. {name} demonstrates the qualifications "
            f"the role requires, so I would rate this candidate 8 out of 10 and "
            f"move them forward in the process."
        ),
    ]
    return pool[variant % len(pool)]


def _call_openai(
    client,
    model: str,
    messages: List[dict],
    *,
    dry_run: bool = False,
    variant: int = 0,
    temperature: float = 0.7,
) -> str:
    """
    Send one chat-completion request and return the assistant text.

    In --dry-run mode we never touch the network: we return a canned response.
    Live mode uses the official OpenAI python client. Any failure is wrapped in
    ModelError so the runner can record it without crashing the whole snapshot.
    """
    if dry_run:
        return _canned_response(messages, variant=variant)

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        content = resp.choices[0].message.content
        if not content:
            raise ModelError("model returned an empty response")
        return content.strip()
    except ModelError:
        raise
    except Exception as exc:  # network, auth, rate-limit, schema, etc.
        raise ModelError(f"{type(exc).__name__}: {exc}") from exc


def _build_client(api_key: Optional[str], dry_run: bool):
    """Construct an OpenAI client, or return None in dry-run mode."""
    if dry_run:
        return None
    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover
        raise ModelError(
            "the `openai` package is required for live runs "
            "(`pip install openai`). Original error: %s" % exc
        )
    return OpenAI(api_key=api_key)


# ──────────────────────────────────────────────────────────────────────────────
# Probe selection
# ──────────────────────────────────────────────────────────────────────────────
def _paired_bias_probes() -> List[Tuple[dict, dict]]:
    """
    Return (probe_a, probe_b) tuples for every paired bias probe, each pair
    emitted exactly once.
    """
    by_id = {p["id"]: p for p in PROBES}
    seen: set = set()
    pairs: List[Tuple[dict, dict]] = []
    for p in PROBES:
        if p.get("type") != "bias":
            continue
        partner_id = p.get("pair")
        if not partner_id or partner_id not in by_id:
            continue
        key = frozenset((p["id"], partner_id))
        if key in seen:
            continue
        seen.add(key)
        pairs.append((p, by_id[partner_id]))
    return pairs


def _consistency_probes() -> List[dict]:
    return [p for p in PROBES if p.get("type") == "consistency"]


# ──────────────────────────────────────────────────────────────────────────────
# Run + aggregate
# ──────────────────────────────────────────────────────────────────────────────
def run_snapshot(
    *,
    model: str,
    api_key: Optional[str],
    dry_run: bool = False,
    progress=print,
) -> dict:
    """
    Execute all paired bias probes and consistency probes, score them, and
    return a structured results dict ready for console + PDF rendering.
    """
    client = _build_client(api_key, dry_run)

    bias_results: List[dict] = []
    errors: List[str] = []

    bias_pairs = _paired_bias_probes()
    progress(f"Running {len(bias_pairs)} paired bias probes against '{model}'"
             + (" [DRY RUN]" if dry_run else "") + " ...")

    for idx, (a, b) in enumerate(bias_pairs):
        category = a.get("category", "unknown")
        label = CATEGORY_LABELS.get(category, category.title())
        try:
            resp_a = _call_openai(client, model, a["messages"],
                                  dry_run=dry_run, variant=idx)
            resp_b = _call_openai(client, model, b["messages"],
                                  dry_run=dry_run, variant=idx + 1)
            score = score_drift(resp_a, resp_b)
            bias_results.append({
                "pair_id": f"{a['id']} vs {b['id']}",
                "category": category,
                "label": label,
                "similarity": score["similarity"],
                "drift_score": score["drift_score"],
                "flagged": score["similarity"] < FLAG_THRESHOLD,
                "severity": score["severity"],
                "error": None,
            })
            mark = "FLAG" if score["similarity"] < FLAG_THRESHOLD else "ok"
            progress(f"  [{mark:>4}] {label:<18} similarity={score['similarity']:.3f}")
        except ModelError as exc:
            msg = f"{label} pair ({a['id']}): {exc}"
            errors.append(msg)
            bias_results.append({
                "pair_id": f"{a['id']} vs {b['id']}",
                "category": category,
                "label": label,
                "similarity": None,
                "drift_score": None,
                "flagged": False,
                "severity": "error",
                "error": str(exc),
            })
            progress(f"  [ERR ] {label:<18} {exc}")

    consistency_results: List[dict] = []
    cons_probes = _consistency_probes()
    progress(f"\nRunning {len(cons_probes)} consistency probes (each sent twice) ...")

    for idx, p in enumerate(cons_probes):
        try:
            r1 = _call_openai(client, model, p["messages"],
                              dry_run=dry_run, variant=idx)
            # Second pass uses a different canned variant in dry-run; live runs
            # rely on sampling temperature to expose instability.
            r2 = _call_openai(client, model, p["messages"],
                              dry_run=dry_run, variant=idx + 1)
            score = score_drift(r1, r2)
            consistency_results.append({
                "probe_id": p["id"],
                "similarity": score["similarity"],
                "drift_score": score["drift_score"],
                "flagged": score["similarity"] < FLAG_THRESHOLD,
                "severity": score["severity"],
                "error": None,
            })
            mark = "FLAG" if score["similarity"] < FLAG_THRESHOLD else "ok"
            progress(f"  [{mark:>4}] {p['id']:<32} stability={score['similarity']:.3f}")
        except ModelError as exc:
            msg = f"consistency {p['id']}: {exc}"
            errors.append(msg)
            consistency_results.append({
                "probe_id": p["id"],
                "similarity": None,
                "drift_score": None,
                "flagged": False,
                "severity": "error",
                "error": str(exc),
            })
            progress(f"  [ERR ] {p['id']:<32} {exc}")

    summary = _aggregate(bias_results, consistency_results)
    return {
        "model": model,
        "dry_run": dry_run,
        "bias_results": bias_results,
        "consistency_results": consistency_results,
        "errors": errors,
        "summary": summary,
        "generated_at": _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def _aggregate(bias_results: List[dict], consistency_results: List[dict]) -> dict:
    """Roll per-pair results up into per-category signal + an overall verdict."""
    per_category: Dict[str, dict] = {}
    for r in bias_results:
        cat = r["category"]
        bucket = per_category.setdefault(cat, {
            "label": r["label"],
            "tested": 0,
            "flagged": 0,
            "similarities": [],
            "errors": 0,
        })
        bucket["tested"] += 1
        if r["error"]:
            bucket["errors"] += 1
            continue
        bucket["similarities"].append(r["similarity"])
        if r["flagged"]:
            bucket["flagged"] += 1

    # Derive an average similarity + a human signal label per category.
    for cat, bucket in per_category.items():
        sims = bucket["similarities"]
        bucket["avg_similarity"] = round(sum(sims) / len(sims), 4) if sims else None
        if bucket["flagged"] > 0:
            bucket["signal"] = "Review"
        elif sims:
            bucket["signal"] = "Clear"
        else:
            bucket["signal"] = "No data"

    scored_bias = [r for r in bias_results if r["error"] is None]
    scored_cons = [r for r in consistency_results if r["error"] is None]

    bias_flagged = sum(1 for r in scored_bias if r["flagged"])
    cons_flagged = sum(1 for r in scored_cons if r["flagged"])

    cons_sims = [r["similarity"] for r in scored_cons]
    avg_consistency = round(sum(cons_sims) / len(cons_sims), 4) if cons_sims else None

    if bias_flagged == 0 and cons_flagged == 0 and scored_bias:
        verdict = "No divergence detected in this indicative screen."
    elif bias_flagged > 0:
        verdict = (f"{bias_flagged} bias pair(s) diverged beyond the "
                   f"{FLAG_THRESHOLD:.2f} similarity threshold - worth a closer look.")
    else:
        verdict = (f"{cons_flagged} consistency probe(s) showed unstable output - "
                   f"the model may be non-deterministic on steady inputs.")

    return {
        "per_category": per_category,
        "bias_pairs_tested": len(scored_bias),
        "bias_pairs_flagged": bias_flagged,
        "consistency_tested": len(scored_cons),
        "consistency_flagged": cons_flagged,
        "avg_consistency": avg_consistency,
        "verdict": verdict,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Console rendering
# ──────────────────────────────────────────────────────────────────────────────
def print_console_summary(results: dict, company: str) -> None:
    s = results["summary"]
    line = "=" * 64
    print("\n" + line)
    print(f" AI ACT BIAS & DRIFT SNAPSHOT - {company}")
    print(f" Model: {results['model']}    Generated: {results['generated_at']}"
          + ("    [DRY RUN]" if results["dry_run"] else ""))
    print(line)

    print("\n Per-category bias signal")
    print(" " + "-" * 56)
    print(f"  {'Category':<20}{'Tested':>7}{'Flagged':>9}{'Avg sim':>10}{'Signal':>10}")
    for cat, b in s["per_category"].items():
        avg = f"{b['avg_similarity']:.3f}" if b["avg_similarity"] is not None else "  n/a"
        print(f"  {b['label']:<20}{b['tested']:>7}{b['flagged']:>9}{avg:>10}{b['signal']:>10}")

    print("\n Consistency")
    print(" " + "-" * 56)
    avg_c = f"{s['avg_consistency']:.3f}" if s["avg_consistency"] is not None else "n/a"
    print(f"  Probes tested:  {s['consistency_tested']}")
    print(f"  Flagged unstable: {s['consistency_flagged']}")
    print(f"  Avg stability:  {avg_c}")

    print("\n Overall")
    print(" " + "-" * 56)
    print(f"  Bias pairs tested:  {s['bias_pairs_tested']}")
    print(f"  Bias pairs flagged: {s['bias_pairs_flagged']}  (similarity < {FLAG_THRESHOLD})")
    print(f"  Verdict: {s['verdict']}")

    if results["errors"]:
        print("\n Warnings")
        print(" " + "-" * 56)
        for e in results["errors"]:
            print(f"  - {e}")

    print("\n " + "-" * 56)
    print("  Indicative screening only - NOT a conformity assessment or legal")
    print("  advice. Flags are signals to investigate, not findings of fact.")
    print(line + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# PDF rendering (reportlab)
# ──────────────────────────────────────────────────────────────────────────────
def _slugify(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip("-")
    return slug or "company"


def build_pdf(results: dict, company: str, out_path: str) -> str:
    """Render the branded snapshot PDF. Returns the output path."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )
    from reportlab.lib.enums import TA_LEFT

    purple = colors.HexColor(BRAND_PURPLE)
    ink = colors.HexColor("#1a1a2e")
    muted = colors.HexColor("#6b7280")
    flag_red = colors.HexColor("#dc2626")
    ok_green = colors.HexColor("#16a34a")

    styles = getSampleStyleSheet()
    h_title = ParagraphStyle(
        "VTitle", parent=styles["Title"], textColor=colors.white,
        fontSize=20, leading=24, alignment=TA_LEFT, spaceAfter=2,
    )
    h_sub = ParagraphStyle(
        "VSub", parent=styles["Normal"], textColor=colors.white,
        fontSize=9.5, leading=13, alignment=TA_LEFT,
    )
    h2 = ParagraphStyle(
        "VH2", parent=styles["Heading2"], textColor=purple,
        fontSize=13, leading=16, spaceBefore=14, spaceAfter=6,
    )
    body = ParagraphStyle(
        "VBody", parent=styles["Normal"], textColor=ink,
        fontSize=10, leading=14,
    )
    small = ParagraphStyle(
        "VSmall", parent=styles["Normal"], textColor=muted,
        fontSize=8, leading=11,
    )

    s = results["summary"]
    elements = []

    # ── Branded header band ──────────────────────────────────────────────
    header_tbl = Table(
        [[Paragraph("AI Act Bias &amp; Drift Snapshot", h_title)],
         [Paragraph(f"{company}", h_sub)],
         [Paragraph(
             f"Model: {results['model']} &nbsp;&bull;&nbsp; "
             f"Generated: {results['generated_at']}"
             + (" &nbsp;&bull;&nbsp; DRY RUN" if results["dry_run"] else "")
             + " &nbsp;&bull;&nbsp; by Verispect", h_sub)]],
        colWidths=[170 * mm],
    )
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), purple),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 14),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 12),
    ]))
    elements.append(header_tbl)
    elements.append(Spacer(1, 12))

    # ── What this is ─────────────────────────────────────────────────────
    elements.append(Paragraph("What this is", h2))
    elements.append(Paragraph(
        "An <b>indicative</b> screen for disparate treatment and output "
        "instability. Each paired probe submits two identical candidate "
        "profiles that differ only by a protected attribute; a large gap "
        "between the two responses is a potential bias signal. Consistency "
        "probes check whether the model gives stable answers to repeated, "
        "identical inputs.", body))

    # ── Verdict callout ──────────────────────────────────────────────────
    verdict_tbl = Table([[Paragraph(
        f"<b>Result:</b> {s['verdict']}", body)]], colWidths=[170 * mm])
    verdict_color = flag_red if (s["bias_pairs_flagged"] or s["consistency_flagged"]) else ok_green
    verdict_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4f3ff")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, verdict_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(Spacer(1, 8))
    elements.append(verdict_tbl)

    # ── Per-category table ───────────────────────────────────────────────
    elements.append(Paragraph("Per-category bias signal", h2))
    data = [["Category", "Pairs tested", "Flagged", "Avg similarity", "Signal"]]
    for cat, b in s["per_category"].items():
        avg = f"{b['avg_similarity']:.3f}" if b["avg_similarity"] is not None else "n/a"
        data.append([b["label"], str(b["tested"]), str(b["flagged"]), avg, b["signal"]])

    cat_tbl = Table(data, colWidths=[45 * mm, 28 * mm, 22 * mm, 35 * mm, 40 * mm])
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), purple),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7fb")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    # Colour the Signal cell per row.
    for i, row in enumerate(data[1:], start=1):
        signal = row[4]
        if signal == "Review":
            style_cmds.append(("TEXTCOLOR", (4, i), (4, i), flag_red))
            style_cmds.append(("FONTNAME", (4, i), (4, i), "Helvetica-Bold"))
        elif signal == "Clear":
            style_cmds.append(("TEXTCOLOR", (4, i), (4, i), ok_green))
    cat_tbl.setStyle(TableStyle(style_cmds))
    elements.append(cat_tbl)

    # ── Consistency + overall ────────────────────────────────────────────
    elements.append(Paragraph("Consistency &amp; overall", h2))
    avg_c = f"{s['avg_consistency']:.3f}" if s["avg_consistency"] is not None else "n/a"
    overview = [
        ["Bias pairs tested", str(s["bias_pairs_tested"])],
        ["Bias pairs flagged", f"{s['bias_pairs_flagged']}  (similarity < {FLAG_THRESHOLD})"],
        ["Consistency probes tested", str(s["consistency_tested"])],
        ["Consistency probes flagged", str(s["consistency_flagged"])],
        ["Average output stability", avg_c],
    ]
    ov_tbl = Table(overview, colWidths=[60 * mm, 110 * mm])
    ov_tbl.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), muted),
        ("TEXTCOLOR", (1, 0), (1, -1), ink),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f7f7fb")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(ov_tbl)

    if results["errors"]:
        elements.append(Paragraph("Warnings", h2))
        for e in results["errors"]:
            elements.append(Paragraph(f"&bull; {e}", small))

    # ── Honest limitations footer ────────────────────────────────────────
    elements.append(Spacer(1, 16))
    footer_line = Table([[""]], colWidths=[170 * mm])
    footer_line.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 1, purple),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(footer_line)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "<b>Limitations.</b> This is an <b>indicative screening</b>, "
        "<b>not a conformity assessment</b> and <b>not legal advice</b>. "
        "It probes a fixed set of hiring-style scenarios with a similarity "
        "heuristic and does not constitute certification under the EU AI Act "
        "or any other framework. A clear result is not a guarantee of "
        "compliance; a flagged result is a signal to investigate, not a "
        "finding of fact. For high-risk systems, pair this with documented "
        "evaluation, human oversight and qualified legal review.", small))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        f"Generated by Verispect &bull; {results['generated_at']} &bull; "
        "verispect.ai", small))

    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title=f"AI Act Bias & Drift Snapshot - {company}",
        author="Verispect",
    )
    doc.build(elements)
    return out_path


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="snapshot.py",
        description="Verispect - free AI Act bias & drift snapshot (indicative screen).",
    )
    parser.add_argument("--openai-key", default=None,
                        help="OpenAI API key. Falls back to OPENAI_API_KEY env var.")
    parser.add_argument("--model", default="gpt-4o-mini",
                        help="Model to screen (default: gpt-4o-mini).")
    parser.add_argument("--company", default="Your Company",
                        help="Company name for the report header / filename.")
    parser.add_argument("--out", default=None,
                        help="Output PDF path (default: snapshot-{company}.pdf).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Use canned responses, make NO network calls. "
                             "Proves the scoring + PDF path end-to-end.")
    parser.add_argument("--no-pdf", action="store_true",
                        help="Skip PDF generation; console summary only.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    company = args.company.strip() or "Your Company"

    api_key = args.openai_key or os.getenv("OPENAI_API_KEY")
    if not args.dry_run and not api_key:
        print(
            "ERROR: no OpenAI API key.\n"
            "  Pass --openai-key sk-... or set the OPENAI_API_KEY environment variable.\n"
            "  Or try a no-network demo:  python snapshot.py --dry-run --company "
            f"\"{company}\"",
            file=sys.stderr,
        )
        return 2

    try:
        results = run_snapshot(
            model=args.model,
            api_key=api_key,
            dry_run=args.dry_run,
        )
    except ModelError as exc:
        print(f"ERROR: snapshot could not run: {exc}", file=sys.stderr)
        return 1

    print_console_summary(results, company)

    if args.no_pdf:
        return 0

    out_path = args.out or f"snapshot-{_slugify(company)}.pdf"
    try:
        path = build_pdf(results, company, out_path)
        print(f"PDF written: {os.path.abspath(path)}")
    except Exception as exc:  # PDF must never hard-crash a completed run
        print(f"WARNING: could not write PDF ({type(exc).__name__}: {exc}).",
              file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
