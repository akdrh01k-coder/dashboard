# -*- coding: utf-8 -*-
#C:\Users\82102\eco-ship\pages\1_2. 위치_모니터링_LiDAR.py
# 📡 LiDAR 실시간 모니터링 + 2D SLAM(간소화) + DBSCAN 군집 박스(탑뷰)

import time, importlib

from typing import Tuple

import numpy as np

import streamlit as st

import matplotlib.pyplot as plt

import matplotlib

import matplotlib.font_manager as fm

from sklearn.cluster import DBSCAN


# ---------- 폰트 ----------

def _use_korean_font():

    candidates = ["Malgun Gothic","MalgunGothic","NanumGothic","AppleGothic"]

    installed = {f.name for f in fm.fontManager.ttflist}

    for name in candidates:

        if name in installed:

            matplotlib.rcParams["font.family"] = name; break

    matplotlib.rcParams["axes.unicode_minus"] = False

_use_korean_font()


st.set_page_config(layout="wide")

st.header("📡 LiDAR 모니터링 + 2D 누적")


# ---------- 고정 설정(숨김) ----------

COM_PORT  = r"\\.\COM10"

BAUDRATE  = 128000

HZ        = 10

INTERVAL  = max(1e-3, 1.0/HZ)

RES_M     = 0.05      # 5cm/px

DECAY_PCT = 5         # 프레임당 5% 감쇠


# ---------- 상단 컨트롤 ----------

ctrl1, ctrl2, ctrl3 = st.columns([1,1,6])

with ctrl1:

    run = st.toggle("실시간 시작", value=False, key="live_toggle")

with ctrl2:

    do_reset = st.button("맵 초기화", type="secondary")

# 맵 크기: 2~20m (기본 4m)

map_size_m = st.slider("맵 크기(한 변, m)", 2, 20, 4, 1, key="map_size_slider")


# 좌/우 레이아웃

c_left, c_right = st.columns(2)

ph_scan  = c_left.empty()

ph_map   = c_right.empty()


# ---------- 세션 상태 ----------

ss = st.session_state

def _init_map():

    px = int(ss.map_size/ss.res)

    ss.occ_map = np.zeros((px, px), np.float32)

    ss.T       = np.eye(3, dtype=np.float64)

    ss.traj    = [(0.0,0.0)]

    ss.icp_prev = None

    ss.last_world = None


if "map_size" not in ss: ss.map_size = map_size_m

if "res" not in ss: ss.res = RES_M

if ("occ_map" not in ss) or (ss.map_size != map_size_m) or (ss.res != RES_M):

    ss.map_size = map_size_m; ss.res = RES_M; _init_map()

if do_reset: _init_map()


if "ydlidar_L" not in ss: ss.ydlidar_L = None

if "lidar_open" not in ss: ss.lidar_open = False

if "lidar_fail_until" not in ss: ss.lidar_fail_until = 0.0


# ---------- LiDAR 제어 ----------

def stop_lidar():

    try:

        if ss.ydlidar_L is not None:

            ss.ydlidar_L.turnOff()

            ss.ydlidar_L.disconnecting()

    except Exception:

        pass

    ss.ydlidar_L = None

    ss.lidar_open = False


# OFF면 언제든 즉시 정지

if not run and ss.ydlidar_L is not None:

    stop_lidar()


# ---------- LiDAR 프레임 ----------

