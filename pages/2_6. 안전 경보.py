# safety_dashboard.py — 안전/경보 페이지 (디자인 통일 + '임계 5s' 제목 옆 표시)

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="안전/경보 대시보드",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 전역 스타일(메인 대시보드와 톤 맞춤) ==========
st.markdown("""
<style>
/* 기본 요소 숨김(메뉴/기본헤더/푸터) */
#MainMenu, header, footer {visibility: hidden;}

/* 상단 고정 바와 충돌 안 나게 여백 확보 */
.main .block-container { padding-top: 96px !important; }

/* 사이드바 톤(밝은 회색) */
section[data-testid="stSidebar"] {
    background: #F1F1F9 !important;
    border-right: 1px solid #F1F1F9;
}

/* 페이지 헤더(제목 바) */
.page-header{
  margin: 6px 0 16px 0; padding: 14px 16px;
  background: linear-gradient(90deg,#eef4ff,#ffffff);
  border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.06);
  display:flex; align-items:center; justify-content:space-between; gap:12px;
}
.page-title{font-size:22px; font-weight:800; color:#1f2b4d;}
.page-sub{font-size:13px; color:#64748b;}

/* KPI/카드 공통 */
.dash-card {
    background: #F6F7FB;
    border: 1px solid #EBEDF5;
    border-radius: 16px;
    padding: 12px 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

/* 상단 고정 헤더바 */
.app-topbar{
  position: fixed; top:0; left:0; right:0; height:64px;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 22px; z-index:1000;
  color:#fff; border-bottom:1px solid rgba(255,255,255,.15);
  background:linear-gradient(90deg,#3b4a67 0%, #536a92 100%);
  box-shadow:0 8px 24px rgba(0,0,0,.18);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
}
.app-topbar .brand{ font-weight:800; letter-spacing:.2px; }
.app-topbar .right{ display:flex; gap:14px; align-items:center; }
.app-pill{ background:rgba(255,255,255,.18); padding:6px 10px; border-radius:999px; font-weight:700; }
.app-link{ color:#fff; text-decoration:none; }
.app-link:hover{ text-decoration:underline; }

/* Streamlit 헤더 z-index 보정 */
[data-testid="stHeader"] { z-index: 0 !important; background: transparent !important; }
.app-topbar { z-index: 99999 !important; }
[data-testid="stSidebarCollapseControl"],
[data-testid="stSidebarCollapseButton"]{
    position:fixed; top:12px; left:12px;
    z-index:100000 !important;
    display:flex !important; opacity:1 !important; pointer-events:auto !important;
}

/* 팀정보 카드(사이드바용) */
.team-container {
    background-color: #f7f8fc;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.06);
    font-family: 'Segoe UI', sans-serif;
    margin-top: 8px;
}
.team-title {
    font-size: 18px; font-weight: 800; margin-bottom: 6px;
    color: #2c3e50 !important;
}
.team-subtitle {
    font-size: 14px; font-weight: 700; margin-bottom: 6px;
    color: #34495e !important;
}
.team-member { font-size: 13px; padding: 2px 0; color: #2c3e50 !important; }
.mentor { margin-top: 10px; font-size: 12px; font-style: italic; color: #7f8c8d !important; }

/* 소제목(=subheader) 간격 */
h2, .stMarkdown h2 { font-size: 20px !important; margin-top: 8px !important; margin-bottom: 6px !important; line-height: 1.25 !important; }
hr { margin: 4px 0 !important; }

/* 데이터프레임 패딩 */
[data-testid="stDataFrame"] .st-emotion-cache-1xarl3l,
[data-testid="stDataFrame"] .st-emotion-cache-1y4p8pa { padding-top: 6px !important; padding-bottom: 6px !important; }

/* expander 문단 여백 */
[data-testid="stExpander"] p { margin: 4px 0 !important; }
</style>
""", unsafe_allow_html=True)

