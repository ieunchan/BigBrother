import cv2
from face_logics.face_embedder import embed_face_rgb

IMAGE_PATH = 'data/owner_faces/face_20260130_0116.jpg'

bgr = cv2.imread(IMAGE_PATH)
# 이미지가 존재하는지 확인
if bgr is None:
    raise ValueError('이미지가 존재하지 않음')

# 이미지 형식을 변환 cv2는 BGR, 미디어파이프는 RGB
rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

# 임베딩 테스트
embedding = embed_face_rgb(rgb)
OUTPUT_PATH = 'test.txt'

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(f"임베딩 타입: {type(embedding)}\n")
    f.write('-' * 40 + '\n')
    f.write(f"임베딩 쉐입: {embedding.shape}\n")
    f.write('-' * 40 + '\n')
    f.write(f"임베딩 결과\n")
    f.write(str(embedding))