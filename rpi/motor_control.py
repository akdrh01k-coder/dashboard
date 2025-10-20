# motor_control.py (하드웨어 PWM을 사용하는 pigpio 버전)

import pigpio
import time

# --- 1. 하드웨어 핀 설정 (BCM 번호 기준) ---
# pigpio는 BCM 핀 번호만 사용합니다.
ENA = 12; IN1 = 6;  IN2 = 5   # 왼쪽 모터
ENB = 13; IN3 = 20; IN4 = 21  # 오른쪽 모터
SERVO_PIN = 18                # 서보모터

# pigpio 인스턴스 생성
pi = pigpio.pi()

# --- 2. 초기 설정 및 정리 함수 ---
def setup():
    """pigpio를 사용하여 GPIO 초기 설정을 수행합니다."""
    # DC 모터 핀들을 출력으로 설정
    for pin in [IN1, IN2, IN3, IN4]:
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.write(pin, 0)

    # PWM 핀 설정 (주파수는 pigpio가 관리)
    for pin in [ENA, ENB]:
        pi.set_mode(pin, pigpio.OUTPUT)
    
    # 서보 핀 설정
    pi.set_mode(SERVO_PIN, pigpio.OUTPUT)
    
    print("✅ [motor_control] 하드웨어 초기화 완료 (pigpio).")
    control_servo_angle(90) # 중앙에서 시작
    time.sleep(1)

def cleanup():
    """프로그램 종료 시 모든 모터 정지 및 GPIO 리소스 정리"""
    print("\n⏹️ [motor_control] 모든 동작 정지 및 pigpio 리소스 정리")
    # PWM 정지
    pi.set_PWM_dutycycle(ENA, 0)
    pi.set_PWM_dutycycle(ENB, 0)
    pi.set_servo_pulsewidth(SERVO_PIN, 0) # 서보 신호 끄기
    pi.stop() # pigpio 연결 종료

# --- 3. 핵심 제어 함수 ---
def control_dc_motors(speed_percent):
    """추진력을 제어합니다. (-100 ~ 100)"""
    # pigpio의 Duty Cycle은 0~255 범위 사용
    duty_cycle = int(min(abs(speed_percent), 100) / 100.0 * 255)
    
    if speed_percent > 0: # 전진
        pi.write(IN1, 1); pi.write(IN2, 0)
        pi.write(IN3, 1); pi.write(IN4, 0)
    elif speed_percent < 0: # 후진
        pi.write(IN1, 0); pi.write(IN2, 1)
        pi.write(IN3, 0); pi.write(IN4, 1)
    else: # 정지
        pi.write(IN1, 0); pi.write(IN2, 0)
        pi.write(IN3, 0); pi.write(IN4, 0)
        
    pi.set_PWM_dutycycle(ENA, duty_cycle)
    pi.set_PWM_dutycycle(ENB, duty_cycle)

def control_servo_angle(angle):
    """방향타의 각도를 제어합니다. (0 ~ 180)"""
    # pigpio는 각도보다 더 정밀한 pulsewidth(500~2500)를 사용합니다.
    pulsewidth = 500 + (angle / 180.0) * 2000
    pi.set_servo_pulsewidth(SERVO_PIN, pulsewidth)