def fetch_pc_frame(port: str, baud: int) -> Tuple[np.ndarray, np.ndarray, float]:

    now = time.time()

    if now < ss.lidar_fail_until:

        return np.array([]), np.array([]), now

    try:

        ydlidar = importlib.import_module("ydlidar")

    except Exception:

        if not ss.get("warned_no_sdk", False):

            st.error("ydlidar 모듈이 없습니다. (SDK 설치 필요)")

            ss.warned_no_sdk = True

        ss.lidar_fail_until = now + 5.0

        return np.array([]), np.array([]), now

    if not run:

        return np.array([]), np.array([]), now

    if ss.ydlidar_L is None and not ss.lidar_open:

        ydlidar.os_init()

        L = ydlidar.CYdLidar()

        L.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)  # X4

        L.setlidaropt(ydlidar.LidarPropSerialPort, port)

        ok = False

        for b in (int(baud), 115200):

            L.setlidaropt(ydlidar.LidarPropSerialBaudrate, b)

            L.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)

            L.setlidaropt(ydlidar.LidarPropAutoReconnect, True)

            L.setlidaropt(ydlidar.LidarPropFixedResolution, True)

            if hasattr(ydlidar, "LidarPropSupportMotorDtrCtrl"):

                L.setlidaropt(ydlidar.LidarPropSupportMotorDtrCtrl, True)

            if L.initialize() and L.turnOn():

                ss.ydlidar_L = L; ss.lidar_open = True; ok = True; break

            try: L.turnOff(); L.disconnecting()

            except Exception: pass

        if not ok:

            ss.lidar_fail_until = now + 5.0

            st.error("LiDAR init 실패 (포트 점유/보레이트 문제)")

            return np.array([]), np.array([]), now

    L = ss.ydlidar_L

    if L is None:

        return np.array([]), np.array([]), now

    scan = ydlidar.LaserScan()

    ok = L.doProcessSimple(scan)

    ts = time.time()

    if not ok: return np.array([]), np.array([]), ts

    if hasattr(scan, "points") and scan.points:

        ang = np.array([p.angle for p in scan.points], float)

        rng = np.array([p.range for p in scan.points], float)

        return ang, rng, ts

    if hasattr(scan, "ranges") and scan.ranges:

        rng = np.array(list(scan.ranges), float)

        a0 = getattr(scan, "angle_min", None)

        inc = getattr(scan, "angle_increment", None)

        if a0 is not None and inc is not None:

            n = len(rng); ang = a0 + inc*np.arange(n, dtype=float)

            return ang, rng, ts

    return np.array([]), np.array([]), ts


# ---------- 유틸 ----------

def pol2xy(theta, r):

    if r.size == 0 or theta.size == 0: return np.empty((0,2), np.float32)

    m = np.isfinite(r) & (r > 0.05) & (r < ss.map_size*0.9)

    theta = theta[m]; r = r[m]

    x = r*np.cos(theta); y = r*np.sin(theta)

    return np.stack([x,y], axis=1).astype(np.float32)


def se2(dx, dy, dth):

    c,s = np.cos(dth), np.sin(dth)

    return np.array([[c,-s,dx],[s,c,dy],[0,0,1]], np.float64)


def apply_se2(T, pts):

    if pts.size == 0: return pts

    hom = np.c_[pts, np.ones(len(pts))]

    out = hom @ T.T

    return out[:,:2]


def update_occ(world_xy):

    m = ss.occ_map; half = ss.map_size/2.0; res = ss.res; px = m.shape[0]

    if world_xy.size == 0: return

    ix = ((world_xy[:,0] + half)/res).astype(int)

    iy = ((half - world_xy[:,1])/res).astype(int)

    inb = (ix>=0)&(iy>=0)&(ix<px)&(iy<px)

    if np.any(inb):

        m[iy[inb], ix[inb]] = np.clip(m[iy[inb], ix[inb]] + 0.35, 0.0, 1.0)

    if DECAY_PCT>0: m[:] *= (1.0 - DECAY_PCT/100.0)


# ---------- ICP (Open3D optional) ----------

try:

    import open3d as o3d

    HAS_O3D = True

except Exception:

    HAS_O3D = False

    st.warning("Open3D 없음: 정합(ICP) 비활성 — 원점 누적만 표시")


def icp_step(curr_xy):

    if not HAS_O3D: return 0.0,0.0,0.0

    if ss.icp_prev is None or curr_xy.shape[0] < 50 or ss.icp_prev.shape[0] < 50:

        return 0.0,0.0,0.0

    src = o3d.geometry.PointCloud(); src.points = o3d.utility.Vector3dVector(np.c_[curr_xy, np.zeros(len(curr_xy))])

    tgt = o3d.geometry.PointCloud(); tgt.points = o3d.utility.Vector3dVector(np.c_[ss.icp_prev, np.zeros(len(ss.icp_prev))])

    reg = o3d.pipelines.registration.registration_icp(

        src, tgt, 0.30, np.eye(4),

        o3d.pipelines.registration.TransformationEstimationPointToPoint(),

        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=30)

    )

    T4 = reg.transformation

    dx, dy = float(T4[0,3]), float(T4[1,3])

    dth    = float(np.arctan2(T4[1,0], T4[0,0]))

    return dx, dy, dth


