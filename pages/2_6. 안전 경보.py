# safety_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="안전/경보 대시보드",
    page_icon="⚠️",
    layout="wide",
)

# 사이드바 제목(이모지 포함)
st.sidebar.title("⚠️ 안전/경보 메뉴")
st.sidebar.caption("실측 기반 규칙으로 안전 상태를 판정합니다.")

st.title("⚠️ 안전/경보 (Safety/Alarm)")
st.caption("실측 기반 임계값 규칙으로 안전 상태를 판정하고, 경보를 기록합니다.")
st.markdown("---")

# ------------------------------------------------------------
# 임계값(예시) — 실제 시스템에 맞추어 조정하십시오.
# ------------------------------------------------------------
THRESH = {
    # 전기/에너지
    "batt_v_min": 10.8,          # [V]
    "batt_v_crit": 10.2,         # [V]
    "batt_soc_low": 20.0,        # [%]
    "motor_i_warn": 8.0,         # [A]
    "motor_i_crit": 12.0,        # [A]
    "esc_temp_warn": 60.0,       # [°C]
    "esc_temp_crit": 75.0,       # [°C]
    "uv_drop_under_load": 1.2,   # [V]

    # 항법/주행
    "lidar_min_warn": 1.0,       # [m]
    "lidar_min_crit": 0.5,       # [m]
    "gps_sats_min": 5,           # [개] (경보 규칙용 내부 사용)
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
PERSIST_N = 1       # 데모: 1회 충족 시 즉시 발생
COOLDOWN_S = 0      # 데모: 같은 알람 트리거 쿨다운 없음(로그는 별도 쿨다운 적용)

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
# 더미: 6단계 데모 시나리오(5초 주기) → 30초 내 정상/주의/경고/위험 모두 노출
#   0: 정상
#   1: 주의 (배터리 SoC 낮음)
#   2: 경고 (LiDAR 접근)
#   3: 위험 (LiDAR 임박)
#   4: 경고 (모터 과전류 경고)
#   5: 주의 (GPS 위성 부족)   *GPS 값은 표시하지 않지만 규칙 내부에서는 사용 가능
# ------------------------------------------------------------
def read_latest(prev=None):
    now = datetime.now()
    phase = st.session_state.tick % 6

    # 기본은 정상 범위
    batt_v  = 12.2 + np.random.normal(0, 0.1)
    batt_soc = np.clip(65 + np.random.normal(0, 5), 0, 100)
    motor_i = abs(np.random.normal(3.0, 1.0))
    motor_v = 12.0 + np.random.normal(0, 0.1)
    esc_temp = 52 + np.random.normal(0, 2)
    pemfc_v = 12.5 + np.random.normal(0, 0.2)
    pemfc_i = max(0, 0.6 + np.random.normal(0, 0.05))
    solar_v = 17.5 + np.random.normal(0, 0.3)
    solar_i = max(0, 0.4 + np.random.normal(0, 0.05))
    lidar_min = 1.8 + np.random.normal(0, 0.1)
    gps_sats = int(np.clip(8 + np.random.normal(0, 0.5), 0, 12))
    gps_speed = abs(0.28 + np.random.normal(0, 0.03))
    pi_temp = 55 + np.random.normal(0, 1.0)
    link_age = np.random.uniform(0, 1.0)

    # 단계별 시나리오
    if phase == 1:
        batt_soc = 15.0  # 주의
    elif phase == 2:
        lidar_min = 0.8  # 경고
    elif phase == 3:
        lidar_min = 0.3  # 위험
    elif phase == 4:
        motor_i = THRESH["motor_i_warn"] + 1.0  # 경고
    elif phase == 5:
        gps_sats = THRESH["gps_sats_min"] - 1   # 주의 (표시는 안 함)

    # 전력 계산(개략)
    motor_p = max(0, motor_v * motor_i)
    gen_p = max(0, pemfc_v * pemfc_i) + max(0, solar_v * solar_i)
    power_balance = gen_p - motor_p

    # 전압강하(로드 드롭): 이전 배터리 전압 대비
    uv_drop = 0.0
    if prev is not None:
        uv_drop = max(0.0, prev["batt_v"] - batt_v)

    return {
        "ts": now,
        "batt_v": batt_v,
        "batt_soc": batt_soc,
        "motor_i": motor_i,
        "motor_v": motor_v,
        "motor_p": motor_p,
        "esc_temp": esc_temp,
        "pemfc_v": pemfc_v,
        "pemfc_i": pemfc_i,
        "solar_v": solar_v,
        "solar_i": solar_i,
        "gen_p": gen_p,
        "power_balance": power_balance,
        "lidar_min": lidar_min,
        "gps_sats": gps_sats,
        "gps_speed": gps_speed,
        "pi_temp": pi_temp,
        "link_age": link_age,
        "uv_drop": uv_drop,
    }

# ------------------------------------------------------------
# 규칙 평가 → 경보 생성 (측정치 연동)
# ------------------------------------------------------------
def evaluate_rules(x):
    alarms = []

    # 배터리 전압/SoC
    _push_alarm(alarms, "batt_v_crit", "배터리 저전압", "위험",
                f"{x['batt_v']:.2f}V < {THRESH['batt_v_crit']}V",
                x["batt_v"] < THRESH["batt_v_crit"])
    _push_alarm(alarms, "batt_v_min", "배터리 저전압", "경고",
                f"{x['batt_v']:.2f}V < {THRESH['batt_v_min']}V",
                x["batt_v"] < THRESH["batt_v_min"])
    _push_alarm(alarms, "batt_soc_low", "배터리 SoC 낮음", "주의",
                f"{x['batt_soc']:.1f}% < {THRESH['batt_soc_low']}%",
                x["batt_soc"] < THRESH["batt_soc_low"])

    # 모터 과전류
    _push_alarm(alarms, "motor_i_crit", "모터 과전류", "위험",
                f"{x['motor_i']:.1f}A > {THRESH['motor_i_crit']}A",
                x["motor_i"] > THRESH["motor_i_crit"])
    _push_alarm(alarms, "motor_i_warn", "모터 과전류", "경고",
                f"{x['motor_i']:.1f}A > {THRESH['motor_i_warn']}A",
                x["motor_i"] > THRESH["motor_i_warn"])

    # ESC/모터 온도
    _push_alarm(alarms, "esc_temp_crit", "ESC/모터 과열", "위험",
                f"{x['esc_temp']:.1f}°C > {THRESH['esc_temp_crit']}°C",
                x["esc_temp"] > THRESH["esc_temp_crit"])
    _push_alarm(alarms, "esc_temp_warn", "ESC/모터 과열", "경고",
                f"{x['esc_temp']:.1f}°C > {THRESH['esc_temp_warn']}°C",
                x["esc_temp"] > THRESH["esc_temp_warn"])

    # 부하 중 전압강하
    _push_alarm(alarms, "uv_drop", "부하 전압강하", "주의",
                f"ΔV={x['uv_drop']:.2f}V > {THRESH['uv_drop_under_load']}V",
                (x["uv_drop"] > THRESH["uv_drop_under_load"]) and (x["motor_i"] > 1.0))

    # 발전-소비 불균형(데모 완화)
    _push_alarm(alarms, "power_balance", "전력 불균형(방전 우세)", "경고",
                f"{x['power_balance']:.1f} W", x["power_balance"] < -20.0)

    # LiDAR
    _push_alarm(alarms, "lidar_crit", "충돌 임박", "위험",
                f"{x['lidar_min']:.2f} m < {THRESH['lidar_min_crit']} m",
                x["lidar_min"] < THRESH["lidar_min_crit"])
    _push_alarm(alarms, "lidar_warn", "장애물 접근", "경고",
                f"{x['lidar_min']:.2f} m < {THRESH['lidar_min_warn']} m",
                x["lidar_min"] < THRESH["lidar_min_warn"])

    # GPS/스톨 (표시는 제거했지만 규칙은 유지 가능)
    _push_alarm(alarms, "gps_sats_low", "GPS 신호 불량", "주의",
                f"{x['gps_sats']} < {THRESH['gps_sats_min']} 위성",
                x["gps_sats"] < THRESH["gps_sats_min"])
    _push_alarm(alarms, "stall_suspect", "추진 스톨 의심", "경고",
                f"속도 {x['gps_speed']:.2f} m/s, 전류 {x['motor_i']:.1f} A",
                (x["gps_speed"] < THRESH["speed_stall_max"]) and (x["motor_i"] > THRESH["stall_i_min"]))

    # 시스템/데이터
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
# 세션 상태 준비 (로그 및 로그 쿨다운)
# ------------------------------------------------------------
if "last_sample" not in st.session_state:
    st.session_state.last_sample = None
if "alarm_log" not in st.session_state:
    st.session_state.alarm_log = pd.DataFrame(columns=["시간", "경보 종류", "심각도", "세부"])
if "last_logged" not in st.session_state:
    st.session_state.last_logged = {}   # {경보 종류: 마지막 로그 시각}

LOG_COOLDOWN_S = 20  # 같은 '경보 종류'는 20초 이내 재기록 안 함

# ------------------------------------------------------------
# 최신 데이터 읽기 & 규칙 평가
# ------------------------------------------------------------
sample = read_latest(st.session_state.last_sample)
alarms = evaluate_rules(sample)
st.session_state.last_sample = sample

# 최상위 심각도
top_sev = max([SEVERITY_ORDER[a[1]] for a in alarms], default=0)

# ------------------------------------------------------------
# 실시간 시스템 상태 (예쁜 카드 UI)
# ------------------------------------------------------------
st.subheader("실시간 시스템 상태")

def stat_card(icon: str, title: str, value: str, sub: str | None = None, tone: str = "neutral"):
    # 영롱한 파스텔 그라디언트 팔레트
    gradients = {
        "neutral": "linear-gradient(135deg, #EEF2FF 0%, #E9F5FF 100%)",  # 라일락-스카이
        "ok":      "linear-gradient(135deg, #E6FFF5 0%, #EAFFF0 100%)",  # 민트-그린
        "warn":    "linear-gradient(135deg, #FFF7E6 0%, #FFF1E6 100%)",  # 살구-앰버
        "danger":  "linear-gradient(135deg, #FFE6EA 0%, #FFD6E1 100%)",  # 로즈-핑크
    }
    borders = {
        "neutral": "#c9d6ea",
        "ok": "#9ad7a6",
        "warn": "#f3cc69",
        "danger": "#f08b86",
    }
    bg = gradients.get(tone, gradients["neutral"])
    bd = borders.get(tone, borders["neutral"])
    html = f"""
    <div style="
        background:{bg};
        border:1px solid {bd};
        border-radius:16px;
        padding:14px 16px;
        height:100%;
        box-shadow:0 2px 10px rgba(0,0,0,0.06)">
      <div style="font-size:18px; font-weight:700; display:flex; gap:8px; align-items:center;">
        <span style="font-size:20px;">{icon}</span>{title}
      </div>
      <div style="font-size:22px; font-weight:800; margin-top:6px;">{value}</div>
      {"<div style='opacity:0.8; margin-top:4px; font-size:13px;'>"+sub+"</div>" if sub else ""}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 카드 표시하기 전에 톤 계산 ---
tone_batt  = "danger" if sample["batt_v"] < THRESH["batt_v_crit"] else ("warn" if sample["batt_v"] < THRESH["batt_v_min"] else "ok")
tone_soc   = "warn" if sample["batt_soc"] < THRESH["batt_soc_low"] else "ok"
tone_motor = "danger" if sample["motor_i"] > THRESH["motor_i_crit"] else ("warn" if sample["motor_i"] > THRESH["motor_i_warn"] else "ok")
tone_gen   = "neutral"
tone_lidar = "danger" if sample["lidar_min"] < THRESH["lidar_min_crit"] else ("warn" if sample["lidar_min"] < THRESH["lidar_min_warn"] else "ok")

# --- 카드 출력 (tone을 '키워드 인자'로 전달해야 함!)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    stat_card("🔋", "배터리 전압", f"{sample['batt_v']:.2f} V", tone=tone_batt)
with c2:
    stat_card("🪫", "배터리 SoC", f"{sample['batt_soc']:.1f} %", tone=tone_soc)
with c3:
    stat_card("⚙️", "모터 전류", f"{sample['motor_i']:.1f} A", tone=tone_motor)
    # ✅ 가운데 정렬, 파란색, 16px
    st.markdown(
        f"<div style='color:#1f77b4; font-size:16px; font-weight:600; text-align:center; margin-top:4px;'>"
        f"P ≈ {sample['motor_p']:.0f} W</div>",
        unsafe_allow_html=True
    )
with c4:
    stat_card("⚡", "발전 합계", f"{sample['gen_p']:.0f} W", tone=tone_gen)
    # ✅ 가운데 정렬, 파란색, 16px
    st.markdown(
        f"<div style='color:#1f77b4; font-size:16px; font-weight:600; text-align:center; margin-top:4px;'>"
        f"ΔP = {sample['power_balance']:.0f} W</div>",
        unsafe_allow_html=True
    )
with c5:
    stat_card("📡", "LiDAR 최소거리", f"{sample['lidar_min']:.2f} m", tone=tone_lidar)


# 최상위 심각도 배너
if top_sev == SEVERITY_ORDER["위험"]:
    st.error("위험 상태입니다. 즉시 조치하십시오.", icon="🚨")
elif top_sev == SEVERITY_ORDER["경고"]:
    st.warning("경고 상태입니다. 동작 상태를 점검하십시오.", icon="⚠️")
else:
    st.success("정상 상태입니다. 특이사항이 없습니다.", icon="✅")

# 규칙 설명(접이식)
with st.expander("경보 규칙"):
    st.markdown(
        """
        - **전기/에너지**: 배터리 전압·SoC, 모터 전류·전력, 부하 전압강하, 전력 불균형을 점검합니다.  
        - **항법/주행**: LiDAR 최소거리와 속도를 근거로 장애물 접근 및 추진 스톨을 탐지합니다.  
        - **시스템/데이터**: 링크 지연과 라즈베리파이 CPU 온도를 점검합니다.  
        ※ 모든 경보는 위 지표의 **실측 값**에 기반하여 산출합니다.
        """
    )

# ------------------------------------------------------------
# 이번 측정에서 감지된 경보 (index 숨김)
# ------------------------------------------------------------
st.markdown("### 위험 감지")
if alarms:
    df_now = pd.DataFrame(
        [{"시간": sample["ts"].strftime("%Y-%m-%d %H:%M:%S"),
          "경보 종류": a[0], "심각도": a[1], "세부": a[2]} for a in alarms]
    )
    st.dataframe(df_now, use_container_width=True, hide_index=True)

    # 로그 기록(같은 경보 종류 20초 쿨다운)
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
# 하단: 경보 발생 로그 (index 숨김)
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

# 범례 위 여백
st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

# (2) 색상 범례 (한 줄 배치)
st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

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

st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

# 범례 아래 여백
st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# 5초마다 자동 갱신 + tick 증가
# ------------------------------------------------------------
st.session_state.tick += 1
time.sleep(5)
st.rerun()
