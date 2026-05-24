# canary.py — Drift detection engine
# Fires calibrated probes on ~10% of real traffic, scores against baselines
import random
from probes import PROBES
from forwarder import forward_to_openai
from scorer import score_drift
from database import log_call, get_baseline

CANARY_RATE = 0.10


async def maybe_run_canary(body: dict, auth: str):
    if random.random() > CANARY_RATE:
        return

    probe = random.choice(PROBES)
    probe_body = {
        "model": body.get("model", "gpt-4o-mini"),
        "messages": probe["messages"]
    }

    try:
        result = await forward_to_openai(probe_body, auth)
        new_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Get real stored baseline
        baseline = await get_baseline(probe["id"])

        if not baseline:
            print(f"No baseline for {probe['id']} — run calibrate.py first")
            return

        drift = score_drift(baseline, new_response)

        # For bias probes — also compare against the paired probe
        pair_note = ""
        if probe["pair"]:
            pair_baseline = await get_baseline(probe["pair"])
            if pair_baseline:
                pair_drift = score_drift(new_response, pair_baseline)
                pair_note = f" | Pair divergence: {pair_drift['drift_score']}"
                # If paired responses are diverging — that's bias signal
                if pair_drift["flagged"]:
                    print(f"BIAS SIGNAL — {probe['id']} vs {probe['pair']} — divergence {pair_drift['drift_score']}")

        # Log the canary result with all fields in one insert
        await log_call(
            model=probe_body["model"],
            prompt=str(probe["messages"]),
            response=new_response,
            prompt_tokens=result.get("usage", {}).get("prompt_tokens", 0),
            completion_tokens=result.get("usage", {}).get("completion_tokens", 0),
            latency_ms=0,
            is_canary=1,
            drift_score=drift["drift_score"],
            flagged=int(drift["flagged"]),
            probe_id=probe["id"],
            severity=drift["severity"],
            probe_category=probe.get("category", "unknown")
        )

        status = "DRIFT DETECTED" if drift["flagged"] else "OK"
        print(f"{status} — {probe['id']} [{drift['severity']}] — score {drift['drift_score']}{pair_note}")

    except Exception as e:
        print(f"Canary failed silently: {e}")