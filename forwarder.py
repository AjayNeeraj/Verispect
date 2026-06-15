import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ── Multi-provider routing ────────────────────────────────────────────────────
# Every provider below exposes an OpenAI-compatible /chat/completions endpoint,
# so the same request/response shape (and the same probe library) works across all.
# Pick the target by: body["provider"]  →  else infer from the model name  →  else OpenAI.
PROVIDER_URLS = {
    "openai":     "https://api.openai.com/v1/chat/completions",
    "anthropic":  "https://api.anthropic.com/v1/chat/completions",       # OpenAI-compat layer
    "gemini":     "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "perplexity": "https://api.perplexity.ai/chat/completions",
    "xai":        "https://api.x.ai/v1/chat/completions",                # Grok
    "mistral":    "https://api.mistral.ai/v1/chat/completions",
    "deepseek":   "https://api.deepseek.com/v1/chat/completions",
    "groq":       "https://api.groq.com/openai/v1/chat/completions",
}

# Model-name prefixes → provider (used when body has no explicit "provider").
_MODEL_HINTS = [
    ("claude",   "anthropic"),
    ("gemini",   "gemini"),
    ("grok",     "xai"),
    ("sonar",    "perplexity"),
    ("mistral",  "mistral"), ("mixtral", "mistral"), ("ministral", "mistral"), ("magistral", "mistral"),
    ("deepseek", "deepseek"),
    ("gpt",      "openai"), ("o1", "openai"), ("o3", "openai"), ("o4", "openai"), ("chatgpt", "openai"),
]


def resolve_provider(body: dict) -> str:
    p = (body.get("provider") or "").strip().lower()
    if p in PROVIDER_URLS:
        return p
    model = (body.get("model") or "").lower()
    for prefix, prov in _MODEL_HINTS:
        if model.startswith(prefix) or prefix in model:
            return prov
    return "openai"


def _target(body: dict):
    """Return (url, body_without_internal_fields). Strips our 'provider' field before forwarding."""
    provider = resolve_provider(body)
    url = PROVIDER_URLS[provider]
    if "provider" in body:
        body = {k: v for k, v in body.items() if k != "provider"}
    return url, body


async def forward_to_openai(body: dict, auth_header: str) -> dict:
    """Non-streaming. Name kept for backward compatibility — now routes to any provider."""
    url, body = _target(body)
    headers = {
        "Authorization": auth_header or f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()


async def stream_openai(body: dict, auth_header: str):
    """
    Streaming async generator (OpenAI-compatible SSE) — routes to any provider.
    Forwards each SSE line to the client immediately and collects delta.content
    fragments into parsed_fragments for post-stream reassembly.
    """
    url, body = _target(body)
    headers = {
        "Authorization": auth_header or f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    parsed_fragments = []

    async def _gen():
        nonlocal parsed_fragments
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=body, headers=headers) as resp:
                resp.raise_for_status()

                event_lines = []

                async for line in resp.aiter_lines():
                    if line is None:
                        continue

                    try:
                        yield (line + "\n").encode("utf-8")
                    except Exception:
                        pass

                    if line == "":
                        for ev in event_lines:
                            if ev.startswith("data:"):
                                payload = ev[len("data:"):].strip()
                                if payload == "[DONE]":
                                    return
                                try:
                                    obj = json.loads(payload)
                                    choices = obj.get("choices", [])
                                    if choices:
                                        delta = choices[0].get("delta", {})
                                        content_piece = delta.get("content")
                                        if content_piece:
                                            parsed_fragments.append(content_piece)
                                except Exception:
                                    pass
                        event_lines = []
                    else:
                        event_lines.append(line)

                if event_lines:
                    for ev in event_lines:
                        if ev.startswith("data:"):
                            payload = ev[len("data:"):].strip()
                            if payload != "[DONE]":
                                try:
                                    obj = json.loads(payload)
                                    choices = obj.get("choices", [])
                                    if choices:
                                        delta = choices[0].get("delta", {})
                                        content_piece = delta.get("content")
                                        if content_piece:
                                            parsed_fragments.append(content_piece)
                                except Exception:
                                    pass

    gen = _gen()
    gen.parsed_fragments = parsed_fragments
    return gen
