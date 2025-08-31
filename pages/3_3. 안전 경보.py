# safety_dashboard.py

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

# ======== Sidebar (minimal customize as requested) ========
def custom_sidebar():
    import os
    st.markdown("""
    <style>
      [data-testid="stSidebarNav"] { display: none !important; }
      section[data-testid="stSidebar"] {
        background: #3E4A61 !important; color: #fff !important;
      }
      section[data-testid="stSidebar"] * { color:#fff !important; }
      .sb-title { font-weight: 800; font-size: 20px; margin: 6px 0 8px 0; }
      .sb-link [data-testid="stPageLink"] a{ color:#fff !important; text-decoration:none !important; }
      .sb-link [data-testid="stPageLink"] a:hover{ background: rgba(255,255,255,0.12); border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

    def page_link_if_exists(candidates, label):
        for p in candidates:
            if os.path.exists(p):
                st.sidebar.page_link(p, label=label)
                return

    st.sidebar.markdown('<div class="sb-title">Eco-Friendship Dashboard</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sb-link">', unsafe_allow_html=True)

    # 🏠 엔트리포인트(홈)
    page_link_if_exists(["Home.py"], "🏠 홈")

    # 🧭 메인 컨트롤
    page_link_if_exists([
        "pages/1_1. 메인_컨트롤.py",
        "pages/1_1.메인_컨트롤.py",
    ], "🧭 메인 컨트롤")

    # ⚡ 에너지 모니터링
    page_link_if_exists([
        "pages/2_2. 에너지_모니터링.py",
        "pages/2_2.에너지_모니터링.py",
    ], "⚡ 에너지 모니터링")

    # ⚠️ 안전 경보
    page_link_if_exists([
        "pages/3_3. 안전 경보.py",
        "pages/3_3.안전 경보.py",
        "pages/3_3. 안전_경보.py",
        "pages/3_3.안전_경보.py",
    ], "⚠️ 안전 경보")

    # 🌱 친환경 지표 (띄어쓰기/언더스코어 모두 대응)
    page_link_if_exists([
        "pages/4_4. 친환경 지표.py",
        "pages/4_4.친환경 지표.py",
        "pages/4_4. 친환경_지표.py",
        "pages/4_4.친환경_지표.py",
    ], "🌱 친환경 지표")

    # 🔐 로그인 (공백/무공백 모두 대응)
    page_link_if_exists([
        "pages/5_5. 로그인.py",
        "pages/5_5.로그인.py",
    ], "🔐 로그인")

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <style>
      /* 기본 사이드바 내비 숨김 (커스텀 링크 사용) */
      [data-testid="stSidebarNav"] { display: none !important; }

      /* 사이드바 배경/텍스트를 헤더와 통일 (div/section 모두 호환) */
      section[data-testid="stSidebar"], div[data-testid="stSidebar"] {
        background: #3E4A61 !important;
        color: #fff !important;
      }
      section[data-testid="stSidebar"] *, div[data-testid="stSidebar"] * {
        color: #fff !important;
      }

      /* 파일 상단 전역 CSS에서 넣었던 테두리/그림자 무력화 */
      [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        border-right: none !important;
        box-shadow: none !important;
      }

      /* 제목 스타일 */
      .sb-title {
        font-weight: 800;
        font-size: 20px;
        margin: 6px 0 8px 0;
      }

      /* 링크 색/호버만 맞춤 */
      .sb-link [data-testid="stPageLink"] a{
        color:#fff !important;
        text-decoration:none !important;
        display:block;
        padding:6px 8px;
        border-radius:6px;
      }
      .sb-link [data-testid="stPageLink"] a:hover{
        background: rgba(255,255,255,0.12);
      }
    </style>
    """, unsafe_allow_html=True)

custom_sidebar()

# --- 세션 기본값 ---
st.session_state.setdefault("logged_in", False)

# LOGOUT 처리 (헤더에서 ?logout=1로 이동시 세션 해제)
qp = st.query_params
if qp.get("logout") == "1":
    st.session_state["logged_in"] = False
    # 주소창 깔끔히 정리
    try:
        st.query_params.clear()
    except Exception:
        pass

