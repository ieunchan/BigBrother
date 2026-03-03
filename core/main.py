import sys
import cv2
import atexit
import threading
from auth.face_detector import capture_face_for_verification
from auth.face_embedder import embed_face_rgb
from auth.face_verifier import is_owner
from monitor.app_monitor import start_app_monitor
from monitor.file_monitor import start_file_monitor
from monitor.key_monitor import start_key_monitor
from monitor.key_monitor import reconstruct_logs

def start_monitoring():
    # 키보드 추적 활성화
    key_thread = threading.Thread(target=start_key_monitor, daemon=True)
    key_thread.start()
    # 파일 추적 활성화
    file_thread = threading.Thread(target=start_file_monitor, daemon=True)
    file_thread.start()
    # 앱 사용 추적 활성화
    start_app_monitor()

if __name__ == '__main__':
    try:
        print("[SYSTEM] Face verification started...")
        atexit.register(reconstruct_logs)
        face_bgr = capture_face_for_verification()
        if face_bgr is None:
            print("[SYSTEM] No face detected. Exiting.")
            sys.exit(0)
        face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        # 현재 사용자 임베딩 생성
        current_embedding = embed_face_rgb(face_rgb)
        if is_owner(current_embedding):
            print("[SYSTEM] Owner Detected. Exiting the Process.")
            sys.exit(0)
        print("[SYSTEM] Unauthorized User Detected. Activating Monitor.")
        start_monitoring()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Monitor stopped manually.")
        sys.exit(0)