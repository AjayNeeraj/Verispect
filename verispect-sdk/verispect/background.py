"""
background.py
Queue-based background worker that runs in a daemon thread.
The main thread enqueues tasks and returns immediately.
The daemon thread processes them — if the process exits, it exits too (no hanging).

Handles:
  - Sending ingest payloads to /api/ingest
  - Sending probe results to /api/probe-result
  - Fetching probe specs from /api/probe
  - Local golden probe storage
"""

import threading
import queue
import hashlib
import logging
import json
from typing import Optional

logger = logging.getLogger("verispect")

_QUEUE_MAX = 2000  # Drop silently if full — never block the caller


class BackgroundWorker:
    def __init__(self, verispect_key: str, endpoint: str):
        self._key = verispect_key
        self._endpoint = endpoint.rstrip("/")
        self._queue: queue.Queue = queue.Queue(maxsize=_QUEUE_MAX)

        self._thread = threading.Thread(
            target=self._run,
            name="verispect-bg",
            daemon=True,   # Exits when the main process exits
        )
        self._thread.start()
        logger.debug("Verispect background worker started.")

    # ── Public API ────────────────────────────────────────────────────────────

    def enqueue(self, task: dict) -> None:
        """Non-blocking. Drops the task silently if the queue is full."""
        try:
            self._queue.put_nowait(task)
        except queue.Full:
            logger.debug("Verispect queue full — task dropped.")

    def fetch_probe(self, model: str) -> Optional[dict]:
        """
        Synchronously fetch a probe spec from the server.
        Returns None on any error — caller handles gracefully.
        """
        try:
            import httpx
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(
                    f"{self._endpoint}/api/sdk/probe",
                    params={"model": model},
                    headers={"X-Verispect-Key": self._key},
                )
                if resp.status_code == 200:
                    return resp.json()
                logger.debug(f"Probe fetch returned {resp.status_code}")
        except Exception as e:
            logger.debug(f"Verispect probe fetch error: {e}")
        return None

    # ── Worker loop ───────────────────────────────────────────────────────────

    def _run(self) -> None:
        """Daemon thread loop. Processes tasks one at a time."""
        while True:
            try:
                task = self._queue.get(timeout=2)
                self._dispatch(task)
            except queue.Empty:
                continue
            except Exception as e:
                logger.debug(f"Verispect worker loop error: {e}")

    def _dispatch(self, task: dict) -> None:
        t = task.get("type")
        try:
            if t == "ingest":
                self._handle_ingest(task)
            elif t == "probe_result":
                self._handle_probe_result(task)
            else:
                logger.debug(f"Unknown task type: {t}")
        except Exception as e:
            logger.debug(f"Verispect dispatch error ({t}): {e}")

    # ── Ingest handler ────────────────────────────────────────────────────────

    def _handle_ingest(self, task: dict) -> None:
        from .embedder import compute_embedding
        from .local_store import LocalStore

        response_text = task.get("response_text", "")
        if not response_text.strip():
            return

        # Compute embedding locally — only this goes to the server, not the text
        embedding = compute_embedding(response_text)
        if not embedding:
            return  # embedder unavailable — skip silently

        prompt_hash = task["prompt_hash"]
        model = task["model"]
        is_golden = task.get("is_golden", False)
        prompt_text = task.get("prompt_text")  # Only present when is_golden=True

        payload: dict = {
            "prompt_hash": prompt_hash,
            "response_embedding": embedding,
            "model": model,
            "latency_ms": task.get("latency_ms", 0),
            "prompt_tokens": task.get("prompt_tokens", 0),
            "completion_tokens": task.get("completion_tokens", 0),
            "is_golden": is_golden,
        }

        if is_golden and prompt_text:
            golden_id = hashlib.sha256(
                f"{prompt_hash}:{model}".encode()
            ).hexdigest()[:24]

            # Save RAW prompt text to LOCAL SQLite — never sent to server
            store = LocalStore()
            saved = store.save_golden(
                golden_id=golden_id,
                prompt_hash=prompt_hash,
                prompt_text=prompt_text,
                model=model,
                embedding=embedding,
            )
            if saved:
                logger.debug(f"Golden probe stored locally: {golden_id}")

            # Tell server: a golden probe exists with this id+hash+embedding
            # Server stores only the embedding — NOT the prompt text
            payload["golden_id"] = golden_id
            payload["golden_embedding"] = embedding

        self._post("/api/sdk/ingest", payload)

    # ── Probe result handler ──────────────────────────────────────────────────

    def _handle_probe_result(self, task: dict) -> None:
        self._post("/api/sdk/probe-result", task)

    # ── HTTP helper ───────────────────────────────────────────────────────────

    def _post(self, path: str, payload: dict) -> None:
        try:
            import httpx
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"{self._endpoint}{path}",
                    json=payload,
                    headers={"X-Verispect-Key": self._key},
                )
                if resp.status_code not in (200, 201):
                    logger.debug(
                        f"Verispect POST {path} returned {resp.status_code}: {resp.text[:200]}"
                    )
        except Exception as e:
            logger.debug(f"Verispect POST {path} error: {e}")
