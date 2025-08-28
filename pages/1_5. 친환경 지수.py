# pages/1_5. 친환경 지수.py
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="친환경 지수", layout="wide")

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

# ---------- 스타일 ----------
COL = {
    "primary":"#2563eb","success":"#16a34a","warn":"#f59e0b","danger":"#dc2626",
    "teal":"#14b8a6","muted":"#64748b","border":"#e2e8f0","card":"#ffffff",
    "header":"#f1f5f9","title":"#0f172a",
    "solar":"#f59e0b","hydrogen":"#0ea5e9","other":"#e2e8f0"
}

st.markdown(f"""
<style>
.card {{
  background:{COL["card"]}; border:1px solid {COL["border"]};
  border-radius:12px; padding:10px;
}}
.card-header {{
  background:{COL["header"]}; border-radius:8px; padding:6px 10px; margin-bottom:6px;
  display:flex; justify-content:space-between; align-items:center;
}}
.card-title {{ font-weight:700; color:{COL["title"]}; font-size:15px; }}
.badge {{
  padding:4px 10px; border-radius:999px; color:#fff; font-weight:700; font-size:12px;
}}
.status-banner {{
  width:100%; border-radius:6px; padding:6px 8px; color:white; font-weight:700; font-size:14px;
  text-align:center; margin-top:6px;
}}
.action-box {{
  border:1px dashed {COL["border"]}; background:#f8fafc;
  border-radius:6px; padding:6px 8px; margin-top:6px;
}}
.action-box ul {{ margin:0 0 0 16px; padding:0; }}
.action-box li {{ font-size:12.5px; color:#334155; margin:3px 0; }}
</style>
""", unsafe_allow_html=True)

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
if len(last_valid)>0:
    prev_cum_t = float(last_valid.iloc[-1])
co2_cum_t = float(prev_cum_t + co2_saved_g/1_000_000.0)
st.session_state["saved_co2_t"] = co2_cum_t

# 기록
now = pd.Timestamp.utcnow()
new_row = {"time":now,"motor_w":motor_w,"fc_w":fc_w,"pv_w":pv_w,"batt_w":batt_w,
           "other_w":other_w,"soc":soc,"eff_index":eff_index,
           "co2_saved_g":co2_saved_g,"co2_cum_t":co2_cum_t}
st.session_state["history"] = pd.concat([st.session_state["history"], pd.DataFrame([new_row])],
                                        ignore_index=True).tail(500)
hist = st.session_state["history"]

# 최근 추세 기울기(slope) 계산 — 권장 액션에서 쓰기 전에 미리 계산
slope = None
if len(hist) >= 10 and "eff_index" in hist.columns:
    y = hist["eff_index"].tail(10).astype(float).values
    x = np.arange(len(y))
    if y.size > 1:
        slope = float(np.polyfit(x, y, 1)[0])

# 등급
def grade_by_eff(idx):
    if idx >= 85: return "A","최적",COL["success"]
    if idx >= 70: return "B","양호",COL["primary"]
    if idx >= 55: return "C","주의",COL["warn"]
    return "D","비효율",COL["danger"]
grade, grade_text, grade_color = grade_by_eff(eff_index)

