import time
import os
from statistics import Counter
import RPi.GPIO as GPIO
from hx711 import HX711
from record_video import record_video_mp4
from detect_person import analyze_video_for_person

#핀 설정 및 저울 오프셋 설정
hx = HX711(dout_pin = 5, pd_sck_pin = 6)
GPIO.setmode(GPIO.BCM)
buzzer = 21
is_blinded = 17
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(is_blinded, GPIO.IN)
offset_data = hx.get_raw_data(times = 10)
offset = sum(offset_data)/len(offset_data)

def get_weight():
    return (sum(hx.get_raw_data(times=3))/3 - offset)/100



#초기값 설정
weight_last5 = [] #queue
for _ in range(5):
    weight_last5.append(int(get_weight()))
count = Counter(weight_last5) # 각 무게의 빈도수 확인
weight_mode = count.most_common(1)[0][0] # 최빈값 저장
GPIO.output(buzzer, GPIO.LOW)

print("start")

try:
    while(1):
        hx.reset()
        if GPIO.input(is_blinded) == GPIO.LOW: 
            print("카메라 가려짐!")
            GPIO.output(buzzer, GPIO.HIGH)
        elif GPIO.input(is_blinded) == GPIO.HIGH: 
            GPIO.output(buzzer, GPIO.LOW)
            
        #queue update
        weight_last5.pop(0)
        weight_last5.append(int(get_weight()))
        
        count_tmp = Counter(weight_last5)
        weight_tmp = count_tmp.most_common(1)[0][0] # weight_mode 변수는 이전값으로 취급
        
        print("data: ", weight_last5[-1])
        
        if weight_tmp + 10 < weight_mode:
            #recording
            filename_tmp = record_video_mp4(duration = 3, folder = "videos")
            #detect person
            if analyze_video_for_person(filename_tmp) :
                #notification
                GPIO.output(buzzer, GPIO.HIGH)
                print("도난 발생!")
                time.sleep(1)
                GPIO.output(buzzer, GPIO.LOW)
            else:
                os.remove(filename_tmp)
            
        weight_mode = weight_tmp
        
except KeyboardInterrupt:
    print("end")
finally:
    hx.power_down()
    GPIO.cleanup()

