# record_video.py
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import datetime
import time
import os
def record_video_mp4(duration=30, folder = "videos"):
    """
    Picamera2로 mp4 녹화를 duration초 동안 수행하는 함수
    """
    timeout = time.time()
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    picam2 = Picamera2()
    
    # 날짜 기반 파일명 생성
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder,f"record_{timestamp}.mp4")
    

    # 기본 비디오 설정
    video_config = picam2.create_video_configuration(
        main={"size": (1280, 720)}
    )
    picam2.configure(video_config)

    encoder = H264Encoder(bitrate=8_000_000)
    output = FfmpegOutput(filename)

    # 카메라 시작
    
    picam2.start()
    time.sleep(0.3)  # 워밍업(빠르게 시작하려면 최소값으로)

    print(f"[녹화 시작] 파일: {filename}")
    picam2.start_recording(encoder, output)
    
    print(time.time()-timeout)
    # duration초 녹화
    time.sleep(duration)

    # 녹화 정지
    picam2.stop_recording()
    picam2.stop()
    picam2.close()
    print(f"[녹화 완료] 파일 저장됨: {filename}")

    return filename  # 메인에서 파일명 활용할 수 있게 반환
