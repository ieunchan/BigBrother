![다운로드](https://github.com/user-attachments/assets/a61ba78b-643e-406b-ba8b-fec723ed9703)

# BigBrother

**기기 주인이 아닌 사용자의 컴퓨터 사용을 감지하고 기록하는 개인 보안 모니터링 도구**

BigBrother는  
로그인 이후 **웹캠 기반 얼굴 인식**과  
**파일 시스템 상태 변화 감시**를 결합하여  
기기 주인이 아닌 사용자의 **접근 및 사용 흔적을 기록**하는 것을 목표로 합니다.

---

## 프로젝트 개요

- MediaPipe **Tasks API** 기반 얼굴 감지 및 임베딩
- MacBook 내장 웹캠 사용
- macOS에서 파일 “열람” 이벤트를 직접 감지할 수 없는 한계를 고려하여  
  **스냅샷 + diff 기반 접근 추론 방식** 채택
- 키 입력 로깅(Key Logging) 및 파일 접근 흔적 수집
- Solutions API가 아닌 **최신 MediaPipe Tasks API** 사용

---

## 기술 스택

- Python
- OpenCV
- MediaPipe (Tasks API)
- MediaPipe (Image Embedder)
- macOS Spotlight (`mdls`)
- pynput (Keyboard Listener)
- python-decouple (.env 기반 설정 관리)

---

## 얼굴 감지 & 임베딩 (Face Embedding)

- MediaPipe **Image Embedder (Tasks API)** 사용
- 얼굴 이미지를 고정 차원 벡터(현재 1024차원)로 변환
- 로그인 시 1회 실행을 목표로 한 **함수형 임베딩 구조**
- 얼굴 bounding box 기준 crop 후 임베딩 수행

---

## Owner Embedding 전략

- `data/owner_faces/` 폴더에 여러 장의 주인 얼굴 이미지 저장  
  (여러 각도, 안경 유/무 등)
- 각 이미지를 얼굴 임베딩 벡터로 변환
- 모든 임베딩의 **평균값(mean vector)**을 계산하여 `owner_embedding` 생성
- 비교는 항상  
  **현재 사용자 임베딩 ↔ owner_embedding** 구조로 수행

> owner_faces 내부 이미지끼리의 비교는 수행하지 않음

---

## 키보드 입력 감시 (Key Logging)

- `pynput` 기반 키 입력 감지
- 키 입력을 **Raw Log 형태로 저장**
- 특수 키(Enter, Backspace, Cmd 조합 등) 처리
- 입력 흐름을 재구성할 수 있도록 로그 구조 설계
- macOS 접근성 권한 필요

> 키 로깅은 실제 텍스트 복원이 아닌  
> **사용 행위 존재 여부 및 패턴 파악**을 목적으로 함

---

## 파일 시스템 감시 (Snapshot-based Monitoring)

macOS에서는 파일 “열람” 이벤트를 실시간으로 직접 추적하기 어렵기 때문에  
**파일 시스템 상태를 주기적으로 기록하고 비교하는 방식**을 사용합니다.

---

### 스냅샷이란?

특정 시점의 파일 시스템 상태를 기록한 데이터입니다.

- `mdls (kMDItemLastUsedDate)` 기반 파일 사용 시점 수집
- 불필요한 시스템/개발 디렉토리 제외
- macOS 패키지(.app, .framework 등)는 **최상위 항목만 기록**

~~~json
{
  "snapshot_time": "...",
  "items": {
    "/Users/.../report.pdf": "2026-02-09 08:57:01 +0000",
    "/Applications/Chrome.app": "2026-02-09 09:12:44 +0000"
  }
}
~~~

---

### 스냅샷 운용 방식

- **Baseline Snapshot**
  - 주인 로그인 시 **1회 생성**
  - 정상 상태 기준선

- **Monitoring Snapshot**
  - 주기적으로 생성
  - **직전 스냅샷(previous)** 과 diff 비교

> 스냅샷은 누적 저장하지 않으며  
> **baseline + previous 상태만 유지**

---

### 파일 접근 추론 기준

다음 중 하나라도 발생하면  
**파일 접근 또는 사용이 있었던 것으로 추론**

- 파일 생성
- 파일 삭제
- `LastUsedDate` 변경

---

## 설정 관리 (Config)

- `.env` 파일 기반 설정 관리
- `python-decouple` 사용
- 개인 경로 및 민감 정보는 코드에 포함하지 않음

~~~env
MAIN_DIR=/Users/username/Desktop
SNAPSHOT_FILE=snapshot.json
~~~

---
