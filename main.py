import time
import statics
import RPi.GPIO as GPIO
from hx711 import HX711

#핀 설정 및 저울 오프셋 설정
hx = HX711(dout_pin = 5, pd_sck_pin = 6)
GPIO.setmode(GPIO.BCM)
buzzer = 21
GPIO.setup(buzzer, GPIO.OUT)
offset_data = hx.get_raw_data(times = 30)
offset = sum(offset_data)/len(offset_data)정

def get_weight():
    return (sum(hx.get_raw_data())/5 - offset)/100

weight_last5 = [] #queue

#초기값 설정
for _ in range(5):
    weight_last5.append(int(get_weight()))
count = Counter(weight_last5) # 각 수의 빈도수 확인
weight_mode = count.most_common(1) # 최빈값 저장

print("start")

try:
    while(1):
        hx.reset()
        #queue update
        weight_last5.pop(0)
        weight_last5.append(int(get_weight())
        
        count_tmp = Counter(weight_last5)
        weight_tmp = count_tmp.most_common(1) # weight_mode 변수는 이전값으로 취급
        
        print("data: ", weight_last5[-1])
        
        if weight_tmp + 10 < weight_mod:
            GPIO.output(buzzer, GPIO.HIGH)
            print("도난 발생!")
            time.sleep(5)
            GPIO.output(buzzer, GPIO.LOW)
            
        weight_mode = weight_tmp
        
except KeyboardInterrupt:
    print("end")
finally:
    hx.power_down()            
    GPIO.cleanup()

