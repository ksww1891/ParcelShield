# record_video.py
import time
import os
import threading
from collections import deque

import cv2
from picamera2 import Picamera2

# ====================================
# 설정값
# ====================================
FPS = 20
PRE_EVENT_SEC = 8
POST_EVENT_SEC = 5
BUFFER_SEC = 15

VIDEO_FOLDER = "videos"
os.makedirs(VIDEO_FOLDER, exist_ok=True)

# ====================================
# 전역 변수: 카메라 & 버퍼
# ====================================
frame_buffer = deque()        # (timestamp, frame)
buffer_lock = threading.Lock()
camera_running = False
camera_thread = None
picam2 = None


# ====================================
# 카메라 스레드: 프레임 버퍼 저장
# ====================================
def camera_loop():
    global frame_buffer, camera_running

    print("[record_video] 카메라 스레드 시작")

    while camera_running:
        frame = picam2.capture_array()   # RGB888 프레임
        now = time.time()

        with buffer_lock:
            frame_buffer.append((now, frame.copy()))

            # 오래된 프레임 자동 제거
            cutoff = now - BUFFER_SEC
            while frame_buffer and frame_buffer[0][0] < cutoff:
                frame_buffer.popleft()

        time.sleep(1.0 / FPS * 0.5)

    print("[record_video] 카메라 스레드 종료")


# ====================================
# 카메라 시작 함수 (main에서 호출)
# ====================================
def start_camera():
    global picam2, camera_running, camera_thread

    if camera_running:
        return  # 이미 실행 중

    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": (1280, 720), "format": "RGB888"}
    )
    picam2.configure(config)
    picam2.start()

    camera_running = True
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()

    print("[record_video] 카메라 시작됨")


# ====================================
# 카메라 종료 함수 (main 종료 시 호출)
# ====================================
def stop_camera():
    global camera_running

    if not camera_running:
        return

    camera_running = False
    time.sleep(0.5)

    if picam2:
        picam2.stop()
        picam2.close()

    print("[record_video] 카메라 종료됨")


# ====================================
# 이벤트 전후 영상 저장 함수
# ====================================
def save_event_clip(event_time, pre_sec=PRE_EVENT_SEC, post_sec=POST_EVENT_SEC):
    """
    event_time 기준으로 [전 pre_sec 초 ~ 후 post_sec 초]의 프레임을 모아
    mp4로 저장하고 파일명을 반환.
    """
    global frame_buffer

    # 이벤트 후 영상 확보 위해 기다리기
    time.sleep(post_sec)

    with buffer_lock:
        snapshot = list(frame_buffer)

    # 구간 지정
    start_t = event_time - pre_sec
    end_t = event_time + post_sec

    selected = [(t, f) for (t, f) in snapshot if start_t <= t <= end_t]

    print(f"[record_video] 선택된 프레임 수: {len(selected)}")

    if not selected:
        print("[record_video] 선택된 프레임 없음 → 저장하지 않음")
        return None

    # 첫 프레임 해상도로 VideoWriter 생성
    _, first_frame = selected[0]
    h, w, _ = first_frame.shape

    ts = time.strftime("%Y%m%d_%H%M%S", time.localtime(event_time))
    filename = os.path.join(VIDEO_FOLDER, f"event_{ts}.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, FPS, (w, h))

    if not out.isOpened():
        print("[record_video] VideoWriter 열기 실패")
        return None

    for (_, frame) in selected:
        out.write(frame)

    out.release()
    print(f"[record_video] 저장 완료: {filename}")

    return filename
