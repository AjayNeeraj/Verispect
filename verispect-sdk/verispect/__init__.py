"""
Verispect SDK
=============
AI drift detection and compliance monitoring.
Wraps any OpenAI-compatible client with one line.

Usage:
    from openai import OpenAI
    from verispect import wrap

    client = wrap(
        OpenAI(api_key="sk-..."),
        verispect_key="vs_live_abc123"
    )

    # Use exactly as before — nothing else changes
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}]
    )
"""

from .wrapper import VerispectWrapper


def wrap(
    client,
    verispect_key: str,
    endpoint: str = "https://verispectai.com",
    probe_rate: float = 0.02,
    golden_rate: float = 0.02,
) -> VerispectWrapper:
    """
    Wrap an OpenAI-compatible client with Verispect monitoring.

    Args:
        client:         An initialized OpenAI (or compatible) client instance.
        verispect_key:  Your Verispect API key (from verispectai.com/dashboard).
        endpoint:       Verispect server URL. Defaults to https://verispectai.com.
        probe_rate:     Fraction of calls that trigger a canary probe (default 0.02 = 2%).
        golden_rate:    Fraction of calls sampled as golden behavioral probes (default 0.02 = 2%).

    Returns:
        A wrapped client with an identical interface to the original.
        All calls still go directly to OpenAI — Verispect only observes.

    Privacy guarantee:
        Raw prompt text NEVER leaves your machine.
        Only SHA-256 hashes and response embeddings (mathematical vectors)
        are sent to the Verispect server.
    """
    return VerispectWrapper(
        client=client,
        verispect_key=verispect_key,
        endpoint=endpoint,
        probe_rate=probe_rate,
        golden_rate=golden_rate,
    )


__all__ = ["wrap", "VerispectWrapper"]
__version__ = "0.1.0"
