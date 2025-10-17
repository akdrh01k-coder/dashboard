import os, math, time, threading
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

try:
    import ydlidar
    HAS_LIDAR = True
except Exception:
    HAS_LIDAR = False

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

_lock = threading.Lock()
# 라이다 "각도(도), 거리(m)" 를 보관
_latest = {"ts": 0.0, "angles": [], "ranges": [], "source": "sim"}

def _sim_loop():
    ang = np.arange(720, dtype=float)  # 0.5도 간격
    while True:
        t = time.time()
        rng = 6.0 + 1.5*np.sin(np.deg2rad(ang*0.5) + t*0.6)
        with _lock:
            _latest["ts"] = t
            _latest["angles"] = (ang*0.5).tolist()
            _latest["ranges"] = rng.astype(float).tolist()
            _latest["source"] = "sim"
        time.sleep(0.05)

def _lidar_loop():
    port = os.getenv("LIDAR_PORT", "/dev/ttyUSB0")
    baud = int(os.getenv("LIDAR_BAUD", "128000"))
    if not HAS_LIDAR:
        print("[lidar_server] ydlidar 모듈 없음 → 시뮬레이터로 동작")
        return _sim_loop()

    ydlidar.os_init()
    L = ydlidar.CYdLidar()
    L.setlidaropt(ydlidar.LidarPropSerialPort, port)
    L.setlidaropt(ydlidar.LidarPropSerialBaudrate, baud)
    L.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
    L.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
    L.setlidaropt(ydlidar.LidarPropAutoReconnect, True)
    L.setlidaropt(ydlidar.LidarPropFixedResolution, True)
    if not (L.initialize() and L.turnOn()):
        print("[lidar_server] LiDAR 초기화 실패 → 시뮬레이터로 동작")
        return _sim_loop()

    print(f"[lidar_server] LiDAR 연결: {port}@{baud}")
    scan = ydlidar.LaserScan()
    while True:
        if L.doProcessSimple(scan):
            ang_deg, rng = [], []
            if hasattr(scan, "points") and scan.points:
                for p in scan.points:
                    if p.range > 0:
                        ang_deg.append(math.degrees(p.angle))
                        rng.append(float(p.range))
            elif hasattr(scan, "ranges") and scan.ranges:
                a0 = getattr(scan, "angle_min", 0.0)
                inc = getattr(scan, "angle_increment", 0.0)
                for i, d in enumerate(list(scan.ranges)):
                    if d > 0:
                        ang_deg.append(math.degrees(a0 + inc*i))
                        rng.append(float(d))
            with _lock:
                _latest["ts"] = time.time()
                _latest["angles"] = ang_deg
                _latest["ranges"] = rng
                _latest["source"] = port
        time.sleep(0.03)

@app.get("/health")
def health():
    with _lock:
        return {
            "ok": True,
            "source": _latest["source"],
            "points": len(_latest["ranges"]),
            "ts": _latest["ts"],
        }

@app.get("/lidar/latest")
def lidar_latest():
    with _lock:
        # 대시보드가 기대하는 형식 그대로 반환
        return {
            "ts": _latest["ts"],
            "angles": _latest["angles"],
            "ranges": _latest["ranges"],
        }

if __name__ == "__main__":
    import uvicorn, threading
    threading.Thread(target=_lidar_loop, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8001)