# ---------- 렌더 ----------

def render_polar(theta, r):

    # 대시보드 배율 고정(맵크기 기반): 갑작스런 확대/축소 방지

    R_VIEW = max(2.0, ss.map_size/2.0 + 0.5)

    fig = plt.figure(figsize=(6.4,6.4))

    ax = fig.add_subplot(111, projection="polar")

    ax.set_theta_zero_location("E"); ax.set_theta_direction(-1)

    ax.set_rmax(R_VIEW)

    ax.grid(True, alpha=0.35)

    if r.size and theta.size:

        ax.scatter(theta, r, s=8, c="#1f77b4", alpha=0.9)

    ax.set_title("실시간 스캔")

    ph_scan.pyplot(fig, clear_figure=True); plt.close(fig)


def render_map():

    half = ss.map_size/2.0

    m = ss.occ_map

    fig, ax = plt.subplots(figsize=(6.8,6.8))

    ax.imshow(m, cmap="viridis", origin="upper",

              extent=[-half, half, -half, half], vmin=0, vmax=1)

    ax.set_aspect("equal")

    ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)")

    ax.set_title("누적 맵")


    # 궤적

    if ss.traj:

        tx,ty = np.array(ss.traj).T

        ax.plot(tx, ty, color="w", lw=1.5, alpha=0.9)

        ax.plot(tx[-1], ty[-1], "ro", ms=5)


    # --- DBSCAN 군집 박스 (탑뷰 전용) ---

    try:

        if ss.get("last_world") is not None and ss.last_world.size > 0:

            pts = ss.last_world

            # 맵 범위 내 포인트만 사용

            mask = (pts[:,0] > -half) & (pts[:,0] < half) & (pts[:,1] > -half) & (pts[:,1] < half)

            pts = pts[mask]

            if pts.shape[0] >= 20:

                db = DBSCAN(eps=0.25, min_samples=8).fit(pts)

                labels = db.labels_

                uniq = [c for c in np.unique(labels) if c != -1]

                import matplotlib.patches as patches

                for c in uniq:

                    cluster = pts[labels==c]

                    if cluster.shape[0] < 8:

                        continue

                    xmin, ymin = cluster.min(axis=0)

                    xmax, ymax = cluster.max(axis=0)

                    rect = patches.Rectangle((xmin, ymin), xmax-xmin, ymax-ymin,

                                             fill=False, ec="orange", lw=1.5, alpha=0.9)

                    ax.add_patch(rect)

                    cx, cy = cluster.mean(axis=0)

                    ax.plot(cx, cy, marker="x", ms=6, color="orange", alpha=0.9)

    except Exception:

        pass


    ph_map.pyplot(fig, clear_figure=True); plt.close(fig)


def draw_once(active: bool):

    if not active:

        # OFF여도 틀 표시

        render_polar(np.array([]), np.array([]))

        render_map()

        return

    # 1) 라이다 프레임

    th, rr, _ = fetch_pc_frame(COM_PORT, BAUDRATE)

    # 2) 스캔 렌더(고정 배율)

    render_polar(th, rr)

    # 3) SLAM 업데이트

    xy = pol2xy(th, rr)

    dx,dy,dth = icp_step(xy)

    ss.T = ss.T @ se2(dx,dy,dth)

    world = apply_se2(ss.T, xy)

    ss.last_world = world

    update_occ(world)

    ss.traj.append((float(ss.T[0,2]), float(ss.T[1,2])))

    if len(ss.traj) > 4000: ss.traj = ss.traj[-4000:]

    ss.icp_prev = xy

    # 4) 지도 렌더

    render_map()


# ---------- 최초 표시(OFF여도 틀 보이게) ----------

draw_once(False)


# ---------- 루프 ----------

if run:

    try:

        while st.session_state.get("live_toggle", False):

            t0 = time.time()

            draw_once(True)

            time.sleep(max(0.0, INTERVAL - (time.time()-t0)))

    finally:

        stop_lidar()





