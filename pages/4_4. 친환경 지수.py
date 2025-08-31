import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import time
from urllib import parse as _url


st.set_page_config(page_title="친환경 지표", layout="wide")

# ---------- 스타일 팔레트 (가장 먼저 선언) ----------
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
    "sidebar_bg": "#f8fafc",
}

# ---------- 전역 CSS ----------
st.markdown(f"""
<style>
.stApp {{
  background: {COL["app_bg"]};
  color: #1f2937;
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, 'Noto Sans KR', sans-serif;
}}
.card {{
  background: {COL["card"]};
  border: 1px solid {COL["border"]};
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 1px 1px rgba(16,24,40,.02);
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
[data-testid="stSidebar"] > div:first-child {{
  background: {COL["sidebar_bg"]};      /* 연한 회색으로 복구 */
  border-right: 1px solid {COL["border"]};
  box-shadow: 0 0 0 1px rgba(0,0,0,0.02) inset;
}}

div[data-testid="stSidebarNav"] a {{ border-radius: 10px; }}
div[data-testid="stSidebarNav"] a[aria-current="page"] {{
  background: #e9f0ff; color: {COL["primary"]} !important; font-weight: 700;
}}

[data-testid="stMetricValue"] {{ font-weight: 800; color: {COL["title"]}; }}
[data-testid="stMetricDelta"] {{ font-weight: 700; }}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.big-num { 
  font-size: 40px;      /* 더 크게 */
  font-weight: 900;     /* 더 굵게 */
  letter-spacing: -0.01em;
  margin: 2px 0 6px 2px;
  color: #0f172a;
}
</style>
""", unsafe_allow_html=True)

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
        st.markdown('<div class="login-right">', unsafe_allow_html=True)
        if not st.session_state.get("logged_in", False):
            st.page_link("pages/5_5. 로그인.py", label="LOGIN")
        else:
            if st.button("LOGOUT", use_container_width=True):
                st.session_state["logged_in"] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
    "<div style='font-size:26px; font-weight:800; margin:-10px 0 2px 0;'>"
    "🌱 친환경 지표"
    "</div>",
    unsafe_allow_html=True
    )

top_header()
st.caption("재생에너지 비중과 효율 지수를 기반으로 친환경 운항 상태를 평가합니다.")
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
