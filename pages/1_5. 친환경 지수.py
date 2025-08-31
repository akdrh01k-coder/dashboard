# pages/1_5. 친환경 지수.py
import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu  # ✅ 추가
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from urllib import parse as _url
import time

# ========== 기본 설정 ==========
st.set_page_config(
    page_title="친환경 지표",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ 기본 멀티페이지 사이드바 내비 숨김 (option_menu/커스텀만 보이게)
st.markdown("""
<style>
  [data-testid="stSidebarNav"] { display: none !important; }
  section[data-testid="stSidebar"] nav { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ========== 팔레트 ==========
COL = {
    "primary":  "#2563eb",
    "title":    "#0f172a",
    "success":  "#16a34a",
    "warn":     "#f59e0b",
    "danger":   "#dc2626",
    "muted":    "#64748b",
    "border":   "#e5e7eb",
    "card":     "#ffffff",
    "header":   "#f1f5f9",
    "app_bg":   "#ffffff",
    "hydrogen": "#0ea5e9",
    "solar":    "#f59e0b",
    "other":    "#e2e8f0",
    "motor":    "#475569",
    "teal":     "#14b8a6",
    "sidebar_bg": "#F1F1F9",
}

# ========== 전역 스타일 ==========
now_str = datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
<style>
/* 기본 UI 정리 */
#MainMenu, header, footer {{visibility: hidden;}}
.main .block-container {{ padding-top: 96px !important; }}  /* 상단바와 여백 매칭 */

/* 상단 고정 헤더바 (메인/안전 페이지와 동일) */
.app-topbar{{
  position: fixed; top:0; left:0; right:0; height:64px;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 22px; z-index:1000;
  color:#fff; border-bottom:1px solid rgba(255,255,255,.15);
  background:linear-gradient(90deg,#3b4a67 0%, #536a92 100%);
  box-shadow:0 8px 24px rgba(0,0,0,.18);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
}}
.app-topbar .brand{{ font-weight:800; letter-spacing:.2px; }}
.app-topbar .right{{ display:flex; gap:14px; align-items:center; }}
.app-pill{{ background:rgba(255,255,255,.18); padding:6px 10px; border-radius:999px; font-weight:700; }}
.app-link{{ color:#fff; text-decoration:none; }}
.app-link:hover{{ text-decoration:underline; }}

/* 페이지 상단 섹션 헤더 */
.page-header{{
  margin: 6px 0 16px 0; padding: 14px 16px;
  background: linear-gradient(90deg,#eef4ff,#ffffff);
  border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.06);
  display:flex; align-items:center; justify-content:space-between; gap:12px;
}}
.page-title{{font-size:22px; font-weight:800; color:#1f2b4d;}}
.page-sub{{font-size:13px; color:#64748b;}}

/* 카드 공통 */
.card {{
  background: {COL["card"]};
  border: 1px solid {COL["border"]};
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.06);
}}
.card-header {{
  background: {COL["header"]};
  border: 1px solid {COL["border"]};
  border-radius: 10px;
  padding: 8px 12px;
  margin-bottom: 8px;
  display:flex; justify-content:space-between; align-items:center;
}}
.card-title {{
  font-weight: 800; letter-spacing: -.01em;
  color: {COL["title"]}; font-size: 16px;
}}
.badge {{
  padding: 4px 10px; border-radius: 999px; color: #fff;
  font-weight: 700; font-size: 12px;
}}
.status-banner {{
  width:100%; border-radius: 8px; padding: 10px 12px;
  color: white; font-weight: 800; font-size: 14px;
  text-align:left; display:flex; gap:8px; align-items:center;
}}
.action-box {{
  border: 1px dashed {COL["border"]}; background: #f8fafc;
  border-radius: 10px; padding: 8px 10px; margin-top: 8px;
}}
.action-box ul {{ margin: 0 0 0 18px; padding: 0; }}
.action-box li {{ font-size: 12.5px; color: #334155; margin: 4px 0; }}
.big-num {{ font-weight: 900; font-size: 28px; color: {COL["title"]}; }}
.subtle {{ color:#334155; opacity:.9; font-size:13px; }}

/* 헤더/사이드바 토글 버튼 z-index */
[data-testid="stHeader"] {{ z-index: 0 !important; background: transparent !important; }}
.app-topbar {{ z-index: 99999 !important; }}
[data-testid="stSidebarCollapseControl"],
[data-testid="stSidebarCollapseButton"]{{
  position:fixed; top:12px; left:12px;
  z-index:100000 !important;
  display:flex !important; opacity:1 !important; pointer-events:auto !important;
}}

</style>

<!-- 상단 고정 헤더바 -->
<div class="app-topbar">
  <div class="brand">Eco-Friendship Dashboard</div>
  <div class="right">
    <div class="app-pill" id="clock">{now_str}</div>
    <a class="app-pill app-link" href="/pages/3_7. 로그인" target="_self" rel="noopener">Login</a>
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

# ========== 페이지 상단 헤더 ==========
def page_header(title: str, subtitle: str | None = None):
    right = f"<div class='page-sub'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="page-header">
          <div class="page-title">{title}</div>
          {right}
        </div>
        """,
        unsafe_allow_html=True
    )

# ======== Sidebar (기존 유지, 약간의 스타일만) ========
def custom_sidebar():
    st.markdown("""
    <style>
      [data-testid="stSidebarNav"] { display: none !important; }
      section[data-testid="stSidebar"] {
        background: #3E4A61 !important;
        color: #fff !important;
      }
      section[data-testid="stSidebar"] * { color:#fff !important; }
      .sb-title {
        font-weight: 800;
        font-size: 20px;
        margin: 6px 0 8px 0;
      }
      .sb-link [data-testid="stPageLink"] a{
        color:#fff !important;
        text-decoration:none !important;
      }
      .sb-link [data-testid="stPageLink"] a:hover{
        background: rgba(255,255,255,0.12);
        border-radius: 6px;
      }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown('<div class="sb-title">Eco-Friendship Dashboard</div>', unsafe_allow_html=True)

    st.sidebar.markdown('<div class="sb-link">', unsafe_allow_html=True)
    st.sidebar.page_link("pages/1_5. 친환경 지수.py", label="🌱 친환경 지표")
    st.sidebar.page_link("pages/2_6. 안전 경보.py", label="⚠️ 안전/경보")
    st.sidebar.page_link("pages/3_7. 로그인.py",     label="🔐 로그인")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

custom_sidebar()

# ========== 친환경 지표 설정 ==========
CONFIG = {
    "WARMUP_SAMPLES": 60,
    "V_MAX_BONUS": 1.2,
    "EFF_W_ECO": 0.7,
    "EFF_W_SPEED": 0.3,
    "INIT_REF_SPW": 0.002,
    "EF_DIESEL": 720.0,
    "EF_FC": 0.0,
    "EF_PV": 0.0,
}

# ========== 상단 페이지 타이틀 ==========
page_header("🌱 친환경 지표")

# ---------- 세션 ----------
if "history" not in st.session_state:
    st.session_state["history"] = pd.DataFrame(
        columns=[
            "time","motor_w","fc_w","pv_w","batt_w","other_w",
            "eff_index","eco_ratio","V_score",
            "co2_saved_g","co2_cum_t","ship_speed",
            "co2_diesel_g","co2_actual_g","co2_diesel_cum_t","co2_actual_cum_t"
        ]
    )
if "saved_co2_t" not in st.session_state:
    st.session_state["saved_co2_t"] = 0.0
if "ref_samples" not in st.session_state:
    st.session_state["ref_samples"] = []

# ---------- 더미 데이터 ----------
motor_w = float(np.random.uniform(90, 180))
eco_share = float(np.random.uniform(0.35, 0.80))
eco_total = motor_w * eco_share
fc_w = eco_total * np.random.uniform(0.3, 0.7)
pv_w = eco_total - fc_w
other_w = max(0.0, motor_w - (fc_w + pv_w))
batt_w = float(min(other_w, np.random.uniform(10, 60)))  # 기록용

# ---------- 속도(데모) ----------
ship_speed = float(np.random.uniform(0.6, 1.6))  # m/s

# ---------- 친환경 비중 & 속도 효율 ----------
eco_ratio = (fc_w + pv_w) / max(1e-6, motor_w) * 100.0  # %
speed_per_w = ship_speed / max(1e-6, motor_w)

# ref 학습(디젤 위주 구간)
if eco_ratio < 10:
    st.session_state["ref_samples"].append(speed_per_w)
    st.session_state["ref_samples"] = st.session_state["ref_samples"][-500:]

ref_spw = float(np.median(st.session_state["ref_samples"])) if st.session_state["ref_samples"] else CONFIG["INIT_REF_SPW"]
ratio = speed_per_w / max(1e-9, ref_spw)
V_score = float(100.0 * np.clip(ratio / CONFIG["V_MAX_BONUS"], 0.0, 1.0))

# ---------- 최종 에너지 효율 지수 ----------
eff_index = float(CONFIG["EFF_W_ECO"] * eco_ratio + CONFIG["EFF_W_SPEED"] * V_score)
eff_index = float(np.clip(eff_index, 0.0, 100.0))

# ---------- CO2 절감량(운항단계) ----------
E_kWh = motor_w * 5.0 / 3_600_000.0
fc_share = fc_w / max(1e-6, motor_w)
pv_share = pv_w / max(1e-6, motor_w)
diesel_share = max(0.0, 1.0 - (fc_share + pv_share))
EFd = CONFIG["EF_DIESEL"]; EFfc = CONFIG["EF_FC"]; EFpv = CONFIG["EF_PV"]
co2_diesel_only_g = E_kWh * EFd
co2_actual_g = E_kWh * (EFd * diesel_share + EFfc * fc_share + EFpv * pv_share)
co2_saved_g = max(0.0, co2_diesel_only_g - co2_actual_g)

# 누적 (tCO2)
prev_cum_t = float(st.session_state.get("saved_co2_t", 0.0))
co2_cum_t = float(prev_cum_t + co2_saved_g/1_000_000.0)
st.session_state["saved_co2_t"] = co2_cum_t

# 기록
now = pd.Timestamp.utcnow()
new_row = {
    "time":now,
    "motor_w":motor_w,"fc_w":fc_w,"pv_w":pv_w,"batt_w":batt_w,"other_w":other_w,
    "eff_index":eff_index,"eco_ratio":eco_ratio,"V_score":V_score,
    "co2_saved_g":co2_saved_g,"co2_cum_t":co2_cum_t,"ship_speed":ship_speed,
    "co2_diesel_g":co2_diesel_only_g,"co2_actual_g":co2_actual_g,
    "co2_diesel_cum_t":np.nan,"co2_actual_cum_t":np.nan
}
st.session_state["history"] = pd.concat(
    [st.session_state["history"], pd.DataFrame([new_row])],
    ignore_index=True
).tail(500)

# 누적 라인 계산
hist = st.session_state["history"].copy()
if not hist.empty:
    hist["co2_diesel_cum_t"] = (hist["co2_diesel_g"].fillna(0).cumsum())/1_000_000.0
    hist["co2_actual_cum_t"] = (hist["co2_actual_g"].fillna(0).cumsum())/1_000_000.0

# 등급
def grade_by_eff(idx: float):
    if idx >= 85: return "A","안전 항해",COL["success"]
    if idx >= 70: return "B","양호",COL["primary"]
    if idx >= 55: return "C","주의",COL["warn"]
    return "D","비효율",COL["danger"]
grade, grade_text, grade_color = grade_by_eff(eff_index)

# 권장 액션
actions = []
if grade in ["C","D"]:
    actions.append("효율 저하: 추진계 정렬·프로펠러·베어링 점검 권장.")
if (len(hist) >= 10):
    y = hist["eff_index"].tail(10).astype(float).values
    if y.size > 1 and np.polyfit(np.arange(len(y)), y, 1)[0] < -0.3:
        actions.append("하락 추세: 최근 급가감속·하중 변동 여부 확인.")
if (grade == "B") and (eco_ratio < 60):
    actions.append("개선 포인트: 재생 비중을 높이고 불필요한 가감속을 줄이면 A에 근접.")
if not actions:
    actions.append("안정 운영: 현재 전략 유지하며 데이터 누적.")

# =========================
# 상단: 지수(반원 게이지) / 좌(에너지비중) / 우(CO2·그린운항)
# =========================
c1, c2 = st.columns([1.35, 2.15], gap="small")

# c1 — 에너지 효율 지수
with c1:
    st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card-header"><div class="card-title">📊 에너지 효율 지수</div>'
        f'<span class="badge" style="background:{grade_color};">{grade_text}</span></div>',
        unsafe_allow_html=True,
    )
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(eff_index,1),
        number={"suffix":" %","font":{"size":24, "color":"#1e293b"}},
        gauge={
            "axis":{"range":[0,100], "tickmode":"linear", "dtick":10, "ticks":"outside",
                    "tickfont":{"size":12}, "tickcolor":"#94a3b8"},
            "bar":{"thickness":0.25,"color":grade_color},
            "steps":[
                {"range":[0,55],"color":"#fee2e2"},
                {"range":[55,70],"color":"#ffedd5"},
                {"range":[70,85],"color":"#dbeafe"},
                {"range":[85,100],"color":"#dcfce7"},
            ],
        },
        domain={"x":[0,1], "y":[0.10,1]}
    ))
    # 🔧 위 dict 표기 주의: streamlit 복붙 시 중괄호 2번이 set로 오인되면 에러 → 한 번만 남기세요.
    gauge.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=40, b=32),
        paper_bgcolor="white", plot_bgcolor="white"
    )
    st.plotly_chart(gauge, use_container_width=True, theme=None)

    st.markdown(
        f'<div class="card-header" style="margin-top:36px;"><div class="card-title">💡 등급 & 상태</div>'
        f'<span class="badge" style="background:{grade_color};">등급 {grade}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="status-banner" style="background:{grade_color};">✅ <span>{grade_text}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="action-box"><ul>{"".join([f"<li>{a}</li>" for a in actions])}</ul></div>',
        unsafe_allow_html=True,
    )
    with st.expander("에너지 효율 지수 계산식"):
        st.markdown(
            """
            - **R(친환경 비중)** = (연료전지 + 태양광) / 모터소비전력 × 100  
            - **V(속도 효율)** = 100 × clamp( ( (속도/전력) / ref ) / 1.2, 0, 1 )  
            - **최종 지수** = 0.7 × R + 0.3 × V  
            *ref는 eco_ratio < 10% 구간의 최근 중앙값(m/s per W)이며, ref의 1.2배 성능에서 100점으로 캡핑.*
            """
        )
    st.markdown('</div>', unsafe_allow_html=True)

# c2 — 좌(친환경 비중) / 우(CO2·그린운항)
with c2:
    left, right = st.columns(2, gap="small")

    # 좌: 친환경 에너지 비중
    with left:
        st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card-header"><div class="card-title">🌱 친환경 에너지 비중</div>'
            f'<span class="badge" style="background:{COL["teal"]};">{eco_ratio:.1f}%</span></div>',
            unsafe_allow_html=True,
        )
        fc_pct = fc_w / motor_w * 100.0
        pv_pct = pv_w / motor_w * 100.0
        other_pct = other_w / motor_w * 100.0

        fig_mix = go.Figure()
        fig_mix.add_trace(go.Bar(name="수소 연료전지", x=["공급원"], y=[fc_w],
                                 marker_color=COL["hydrogen"],
                                 text=[f"{fc_w:.0f}W ({fc_pct:.1f}%)"], textposition="inside"))
        fig_mix.add_trace(go.Bar(name="태양광", x=["공급원"], y=[pv_w],
                                 marker_color=COL["solar"],
                                 text=[f"{pv_w:.0f}W ({pv_pct:.1f}%)"], textposition="inside"))
        fig_mix.add_trace(go.Bar(name="보충", x=["공급원"], y=[other_w],
                                 marker_color=COL["other"],
                                 text=[f"{other_w:.0f}W ({other_pct:.1f}%)"], textposition="inside"))
        fig_mix.add_trace(go.Bar(name="모터 부하", x=["모터"], y=[motor_w],
                                 marker_color=COL["motor"],
                                 text=[f"{motor_w:.0f}W (100%)"], textposition="inside"))

        fig_mix.update_layout(
            barmode="relative", height=260,
            margin=dict(t=20, b=20, l=56, r=20),
            yaxis=dict(title="출력 (W)", title_standoff=12, automargin=True, gridcolor=COL["border"]),
            paper_bgcolor="white", plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_mix, use_container_width=True, theme=None)
        st.markdown('</div>', unsafe_allow_html=True)

    # 우: CO2 절감량 + 그린 운항 시간 비율
    with right:
        st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)

        st.markdown(
            f'<div class="card-header"><div class="card-title">🌍 CO₂ 절감량</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='big-num'>{co2_saved_g:.2f} g</div>", unsafe_allow_html=True)
        if not hist.empty:
            st.caption(f"누적 절감: {hist['co2_diesel_cum_t'].iloc[-1] - hist['co2_actual_cum_t'].iloc[-1]:,.3f} tCO₂")
        else:
            st.caption("누적 절감: 0.000 tCO₂")
        with st.expander("이산화탄소 절감량 계산식"):
            st.markdown(
                """
                - **E** = (모터전력 × 5초) / 3,600,000 → kWh  
                - **실제배출** = E × [ EF<sub>diesel</sub>×(1−(FC+PV)비중) + EF<sub>FC</sub>×FC비중 + EF<sub>PV</sub>×PV비중 ]  
                - **디젤기준배출** = E × EF<sub>diesel</sub>  
                - **절감량** = 디젤기준배출 − 실제배출 (gCO₂)  
                *기본값: EF<sub>diesel</sub>=720 gCO₂/kWh, EF<sub>FC</sub>=0, EF<sub>PV</sub>=0 (운항단계)*
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div class="card-header" style="margin-top:8px;"><div class="card-title">🟢 그린 운항 시간비율</div></div>',
            unsafe_allow_html=True,
        )

        # 5분 주기 샘플 × 12 = 최근 1시간
        win = 12
        eco_tail = hist["eco_ratio"].astype(float).tail(win) if not hist.empty else pd.Series([eco_ratio])
        green_ratio = (eco_tail >= 60).mean() * 100.0

        st.markdown(f"<div class='big-num'>{green_ratio:.1f} %</div>", unsafe_allow_html=True)

        # 라인 그래프 (축 눈금 표시)
        mini = go.Figure()
        if not eco_tail.empty:
            mini.add_scatter(
                x=list(range(len(eco_tail))), y=eco_tail.values,
                mode="lines", name="재생 비중(%)", line=dict(width=2)
            )
            mini.add_hline(y=60, line_width=1, line_dash="dot")

        mini.update_layout(
            height=110,
            margin=dict(l=40, r=30, t=4, b=40),
            yaxis=dict(title="", showticklabels=True, gridcolor=COL["border"]),
            xaxis=dict(title="", showticklabels=True),
            paper_bgcolor="white", plot_bgcolor="white", showlegend=False
        )
        st.plotly_chart(mini, use_container_width=True, theme=None)

        with st.expander("그린 운항 시간 비율 계산식"):
            st.markdown(
                """ 
                - **eco_ratio** = (연료전지+태양광) / 모터소비전력 × 100  
                - **그린 운항 시간비율(%)** = ( eco_ratio ≥ 60% 인 샘플 수 / 전체 샘플 수 ) × 100
                """
            )

# =========================
# 하단: 비교 그래프 2개 (카드+헤더 포함)
# =========================
st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
g_left, g_right = st.columns(2, gap="small")

with g_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="card-header"><div class="card-title">📈 에너지 효율 지수 비교 (Eco vs Diesel)</div></div>',
        unsafe_allow_html=True
    )
    comp_df = hist.tail(240)
    fig_eff = go.Figure()
    if not comp_df.empty:
        fig_eff.add_scatter(
            x=comp_df["time"], y=comp_df["eff_index"],
            mode="lines", name="Eco-friendShip (지수)",
            line=dict(width=2, color=COL["primary"])
        )
        fig_eff.add_scatter(
            x=comp_df["time"], y=0.3*comp_df["V_score"],
            mode="lines", name="Diesel baseline (지수)",
            line=dict(width=2, color="#475569", dash="dash")
        )
    fig_eff.update_layout(
        height=240, margin=dict(l=40, r=30, t=10, b=40),
        yaxis=dict(title="지수 (0~100)", range=[0,100], gridcolor=COL["border"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="white", plot_bgcolor="white"
    )
    st.plotly_chart(fig_eff, use_container_width=True, theme=None)
    st.markdown('</div>', unsafe_allow_html=True)

with g_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="card-header"><div class="card-title">🌍 CO₂ 배출량 비교 (누적)</div></div>',
        unsafe_allow_html=True
    )
    co2_df = hist.tail(240)
    fig_co2 = go.Figure()
    if not co2_df.empty:
        fig_co2.add_scatter(
            x=co2_df["time"], y=co2_df["co2_diesel_cum_t"],
            mode="lines", name="Diesel baseline (누적 tCO₂)",
            line=dict(width=2, color="#9ca3af")
        )
        fig_co2.add_scatter(
            x=co2_df["time"], y=co2_df["co2_actual_cum_t"],
            mode="lines", name="Eco-friendShip (누적 tCO₂)",
            line=dict(width=2, color=COL["success"])
        )
        fig_co2.add_scatter(
            x=pd.concat([co2_df["time"], co2_df["time"][::-1]]),
            y=pd.concat([co2_df["co2_diesel_cum_t"], co2_df["co2_actual_cum_t"][::-1]]),
            fill="toself", fillcolor="rgba(37,99,235,0.08)", line=dict(color="rgba(0,0,0,0)"),
            name="절감 영역"
        )
    fig_co2.update_layout(
        height=240, margin=dict(l=40, r=30, t=10, b=40),
        yaxis=dict(title="누적 배출량 (tCO₂)", gridcolor=COL["border"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="white", plot_bgcolor="white"
    )
    st.plotly_chart(fig_co2, use_container_width=True, theme=None)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- 자동 갱신 ----------
time.sleep(5)
st.rerun()
