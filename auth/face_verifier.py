import numpy as np
from pathlib import Path
from decouple import config

OWNER_EMBEDDING_OUTPUT = Path(config('OWNER_EMBEDDING_OUTPUT'))
THRESHOLD = 0.62


def cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
    numerator = np.dot(vector1, vector2)
    denominator = np.linalg.norm(vector1) * np.linalg.norm(vector2)

    if denominator == 0:
        return 0.0
    return float(numerator / denominator)

def is_owner(current_embedding: np.ndarray) -> bool:
    if not OWNER_EMBEDDING_OUTPUT.exists():
        raise FileNotFoundError('no embedding data')
    owner_embedding = np.load(OWNER_EMBEDDING_OUTPUT)
    similarity = cosine_similarity(owner_embedding, current_embedding)
    print(f'[VERIFY] Similarity: {similarity:.4f}')
    return similarity >= THRESHOLD