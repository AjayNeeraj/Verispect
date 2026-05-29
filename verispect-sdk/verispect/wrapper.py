"""
wrapper.py
Intercepts OpenAI client calls transparently.
- Returns responses to the caller IMMEDIATELY — zero latency added.
- All logging, embedding, and probe work happens in a background thread.
"""

import time
import hashlib
import logging

from .background import BackgroundWorker
from .probe_runner import ProbeRunner

logger = logging.getLogger("verispect")


class VerispectWrapper:
    """
    Drop-in replacement for the OpenAI client.
    Exposes the same interface; intercepts chat.completions.create().
    """

    def __init__(
        self,
        client,
        verispect_key: str,
        endpoint: str,
        probe_rate: float,
        golden_rate: float,
    ):
        self._client = client          # original, unwrapped OpenAI client
        self._golden_rate = golden_rate

        self._worker = BackgroundWorker(
            verispect_key=verispect_key,
            endpoint=endpoint,
        )
        self._probe_runner = ProbeRunner(
            original_client=client,
            worker=self._worker,
            probe_rate=probe_rate,
        )

        # Replace chat.completions with our interceptor
        self.chat = _ChatWrapper(
            original_chat=client.chat,
            worker=self._worker,
            probe_runner=self._probe_runner,
            golden_rate=golden_rate,
        )

    def __getattr__(self, name):
        # Transparently proxy everything else (models, embeddings, etc.)
        return getattr(self._client, name)


class _ChatWrapper:
    def __init__(self, original_chat, worker, probe_runner, golden_rate):
        self._chat = original_chat
        self.completions = _CompletionsWrapper(
            original_completions=original_chat.completions,
            worker=worker,
            probe_runner=probe_runner,
            golden_rate=golden_rate,
        )

    def __getattr__(self, name):
        return getattr(self._chat, name)


class _CompletionsWrapper:
    def __init__(self, original_completions, worker, probe_runner, golden_rate):
        self._completions = original_completions
        self._worker = worker
        self._probe_runner = probe_runner
        self._golden_rate = golden_rate

    def create(self, **kwargs):
        import random

        start = time.time()

        # ── Make the real call — client is NEVER blocked by our work ──────────
        response = self._completions.create(**kwargs)
        latency_ms = int((time.time() - start) * 1000)

        # ── Extract metadata ──────────────────────────────────────────────────
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "unknown")
        prompt_text = str(messages)
        prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        is_golden = random.random() < self._golden_rate

        # ── Streaming path ────────────────────────────────────────────────────
        if kwargs.get("stream", False):
            return _StreamCollector(
                stream=response,
                prompt_hash=prompt_hash,
                prompt_text=prompt_text if is_golden else None,
                model=model,
                latency_ms=latency_ms,
                is_golden=is_golden,
                worker=self._worker,
                probe_runner=self._probe_runner,
            )

        # ── Non-streaming path ────────────────────────────────────────────────
        try:
            response_text = response.choices[0].message.content or ""
            prompt_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
            completion_tokens = getattr(response.usage, "completion_tokens", 0) or 0
        except Exception:
            response_text = ""
            prompt_tokens = 0
            completion_tokens = 0

        # Queue all background work — non-blocking
        self._worker.enqueue({
            "type": "ingest",
            "prompt_hash": prompt_hash,
            "prompt_text": prompt_text if is_golden else None,
            "response_text": response_text,
            "model": model,
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "is_golden": is_golden,
        })

        # Maybe fire a canary probe in a separate daemon thread
        self._probe_runner.maybe_fire(model)

        return response

    def __getattr__(self, name):
        return getattr(self._completions, name)


class _StreamCollector:
    """
    Transparent wrapper around a streaming OpenAI response.
    Yields chunks immediately. After the final chunk, queues background logging.
    """

    def __init__(
        self,
        stream,
        prompt_hash: str,
        prompt_text,
        model: str,
        latency_ms: int,
        is_golden: bool,
        worker,
        probe_runner,
    ):
        self._stream = stream
        self._prompt_hash = prompt_hash
        self._prompt_text = prompt_text
        self._model = model
        self._latency_ms = latency_ms
        self._is_golden = is_golden
        self._worker = worker
        self._probe_runner = probe_runner

    def __iter__(self):
        collected = []

        for chunk in self._stream:
            yield chunk
            try:
                content = chunk.choices[0].delta.content
                if content:
                    collected.append(content)
            except Exception:
                pass

        # Stream ended — queue logging
        response_text = "".join(collected)
        self._worker.enqueue({
            "type": "ingest",
            "prompt_hash": self._prompt_hash,
            "prompt_text": self._prompt_text,
            "response_text": response_text,
            "model": self._model,
            "latency_ms": self._latency_ms,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "is_golden": self._is_golden,
        })
        self._probe_runner.maybe_fire(self._model)

    # Support `with client.chat.completions.create(stream=True) as stream:`
    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self._stream.__exit__(*args)
        except Exception:
            pass

    def __getattr__(self, name):
        return getattr(self._stream, name)
