import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


async def forward_to_openai(body: dict, auth_header: str) -> dict:
    # existing non-streaming behavior: POST and return parsed JSON
    headers = {
        "Authorization": auth_header or f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENAI_URL, json=body, headers=headers)
        response.raise_for_status()
        return response.json()


async def stream_openai(body: dict, auth_header: str):
    """
    Simpler async generator: iterate OpenAI SSE by lines (text), forward each line
    immediately to the client as bytes, and collect `delta.content` fragments into
    parsed_fragments for reassembly after the stream completes.
    """
    headers = {
        "Authorization": auth_header or f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    parsed_fragments = []

    async def _gen():
        nonlocal parsed_fragments
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", OPENAI_URL, json=body, headers=headers) as resp:
                resp.raise_for_status()

                event_lines = []

                # Use aiter_lines for simpler SSE parsing (yields text lines without newline)
                async for line in resp.aiter_lines():
                    if line is None:
                        continue

                    # Forward the original line (with newline) to the downstream client
                    try:
                        yield (line + "\n").encode("utf-8")
                    except Exception:
                        # Best-effort: ignore encoding/yield errors to keep streaming stable
                        pass

                    # Accumulate lines to detect end-of-event (blank line)
                    if line == "":
                        # End of one SSE event -> process event_lines
                        for ev in event_lines:
                            if ev.startswith("data:"):
                                payload = ev[len("data:"):].strip()
                                if payload == "[DONE]":
                                    return
                                try:
                                    obj = json.loads(payload)
                                    choices = obj.get("choices", [])
                                    if choices:
                                        # prefer incremental delta content
                                        delta = choices[0].get("delta", {})
                                        content_piece = delta.get("content")
                                        if content_piece:
                                            parsed_fragments.append(content_piece)
                                except Exception:
                                    # ignore JSON/parse errors to keep streaming robust
                                    pass
                        event_lines = []
                    else:
                        event_lines.append(line)

                # If stream ends without explicit [DONE], process any remaining event
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