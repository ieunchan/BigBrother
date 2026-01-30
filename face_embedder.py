import os
import cv2
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

# 주인 얼굴의 평균 벡터값
def build_owner_embedding(
        owner_faces_dir: str = 'data/owner_faces', 
        output_path: str = 'data/owner_embedding.npy'
    ):
    # data/owner_faces의 파일들을 임베딩 -> 각 벡터값들의 평균벡터 추출
    embeddings = []
    for file in os.listdir(owner_faces_dir):
        if not file.lower().endswith(('.jpg', '.jpeg')):
            continue
        image_path = os.path.join(owner_faces_dir, file)
        bgr_image = cv2.imread(image_path)

        if bgr_image is None:
            print(f"[WARNING] Fail to load Image: {file}")
            continue
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        embedding = embed_face_rgb(rgb_image)

        if embedding is None or embedding.size == 0:
            print(f"[WARNING] Fail to embed image: {file}")
        embeddings.append(embedding)
        print(f"[SUCCESS] Embedding Completed: {file}")

    owner_embeddings = np.mean(embeddings, axis=0)
    np.save(output_path, owner_embeddings)
    