# =========================
#  상단 헤더바 + 제목 (메인과 통일)
# =========================
def top_header():
    # 레이아웃: [헤더(시계까지)] | [LOGIN]
    left, right = st.columns([1, 0.13])  # 우측 폭은 필요시 0.12~0.16 사이로 조절

    with left:
        components.html(
            """
            <div id="topbar" style="
                background:#3E4A61; color:white; padding:10px 20px;
                display:flex; justify-content:space-between; align-items:center;
                border-radius:8px; font-family:system-ui, -apple-system, Segoe UI, Roboto;">
              <div style="font-size:18px; font-weight:700;">Eco-Friendship Dashboard</div>
              <!-- 우측: 시계만 (여기서 헤더 끝) -->
              <div style="font-size:14px;">
                  <span id="clock"></span>
              </div>
            </div>
            <script>
              function updateClock(){
                var n=new Date();
                var h=String(n.getHours()).padStart(2,'0');
                var m=String(n.getMinutes()).padStart(2,'0');
                var s=String(n.getSeconds()).padStart(2,'0');
                var el=document.getElementById('clock');
                if(el) el.textContent=h+":"+m+":"+s;
              }
              updateClock();
              setInterval(updateClock,1000);
            </script>
            """,
            height=56,
        )

    with right:
        # 헤더와 수직 정렬 맞춤 + 스타일 통일
        st.markdown(
            """
            <style>
              .login-right [data-testid="stPageLink"] a{
                display:inline-block;
                width:100%;
                text-align:center;
                color:white !important; font-weight:700; text-decoration:none !important;
                background:#3E4A61; border:1px solid rgba(255,255,255,0.35);
                height:56px; line-height:56px; border-radius:8px;
              }
              .login-right [data-testid="stPageLink"] a:hover{
                background:#46526b; border-color:white;
              }
            </style>
            """,
            unsafe_allow_html=True
        )
        # ✅ 파일 경로 기준 (엔트리포인트에서 상대경로)
        st.markdown('<div class="login-right">', unsafe_allow_html=True)
        if not st.session_state.get("logged_in", False):
            st.page_link("pages/5_5. 로그인.py", label="LOGIN")
        else:
            # 로그인 상태면 LOGOUT 버튼 (동일 톤)
            if st.button("LOGOUT", use_container_width=True):
                st.session_state["logged_in"] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 페이지 큰 제목
    st.markdown(
        "<div style='font-size:26px; font-weight:800; margin:-10px 0 2px 0;'>⚠️ 안전/경보</div>",
        unsafe_allow_html=True
    )

