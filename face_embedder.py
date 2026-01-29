import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

def embed_face_rgb(face_rgb):
    np.set_printoptions(threshold=np.inf)

    MODEL_PATH = "models/mobilenet_v3_small_075_224_embedder.tflite"
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.ImageEmbedderOptions(
        base_options=base_options, l2_normalize=True, quantize=False
    )

    with vision.ImageEmbedder.create_from_options(options) as embedder:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=face_rgb)
        result = embedder.embed(mp_image)

        embedding = result.embeddings[0].embedding
        return np.array(embedding)
