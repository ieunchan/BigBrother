import cv2
import os
import mediapipe as mp
from datetime import datetime
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# STEP 1: 
CAPTURE_DIR = "captures"
MODEL_PATH = "face_detector.task"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Face Detector 옵션
BaseOptions = python.BaseOptions
FaceDetector = vision.FaceDetector
FaceDetectorOptions = vision.FaceDetectorOptions
VisionRunningMode = vision.RunningMode

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    min_detection_confidence=0.6,
)
detector = FaceDetector.create_from_options(options)

# 웹캠에서 프레임 1장 캡쳐
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Unable to open the Camera")
ret, frame = cap.read()
cap.release()
if not ret:
    raise RuntimeError("Capture Frame Failed")
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


# 이미지 생성
image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

detection_result = detector.detect(image)
print(detection_result)