top_header()
st.caption("실측 기반 임계값 규칙으로 안전 상태를 판정하고, 경보를 기록합니다.")
st.markdown("""
<style>
/* 페이지 큰 제목은 이미 custom div로 작게 여백 설정됨. 아래는 소제목(=subheader)만 축소 */
h2, .stMarkdown h2 {
  font-size: 20px !important;      /* 소제목을 페이지 제목보다 작게 */
  margin-top: 8px !important;
  margin-bottom: 6px !important;
  line-height: 1.25 !important;
}
/* 기본 구분선 여백 줄이기 */
hr { margin: 4px 0 !important; }
/* 테이블(데이터프레임) 셀 패딩 살짝 축소 */
[data-testid="stDataFrame"] .st-emotion-cache-1xarl3l,  /* header cell */
[data-testid="stDataFrame"] .st-emotion-cache-1y4p8pa {  /* body cell */
  padding-top: 6px !important;
  padding-bottom: 6px !important;
}
/* expander 안쪽 문단 여백 축소 */
[data-testid="stExpander"] p { margin: 4px 0 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------------------------
# 임계값(예시) — 실제 시스템에 맞추어 조정하십시오.
# ------------------------------------------------------------
THRESH = {
    # 전기/에너지
    "motor_i_warn": 8.0,         # [A]
    "motor_i_crit": 12.0,        # [A]
    "uv_drop_under_load": 1.2,   # [V]

    # 항법/주행
    "lidar_min_warn": 1.0,       # [m]
    "lidar_min_crit": 0.5,       # [m]
    "gps_sats_min": 5,           # [개]
    "speed_stall_max": 0.05,     # [m/s]
    "stall_i_min": 5.0,          # [A]

    # 시스템/데이터
    "data_timeout_s": 5,         # [s]
    "pi_temp_warn": 70.0,        # [°C]
    "pi_temp_crit": 80.0,        # [°C]
}

SEVERITY_ORDER = {"주의": 1, "경고": 2, "위험": 3}

# ------------------------------------------------------------
# 경보 디바운스/쿨다운(데모 완화: 트리거 빈도 제어)
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
# 더미: 6단계 데모 시나리오(5초 주기)
# ------------------------------------------------------------
def read_latest(prev=None):
    now = datetime.now()
    phase = st.session_state.tick % 6

    # 기본은 정상 범위
    lidar_min = 2.4 + np.random.normal(0, 0.15)
    cam_obstacle_center = False
    gps_speed = abs(0.55 + np.random.normal(0, 0.08))
    motor_i = abs(np.random.normal(1.6, 0.5))
    pi_temp = 55 + np.random.normal(0, 1.5)
    link_age = np.random.uniform(0, 1.0)

    # 단계별 시나리오
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
# 실시간 시스템 상태 — 카드 5개 (사진 스타일)
# ------------------------------------------------------------
st.subheader("실시간 시스템 상태")

# ✅ 카드 공용 CSS (사진 톤)
st.markdown("""
<style>
.status-card{
  background:#E8FAF1;                 /* 연한 민트 배경 */
  border:1px solid #C8EEDC;            /* 연녹 테두리 */
  border-radius:18px;                  /* 둥근 모서리 */
  box-shadow: 0 2px 6px rgba(0,0,0,0.04); /* 아주 약한 그림자 */
  padding:16px 18px;
  min-height:110px;                    /* 높이 통일감 */
  display:flex; flex-direction:column; justify-content:center;
}
.status-card .title{
  display:flex; align-items:center; gap:10px; flex-wrap:nowrap;
  font-weight:800; font-size:18px; color:#0b3d2e; /* 진한 녹 톤 */
}
.status-card .title .icon{ font-size:20px; line-height:1; }
.status-card .title .tag{ font-size:12px; font-weight:600; color:#6b7280; margin-left:4px; }
.status-card .value{
  margin-top:8px;
  font-size:22px; font-weight:800; color:#0b3d2e;  /* 값은 더 굵고 크게 */
  text-align:center;
}
.status-card .sub{
  margin-top:4px; font-size:12px; opacity:.85;
}
</style>
""", unsafe_allow_html=True)

def stat_card(icon: str, title: str, value: str, sub: str | None = None,
              tone: str = "neutral", title_tag: str | None = None):
    # tone 파라미터는 무시(사진처럼 단일 스타일)
    html = f"""
    <div class="status-card">
      <div class="title">
        <span class="icon">{icon}</span>
        <span>{title}</span>
        {'<span class="tag">'+title_tag+'</span>' if title_tag else ''}
      </div>
      <div class="value">{value}</div>
      {f'<div class="sub">{sub}</div>' if sub else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# 그대로 사용
TH = THRESH
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    stat_card("📡", "LiDAR 최소거리", f"{sample['lidar_min']:.2f} m")
with c2:
    stat_card("🎥", "카메라 전방", "감지됨" if sample["cam_obstacle_center"] else "정상")
with c3:
    stat_card("🚤", "선박 속도", f"{sample['gps_speed']:.2f} m/s")
with c4:
    stat_card("⚙️", "모터 전류", f"{sample['motor_i']:.2f} A")
with c5:
    stat_card("📶", "데이터 지연", f"{sample['link_age']:.2f} s", title_tag=f"(임계 {TH['data_timeout_s']}s)")

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
