# yolo_picamera2_live_skip.py
# Pi 5 + Camera Module 3 + Picamera2 + YOLO (추론 프레임 스킵)
from picamera2 import Picamera2
import cv2
from ultralytics import YOLO
import time

MODEL_PATH = "yolov8n.pt"      # 또는 "yolo11n.pt"
CONF = 0.5                     # 신뢰도 임계값
PERSON_CLASS_ID = 0            # COCO 'person'
IM_SIZE = (640, 480)           # 카메라 출력 해상도 (빠르게 하려면 (320,240) 추천)
IMGSZ = 320                    # YOLO 내부 입력 크기(작게 할수록 빠름: 256/320/416/640 등)

INFER_EVERY_N = 3              # N프레임마다 1회만 추론
SHOW_FPS = True

def main():
    # Picamera2 설정
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": IM_SIZE, "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(0.2)

    # YOLO 로드
    model = YOLO(MODEL_PATH)

    print("✅ YOLO live (skip inference) start — ESC로 종료")
    frame_count = 0
    last_boxes = []   # 직전 추론 결과 캐시 [(x1,y1,x2,y2,conf), ...]
    last_time = time.time()
    fps = 0.0

    while True:
        frame = picam2.capture_array()  # RGB (H,W,3)

        # 매 N프레임마다만 추론
        do_infer = (frame_count % INFER_EVERY_N == 0)
        if do_infer:
            results = model.predict(
                source=frame,
                conf=CONF,
                classes=[PERSON_CLASS_ID],
                imgsz=IMGSZ,
                verbose=False
            )
            r = results[0]
            last_boxes = []
            if r.boxes is not None and len(r.boxes) > 0:
                for b in r.boxes:
                    x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                    conf = float(b.conf[0])
                    last_boxes.append((x1, y1, x2, y2, conf))

        # 현재 프레임에 직전(혹은 방금) 결과 박스 그리기
        for (x1, y1, x2, y2, conf) in last_boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, f"person {conf:.2f}", (x1, max(0, y1-6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
# FPS 표시
        if SHOW_FPS:
            now = time.time()
            if now - last_time > 0:
                fps = 1.0 / (now - last_time)
            last_time = now
            cv2.putText(frame, f"FPS: {fps:.1f} (infer/ {INFER_EVERY_N}f, imgsz={IMGSZ})",
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        cv2.imshow("YOLO + Picamera2 (person, skip)", frame)
        frame_count += 1

        if cv2.waitKey(1) == 27:  # ESC
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
