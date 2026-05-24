from sentence_transformers import SentenceTransformer
import numpy as np

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