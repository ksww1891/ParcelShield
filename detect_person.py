# detect_person.py
from ultralytics import YOLO
import cv2

# 1. YOLO 모델 로드 (COCO 기반, class 0: person)
model = YOLO("yolov8n.pt")  # 처음에는 자동으로 모델 파일 다운로드됨

def analyze_video_for_person(video_path, conf_thres=0.5):
    """
    video_path: 분석할 mp4 파일 경로
    conf_thres: YOLO confidence threshold (기본 0.5)
    """

    cap = cv2.VideoCapture(video_path)
    person_flag = False
    if not cap.isOpened():
        print(f"영상 파일을 열 수 없습니다: {video_path}")
        return

    frame_idx = 0

    print(f"[분석 시작] {video_path}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 더 이상 프레임 없음

        frame_idx += 1
        if frame_idx % 10 != 0 : continue
        # 2. 이 프레임에 대해 YOLO 한 번 실행
        results = model.predict(frame, conf=conf_thres, verbose=False)

        person_found = False

        for r in results:
            # r.boxes에 탐지된 객체들이 들어 있음
            for box in r.boxes:
                cls_id = int(box.cls[0])         # 클래스 인덱스
                cls_name = model.names[cls_id]   # 예: 'person', 'car', ...

                if cls_name == "person":
                    person_found = True
                    break

            if person_found:
                break

        # 3. 결과 출력 (필요하면 다른 로직으로 바꿔도 됨)
        if person_found:
            print(f"프레임 {frame_idx}: 사람 O")
            person_flag = True
        else:
            print(f"프레임 {frame_idx}: 사람 X")

    cap.release()
    print(f"[분석 완료] 총 {frame_idx/10}개 프레임 검사")
    return person_flag
