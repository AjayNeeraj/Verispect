from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def score_drift(baseline: str, new_response: str) -> dict:
    model = get_model()
    embeddings = model.encode([baseline, new_response])
    a, b = np.array(embeddings[0]), np.array(embeddings[1])
    similarity = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    drift_score = round(1.0 - similarity, 4)

    # Severity classification
    if similarity >= 0.90:
        severity = "none"
    elif similarity >= 0.82:
        severity = "low"
    elif similarity >= 0.70:
        severity = "medium"
    else:
        severity = "high"

    return {
        "similarity": round(similarity, 4),
        "drift_score": drift_score,
        "flagged": similarity < 0.82,
        "severity": severity
    }


def score_drift_from_embeddings(baseline: List[float], new: List[float]) -> dict:
    """
    Score drift between two pre-computed embedding vectors.
    Used for golden probe results where the server never has the raw text.
    """
    if not baseline or not new or len(baseline) != len(new):
        return {
            "similarity": None,
            "drift_score": None,
            "flagged": False,
            "severity": "unknown",
        }
    a = np.array(baseline, dtype=np.float32)
    b = np.array(new, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return {"similarity": 0.0, "drift_score": 1.0, "flagged": True, "severity": "high"}

    similarity = float(np.dot(a, b) / (norm_a * norm_b))
    drift_score = round(1.0 - similarity, 4)

    if similarity >= 0.90:
        severity = "none"
    elif similarity >= 0.82:
        severity = "low"
    elif similarity >= 0.70:
        severity = "medium"
    else:
        severity = "high"

    return {
        "similarity": round(similarity, 4),
        "drift_score": drift_score,
        "flagged": similarity < 0.82,
        "severity": severity,
    }