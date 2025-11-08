import time
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin = 5, pd_sck_pin = 6)
buzzer = 21

print("start")

offset_data = hx.get_raw_data(times = 30)
offset = sum(offset_data)/len(offset_data)
GPIO.setup(buzzer, GPIO.OUT)

reading = (sum(hx.get_raw_data())/5 - offset)/100 #이전값

try:
    while(1):
        hx.reset()
        reading_tmp = (sum(hx.get_raw_data())/5 - offset)/100
        print("data: ", reading_tmp)
        if(reading_tmp + 10 < reading):
            GPIO.output(buzzer, GPIO.HIGH)
            print("도난 발생!")
            time.sleep(5)
            GPIO.output(buzzer, GPIO.LOW)

        reading = reading_tmp
        
except KeyboardInterrupt:
    print("end")
finally:
    hx.power_down()            
    GPIO.cleanup()

