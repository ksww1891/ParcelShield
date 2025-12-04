# main.py
import time
import os
from collections import Counter

import RPi.GPIO as GPIO
from hx711 import HX711

from record_video import start_camera, stop_camera, save_event_clip
from detect_person import analyze_video_for_person

hx = HX711(dout_pin=5, pd_sck_pin=6)

GPIO.setmode(GPIO.BCM)

buzzer = 21         # 부저 핀
is_blinded = 17     # 카메라 가려짐 센서 핀

GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(is_blinded, GPIO.IN)

# 저울 오프셋 측정
offset_data = hx.get_raw_data(times=10)
offset = sum(offset_data) / len(offset_data)

def get_weight():
    raw = sum(hx.get_raw_data(times=3)) / 3
    return (raw - offset) / 100

GPIO.output(buzzer, GPIO.LOW)

# ==========================
# 초기 weight 큐 설정
# ==========================
weight_last5 = []
for _ in range(5):
    weight_last5.append(int(get_weight()))

count = Counter(weight_last5)
weight_mode = count.most_common(1)[0][0]

print("start")

start_camera()
try:
    while True:
        hx.reset()

        # 카메라 가려짐 체크
        if GPIO.input(is_blinded) == GPIO.LOW:
            print("카메라 가려짐!")
            GPIO.output(buzzer, GPIO.HIGH)
        else:
            GPIO.output(buzzer, GPIO.LOW)

        # 무게 측정 및 큐 업데이트
        current_weight = int(get_weight())
        weight_last5.pop(0)
        weight_last5.append(current_weight)

        count_tmp = Counter(weight_last5)
        weight_tmp = count_tmp.most_common(1)[0][0]  # 현재 최빈값

        print("data:", weight_last5[-1], "mode:", weight_tmp)

        # 무게 감소 감지 (임계값 10, 필요하면 조정)
        if weight_tmp + 10 < weight_mode or GPIO.input(is_blinded) == GPIO.LOW:
            event_time = time.time()
            print("[이벤트] 무게 감소 감지! event_time =", event_time)

            # 버퍼에 들어있는 "이벤트 전후 5초" 영상을 하나의 파일로 저장
            clip_path = save_event_clip(event_time)

            if clip_path is not None:
                # 사람 인식
                if analyze_video_for_person(clip_path):
                    GPIO.output(buzzer, GPIO.HIGH)
                    print("도난 발생! (사람 인지)")
                    time.sleep(1)
                    GPIO.output(buzzer, GPIO.LOW)
                else:
                    print("사람 미검출, 파일 삭제:", clip_path)
                    os.remove(clip_path)

        # 기준 최빈값 업데이트
        weight_mode = weight_tmp

        # 루프 속도 조절
        time.sleep(0.1)

except KeyboardInterrupt:
    print("end")

finally:
    stop_camera()
    hx.power_down()
    GPIO.cleanup()
    print("GPIO cleanup 및 종료 완료")
