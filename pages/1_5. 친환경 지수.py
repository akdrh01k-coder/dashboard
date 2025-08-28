# pages/1_5. 친환경 지수.py
import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="친환경 지수", layout="wide")

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

# ======== Sidebar (minimal customize as requested) ========
def custom_sidebar():
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

    # 제목(문구 유지)
    st.sidebar.markdown('<div class="sb-title">Eco-Friendship Dashboard</div>', unsafe_allow_html=True)

    # 메뉴 (라벨에 이모지 추가)
    st.sidebar.markdown('<div class="sb-link">', unsafe_allow_html=True)
    st.sidebar.page_link("pages/1_5. 친환경 지수.py", label="🌱 친환경 지수")
    st.sidebar.page_link("pages/2_6. 안전 경보.py", label="⚠️ 안전/경보")
    st.sidebar.page_link("pages/3_7. 로그인.py", label="🔐 로그인")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

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
            st.page_link("pages/3_7. 로그인.py", label="LOGIN")
        else:
            if st.button("LOGOUT", use_container_width=True):
                st.session_state["logged_in"] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
    "<div style='font-size:26px; font-weight:800; margin:10px 0 2px 0;'>"
    "🌱 친환경 지수"
    "</div>",
    unsafe_allow_html=True
    )

top_header()
custom_sidebar()
st.caption("운영·분석용 데모 · 5초 자동 갱신")
st.markdown("---")

# ---------- 세션 ----------
if "history" not in st.session_state:
    st.session_state["history"] = pd.DataFrame(
        columns=["time","motor_w","fc_w","pv_w","batt_w","other_w",
                 "soc","eff_index","co2_saved_g","co2_cum_t"]
    )
if "saved_co2_t" not in st.session_state:
    st.session_state["saved_co2_t"] = 125.7
if "diesel_ref" not in st.session_state:
    base_t = pd.date_range(end=pd.Timestamp.utcnow(), periods=72, freq="5S")
    base = np.clip(np.random.normal(loc=54, scale=4, size=len(base_t)), 40, 65)
    st.session_state["diesel_ref"] = pd.DataFrame({"time": base_t, "score": base})

# ---------- 더미 데이터 ----------
motor_w = float(np.random.uniform(90, 180))
eco_share = float(np.random.uniform(0.35, 0.80))
eco_total = motor_w * eco_share
fc_w = eco_total * np.random.uniform(0.3, 0.7)
pv_w = eco_total - fc_w
other_w = max(0.0, motor_w - (fc_w + pv_w))
batt_w = float(min(other_w, np.random.uniform(10, 60)))

soc_prev = float(np.random.uniform(0.6,0.9)) if st.session_state["history"].empty else float(st.session_state["history"].iloc[-1]["soc"])
soc = float(np.clip(soc_prev - batt_w*0.0005, 0.2, 0.98))

eco_ratio = (fc_w + pv_w) / max(1e-6, motor_w) * 100.0
eff_index = float(np.random.uniform(62, 90))

diesel_ef = 700.0
eco_ef = (1.0 - eco_ratio/100.0) * 300.0
sample_kwh = motor_w * 5.0 / 3_600_000.0
diesel_co2_g = sample_kwh * diesel_ef
eco_co2_g = sample_kwh * eco_ef
co2_saved_g = max(0.0, diesel_co2_g - eco_co2_g)

prev_cum_t = float(st.session_state.get("saved_co2_t", 0.0))
last_valid = st.session_state["history"]["co2_cum_t"].dropna() if not st.session_state["history"].empty else []
if len(last_valid) > 0:
    prev_cum_t = float(last_valid.iloc[-1])
co2_cum_t = float(prev_cum_t + co2_saved_g/1_000_000.0)
st.session_state["saved_co2_t"] = co2_cum_t

# 기록
now = pd.Timestamp.utcnow()
new_row = {"time":now,"motor_w":motor_w,"fc_w":fc_w,"pv_w":pv_w,"batt_w":batt_w,
           "other_w":other_w,"soc":soc,"eff_index":eff_index,
           "co2_saved_g":co2_saved_g,"co2_cum_t":co2_cum_t}
st.session_state["history"] = pd.concat(
    [st.session_state["history"], pd.DataFrame([new_row])],
    ignore_index=True
).tail(500)
hist = st.session_state["history"]

# 최근 추세 기울기(slope)
slope = None
if len(hist) >= 10 and "eff_index" in hist.columns:
    y = hist["eff_index"].tail(10).astype(float).values
    x = np.arange(len(y))
    if y.size > 1:
        slope = float(np.polyfit(x, y, 1)[0])

# 등급
def grade_by_eff(idx: float):
    if idx >= 85: return "A","안전 항해",COL["success"]
    if idx >= 70: return "B","양호",COL["primary"]
    if idx >= 55: return "C","주의",COL["warn"]
    return "D","비효율",COL["danger"]

grade, grade_text, grade_color = grade_by_eff(eff_index)

# =========================
# 상단 레이아웃: c1(크게) | c2(상단 2분할 + 하단 그래프 2개)
# =========================
c1, c2 = st.columns([1.35, 2.15], gap="small")  # ← c1 가로 더 넓힘

# 권장 액션 (필요 시 유지)
actions = []
if grade in ["C","D"]:
    actions.append("효율 저하: 추진계 정렬·프로펠러·베어링 점검 권장.")