# ---------- 헤더 ----------
st.markdown("## 🌍 친환경 지수")
st.caption(f"운영·분석용 데모 · 5초 자동 갱신 · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =========================
# 1) 효율+등급 / 에너지 비중 / SOC+CO₂
# =========================
c1, c2, c3 = st.columns([1,1,1], gap="small")

# =========================
# 1) 효율+등급/액션 / 에너지 비중 / SOC+CO₂  (칼럼폭 조정: [넓음, 보통, 좁음])
# =========================

# 권장 액션 계산 (최소 1개 보장)
actions = []
if grade in ["C","D"]:
    actions.append("효율 저하: 추진계 정렬·프로펠러·베어링 점검 권장.")
if (slope is not None) and (slope < -0.3):
    actions.append("하락 추세: 최근 급가감속·하중 변동 여부 확인.")
if (grade == "B") and (eco_ratio < 60):
    actions.append("개선 포인트: 재생 비중을 높이고 불필요한 가감속을 줄이면 A에 근접.")
if not actions:
    actions.append("안정 운영: 현재 전략 유지하며 데이터 누적.")

c1, c2, c3 = st.columns([1.4, 1.0, 0.8], gap="small")

# --- (1) 에너지 효율 지수 + 등급/상태/권장 액션 (넓게) ---
with c1:
    st.markdown(f"""<div class="card" style="height:100%;">""", unsafe_allow_html=True)

    # 에너지 효율 지수
    st.markdown(
        f"""<div class="card-header"><div class="card-title">📊 에너지 효율 지수</div>
        <span class="badge" style="background:{grade_color};">{grade_text}</span></div>""",
        unsafe_allow_html=True,
    )
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=eff_index,
        number={"suffix":" / 100","font":{"size":20, "color":"#1e293b"}},
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
    # 그래프를 살짝 아래로
    gauge.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(gauge, use_container_width=True, theme=None)

    # 등급 & 상태 + 권장 액션 (한 카드 안에)
    st.markdown(f"""
    <div class="card" style="margin-top:10px;">
      <div class="card-header">
        <div class="card-title">💡 등급 & 상태</div>
        <span class="badge" style="background:{grade_color};">등급 {grade}</span>
      </div>
      <div class="status-banner" style="background:{grade_color};">{grade_text}</div>
      <div class="action-box"><ul>{"".join([f"<li>{a}</li>" for a in actions])}</ul></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --- (2) 친환경 에너지 비중 (세로 길이 유지/강조) ---
with c2:
    eco_pct_display = eco_ratio
    st.markdown(f"""<div class="card" style="height:100%;">""", unsafe_allow_html=True)

    st.markdown(
        f"""<div class="card-header"><div class="card-title">🌱 친환경 에너지 비중</div>
        <span class="badge" style="background:{COL["teal"]};">{eco_pct_display:.1f}%</span></div>""",
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
                             marker_color="#475569",
                             text=[f"{motor_w:.0f}W (100%)"], textposition="inside"))

    # 세로 길이를 길게 유지
    fig_mix.update_layout(
        barmode="relative", height=260,
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis=dict(title="출력 (W)", gridcolor="#e2e8f0"),
        plot_bgcolor="white", paper_bgcolor="white"
    )
    st.plotly_chart(fig_mix, use_container_width=True, theme=None)

    st.markdown("</div>", unsafe_allow_html=True)

# --- (3) SOC + CO₂ (조금 좁게, 숫자 작게, CO₂는 누적만) ---
with c3:
    st.markdown(f"""<div class="card" style="height:100%;">""", unsafe_allow_html=True)

    # SOC
    soc_status = "적정" if 0.4 <= soc <= 0.8 else ("낮음" if soc < 0.4 else "높음")
    soc_color = COL["success"] if soc_status=="적정" else COL["warn"]
    st.markdown(
        f"""<div class="card-header"><div class="card-title">🔋 배터리 SOC</div>
        <span class="badge" style="background:{soc_color};">{soc_status}</span></div>""",
        unsafe_allow_html=True,
    )
    # metric 글자 크기 줄이기 효과를 위해 label 감추고 값만 표시
    st.metric("", f"{soc*100:.1f}%", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # CO₂ (누적만, 최근 5초 제거)
    st.markdown(f"""<div class="card" style="margin-top:10px;">
      <div class="card-header"><div class="card-title">🌍 총 CO₂ 절감량</div>
      <span class="badge" style="background:{COL["primary"]};">누적</span></div>""",
      unsafe_allow_html=True)
    st.metric("누적 절감", f"{co2_cum_t:.2f} tCO₂")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


st.divider()

# =========================
# 2) Eco vs Diesel
# =========================
g1,g2 = st.columns(2, gap="small")
with g1:
    st.markdown(f"""<div class="card">
    <div class="card-header"><div class="card-title">📈 Eco-Ship 효율 지수 추세</div></div>""", unsafe_allow_html=True)
    eco_df = hist.tail(120)
    fig_eco = go.Figure()
    if not eco_df.empty:
        fig_eco.add_scatter(x=eco_df["time"], y=eco_df["eff_index"],
                            mode="lines+markers", line=dict(color=COL["primary"], width=2))
    fig_eco.update_layout(height=200, margin=dict(l=40,r=30,t=30,b=40),
                          yaxis=dict(range=[30,100]), plot_bgcolor="white")
    st.plotly_chart(fig_eco, use_container_width=True, theme=None)
    st.markdown("</div>", unsafe_allow_html=True)

with g2:
    st.markdown(f"""<div class="card">
    <div class="card-header"><div class="card-title">📉 Diesel Ship 효율 지수</div></div>""", unsafe_allow_html=True)
    ddf = st.session_state["diesel_ref"]
    fig_d = go.Figure()
    fig_d.add_scatter(x=ddf["time"], y=ddf["score"], mode="lines", line=dict(color="#475569", width=2))
    fig_d.update_layout(height=200, margin=dict(l=40,r=30,t=30,b=40),
                        yaxis=dict(range=[30,100]), plot_bgcolor="white")
    st.plotly_chart(fig_d, use_container_width=True, theme=None)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 자동 갱신 ----------
time.sleep(5)
st.rerun()
