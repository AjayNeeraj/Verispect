"""
embedder.py
Computes sentence embeddings LOCALLY using all-MiniLM-L6-v2.

PRIVACY: This module runs entirely on the client's machine.
Raw text is NEVER sent to the Verispect server.
Only the resulting 384-float vector is transmitted.

The model is loaded lazily on first use (~30MB, cached by sentence-transformers).
"""

import logging
from typing import List

logger = logging.getLogger("verispect")

_model = None
_model_load_failed = False  # Avoid retrying after a permanent failure

# Cap text length before embedding to keep latency low
_MAX_CHARS = 2000


def get_model():
    global _model, _model_load_failed

    if _model is not None:
        return _model

    if _model_load_failed:
        return None

    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.debug("Verispect: embedding model loaded.")
        return _model
    except ImportError:
        _model_load_failed = True
        logger.warning(
            "Verispect: sentence-transformers not installed. "
            "Drift scoring disabled. "
            "Install with: pip install sentence-transformers"
        )
    except Exception as e:
        _model_load_failed = True
        logger.warning(f"Verispect: failed to load embedding model: {e}")

    return None


def compute_embedding(text: str) -> List[float]:
    """
    Returns a list of 384 floats representing the semantic embedding of `text`.
    Returns an empty list if the model is unavailable — callers must handle this.
    """
    if not text or not text.strip():
        return []

    model = get_model()
    if model is None:
        return []

    try:
        truncated = text[:_MAX_CHARS]
        vector = model.encode([truncated], show_progress_bar=False)[0]
        return [round(float(x), 6) for x in vector]
    except Exception as e:
        logger.debug(f"Verispect: embedding computation failed: {e}")
        return []
