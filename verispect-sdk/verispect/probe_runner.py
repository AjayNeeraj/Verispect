"""
probe_runner.py
Fires canary probes using the CLIENT'S own OpenAI key — never yours.

Two probe types:
  1. Regulatory  — hardcoded bias/consistency prompts from your server.
                   Response TEXT is sent back (safe — synthetic prompt, no PII).

  2. Golden      — the client's own real prompts, stored locally, replayed.
                   Only the response EMBEDDING is sent back — never the text.

Probes fire in daemon threads: the real response has already been returned
to the caller before any probe work starts.
"""

import random
import threading
import logging
import json
from typing import Optional

logger = logging.getLogger("verispect")


class ProbeRunner:
    def __init__(self, original_client, worker, probe_rate: float = 0.02):
        """
        Args:
            original_client: The raw, unwrapped OpenAI client.
                             MUST be the original — not the wrapped version —
                             to avoid recursive interception loops.
            worker:          BackgroundWorker instance for fetching probes and
                             sending results.
            probe_rate:      Fraction of real calls that trigger a probe (0.02 = 2%).
        """
        self._client = original_client
        self._worker = worker
        self._probe_rate = probe_rate
        self._store: Optional[object] = None   # LocalStore, lazy-initialized

    # ── Public ────────────────────────────────────────────────────────────────

    def maybe_fire(self, model: str) -> None:
        """Called after every real request. Non-blocking — spawns a daemon thread."""
        if random.random() > self._probe_rate:
            return
        t = threading.Thread(
            target=self._fire,
            args=(model,),
            daemon=True,
            name="verispect-probe",
        )
        t.start()

    # ── Probe dispatch ────────────────────────────────────────────────────────

    def _fire(self, model: str) -> None:
        try:
            probe = self._worker.fetch_probe(model)
            if not probe:
                return

            probe_type = probe.get("type")
            if probe_type == "regulatory":
                self._fire_regulatory(probe, model)
            elif probe_type == "golden":
                self._fire_golden(probe, model)
            else:
                logger.debug(f"Unknown probe type: {probe_type}")
        except Exception as e:
            logger.debug(f"ProbeRunner._fire error: {e}")

    # ── Regulatory probe ──────────────────────────────────────────────────────

    def _fire_regulatory(self, probe: dict, model: str) -> None:
        """
        Fires a synthetic probe from the server's library.
        These prompts contain no client data — safe to return full response text.
        """
        messages = probe.get("messages")
        probe_id = probe.get("probe_id")
        category = probe.get("category", "unknown")

        if not messages or not probe_id:
            return

        try:
            # Use the ORIGINAL client — bypasses the wrapper to avoid infinite loops
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
            )
            response_text = response.choices[0].message.content or ""
        except Exception as e:
            logger.debug(f"Regulatory probe call failed ({probe_id}): {e}")
            return

        # Safe to send full text — it's a synthetic prompt, zero PII
        self._worker.enqueue({
            "type": "probe_result",
            "probe_id": probe_id,
            "probe_type": "regulatory",
            "response_text": response_text,
            "response_embedding": [],    # Server computes from text
            "model": model,
            "category": category,
        })

    # ── Golden probe ──────────────────────────────────────────────────────────

    def _fire_golden(self, probe: dict, model: str) -> None:
        """
        Replays one of the client's own historical prompts.
        The prompt is read from LOCAL storage — never fetched from the server.
        Only the response EMBEDDING is sent back — raw text stays on this machine.
        """
        from .embedder import compute_embedding

        prompt_hash = probe.get("prompt_hash")
        golden_id = probe.get("probe_id")

        if not prompt_hash or not golden_id:
            return

        # Read prompt from LOCAL SQLite — server has no copy of this text
        store = self._get_store()
        prompt_text = store.get_by_hash(prompt_hash)

        if not prompt_text:
            logger.debug(
                f"Golden probe {golden_id}: prompt not found locally "
                f"(hash: {prompt_hash[:12]}...)"
            )
            return

        # Reconstruct messages list (stored as str(list) by wrapper)
        messages = self._parse_messages(prompt_text)

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
            )
            response_text = response.choices[0].message.content or ""
        except Exception as e:
            logger.debug(f"Golden probe call failed ({golden_id}): {e}")
            return

        # Compute embedding locally — send ONLY the vector, never the text
        embedding = compute_embedding(response_text)
        if not embedding:
            return

        self._worker.enqueue({
            "type": "probe_result",
            "probe_id": golden_id,
            "probe_type": "golden",
            "response_text": "",         # Intentionally blank — privacy guarantee
            "response_embedding": embedding,
            "model": model,
            "category": "golden",
        })

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_store(self):
        if self._store is None:
            from .local_store import LocalStore
            self._store = LocalStore()
        return self._store

    @staticmethod
    def _parse_messages(prompt_text: str) -> list:
        """
        The wrapper stores messages as str(list_of_dicts).
        Try JSON first, then eval-safe fallback, then plain text.
        """
        # Try JSON
        try:
            parsed = json.loads(prompt_text)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass

        # Try ast.literal_eval (handles Python repr of list of dicts)
        try:
            import ast
            parsed = ast.literal_eval(prompt_text)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

        # Fallback: treat as plain user message
        return [{"role": "user", "content": prompt_text[:2000]}]
