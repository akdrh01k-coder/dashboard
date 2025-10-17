# 대시보드-api서버 모터 연동 코드
# 터미널에서 uvicorn main:app --host 0.0.0.0 --port 8000 입력 후 서버 ON
# main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import threading

# --- 1. module 불러오기 ---
import motor_control
import cam_api

# --- 2. FastAPI 서버 및 전역 변수 설정 ---
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

lock = threading.Lock()
last_steer_time = time.time()
servo_centered = True

# --- 3. 서버 시작/종료 이벤트 처리 (가장 중요한 수정 부분) ---
@app.on_event("startup")
def startup_event():
    """서버가 시작될 때 딱 한 번 실행됩니다."""
    motor_control.setup()

    try:
        cam_api.cam.start()
        print("✅ Camera has been started.")
    except Exception as e:
        print(f" FAILED to start camera: {e}")
            
    # 서보 자동 복귀 스레드 시작
    watchdog_thread = threading.Thread(target=servo_watchdog, daemon=True)
    watchdog_thread.start()
    
    print("✅ API 서버가 시작되었고, 하드웨어가 초기화되었습니다.")

@app.on_event("shutdown")
def shutdown_event():
    """서버가 종료될 때 딱 한 번 실행됩니다."""
    motor_control.cleanup()
    cam_api.cam.stop()
    print("⏹️ API 서버가 종료되었고, 하드웨어가 정리되었습니다.")

# camera server app <- connect -> /cam route
app.mount("/cam", cam_api.app, name="camera_api")


# --- 4. API 엔드포인트 정의 ---
class ThrottleRequest(BaseModel):
    val: int

class SteerRequest(BaseModel):
    dir: str

@app.post("/cmd/throttle")
def handle_throttle(req: ThrottleRequest):
    with lock:
        current_pwm = req.val
    
    print(f"🚢 [속도 설정] 값: {current_pwm}")
    motor_control.control_dc_motors(current_pwm)
    
    return {"status": "ok", "pwm_set_to": current_pwm}

@app.post("/cmd/steer")
def handle_steer(req: SteerRequest):
    global last_steer_time
    direction = req.dir
    
    print(f"🧭 [방향키 제어] 방향: {direction}")
    
    if direction == "left":
        target_angle = 45
    elif direction == "right":
        target_angle = 145
    else:
        target_angle = 90

    motor_control.control_servo_angle(target_angle)
    last_steer_time = time.time()
    return {"status": "ok", "steer": direction}

# --- 5. 서보 자동 중앙 복귀 ---
def servo_watchdog():
    global last_steer_time, servo_centered
    while True:
        time.sleep(0.05)
        with lock:
            if time.time() - last_steer_time > 0.5 and not servo_centered:
                print("🕹️ [서보] 자동 중앙 복귀")
                motor_control.control_servo_angle(90)
                servo_centered = True
            elif time.time() - last_steer_time <= 0.5:
                servo_centered = False

    
