# BigBrother

나를 제외한 다른 유저가 내 컴퓨터 혹은 노트북 사용을 감지할 시 사용자의 사진과 사용로그를 기록합니다.
로그인 이후 **웹캠을 통해 현재 사용자의 얼굴을 감지**하고,  
추후 **기기 주인 여부를 판단**하는 것을 목표로 합니다.

---

## 프로젝트 개요

- MediaPipe **Tasks API** 기반 얼굴 감지(Face Detection) PoC
- MacBook 내장 웹캠 사용
- Solutions API가 아닌 **최신 Tasks API** 사용
- 자동 모델 로딩이 아닌 **모델 파일 직접 관리 방식**

---

## 기술 스택

- Python
- OpenCV
- MediaPipe (Tasks API)

---

## 현재 구현 상태

- [x] MediaPipe FaceDetector 설정 및 초기화
- [x] 얼굴 감지 모델(`face_detector.task`) 로컬 로딩
- [x] 웹캠 프레임 캡쳐
- [x] OpenCV → MediaPipe 이미지 변환
- [x] 얼굴 감지 결과(`detection_result`) 획득

---
