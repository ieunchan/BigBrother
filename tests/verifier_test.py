import os
import cv2
import numpy as np
from face_logics.face_embedder import embed_face_rgb
from face_logics.face_detector import run_capture_and_save
from face_logics.verifier import cosine_similarity

# TEST_IMAGE_PATH = 'data/owner_faces'
OWNER_EMBEDDING_PATH = 'data/owner_embedding.npy'

owner_embedding = np.load(OWNER_EMBEDDING_PATH)

# images = [
    # face for face in os.listdir(TEST_IMAGE_PATH)
    # if face.lower().endswith(("jpg", "jpeg", "png"))
# ]


print("========== 유사도 측정 테스트 ==========")

images = run_capture_and_save()

print(f"\n[TEST] 사용중인 이미지: {images}")

bgr_image = cv2.imread(images)
if bgr_image is None:
    print("이미지 로드 실패")

rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

current_embedding = embed_face_rgb(rgb_image)
similarity = cosine_similarity(current_embedding, owner_embedding)

print(f"  임베딩 쉐입: {current_embedding.shape}")
print(f"Cosine Similarity: {similarity * 100:.2f}%")

os.remove(images)