# 상단 고정 헤더바(시계 포함)
now_str = datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
<div class="app-topbar">
  <div class="brand">Eco-Friendship Dashboard</div>
  <div class="right">
    <div class="app-pill" id="clock">{now_str}</div>
    <a class="app-pill app-link" href="?nav=%EB%A1%9C%EA%B7%B8%EC%9D%B8" target="_self" rel="noopener">Login</a>
  </div>
</div>
<script>
  function upd(){{
    const el = document.getElementById('clock'); 
    if(!el) return;
    const n = new Date();
    const t = [n.getHours(), n.getMinutes(), n.getSeconds()].map(v=>String(v).padStart(2,'0')).join(':');
    el.textContent = t;
  }}
  setInterval(upd, 1000); upd();
</script>
""", unsafe_allow_html=True)

# ======== Sidebar (처음 버전으로 유지) ========
def custom_sidebar():
    st.markdown("""
    <style>
      [data-testid="stSidebarNav"] { display: none !important; }
      section[data-testid="stSidebar"] { background: #3E4A61 !important; color: #fff !important; }
      section[data-testid="stSidebar"] * { color:#fff !important; }
      .sb-title { font-weight: 800; font-size: 20px; margin: 6px 0 8px 0; }
      .sb-link [data-testid="stPageLink"] a{ color:#fff !important; text-decoration:none !important; }
      .sb-link [data-testid="stPageLink"] a:hover{ background: rgba(255,255,255,0.12); border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sb-title">Eco-Friendship Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-link">', unsafe_allow_html=True)
        st.page_link("pages/1_5. 친환경 지수.py", label="🌱 친환경 지표")
        st.page_link("pages/2_6. 안전 경보.py", label="⚠️ 안전/경보")
        st.page_link("pages/3_7. 로그인.py",     label="🔐 로그인")
        st.markdown('</div>', unsafe_allow_html=True)

custom_sidebar()

# ========== 페이지 헤더 ==========
def page_header(title: str, sub: str | None = None):
    right = f"<div class='page-sub'>{sub}</div>" if sub else ""
    st.markdown(f"""
    <div class="page-header">
      <div class="page-title">{title}</div>
      {right}
    </div>
    """, unsafe_allow_html=True)

page_header("🛟 안전 · 경보", sub="실측 기반 임계값 규칙으로 안전 상태를 판정하고, 경보를 기록합니다.")

# ------------------------------------------------------------
# 임계값 — 측정 가능한 안전 지표만 사용
# ------------------------------------------------------------
THRESH = {
    "lidar_min_warn": 1.2,    # [m]
    "lidar_min_crit": 0.5,    # [m]
    "speed_stall_max": 0.05,  # [m/s]
    "motor_i_warn": 3.0,      # [A]
    "motor_i_crit": 6.0,      # [A]
    "data_timeout_s": 5,      # [s]
    "pi_temp_warn": 70.0,     # [°C]
    "pi_temp_crit": 80.0,     # [°C],
}

SEVERITY_ORDER = {"주의": 1, "경고": 2, "위험": 3}

# ------------------------------------------------------------
# 경보 디바운스/쿨다운
# ------------------------------------------------------------
PERSIST_N = 1
COOLDOWN_S = 0
if "alarm_counters" not in st.session_state:
    st.session_state.alarm_counters = {}
if "alarm_last_ts" not in st.session_state:
    st.session_state.alarm_last_ts = {}
if "tick" not in st.session_state:
    st.session_state.tick = 0

def _can_fire(key: str) -> bool:
    last = st.session_state.alarm_last_ts.get(key)
    if last is None:
        return True
    return (datetime.now() - last).total_seconds() >= COOLDOWN_S

def _update_counter_and_check(key: str, condition: bool) -> bool:
    cnt = st.session_state.alarm_counters.get(key, 0)
    cnt = cnt + 1 if condition else 0
    st.session_state.alarm_counters[key] = cnt
    return cnt >= PERSIST_N

def _push_alarm(alarms, key, name, severity, detail, condition: bool):
    if _update_counter_and_check(key, condition) and _can_fire(key):
        alarms.append((name, severity, detail))
        st.session_state.alarm_last_ts[key] = datetime.now()

# ------------------------------------------------------------
# 더미 데이터(6단계 시나리오)
# ------------------------------------------------------------
def read_latest(prev=None):
    now = datetime.now()
    phase = st.session_state.tick % 6

    lidar_min = 2.4 + np.random.normal(0, 0.15)
    cam_obstacle_center = False
    gps_speed = abs(0.55 + np.random.normal(0, 0.08))
    motor_i = abs(np.random.normal(1.6, 0.5))
    pi_temp = 55 + np.random.normal(0, 1.5)
    link_age = np.random.uniform(0, 1.0)

    if phase == 1:
        cam_obstacle_center = True
    elif phase == 2:
        lidar_min = 0.9; cam_obstacle_center = True
    elif phase == 3:
        lidar_min = 0.35; cam_obstacle_center = True
    elif phase == 4:
        motor_i = 6.8; pi_temp = 62 + np.random.normal(0, 1.5)
    elif phase == 5:
        motor_i = 3.5; gps_speed = 0.02; link_age = np.random.uniform(0, 0.6)

    return {
        "ts": now,
        "lidar_min": lidar_min,
        "cam_obstacle_center": cam_obstacle_center,
        "gps_speed": gps_speed,
        "motor_i": motor_i,
        "pi_temp": pi_temp,
        "link_age": link_age,
    }

# ------------------------------------------------------------
# 규칙 평가 → 경보 생성
# ------------------------------------------------------------
def evaluate_rules(x):
    alarms = []
    _push_alarm(alarms, "lidar_crit", "충돌 임박", "위험",
                f"{x['lidar_min']:.2f} m < {THRESH['lidar_min_crit']} m",
                x["lidar_min"] < THRESH["lidar_min_crit"])
    _push_alarm(alarms, "lidar_warn", "장애물 접근", "경고",
                f"{x['lidar_min']:.2f} m < {THRESH['lidar_min_warn']} m",
                x["lidar_min"] < THRESH["lidar_min_warn"])
    _push_alarm(alarms, "cam_center", "전방 시야 위험(카메라)", "경고",
                "전방 중심부 위험 객체 감지됨",
                bool(x.get("cam_obstacle_center", False)))
    _push_alarm(alarms, "prop_stall", "추진 스톨 의심", "경고",
                f"속도 {x['gps_speed']:.2f} m/s ≤ {THRESH['speed_stall_max']} m/s",
                x["gps_speed"] <= THRESH["speed_stall_max"])
    _push_alarm(alarms, "motor_i_crit", "모터 과전류", "위험",
                f"{x['motor_i']:.1f}A > {THRESH['motor_i_crit']}A",
                x["motor_i"] > THRESH["motor_i_crit"])
    _push_alarm(alarms, "motor_i_warn", "모터 과전류", "경고",
                f"{x['motor_i']:.1f}A > {THRESH['motor_i_warn']}A",
                x["motor_i"] > THRESH["motor_i_warn"])
    _push_alarm(alarms, "link_delay", "데이터 지연/끊김", "경고",
                f"{x['link_age']:.1f} s > {THRESH['data_timeout_s']} s",
                x["link_age"] > THRESH["data_timeout_s"])
    _push_alarm(alarms, "pi_temp_crit", "라즈베리파이 과열", "위험",
                f"{x['pi_temp']:.1f}°C > {THRESH['pi_temp_crit']}°C",
                x["pi_temp"] > THRESH["pi_temp_crit"])
    _push_alarm(alarms, "pi_temp_warn", "라즈베리파이 고온", "경고",
                f"{x['pi_temp']:.1f}°C > {THRESH['pi_temp_warn']}°C",
                x["pi_temp"] > THRESH["pi_temp_warn"])
    return alarms

# ------------------------------------------------------------
# 세션 상태 및 샘플/알람 평가
# ------------------------------------------------------------
if "last_sample" not in st.session_state:
    st.session_state.last_sample = None
if "alarm_log" not in st.session_state:
    st.session_state.alarm_log = pd.DataFrame(columns=["시간", "경보 종류", "심각도", "세부"])
if "last_logged" not in st.session_state:
    st.session_state.last_logged = {}
LOG_COOLDOWN_S = 20

sample = read_latest(st.session_state.last_sample)
alarms = evaluate_rules(sample)
st.session_state.last_sample = sample
top_sev = max([SEVERITY_ORDER[a[1]] for a in alarms], default=0)

# ------------------------------------------------------------
# 실시간 시스템 상태 — 카드 5개
# ------------------------------------------------------------
st.subheader("실시간 시스템 상태")

def stat_card(icon: str, title: str, value: str, sub: str | None = None,
              tone: str = "neutral", title_tag: str | None = None):
    gradients = {
        "neutral": "linear-gradient(135deg, #EEF2FF 0%, #E9F5FF 100%)",
        "ok":      "linear-gradient(135deg, #E6FFF5 0%, #EAFFF0 100%)",
        "warn":    "linear-gradient(135deg, #FFF7E6 0%, #FFF1E6 100%)",
        "danger":  "linear-gradient(135deg, #FFE6EA 0%, #FFD6E1 100%)",
    }
    borders = { "neutral": "#c9d6ea", "ok": "#9ad7a6", "warn": "#f3cc69", "danger": "#f08b86" }
    bg = gradients.get(tone, gradients["neutral"])
    bd = borders.get(tone, borders["neutral"])

    html = f"""
    <div class="dash-card" style="background:{bg}; border:1px solid {bd}; text-align:center;">
      <div style="
        font-size:18px; font-weight:800;
        display:flex; justify-content:center; gap:6px; align-items:center; flex-wrap:wrap;">
        <span style="font-size:20px;">{icon}</span>
        <span>{title}</span>
        {f"<span style='font-size:12px; font-weight:600; color:#64748b; margin-left:2px;'>{title_tag}</span>" if title_tag else ""}
      </div>
      <div style="font-size:20px; font-weight:800; margin-top:6px;">{value}</div>
      {"<div style='opacity:0.8; margin-top:4px; font-size:12px;'>"+sub+"</div>" if sub else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

TH = THRESH
c1, c2, c3, c4, c5 = st.columns(5)

# 1. LiDAR
tone_lidar = "danger" if sample["lidar_min"] < TH["lidar_min_crit"] else ("warn" if sample["lidar_min"] < TH["lidar_min_warn"] else "ok")
with c1:
    stat_card("📡", "LiDAR 최소거리", f"{sample['lidar_min']:.2f} m", tone=tone_lidar)

# 2. 카메라
cam_status = "감지됨" if sample["cam_obstacle_center"] else "정상"
tone_cam = "danger" if sample["cam_obstacle_center"] else "ok"
with c2:
    stat_card("🎥", "카메라 전방", cam_status, tone=tone_cam)

# 3. 속도
tone_speed = "warn" if sample["gps_speed"] <= TH["speed_stall_max"] else "ok"
with c3:
    stat_card("🚤", "선박 속도", f"{sample['gps_speed']:.2f} m/s", tone=tone_speed)

# 4. 모터 전류
tone_motor = "danger" if sample["motor_i"] > TH["motor_i_crit"] else ("warn" if sample["motor_i"] > TH["motor_i_warn"] else "ok")
with c4:
    stat_card("⚙️", "모터 전류", f"{sample['motor_i']:.2f} A", tone=tone_motor)

# 5. 데이터 지연 — (임계 5s) 제목 옆(작은 글씨 유지)
tone_link = "warn" if sample["link_age"] > TH["data_timeout_s"] else "ok"
with c5:
    stat_card(
        icon="📶",
        title="데이터 지연",
        value=f"{sample['link_age']:.2f} s",
        tone=tone_link,
        title_tag=f"(임계 {TH['data_timeout_s']}s)"  # ← 원래 작은 크기(12px)로 표시
    )
# ------------------------------------------------------------
# 좌/우 레이아웃: 상태 배너 & 현재 경보 테이블
# ------------------------------------------------------------
st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
left_sec, right_sec = st.columns(2, gap="large")

with left_sec:
    st.markdown("<div style='margin-top:6px;'>", unsafe_allow_html=True)
    if top_sev == SEVERITY_ORDER["위험"]:
        st.error("위험 상태입니다. 즉시 조치하십시오.", icon="🚨")
    elif top_sev == SEVERITY_ORDER["경고"]:
        st.warning("경고 상태입니다. 동작 상태를 점검하십시오.", icon="⚠️")
    else:
        st.success("정상 상태입니다. 특이사항이 없습니다.", icon="✅")

    with st.expander("경보 규칙"):
        st.markdown(
            """
            - **충돌/장애물**: LiDAR 최소거리, **카메라 전방 감지**로 즉시 위험을 탐지합니다.  
            - **주행 상태**: 선박 속도가 임계치 이하이면 **추진 스톨**을 의심합니다.  
            - **구동 부하**: **모터 전류**로 과부하/이상 저항을 감시합니다.  
            - **시스템/데이터**: **데이터 지연(link_age)** 과 라즈베리파이 온도(내부 룰)로 시스템 위험을 점검합니다.  
            ※ 모든 경보는 위 지표의 **실측 값**에 기반합니다.
            """
        )

with right_sec:
    st.subheader("위험 경보")
    if alarms:
        df_now = pd.DataFrame(
            [{"시간": sample["ts"].strftime("%Y-%m-%d %H:%M:%S"),
              "경보 종류": a[0], "심각도": a[1], "세부": a[2]} for a in alarms]
        )
        st.dataframe(df_now, use_container_width=True, hide_index=True)

        # 로그 기록(쿨다운)
        new_records = []
        now_ts = datetime.now()
        for name, sev, detail in alarms:
            last_t = st.session_state.last_logged.get(name)
            if (last_t is None) or ((now_ts - last_t).total_seconds() >= LOG_COOLDOWN_S):
                new_records.append({
                    "시간": sample["ts"].strftime("%Y-%m-%d %H:%M:%S"),
                    "경보 종류": name,
                    "심각도": sev,
                    "세부": detail
                })
                st.session_state.last_logged[name] = now_ts
        if new_records:
            st.session_state.alarm_log = pd.concat(
                [pd.DataFrame(new_records), st.session_state.alarm_log],
                ignore_index=True
            )
    else:
        st.info("경보가 발생하지 않았습니다.")

# ------------------------------------------------------------
# 하단: 경보 발생 로그
# ------------------------------------------------------------
st.markdown("---")
st.subheader("경보 발생 로그")

def highlight_severity(row):
    if row['심각도'] == '위험':
        return ['background-color: #ff4b4b; color: white'] * len(row)
    elif row['심각도'] == '경고':
        return ['background-color: #ffc44b;'] * len(row)
    elif row['심각도'] == '주의':
        return ['background-color: #cfe8ff;'] * len(row)
    return [''] * len(row)

log_df = st.session_state.alarm_log.copy()
if not log_df.empty:
    log_df["_t"] = pd.to_datetime(log_df["시간"])
    log_df = log_df.sort_values("_t", ascending=False).drop(columns=["_t"])

st.dataframe(
    log_df.style.apply(highlight_severity, axis=1),
    use_container_width=True,
    hide_index=True
)

# (1) 일괄 확인 버튼
if st.button("전체 경보를 확인 처리합니다"):
    st.toast("모든 경보를 확인 처리하였습니다.")

# 범례
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="display:flex; gap:30px; align-items:center; font-size:15px;">
        <div>
            <span style="background:#ff4b4b; color:white; padding:2px 6px; border-radius:4px;">빨강</span>
            <span style="margin-left:6px;"><b>위험</b> (즉시 조치 필요)</span>
        </div>
        <div>
            <span style="background:#ffc44b; padding:2px 6px; border-radius:4px;">노랑</span>
            <span style="margin-left:6px;"><b>경고</b> (상태 점검 필요)</span>
        </div>
        <div>
            <span style="background:#cfe8ff; padding:2px 6px; border-radius:4px;">파랑</span>
            <span style="margin-left:6px;"><b>주의</b> (관찰 지속)</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 5초마다 자동 갱신
st.session_state.tick += 1
time.sleep(5)
st.rerun()
