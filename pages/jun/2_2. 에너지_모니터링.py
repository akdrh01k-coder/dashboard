#C:\Users\82102\eco-ship\pages\2_2. 에너지_모니터링.py
import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import time
from urllib import parse as _url
from datetime import datetime, timedelta

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



# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="에너지 모니터링",
    page_icon="⚡",
    layout="wide",
)

st.markdown(f"""
<style>
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
  color: {COL["title"]}; font-size: 18px;
}}
.badge {{
  padding: 4px 10px; border-radius: 999px; color: #fff;
  font-weight: 700; font-size: 12px;
}}            

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

    # 📡 1-2. 위치 모니터링 LiDAR  ← (여기를 새로 추가)
    page_link_if_exists([
        "pages/1_2. 위치_모니터링_LiDAR.py",  # (선택) 파일명 바꿀 경우 대비
        "pages/1_2.위치_모니터링_LiDAR.py",
    ], "📡 위치 모니터링 LiDAR")

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
    "<div style='font-size:26px; font-weight:800; margin:10px 0 2px 0;'>"
    "⚡ 에너지 모니터링"
    "</div>",
    unsafe_allow_html=True
    )

custom_sidebar()
top_header()
st.caption("실시간으로 에너지 사용량을 모니터링하고 분석합니다.")

# ---------- 시뮬레이터 파라미터(초소형 보트) ----------
BUS_V      = 12.0                 # 시스템 버스 전압(모터/FC)
MOTOR_PR   = 15.0                # 모터 정격(W)
FC_PR      = 18.0                 # PEMFC 정격(W)
PV_AREA    = 0.06                 # m^2
PV_EFF     = 0.16                 # 효율
PV_V       = 6.0                 # PV MPP 전압
T_LIMIT    = 70.0                 # 모터 온도 한계(℃)
DT         = 2.0                  # 샘플 간격(s)

# 외부 일사량(없으면 700으로)
w = st.session_state.get("weather", {"irradiance":700})
IRR = float(w.get("irradiance", 700.0))  # W/m^2
PV_MAX = PV_AREA * PV_EFF * IRR          # 이론치 (상한 걸어줌)

# ---------- 스타일 ----------
st.markdown("""
<style>
.card{padding:12px;border-radius:12px;background:linear-gradient(180deg,#fff,#fbfdff);
  border:1px solid #e8eef8; box-shadow:0 10px 26px rgba(8,30,50,.05);}
.title{font-weight:900;font-size:16px;color:#0b3b66}
.live{display:inline-block;width:8px;height:8px;border-radius:999px;background:#10b981;margin-right:6px;animation:pulse 1.6s infinite}
@keyframes pulse {0%{opacity:1}50%{opacity:.4}100%{opacity:1}}


.delta-up{color:#16a34a;font-weight:900}.delta-down{color:#dc2626;font-weight:900}
.src-grid {display:grid; grid-template-columns:1fr; gap:8px; margin:8px 0;}
.src-card {display:flex; align-items:center; justify-content:space-between; gap:12px;
  padding:10px 12px; border-radius:12px; background:#fff; border:1px solid #e8eef8;}
.src-left{display:flex; align-items:center; gap:10px;}
.src-dot{width:10px;height:10px;border-radius:50%}
.dot-motor{background:#475569}.dot-pv{background:#f59e0b}.dot-fc{background:#0ea5e9}
.src-title{font-weight:800;color:#0b3b66}
.src-sub{font-size:12px;color:#64748b;font-weight:700}

.src-center{display:flex; align-items:flex-end; gap:6px; flex-direction:column}
.src-main{font-weight:900;font-size:18px;color:#0b3b66; letter-spacing:-0.2px}
.src-meter{height:6px;width:120px;border-radius:999px;background:#f1f5f9;overflow:hidden}
.src-meter>span{display:block;height:100%}
.mtr-motor{background:#94a3b8}.mtr-pv{background:#fbbf24}.mtr-fc{background:#38bdf8}

.src-delta{min-width:64px;text-align:right;font-size:18px;font-weight:900}
.up{color:#16a34a}.down{color:#dc2626}.flat{color:#94a3b8}
.blink{animation:flash .9s ease-out 1}
@keyframes flash{0%{box-shadow:0 0 0 0 rgba(59,130,246,.28)}100%{box-shadow:0 0 0 10px rgba(59,130,246,0)}}
            
.badge{padding:6px 10px;border-radius:999px;font-weight:800;font-size:12px;border:1px solid rgba(0,0,0,.06)}
.good{background:#e6f7ea;color:#0b6b2d}.warn{background:#fff7e0;color:#b36b00}.bad{background:#fdecea;color:#b91c1c}
            
.pills{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}

.pill{
  display:flex;align-items:center;gap:8px;
  padding:8px 12px;border:1px solid #e5e7eb;border-radius:12px;background:#fff;
}
            
.kpis{display:grid;grid-template-columns: 1fr 1fr;gap:10px;flex-wrap:wrap;margin:6px 0}
.kpi{background:#fff;border:1px solid #e8eef8;border-radius:12px;padding:8px 12px}
.kpi .h{font-size:12px;color:#64748b;font-weight:700}
.kpi .v{font-size:18px;color:#0b3b66;font-weight:900;letter-spacing:-.2px}
.badge-pill{padding:4px 8px;border-radius:999px;font-weight:800;font-size:12px;
            border:1px solid rgba(0,0,0,.06); background:#f1f5f9; color:#334155}
.badge-green{background:#dcfce7;color:#166534;border-color:#bbf7d0}
.badge-amber{background:#fff7e0;color:#b45309;border-color:#fde68a}
.badge-red{background:#fee2e2;color:#b91c1c;border-color:#fecaca}            
</style>
""", unsafe_allow_html=True)

# ---------- 히스토리 초기화(2초 간격, 2분치) ----------
if "micro_hist" not in st.session_state:
    t0 = datetime.utcnow() - timedelta(seconds=110)
    duty = 0.45
    speed = 0.9      # m/s (≈ 1.75 kn)
    temp  = 40.0
    rows = []
    for i in range(55):
        # 스로틀(랜덤워크, 사용자 조작 느낌)
        duty = float(np.clip(duty + np.random.normal(0, 0.015), 0.10, 0.95))
        # 속도 1차 시스템: 목표 v_max=1.5 m/s, duty에 비례
        v_target = 1.5 * duty
        speed += (v_target - speed)*0.15 + np.random.normal(0, 0.01)
        speed = float(np.clip(speed, 0.35, 1.55))  # 초소형 범위

        # 모터 전력 ~ v^3 (유체저항) + 노이즈
        motor_w = float(np.clip(MOTOR_PR * (speed/1.5)**3 + np.random.normal(0, 3), 8, MOTOR_PR*1.05))
        # PV 전력: irr 기반 (소형 패널)
        pv_w = float(np.clip(PV_AREA*PV_EFF*IRR + np.random.normal(0, 4), 0, min(PV_MAX, 60)))
        # FC 전력: 수요의 일부를 느리게 추종(PI 성격)
        deficit = max(0.0, motor_w - pv_w)              # 부족분
        prev_fc = rows[-1][3] if rows else 40.0
        fc_w = float(np.clip(prev_fc + 0.12*(0.6*deficit - prev_fc) + np.random.normal(0, 1.5), 10, FC_PR))

        # 전류/온도
        i_motor = motor_w / BUS_V
        temp += (0.05*(motor_w/MOTOR_PR) - 0.025)*DT
        temp = float(np.clip(temp, 28, 78))

        rows.append((t0 + timedelta(seconds=i*DT), motor_w, pv_w, fc_w, speed, duty, i_motor, temp))
    st.session_state["micro_hist"] = pd.DataFrame(rows, columns=[
        "time","motor_w","pv_w","fc_w","speed_ms","duty","motor_a","temp_c"
    ])

# ---------- 한 스텝 갱신 ----------
df = st.session_state["micro_hist"].copy()
last = df.iloc[-1]
duty  = float(np.clip(last["duty"] + np.random.normal(0, 0.02), 0.10, 0.95))
v_tgt = 1.5 * duty
speed = float(np.clip(last["speed_ms"] + (v_tgt - last["speed_ms"])*0.18 + np.random.normal(0, 0.012), 0.35, 1.60))

motor_w = float(np.clip(MOTOR_PR * (speed/1.5)**3 + np.random.normal(0, 4), 8, MOTOR_PR*1.08))
pv_w    = float(np.clip(PV_AREA*PV_EFF*IRR + np.random.normal(0, 5), 0, min(PV_MAX, 60)))
deficit = max(0.0, motor_w - pv_w)
fc_prev = float(last["fc_w"])
fc_w    = float(np.clip(fc_prev + 0.15*(0.6*deficit - fc_prev) + np.random.normal(0, 1.8), 10, FC_PR))

i_motor = motor_w / BUS_V
temp    = float(np.clip(last["temp_c"] + (0.06*(motor_w/MOTOR_PR) - 0.03)*DT, 28, 80))

df = pd.concat([df, pd.DataFrame([{
    "time": datetime.utcnow(),
    "motor_w": motor_w, "pv_w": pv_w, "fc_w": fc_w,
    "speed_ms": speed, "duty": duty, "motor_a": i_motor, "temp_c": temp
}])]).tail(150)
st.session_state["micro_hist"] = df

# ---------- 파생 지표 ----------
speed_ms   = float(df.iloc[-1]["speed_ms"])
speed_kn   = speed_ms * 1.94384
speed_30s  = float(df.tail(int(30/DT))["speed_ms"].iloc[-1] - df.tail(int(30/DT))["speed_ms"].iloc[0])
delta_sym  = "▲" if speed_30s>0.03 else ("▼" if speed_30s<-0.03 else "—")
delta_cls  = "delta-up" if speed_30s>0.03 else ("delta-down" if speed_30s<-0.03 else "")

p_now      = motor_w
load_pct   = float(np.clip(p_now/MOTOR_PR*100.0, 0, 200))
headroom   = float(max(0.0, 100.0 - load_pct))
i_now      = i_motor
t_now      = float(df.iloc[-1]["temp_c"])
thermal_hd = float(T_LIMIT - t_now)
state_cls  = "good" if load_pct<=60 else ("warn" if load_pct<=85 else "bad")

# 각 소스의 V/I 계산(전력만 있어도 표시)
motor_V, motor_I = BUS_V, p_now/max(BUS_V,1e-6)
pv_V,    pv_I    = PV_V,  float(pv_w/max(PV_V,1e-6))
fc_V,    fc_I    = BUS_V, float(fc_w/max(BUS_V,1e-6))

# ================= 레이아웃: 상단 2열 =================
left, right = st.columns([1.6, 1.1], gap="small")

# ---- 좌: 실시간 출력 (모터/태양광/연료전지) + P/V/I 칩 ----
with left:
    st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)

    st.markdown(
            f'<div class="card-header"><div class="card-title">📉 실시간 출력 데이터</div></div>',
            unsafe_allow_html=True,
        )



    # ===== P/V/I 칩 =====
    # ===== NEW: 색상 카드 3개 (모터/태양광/연료전지) =====
    pv_cap   = float(min(PV_MAX, 60.0)) if 'PV_MAX' in locals() else 60.0
    motor_prev = float(df.iloc[-2]["motor_w"]) if len(df)>=2 else float(df.iloc[-1]["motor_w"])
    pv_prev    = float(df.iloc[-2]["pv_w"])    if len(df)>=2 else float(df.iloc[-1]["pv_w"])
    fc_prev    = float(df.iloc[-2]["fc_w"])    if len(df)>=2 else float(df.iloc[-1]["fc_w"])

    def delta_fmt(cur, prev):
        d = cur - prev
        if abs(d) < 0.5: return "flat", "— 0 W"
        return ("up" if d>0 else "down", f"{'▲' if d>0 else '▼'} {d:+.0f} W")

    m_class, m_delta = delta_fmt(p_now, motor_prev)
    p_class, p_delta = delta_fmt(pv_w,  pv_prev)
    f_class, f_delta = delta_fmt(fc_w,  fc_prev)

    motor_pct = float(np.clip(p_now / MOTOR_PR * 100.0, 0, 100))
    pv_pct    = float(np.clip(pv_w  / max(1e-6, pv_cap) * 100.0, 0, 100))
    fc_pct    = float(np.clip(fc_w  / FC_PR * 100.0, 0, 100))

    st.markdown('<div class="src-grid">', unsafe_allow_html=True)

    # 모터
    st.markdown(f'''
    <div class="src-card blink">
      <div class="src-left">
        <span class="src-dot dot-motor"></span>
        <div>
          <div class="src-title">모터</div>
          <div class="src-sub">{motor_V:.0f} V · {motor_I:.1f} A</div>
        </div>
      </div>
      <div class="src-center">
        <div class="src-main">{p_now:.0f} W</div>
        <div class="src-meter"><span class="mtr-motor" style="width:{motor_pct:.0f}%"></span></div>
      </div>
      <div class="src-delta {m_class}">{m_delta}</div>
    </div>
    ''', unsafe_allow_html=True)

    # 태양광
    st.markdown(f'''
    <div class="src-card blink">
      <div class="src-left">
        <span class="src-dot dot-pv"></span>
        <div>
          <div class="src-title">태양광</div>
          <div class="src-sub">{pv_V:.0f} V · {pv_I:.1f} A</div>
        </div>
      </div>
      <div class="src-center">
        <div class="src-main">{pv_w:.0f} W</div>
        <div class="src-meter"><span class="mtr-pv" style="width:{pv_pct:.0f}%"></span></div>
      </div>
      <div class="src-delta {p_class}">{p_delta}</div>
    </div>
    ''', unsafe_allow_html=True)

    # 연료전지
    st.markdown(f'''
    <div class="src-card blink">
      <div class="src-left">
        <span class="src-dot dot-fc"></span>
        <div>
          <div class="src-title">연료전지</div>
          <div class="src-sub">{fc_V:.0f} V · {fc_I:.1f} A</div>
        </div>
      </div>
      <div class="src-center">
        <div class="src-main">{fc_w:.0f} W</div>
        <div class="src-meter"><span class="mtr-fc" style="width:{fc_pct:.0f}%"></span></div>
      </div>
      <div class="src-delta {f_class}">{f_delta}</div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ===== 실시간 출력 추이 ===== 

    # --- 그래프를 완만하게 만들기 위한 데이터 스무딩(이동 평균) ---
    # window_size 값을 조절해 얼마나 부드럽게 만들지 결정할 수 있습니다.
    # 값을 키울수록 그래프는 더 완만해집니다. (예: 5, 10, 20)
    window_size = 10 

    df['motor_w_smooth'] = df['motor_w'].rolling(window=window_size, min_periods=1).mean()
    df['pv_w_smooth'] = df['pv_w'].rolling(window=window_size, min_periods=1).mean()
    df['fc_w_smooth'] = df['fc_w'].rolling(window=window_size, min_periods=1).mean()


    fig = go.Figure()

    # 1. 이동 평균을 적용한 '부드러운' 라인 (더 두껍게 표시)
    fig.add_scatter(x=df["time"], y=df["motor_w_smooth"], name="모터 (추세)", mode="lines", line=dict(width=3, color="#475569"))
    fig.add_scatter(x=df["time"], y=df["pv_w_smooth"],    name="태양광 (추세)", mode="lines", line=dict(width=3, color="#f59e0b"))
    fig.add_scatter(x=df["time"], y=df["fc_w_smooth"],    name="연료전지 (추세)", mode="lines", line=dict(width=3, color="#0ea5e9"))

    # 2. 기존의 '뾰족한' 원본 데이터 라인 (더 얇고 투명하게 표시)
    fig.add_scatter(x=df["time"], y=df["motor_w"], name="모터 (원본)", mode="lines", line=dict(width=1, color="#475569"), opacity=0.3, showlegend=False)
    fig.add_scatter(x=df["time"], y=df["pv_w"],    name="태양광 (원본)", mode="lines", line=dict(width=1, color="#f59e0b"), opacity=0.3, showlegend=False)
    fig.add_scatter(x=df["time"], y=df["fc_w"],    name="연료전지 (원본)", mode="lines", line=dict(width=1, color="#0ea5e9"), opacity=0.3, showlegend=False)


    fig.update_layout(height=260, margin=dict(l=40,r=20,t=10,b=40),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                          paper_bgcolor="white", plot_bgcolor="white")
    fig.update_yaxes(title="W", gridcolor="#e5e7eb")
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.markdown('</div>', unsafe_allow_html=True)

# ---- 우: 반원형(half-gauge) 부하율 + 속도/추세/온도/전류 칩 ----
with right:
    st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)

    st.markdown(
            f'<div class="card-header"><div class="card-title">🛠️ 모터 부하율 및 상태 분석</div></div>',
            unsafe_allow_html=True,
        )

    # 반원 게이지 (Indicator)
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=load_pct,
        number={"suffix":" %","font":{"size":18, "color":"#0b3b66"}},
        gauge={
            "axis":{"range":[0,100]},
            "bar":{"color":"#3b82f6","thickness":0.28},
            "steps":[
                {"range":[0,60],  "color":"#dcfce7"},
                {"range":[60,85], "color":"#ffedd5"},
                {"range":[85,100],"color":"#fee2e2"},
            ],
        },
        domain={"x":[0,1], "y":[0,1]}
    ))
    gauge.update_layout(height=170, margin=dict(l=20,r=20,t=10,b=0),
                        paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(gauge, use_container_width=True, theme=None)

    # 핵심 KPI 칩
    st.markdown('<div class="pills">', unsafe_allow_html=True)
    st.markdown(f'<span class="badge {state_cls}">부하 {load_pct:.0f}%</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="pill"><span class="k">속도</span><span class="v">{speed_ms:.2f} m/s ({speed_kn:.2f} kn)</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pill"><span class="k">여유</span><span class="v">{headroom:.0f}%</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pill"><span class="k">온도</span><span class="v">{t_now:.0f}℃ (여유 {thermal_hd:.0f}℃)</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ---- 공통 파생값(지금 시점)
pv_now_w   = float(df.iloc[-1]["pv_w"])
fc_now   = float(df.iloc[-1]["fc_w"])
motor_now= float(df.iloc[-1]["motor_w"])
eco_share_now = float(np.clip((pv_now_w + fc_now) / max(1e-6, motor_now) * 100.0, 0, 100))

# 오늘(세션) 평균 PV (간단 러닝 평균)
if "pv_day_date" not in st.session_state or st.session_state["pv_day_date"] != datetime.utcnow().date():
    st.session_state["pv_day_date"] = datetime.utcnow().date()
    st.session_state["pv_sum_w"] = 0.0
    st.session_state["pv_cnt"] = 0
st.session_state["pv_sum_w"] += pv_now_w
st.session_state["pv_cnt"]   += 1
pv_avg_today = st.session_state["pv_sum_w"] / max(1, st.session_state["pv_cnt"])

# 최적 효율(간단 휴리스틱): FC를 가능한 한 결손을 채우도록 올렸을 때의 eco 비중 기반
fc_opt = min(FC_PR, max(0.0, motor_now - pv_now_w))                         # 결손을 FC가 최대한 메움
eco_opt = float(np.clip((pv_now_w + fc_opt) / max(1e-6, motor_now) * 100.0, 0, 100))
# 효율 지수(데모): 60 + 0.35×친환경비중 - 고부하 페널티
load_pct = float(np.clip(motor_now/MOTOR_PR*100.0, 0, 200))
eff_now  = float(np.clip(60 + 0.35*eco_share_now - max(0, load_pct-85)*0.4, 0, 100))
eff_opt  = float(np.clip(60 + 0.35*eco_opt       - max(0, load_pct-85)*0.4, 0, 100))
eff_gain = eff_opt - eff_now   # 최적 전략 대비 이득
pv_total_today_wh = (df['pv_w'].mean() * (len(df) / 3600.0))  # 대략적인 오늘 PV 총량(Wh)
eff_opt = 95.0
eff_gain = 0.0

# =========================
# 하단 3열: 좌(오늘의 태양광/친환경 예측) | 중(배터리) | 우(RER/ZER)
# =========================
colL, colC, colR = st.columns([1.0, 0.6, 1.1], gap="small")

with colR:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
            f'<div class="card-header"><div class="card-title">☀️ 오늘의 태양광 발전 현황</div></div>',
            unsafe_allow_html=True,
        )

    # KPI 3개
    st.markdown(f"""
    <div class="kpis">
        <div class="kpi">
            <div class="h">☀️ 실시간 발전 전력</div>
            <div class="v">{pv_now_w:.1f} W</div>
        </div>
        <div class="kpi">
            <div class="h">🔋 오늘 총 발전량</div>
            <div class="v">{pv_total_today_wh:.1f} Wh</div>
        </div>
        <div class="kpi">
            <div class="h">👍 현재 발전 효율</div>
            <div class="v">{eff_opt:.1f} / 100 점
                <span class="badge-pill {'badge-green' if eff_gain>0 else 'badge-amber' if abs(eff_gain)<0.5 else 'badge-red' if eff_gain<0 else ''}">{eff_gain:+.1f}p</span>
            </div>
            <div class="sub-h">최적 조건 대비 성능</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

   # --- 그래프를 완만하게 만들기 위한 데이터 스무딩(이동 평균) ---
# window_size 값을 조절해 얼마나 부드럽게 만들지 결정할 수 있습니다.
# 값을 키울수록 그래프는 더 완만해집니다. (예: 5, 10, 20)
    window_size = 10 

    # 'pv_w' 데이터에 대한 이동 평균 계산
    df['pv_w_smooth'] = df['pv_w'].rolling(window=window_size, min_periods=1).mean()


    # PV 스파크라인 (수정됨)
    fig_pv = go.Figure()

    # 1. 이동 평균을 적용한 '부드러운' 라인 (더 두껍게 표시)
    fig_pv.add_scatter(x=df["time"], y=df["pv_w_smooth"], mode="lines", name="발전 전력 (추세)", 
                      line=dict(width=3, color="#f59e0b"))

    # 2. 기존의 '뾰족한' 원본 데이터 라인 (더 얇고 투명하게 표시)
    fig_pv.add_scatter(x=df["time"], y=df["pv_w"], mode="lines", name="발전 전력 (원본)", 
                      line=dict(width=1, color="#f59e0b"), opacity=0.3, showlegend=False)


    fig_pv.update_layout(
        height=170, 
        margin=dict(l=50, r=20, t=10, b=40),
        paper_bgcolor="white", 
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="발전 전력(W)", gridcolor="#e5e7eb", range=[0, df['pv_w'].max() * 1.2]),
    )
    st.plotly_chart(fig_pv, use_container_width=True, theme=None)

    st.markdown('</div>', unsafe_allow_html=True)

with colL:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card-header"><div class="card-title">🔌 배터리 충·방전 · 상태</div></div>',
        unsafe_allow_html=True,
    )

    # 간단한 배터리 모델(충/방전 전력 = PV+FC-Motor)
    BATT_CAP_WH = 240.0      # 12V 20Ah 가정
    if "batt_soc" not in st.session_state: st.session_state["batt_soc"] = 0.65
    if "batt_hist" not in st.session_state:
        st.session_state["batt_hist"] = pd.DataFrame(columns=["time","w","soc"])

    batt_w = float(pv_now_w + fc_now - motor_now)  # +면 충전, -면 방전
    # SOC 적분
    st.session_state["batt_soc"] = float(np.clip(
        st.session_state["batt_soc"] + batt_w * DT / 3600.0 / BATT_CAP_WH, 0.05, 0.98
    ))
    st.session_state["batt_hist"] = pd.concat([st.session_state["batt_hist"],
                                               pd.DataFrame([{"time": datetime.utcnow(),
                                                              "w": batt_w,
                                                              "soc": st.session_state["batt_soc"]}])],
                                              ignore_index=True).tail(180)
    bh = st.session_state["batt_hist"]

    # KPI
    status = "충전" if batt_w>=0 else "방전"
    badge_cls = "badge-green" if batt_w>=0 else "badge-red"
    soc_now = st.session_state["batt_soc"]*100.0
    soc_delta_30s = (bh.tail(int(30/DT))["soc"].iloc[-1] - bh.tail(int(30/DT))["soc"].iloc[0])*100.0 if len(bh)>=int(30/DT) else 0.0

    st.markdown(f"""
    <div class="kpis">
      <div class="kpi"><div class="h">상태</div><div class="v">{status} <span class="badge-pill {badge_cls}">{batt_w:+.0f} W</span></div></div>
      <div class="kpi"><div class="h">SOC</div><div class="v">{soc_now:.1f} % <span class="badge-pill">{soc_delta_30s:+.2f}%/30s</span></div></div>
    </div>
    """, unsafe_allow_html=True)

    # ⭐️ 1. 이동 평균 계산 (이 줄을 추가하세요)
    # window=5는 최근 5개 데이터의 평균을 사용하겠다는 의미입니다. 숫자를 키우면 더 부드러워집니다.
    # min_periods=1은 데이터가 5개 미만일 때도 가능한 만큼만 평균을 내서 처음부터 그래프가 보이게 합니다.
    bh['w_smooth'] = bh['w'].rolling(window=5, min_periods=1).mean()

    # 충/방전 전력 스파크라인
    fig_b = go.Figure()
    # ⭐️ 2. 그래프를 그릴 때 y축 데이터를 'w_smooth'로 변경
    fig_b.add_scatter(x=bh["time"], y=bh["w_smooth"], mode="lines", name="Batt W",
                      line=dict(width=2, color="#6366f1"))
    fig_b.add_hline(y=0, line_color="#e5e7eb")
    fig_b.update_layout(height=170, margin=dict(l=40,r=20,t=10,b=40),
                        yaxis=dict(title="W", gridcolor="#eef2f7"),
                        paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig_b, use_container_width=True, theme=None)

    st.markdown('</div>', unsafe_allow_html=True)
with colC:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
            f'<div class="card-header"><div class="card-title">🧐 RER / ZER 지표</div></div>',
            unsafe_allow_html=True,
        )

    headroom = float(max(0.0, 100.0 - load_pct))
    eco_pct  = float(eco_share_now)

    x = ["RER(여유)","ZER(친환경)"]
    val = [headroom, eco_pct]
    rem = [100-headroom, 100-eco_pct]

    fig_rz = go.Figure()
    # 회색(잔여) 먼저 쌓기
    fig_rz.add_bar(
        x=x, y=rem, name="잔여(100%-지표)",
        marker_color="#eef2f7", hoverinfo="skip",
        marker_line=dict(width=1, color="#e5e7eb")
    )
    # 초록(지표) 위에 쌓기
    fig_rz.add_bar(
        x=x, y=val, name="지표",
        marker_color=["#10b981","#22c55e"],
        text=val,                         # 숫자 그대로 넘기고
        texttemplate="%{text:.0f}%",
        textposition="outside",
        marker_line=dict(width=1, color="#0ea5a0"),
        cliponaxis=False
    )

    fig_rz.update_layout(
        barmode="stack",
        height=200,
        width=200,
        margin=dict(l=40,r=20,t=60,b=40),
        yaxis=dict(range=[0,100], title="%", gridcolor="#eef2f7"),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False,
        uniformtext_minsize=14, uniformtext_mode="show"  
    )
    st.plotly_chart(fig_rz, use_container_width=True, theme=None)

    # 👇 처음 보는 사람도 이해하도록 간단 설명(접기)
    st.markdown("""
<details>
  <summary>ℹ️ RER · ZER가 뭔가요?</summary>
  <ul style="margin:6px 0 0 18px">
    <li><b>RER</b>(Reserve Energy Ratio) = <i>출력 여유율</i>. 현재 모터 부하가 정격 대비 얼마나 여유가 있는지(%)를 뜻합니다.</li>
    <li><b>ZER</b>(Zero-emission Ratio) = <i>무배출 에너지 비중</i>. 태양광+연료전지 전력이 모터 요구 전력의 몇 %를 채우는지입니다.</li>
    <li>그래프는 <b>전체(100%) 대비 지표 값</b>을 초록색으로, 나머지를 회색으로 표현합니다.</li>
  </ul>
</details>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    
# ---------- 자동 새로고침 ----------
if st.session_state.get("auto_on", True):
  time.sleep(st.session_state.get("auto_sec", 2))
  st.rerun()
