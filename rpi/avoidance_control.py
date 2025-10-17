# -*- coding: utf-8 -*-
# 🚤 LiDAR 회피 기동 (간단/튼튼: DBSCAN 없음, 섹터 최소거리 기반)
import time, math, importlib, os, threading
import numpy as np
from motor_control import setup, cleanup, control_dc_motors, control_servo_angle

# ===== 설정값 (2.6×1.75m 풀장 기준) =====
LIDAR_PORT   = os.getenv("LIDAR_PORT", "/dev/ttyUSB0")  # 윈도우면 \\.\COM10
BAUDRATE     = int(os.getenv("LIDAR_BAUD", "128000"))
HZ           = 10
INTERVAL     = 1.0 / HZ

FOV_DEG      = 120             # 전방 ±60°
DECISION_CAP = 1.6             # 판단용 최대거리
WALL_TOL     = 0.10            # 벽 기준치 대비 ±10%면 벽으로 간주

# 임계 (히스테리시스)
AVOID_IN  = 0.50
AVOID_OUT = 0.60
SLOW_IN   = 0.90
SLOW_OUT  = 1.00

# 속도/조향
V_CRUISE  = 40                 # 순항
V_AVOID   = 30                 # 회피
STEER_MAX = 25                 # 회피 조향(±deg)
STEER_CTR = 90                 # 서보 중립

# 부드럽게(EMA)
STEER_ALPHA = 0.3

# 워치독(루프 정지 방지)
WATCHDOG_S = 2.0

# ===== 라이다 최신 프레임을 대시보드/다른 프로세스도 읽을 수 있게 공유 =====
# FastAPI(lidar_api.py)와 같은 프로세스에서 쓰면 공유 가능하지만,
# 여기선 간단히 "로컬 HTTP 서버"가 별도 파일에서 같은 센서를 다시 열지 않도록
# 본 스크립트에서 최신 프레임을 메모리에 저장하고, lidar_api.py가 같은 프로세스에서 함께 실행되게 구성.
latest_frame = {"ts":0.0, "angles":[], "ranges":[]}
latest_lock = threading.Lock()

def publish_frame(ang, rng):
    with latest_lock:
        latest_frame["ts"] = time.time()
        latest_frame["angles"] = ang.tolist() if isinstance(ang, np.ndarray) else list(ang)
        latest_frame["ranges"] = rng.tolist() if isinstance(rng, np.ndarray) else list(rng)

def get_latest_frame():
    with latest_lock:
        return dict(latest_frame)

# ===== 메인 =====
def main():
    setup()
    print("✅ [avoidance_simple] 시작")

    # LiDAR
    ydlidar = importlib.import_module("ydlidar")
    ydlidar.os_init()
    L = ydlidar.CYdLidar()
    L.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
    L.setlidaropt(ydlidar.LidarPropSerialPort, LIDAR_PORT)
    L.setlidaropt(ydlidar.LidarPropSerialBaudrate, BAUDRATE)
    L.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
    L.setlidaropt(ydlidar.LidarPropAutoReconnect, True)
    L.setlidaropt(ydlidar.LidarPropFixedResolution, True)
    if hasattr(ydlidar, "LidarPropSupportMotorDtrCtrl"):
        L.setlidaropt(ydlidar.LidarPropSupportMotorDtrCtrl, True)
    if not L.initialize() or not L.turnOn():
        print("❌ LiDAR 초기화 실패")
        cleanup(); raise SystemExit

    # 벽 기준치 학습
    print("🧭 벽 기준치 측정 중...")
    baseline = None; t0 = time.time()
    while time.time() - t0 < 2.0:
        scan = ydlidar.LaserScan(); L.doProcessSimple(scan)
        if hasattr(scan, "points") and scan.points:
            rng = np.array([p.range for p in scan.points], float)
            baseline = rng if baseline is None else (0.8*baseline + 0.2*rng)
        time.sleep(0.1)
    print("✅ 벽 기준치 학습 완료")

    def sector_mins(angles_rad, ranges_m):
        fov = math.radians(FOV_DEG/2)
        mask = (angles_rad > -fov) & (angles_rad < fov)
        a = angles_rad[mask]; r = ranges_m[mask]
        if a.size == 0: return np.inf, np.inf, np.inf
        r = np.clip(r, 0, DECISION_CAP)
        valid = np.isfinite(r) & (r > 0.05)
        a, r = a[valid], r[valid]
        if baseline is not None and baseline.size >= r.size:
            b = baseline[:r.size]
            diff = np.abs(r - b) / np.maximum(b, 1e-6)
            r[diff <= WALL_TOL] = np.nan
            m2 = np.isfinite(r) & (r > 0.05)
            a, r = a[m2], r[m2]
        if r.size == 0: return np.inf, np.inf, np.inf
        a_deg = np.degrees(a)
        Lm = np.nanmin(r[(a_deg < -20)]) if np.any(a_deg < -20) else np.inf
        Cm = np.nanmin(r[(a_deg >= -20) & (a_deg <= 20)]) if np.any((a_deg >= -20) & (a_deg <= 20)) else np.inf
        Rm = np.nanmin(r[(a_deg > 20)]) if np.any(a_deg > 20) else np.inf
        return Lm, Cm, Rm

    state = "CRUISE"
    steer_ema = STEER_CTR
    control_dc_motors(V_CRUISE); control_servo_angle(STEER_CTR)
    last_loop = time.time()

    try:
        while True:
            t_loop = time.time()
            scan = ydlidar.LaserScan()
            ok = L.doProcessSimple(scan)
            if not ok or not hasattr(scan, "points"):
                control_dc_motors(0); time.sleep(0.1); continue

            ang = np.array([p.angle for p in scan.points], float)
            rng = np.array([p.range for p in scan.points], float)

            # 최신 프레임 publish → FastAPI가 그대로 노출
            publish_frame(ang, rng)

            Lm, Cm, Rm = sector_mins(ang, rng)

            # 상태 전이
            if state != "AVOID" and Cm < AVOID_IN: state = "AVOID"
            elif state == "AVOID" and Cm > AVOID_OUT: state = "SLOW"
            if state != "SLOW" and (AVOID_OUT < Cm < SLOW_IN): state = "SLOW"
            elif state == "SLOW" and Cm > SLOW_OUT: state = "CRUISE"

            # 제어
            if state == "AVOID":
                control_dc_motors(V_AVOID)
                steer = STEER_CTR + (STEER_MAX if Lm < Rm else -STEER_MAX)
            elif state == "SLOW":
                if np.isfinite(Cm):
                    v = V_AVOID + (V_CRUISE - V_AVOID) * max(0.0, min(1.0, (Cm - AVOID_OUT) / (SLOW_IN - AVOID_OUT)))
                else:
                    v = V_AVOID
                control_dc_motors(v); steer = STEER_CTR
            else:
                control_dc_motors(V_CRUISE); steer = STEER_CTR

            steer_ema = (1-STEER_ALPHA)*steer_ema + STEER_ALPHA*steer
            control_servo_angle(float(steer_ema))

            last_loop = time.time()
            dt = last_loop - t_loop
            time.sleep(max(0.0, INTERVAL - dt))

            # 워치독
            if time.time() - last_loop > WATCHDOG_S:
                control_dc_motors(0); control_servo_angle(STEER_CTR)

    except KeyboardInterrupt:
        print("\n🛑 종료")
    finally:
        try:
            L.turnOff()
        except Exception:
            pass
        cleanup()

if __name__ == "__main__":
    main()