if (slope is not None) and (slope < -0.3):
    actions.append("하락 추세: 최근 급가감속·하중 변동 여부 확인.")
if (grade == "B") and (eco_ratio < 60):
    actions.append("개선 포인트: 재생 비중을 높이고 불필요한 가감속을 줄이면 A에 근접.")
if not actions:
    actions.append("안정 운영: 현재 전략 유지하며 데이터 누적.")

# =========================
# c1 — 에너지 효율 지수 + 등급&상태 (크고 높게)
# =========================
with c1:
    st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)

    # (1) 효율 지수 게이지
    st.markdown(
        f'<div class="card-header"><div class="card-title">📊 에너지 효율 지수</div>'
        f'<span class="badge" style="background:{grade_color};">{grade_text}</span></div>',
        unsafe_allow_html=True,
    )
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=eff_index,
        number={"suffix":" / 100","font":{"size":22, "color":"#1e293b"}},
        gauge={
            "axis":{"range":[0,100]},
            "bar":{"thickness":0.25,"color":grade_color},
            "steps":[
                {"range":[0,55],"color":"#fee2e2"},
                {"range":[55,70],"color":"#ffedd5"},
                {"range":[70,85],"color":"#dbeafe"},
                {"range":[85,100],"color":"#dcfce7"},
            ],
        }
    ))
    gauge.update_layout(
        height=240,   # ← 세로 키움
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white", plot_bgcolor="white"
    )
    st.plotly_chart(gauge, use_container_width=True, theme=None)

    # (2) 등급 & 상태 + 액션 (같은 카드 안)
    st.markdown(
        f'<div class="card-header" style="margin-top:52px;"><div class="card-title">💡 등급 & 상태</div>'
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

    st.markdown('</div>', unsafe_allow_html=True)  # 카드 닫기

# =========================
# c2 — 상단(좌/우 2분할) + 하단(그래프 2개)
# =========================
with c2:

    # ---- c2 상단: 좌/우 2분할 ----
    top_left, top_right = st.columns(2, gap="small")

    # (좌) 친환경 에너지 비중
    with top_left:
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
            margin=dict(t=20, b=20, l=56, r=20),  # y축 겹침 방지
            yaxis=dict(title="출력 (W)", title_standoff=12, automargin=True, gridcolor=COL["border"]),
            paper_bgcolor="white", plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_mix.update_yaxes(automargin=True)
        st.plotly_chart(fig_mix, use_container_width=True, theme=None)
        st.markdown('</div>', unsafe_allow_html=True)

    # (우) SOC + CO₂ (한 카드 안)
    with top_right:
        st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)

        # SOC
        soc_status = "적정" if 0.4 <= soc <= 0.8 else ("낮음" if soc < 0.4 else "높음")
        soc_color  = COL["success"] if soc_status=="적정" else COL["warn"]
        st.markdown(
            f'<div class="card-header"><div class="card-title">🔋 배터리 SOC</div>'
            f'<span class="badge" style="background:{soc_color};">{soc_status}</span></div>',
            unsafe_allow_html=True,
        )
        st.metric("", f"{soc*100:.1f}%", label_visibility="collapsed")

        # CO₂
        st.markdown(
            f'<div class="card-header" style="margin-top:8px;"><div class="card-title">🌍 총 CO₂ 절감량</div>'
            f'<span class="badge" style="background:{COL["primary"]};">누적</span></div>',
            unsafe_allow_html=True,
        )
        st.metric("누적 절감", f"{co2_cum_t:,.2f} tCO₂")

        st.markdown('</div>', unsafe_allow_html=True)

    # ---- c2 하단: 그래프 2개 (동일 폭) ----
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)  # 간격 조금
    g_left, g_right = st.columns(2, gap="small")

    with g_left:
        st.markdown(
            '<div class="card-header"><div class="card-title">📈 Eco-Ship 효율 지수 추세</div></div>',
            unsafe_allow_html=True
        )
        eco_df = hist.tail(120)
        fig_eco = go.Figure()
        if not eco_df.empty:
            fig_eco.add_scatter(
                x=eco_df["time"], y=eco_df["eff_index"],
                mode="lines+markers", line=dict(color=COL["primary"], width=2)
            )
        fig_eco.update_layout(
            height=200, margin=dict(l=40, r=30, t=10, b=40),
            yaxis=dict(range=[30,100], gridcolor=COL["border"]),
            paper_bgcolor="white", plot_bgcolor="white"
        )
        st.plotly_chart(fig_eco, use_container_width=True, theme=None)

    with g_right:
        st.markdown(
            '<div class="card-header"><div class="card-title">📉 Diesel Ship 효율 지수</div></div>',
            unsafe_allow_html=True
        )
        ddf = st.session_state["diesel_ref"]
        fig_d = go.Figure()
        fig_d.add_scatter(
            x=ddf["time"], y=ddf["score"],
            mode="lines", line=dict(color="#475569", width=2)
        )
        fig_d.update_layout(
            height=200, margin=dict(l=40, r=30, t=10, b=40),
            yaxis=dict(range=[30,100], gridcolor=COL["border"]),
            paper_bgcolor="white", plot_bgcolor="white"
        )
        st.plotly_chart(fig_d, use_container_width=True, theme=None)


# ---------- 자동 갱신 ----------
import time
time.sleep(5)
st.rerun()
