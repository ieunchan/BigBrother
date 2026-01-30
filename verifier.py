import numpy as np

def cosine_similarity(vector1: np.ndarray, vector2: np.ndarray) -> float:
    numerator = np.dot(vector1, vector2)
    denominator = np.linalg.norm(vector1) * np.linalg.norm(vector2)

    if denominator == 0:
        return 0.0
    return float(numerator / denominator)