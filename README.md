![다운로드](https://github.com/user-attachments/assets/a61ba78b-643e-406b-ba8b-fec723ed9703)

# BigBrother

나를 제외한 다른 유저가 내 컴퓨터 혹은 노트북 사용을 감지할 시 사용자의 사진과 사용로그를 기록합니다.
로그인 이후 **웹캠을 통해 현재 사용자의 얼굴을 감지**하고,  
추후 **기기 주인 여부를 판단**하는 것을 목표로 합니다.

---

## 프로젝트 개요

- MediaPipe **Tasks API** 기반 얼굴 감지(Face Detection)
- MacBook 내장 웹캠 사용
- Solutions API가 아닌 **최신 Tasks API** 사용

---

## 기술 스택

- Python
- OpenCV
- MediaPipe (Tasks API)
- MediaPipe (ImageEmbedder)

---

## 얼굴 임베딩 (Face Embedding)

- MediaPipe **Image Embedder(Task API)** 사용
- 얼굴 이미지를 고정 차원 벡터(현재 1024차원)로 변환
- 로그인 시 1회 실행을 목표로 한 **함수형 임베딩 구조** 채택

## Owner Embedding 전략

- `data/owner_faces/` 폴더에 여러 장(여러 각도, 안경 유/무)의 주인 얼굴 이미지 저장
- 각 이미지를 얼굴 임베딩 벡터로 변환
- 모든 임베딩의 **평균값(mean vector)**을 계산하여 `owner_embedding` 생성
- 비교는 항상  
  **현재 사용자 임베딩 ↔ owner_embedding** 구조로 수행

> owner_faces 내부 이미지끼리 비교하지 않음

## 현재 구현 상태

- [x] MediaPipe FaceDetector (Tasks API) 초기화
- [x] MacBook 웹캠 프레임 캡쳐
- [x] 얼굴 감지 및 bounding box 추출
- [x] 얼굴 이미지 crop 및 로컬 저장
- [x] MediaPipe Image Embedder 적용
- [x] 얼굴 임베딩 벡터 생성 (1024-dim)
- [x] 임베딩 테스트 및 결과 로그(txt) 저장

---
  
## 다음 단계

- [ ] owner_faces 전체 임베딩 → 평균 owner_embedding 생성
- [ ] 로그인 시 캡쳐된 얼굴 임베딩과 owner_embedding 비교
- [ ] cosine similarity 기반 threshold 설정
- [ ] 주인/비주인 판단 로직 구현
- [ ] macOS 로그인 트리거(launchd) 연동
