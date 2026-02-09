import cv2
import os
import mediapipe as mp
from datetime import datetime
from decouple import config
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# STEP 1: 
OWNER_DIR = config("OWNER_DIR")
MODEL_PATH = config("FACE_DETECTOR_MODEL")
os.makedirs(OWNER_DIR, exist_ok=True)

def create_detector():
    BaseOptions = python.BaseOptions
    FaceDetector = vision.FaceDetector
    FaceDetectorOptions = vision.FaceDetectorOptions
    VisionRunningMode = vision.RunningMode

    options = FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.IMAGE,
        min_detection_confidence=0.3,
    )
    return FaceDetector.create_from_options(options)

def capture_frame():
    cap = cv2.VideoCapture(0)
    for _ in range(10):
        cap.read()
    if not cap.isOpened():
        raise RuntimeError("Unable to open the Camera")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("Fail to capture the Frame")
    return frame

def detect_and_save_owner_face(detector, frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    detection_result = detector.detect(image)
    print(detection_result)

    if detection_result.detections:
        detection = detection_result.detections[0]
        bbox = detection.bounding_box

        x = bbox.origin_x
        y = bbox.origin_y
        w = bbox.width
        h = bbox.height

        face_img = frame[y:y+h, x:x+w]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        save_path = os.path.join(OWNER_DIR, f"face_{timestamp}.jpg")

        cv2.imwrite(save_path, face_img)
        print("Saved:", save_path)
        return save_path
    else:
        print("No face detected")
        return None

def run_capture_and_save():
    detector = create_detector()
    frame = capture_frame()
    return detect_and_save_owner_face(detector, frame)

if __name__ == "__main__":
    run_capture_and_save()