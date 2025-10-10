# C:\Users\82102\eco-ship\pages\1_1. 메인_컨트롤.py
import math, time, json
from typing import Tuple, Optional

import numpy as np
import requests
import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt

# ── 상단 UI ─────────────────────────────────
st.header("🕹️ 메인 컨트롤 / Live Cam / 지도")

API_BASE = st.sidebar.text_input("API", "http://127.0.0.1:8000")
mode = st.sidebar.radio("모드", ["수동조작", "자율운항"])
hz = st.sidebar.slider("전송(Hz)", 5, 30, 10)
timeout_s = st.sidebar.slider("타임아웃(s)", 0.2, 3.0, 1.0, 0.1)
send_zero_on_release = st.sidebar.checkbox("키 업 시 정지(0%)", True)

cam_mode = st.sidebar.selectbox("카메라", ["데모", "노트북 웹캠", "MJPEG"])
cam_url = st.sidebar.text_input("MJPEG URL", f"{API_BASE}/cam/mjpeg")

pwm = st.slider("속도(PWM%)", 0, 100, 40, key="pwm_slider")

# ── (A) 리모컨 ───────────────────────────────
def render_big_controller(offset_px: int, api_base: str, pwm_val: int, hz_val: int,
                          timeout_sec: float, send_zero: bool):
    interval_ms = int(1000 / max(1, hz_val))
    html = f"""
    <style>
      .ctr-wrap{{ margin-top:{offset_px}px; }}
      .pad{{ position:relative; width:360px; height:360px; margin:auto; }}
      .btn{{ position:absolute; width:110px; height:110px; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        font-weight:900; font-size:34px; user-select:none; cursor:default;
        background:radial-gradient(circle at 30% 30%, #f4f6fb, #e6e9f3); color:#1f2937;
        border:1px solid #cfd6e3; box-shadow:0 12px 20px rgba(0,0,0,.08), inset 0 -2px 0 rgba(255,255,255,.5);
        transition:transform .05s, box-shadow .05s, background .05s; }}
      .btn.active{{ background:radial-gradient(circle at 30% 30%, #c8f7d0, #86e3a1);
        border-color:#7edaa1; transform:scale(.96); box-shadow:inset 0 4px 12px rgba(0,0,0,.18); }}
      .btn.stop{{ background:radial-gradient(circle at 30% 30%, #ffe2e2, #ffb3b3); border-color:#ff9aa2; font-size:22px; line-height:1.05; }}
      .btn.stop.active{{ background:#ff8b8b; }}
      .btn.up{{ left:125px; top:0; }} .btn.left{{ left:0; top:125px; }}
      .btn.right{{ right:0; top:125px; }} .btn.down{{ left:125px; bottom:0; }}
      .btn.stop{{ left:125px; top:125px; }}
      .pad-ring{{ position:absolute; inset:10px; border-radius:24px; border:2px dashed #e5e7eb; }}
      .hint{{ text-align:center; margin-top:10px; color:#6b7280; font-size:13px; }}
      .warn{{ text-align:center; margin-top:6px; font-size:12px; color:#b91c1c; display:none; }}
    </style>
    <div id="kbbox" class="ctr-wrap" tabindex="0">
      <div class="pad">
        <div class="pad-ring"></div>
        <div id="btnU" class="btn up">▲</div>
        <div id="btnL" class="btn left">◀</div>
        <div id="btnR" class="btn right">▶</div>
        <div id="btnD" class="btn down">▼</div>
        <div id="btnS" class="btn stop">⏹<br>STOP</div>
      </div>
      <div class="hint">↑/←/→/↓ 꾹 누르면 연속 전송 • Space/Enter=정지</div>
      <div id="revWarn" class="warn">/cmd/throttle 없음 → 백엔드 업데이트 필요</div>
    </div>
    <script>
      const API_BASE="{api_base}", PWM={int(pwm_val)}, INTERVAL={interval_ms},
            TIMEOUT={int(timeout_sec*1000)}, SEND_ZERO={json.dumps(send_zero)};
      const box=documen­t.getElementById('kbbox');
      const bU=documen­t.getElementById('btnU'), bL=documen­t.getElementById('btnL'),
            bR=documen­t.getElementById('btnR'), bD=documen­t.getElementById('btnD'),
            bS=documen­t.getElementById('btnS'), revWarn=documen­t.getElementById('revWarn');
      const st={{up:false,left:false,right:false,down:false}}; let timer=null, hasThrottle=true;
      const setA=(el,on)=>el.classList.toggle('active',!!on);
      const paint=()=>{{ setA(bU,st.up); setA(bL,st.left); setA(bR,st.right); setA(bD,st.down); }};
      function post(path, body, cb){{
        const ctrl=new AbortController(); const id=setTimeout(()=>ctrl.abort(), TIMEOUT);
        fetch(API_BASE+path,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body),signal:ctrl.signal}})
          .then(r=>cb&&cb(r.ok,r.status)).catch(()=>cb&&cb(false,0)).finally(()=>clearTimeout(id));
      }}
      function sendThrottle(val){{
        if(!hasThrottle){{ if(val===0) post('/cmd/pwm',{{duty:0}}); return; }}
        post('/cmd/throttle',{{val:val}},(ok,s)=>{{ if(!ok&&(s===404||s===405)){{ hasThrottle=false; revWarn.style.display='block';
          if(val===0) post('/cmd/pwm',{{duty:0}}); }} }});
      }}
      function tick(){{ if(st.up)sendThrottle(+PWM); if(st.down)sendThrottle(-PWM);
        if(st.left)post('/cmd/steer',{{dir:'left'}}); if(st.right)post('/cmd/steer',{{dir:'right'}});
        if(!st.up&&!st.down&&!st.left&&!st.right){{ clearInterval(timer); timer=null; }} }}
      function start(){{ if(!timer) timer=setInterval(tick,INTERVAL); }}
      function stopAll(){{ st.up=st.left=st.right=st.down=false; paint(); sendThrottle(0); if(timer){{clearInterval(timer);timer=null;}} }}
      function bindHold(el,key,action){{
        const down=(e)=>{{ e.preventDefault(); if(action==='stop'){{ stopAll(); el.classList.add('active'); setTimeout(()=>el.classList.remove('active'),120); return; }}
          st[key]=true; paint(); tick(); start(); }};
        const up=(e)=>{{ e.preventDefault(); if(action!=='stop'){{ st[key]=false; paint(); if(SEND_ZERO&&(key==='up'||key==='down')) sendThrottle(0); }} }};
        el.addEventListener('mousedown',down); el.addEventListener('mouseup',up); el.addEventListener('mouseleave',up);
        el.addEventListener('touchstart',down,{{passive:false}}); el.addEventListener('touchend',up,{{passive:false}});
      }}
      bindHold(bU,'up'); bindHold(bL,'left'); bindHold(bR,'right'); bindHold(bD,'down'); bindHold(bS,null,'stop');
      box.addEventListener('keydown',(e)=>{{ if(['ArrowUp','ArrowLeft','ArrowRight','ArrowDown',' ','Enter'].includes(e.key)){{
        e.preventDefault(); if(e.key==='ArrowUp')st.up=true; if(e.key==='ArrowLeft')st.left=true; if(e.key==='ArrowRight')st.right=true;
        if(e.key==='ArrowDown')st.down=true; if(e.key===' '||e.key==='Enter'){{ stopAll(); bS.classList.add('active'); setTimeout(()=>bS.classList.remove('active'),120); return; }}
        paint(); tick(); start(); }} }});
      box.addEventListener('keyup',(e)=>{{ if(['ArrowUp','ArrowLeft','ArrowRight','ArrowDown'].includes(e.key)){{
        e.preventDefault(); if(e.key==='ArrowUp')st.up=false; if(e.key==='ArrowLeft')st.left=false; if(e.key==='ArrowRight')st.right=false; if(e.key==='ArrowDown')st.down=false;
        paint(); if(SEND_ZERO&&(e.key==='ArrowUp'||e.key==='ArrowDown')) sendThrottle(0); }} }});
      document.addEventListener('visibilitychange',()=>{{ if(document.hidden) stopAll(); }}); box.addEventListener('blur',stopAll); setTimeout(()=>box.focus(),100);
    </script>
    """
    components.html(html, height=offset_px + 420)

# ── (B) 카메라 ──────────────────────────────
def render_live_cam():
    st.subheader("📷 Live Cam")
    if cam_mode == "데모":
        components.html("""
        <style>.cam{position:relative;height:360px;border:1px solid #ddd;border-radius:12px;overflow:hidden;background:#111}
        .badge{position:absolute;left:12px;top:12px;background:#fff3;color:#fff;padding:4px 10px;border-radius:999px;font-weight:700}
        canvas{width:100%;height:100%}</style>
        <div class="cam"><div class="badge">DEMO</div><canvas id="c"></canvas></div>
        <script>
        const can=document.getElementById('c'),ctx=can.getContext('2d'); function R(){can.width=can.clientWidth;can.height=can.clientHeight;}
        window.addEventListener('resize',R); R();
        function draw(t){const w=can.width,h=can.height;const g=ctx.createLinearGradient(0,0,0,h);g.addColorStop(0,'#1b2735');g.addColorStop(1,'#090a0f');
          ctx.fillStyle=g;ctx.fillRect(0,0,w,h);const r=40+10*Math.sin(t*0.002),cx=(w/2)+Math.sin(t*0.0015)*w*0.3,cy=h*0.35+Math.sin(t*0.001)*10;
          ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.fillStyle='#ffcc33';ctx.fill();
          ctx.beginPath();for(let x=0;x<w;x++){const y=h*0.6+Math.sin((x*0.02)+(t*0.006))*8+Math.sin((x*0.04)-(t*0.004))*5; if(x===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}
          ctx.strokeStyle='#2ec4b6';ctx.lineWidth=2;ctx.stroke(); requestAnimationFrame(draw);} requestAnimationFrame(draw);
        </script>
        """, height=380)
    elif cam_mode == "노트북 웹캠":
        components.html("""
        <style>.cam{position:relative;height:360px;border:1px solid #ddd;border-radius:12px;overflow:hidden;background:#000}
        .cam video{width:100%;height:100%;object-fit:cover}</style>
        <div class="cam"><video id="v" autoplay playsinline muted></video></div>
        <script>
        let s=null; async function start(){try{ s=await navigator.mediaDevices.getUserMedia({video:true}); document.getElementById('v').srcObject=s;}catch(e){}}
        function stop(){ if(s){ s.getTracks().forEach(t=>t.stop()); s=null; } } document.addEventListener('visibilitychange',()=>{if(document.hidden) stop();});
        start();
        </script>
        """, height=380)
    else:
        components.html(f"""
        <style>.cam{{position:relative;height:360px;border:1px solid #ddd;border-radius:12px;overflow:hidden;background:#000}}
        .cam img{{width:100%;height:100%;object-fit:cover}}</style>
        <div class="cam"><img src="{cam_url}"></div>
        """, height=380)

# ── (C) 지도 ────────────────────────────────
def render_map():
    try:
        from streamlit_folium import st_folium
        import folium
    except Exception:
        st.warning("pip install streamlit-folium folium")
        return

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0088
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1); dl = math.radians(lon2 - lon1)
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*R*math.asin(math.sqrt(a))

    if "pos" not in st.session_state:
        st.session_state.pos = {"lat": 35.1796, "lng": 129.0756}
    if "dst" not in st.session_state:
        st.session_state.dst = {"lat": 35.1700, "lng": 129.1300}

    st.subheader("🗺️ 지도")
    pos = st.session_state.pos; dst = st.session_state.dst
    c1,c2,c3 = st.columns(3)
    pos_lat = c1.number_input("위도", value=pos["lat"], format="%.6f")
    pos_lng = c2.number_input("경도", value=pos["lng"], format="%.6f")
    speed_kn = c3.number_input("선속(kt)", value=max(0.0, round((pwm/100)*6.0, 1)), step=0.1)
    d1,d2 = st.columns(2)
    dst_lat = d1.number_input("목표 위도", value=dst["lat"], format="%.6f")
    dst_lng = d2.number_input("목표 경도", value=dst["lng"], format="%.6f")
    st.session_state.pos = {"lat": float(pos_lat), "lng": float(pos_lng)}
    st.session_state.dst = {"lat": float(dst_lat), "lng": float(dst_lng)}

    dist_km = haversine_km(pos_lat, pos_lng, dst_lat, dst_lng)
    eta_text = "—"
    if speed_kn > 0:
        eta_h = dist_km / (speed_kn * 1.852)
        h, m = int(eta_h), int(round((eta_h - int(eta_h)) * 60))
        eta_text = f"{h}h {m}m"

    center = [(pos_lat + dst_lat)/2, (pos_lng + dst_lng)/2]
    m = folium.Map(location=center, zoom_start=12, tiles="OpenStreetMap")
    folium.Marker([pos_lat, pos_lng], tooltip="현재").add_to(m)
    folium.Marker([dst_lat, dst_lng], tooltip="목표").add_to(m)
    folium.PolyLine([[pos_lat,pos_lng],[dst_lat,dst_lng]], color="#22c55e", weight=5, opacity=0.9,
                    tooltip=f"{dist_km:.2f} km, ETA {eta_text}").add_to(m)
    out = st_folium(m, height=430, use_container_width=True)
    if out and out.get("last_clicked"):
        st.session_state.dst = {"lat": out["last_clicked"]["lat"], "lng": out["last_clicked"]["lng"]}
        try: st.rerun()
        except Exception: pass

# ── (D) LiDAR 패널(자율) ────────────────────
def _simulate_lidar_scan(t: float, n: int, rmax: float, sigma: float,
                         dropout_rate: float, moving_obstacles: bool) -> Tuple[np.ndarray, np.ndarray]:
    theta = np.linspace(0, 2*np.pi, n, endpoint=False)
    base = 6.5 + 0.9*np.cos(theta - 0.3) + 0.6*np.cos(2*theta + 0.6) + 0.25*np.sin(3*theta + 0.5*t)
    r = base + np.random.normal(0.0, sigma, size=n)
    if moving_obstacles:
        ang_a = (0.8*t) % (2*np.pi); idx_a = int(ang_a / (2*np.pi) * n)
        for k in range(-2, 3): r[(idx_a + k) % n] = 1.6 + 0.2*np.random.randn()
        ang_b = (0.8*t + np.pi) % (2*np.pi); idx_b = int(ang_b / (2*np.pi) * n)
        for k in range(-3, 4): r[(idx_b + k) % n] = 3.0 + 0.2*np.random.randn()
    if dropout_rate > 0:
        mask = np.random.rand(n) < (dropout_rate / 100.0); r[mask] = np.nan
    r = np.clip(r, 0.2, rmax)
    return theta, r

def _render_polar(theta: np.ndarray, r: np.ndarray, rmax: float, title: str):
    fig = plt.figure(figsize=(6.2, 6.2))
    ax = fig.add_subplot(111, projection="polar")
    ax.set_theta_zero_location("E"); ax.set_theta_direction(-1); ax.set_rmax(rmax)
    ax.grid(True, alpha=0.35)
    ax.set_rticks([rmax*0.25, rmax*0.5, rmax*0.75, rmax])
    ax.scatter(theta, r, s=9, c="#1f77b4", alpha=0.9)
    ax.set_title(title, pad=20, fontsize=14, fontweight="bold")
    st.pyplot(fig, clear_figure=True); plt.close(fig)

def render_lidar_panel_center(api_base: str):
    st.subheader("📡 LiDAR")
    with st.sidebar.expander("자율운항 ▸ LiDAR", expanded=True):
        run = st.toggle("실시간", value=False, key="lidar_run5")
        hz_l = st.slider("Hz", 1, 30, 10, key="lidar_hz5")

    POINTS, R_MAX, SIGMA, DROPOUT, SHOW_OBS = 360, 20.0, 0.06, 3, True
    placeholder = st.empty(); stats = st.empty()

    def draw_once():
        t = time.time()
        th, rr = _simulate_lidar_scan(t, POINTS, R_MAX, SIGMA, DROPOUT, SHOW_OBS)
        _render_polar(th, rr, R_MAX, "LiDAR")
        stats.caption(f"{time.strftime('%H:%M:%S')} | pts={POINTS}, Rmax={R_MAX:.1f}m")

    if run:
        with placeholder.container(): draw_once()
        interval = 1.0 / max(1, hz_l)
        while st.session_state.get("lidar_run5", False):
            time.sleep(interval)
            with placeholder.container(): draw_once()
    else:
        with placeholder.container(): draw_once()

# ── 3열 배치 ────────────────────────────────
col_cam, col_mid, col_map = st.columns([0.34, 0.32, 0.34], gap="large")
with col_cam: render_live_cam()
with col_mid:
    if mode == "수동조작":
        st.subheader("🕹️ 리모컨")
        render_big_controller(60, API_BASE, pwm, hz, timeout_s, send_zero_on_release)
    else:
        render_lidar_panel_center(API_BASE)
with col_map: render_map()
# pages/5_메인_컨트롤_LiveCam.py
import math, time, json
from typing import Tuple, Optional

import requests
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import time

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


custom_sidebar()



LOGIN_PAGE = "pages/5_5. 로그인.py"

# ── 접근 권한 팝업 ─────────────────────────────────────────────────────────────
# 1) 모달 함수 (Streamlit 1.30+ st.dialog 사용)
try:
    dialog = st.dialog  # 존재 여부 체크
except AttributeError:
    dialog = None

if dialog:
    @dialog("⚠️ 관리자 권한 페이지", width="small")
    def _auth_modal():
        logged_in = bool(st.session_state.get("logged_in", False))
        msg = "접근 권한이 확인되었습니다." if logged_in else "접근 권한이 없습니다."
        st.write(msg)

        c1, c2 = st.columns([1, 0.2])
        with c2:
            # 버튼: 로그인 상태에 따라 동작 분기
            if st.button("예, 알겠습니다.", key="auth_close", use_container_width=True):
                if logged_in:
                    # 그냥 닫고 계속 진행 (이 페이지에 머무름)
                    st.session_state["_auth_modal_shown"] = True
                    st.rerun()
                else:
                    # 로그인 페이지로 이동
                    st.switch_page(LOGIN_PAGE)

    # 2) 최초 진입 시 한 번만 모달 띄우기
    if not st.session_state.get("_auth_modal_shown", False):
        _auth_modal()
        # 미로그인일 땐 뒤 코드 실행 막아서 상호작용 방지
        if not st.session_state.get("logged_in", False):
            st.stop()

else:
    # ── 구버전( st.dialog 없음 ) 대체: 토스트 + 리다이렉트 ──
    if st.session_state.get("logged_in", False):
        if not st.session_state.get("_auth_ok_once", False):
            st.toast("접근 권한이 확인되었습니다.", icon="✅")
            st.session_state["_auth_ok_once"] = True
    else:
        st.toast("접근 권한이 없습니다. 로그인 페이지로 이동합니다.", icon="🚫")
        time.sleep(1.0)
        st.switch_page(LOGIN_PAGE)
        st.stop()

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

st.set_page_config(
    page_title="메인 컨트롤",
    page_icon="🕹️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    "🕹️ 메인 컨트롤"
    "</div>",
    unsafe_allow_html=True
    )
# ── 컨트롤 값의 기본(state) 확보 ──────────────────────────────────────────────
def _get(name, default):
    if name not in st.session_state:
        st.session_state[name] = default
    return st.session_state[name]

API_BASE = _get("api_input", "http://127.0.0.1:8000")
mode = _get("mode", "수동조작 모드")
hz = _get("hz", 10)
timeout_s = _get("timeout_s", 1.0)
send_zero_on_release = _get("send_zero_on_release", True)
cam_mode = _get("cam_mode", "데모(가상 영상)")
cam_url = _get("cam_url", f"{API_BASE}/cam/mjpeg")  # 최초 기본은 API_BASE 기반


custom_sidebar()
top_header()
st.caption("원격으로 선박을 조종하며 Live Cam 과 지도를 이용해 실시간 위치를 파악하고 제어합니다.")




# 수동조작 모드에서만 속도 슬라이더 노출(자율운항 모드도 지도 ETA 계산에는 사용)
pwm = st.slider("속도(PWM%)", 0, 100, 40, key="pwm_slider")

# ──────────────────────────────────────────────────────────────────────────────
# (A) 리모컨: 큰 게임패드(전/후진 + 좌/우 + STOP)
# ──────────────────────────────────────────────────────────────────────────────
def render_big_controller(offset_px: int, api_base: str, pwm_val: int, hz_val: int,
                          timeout_sec: float, send_zero: bool):
    interval_ms = int(1000 / max(1, hz_val))
    html = f"""
    <style>
      .ctr-wrap{{ margin-top:{offset_px}px; }}
      .pad{{ position:relative; width:360px; height:360px; margin:auto; }}
      .btn{{
        position:absolute; width:110px; height:110px; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        font-weight:900; font-size:34px; user-select:none; cursor:default;
        background:radial-gradient(circle at 30% 30%, #f4f6fb, #e6e9f3); color:#1f2937;
        border:1px solid #cfd6e3; box-shadow:0 12px 20px rgba(0,0,0,.08), inset 0 -2px 0 rgba(255,255,255,.5);
        transition:transform .05s, box-shadow .05s, background .05s;
      }}
      .btn.active{{
        background:radial-gradient(circle at 30% 30%, #c8f7d0, #86e3a1);
        border-color:#7edaa1; transform:scale(.96); box-shadow:inset 0 4px 12px rgba(0,0,0,.18);
      }}
      .btn.stop{{ background:radial-gradient(circle at 30% 30%, #ffe2e2, #ffb3b3); border-color:#ff9aa2; font-size:22px; line-height:1.05; }}
      .btn.stop.active{{ background:radial-gradient(circle at 30% 30%, #ffb9b9, #ff8b8b); }}
      .btn.up{{ left:125px; top:0; }}
      .btn.left{{ left:0; top:125px; }}
      .btn.right{{ right:0; top:125px; }}
      .btn.down{{ left:125px; bottom:0; }}
      .btn.stop{{ left:125px; top:125px; }}
      .pad-ring{{ position:absolute; inset:10px; border-radius:24px; border:2px dashed #e5e7eb; }}
      .hint{{ text-align:center; margin-top:10px; color:#6b7280; font-size:13px; }}
      .warn{{ text-align:center; margin-top:6px; font-size:12px; color:#b91c1c; display:none; }}
    </style>

    <div id="kbbox" class="ctr-wrap" tabindex="0">
      <div class="pad">
        <div class="pad-ring"></div>
        <div id="btnU" class="btn up">▲</div>
        <div id="btnL" class="btn left">◀</div>
        <div id="btnR" class="btn right">▶</div>
        <div id="btnD" class="btn down">▼</div>
        <div id="btnS" class="btn stop">⏹<br>STOP</div>
      </div>
      <div class="hint">이 영역을 클릭(포커스 ON) 후 <b>↑ / ← / → / ↓</b> 를 꾹 누르면 연속 전송 • <b>Space/Enter</b>=정지</div>
      <div id="revWarn" class="warn">후진 API(/cmd/throttle)가 서버에 없어요. 먼저 백엔드를 업데이트 해주세요.</div>
    </div>

    <script>
      const API_BASE="{api_base}";
      const PWM={int(pwm_val)};
      const INTERVAL={interval_ms};
      const TIMEOUT={int(timeout_sec*1000)};
      const SEND_ZERO={json.dumps(send_zero)};

      const box=document.getElementById('kbbox');
      const bU=document.getElementById('btnU'), bL=document.getElementById('btnL'),
            bR=document.getElementById('btnR'), bD=document.getElementById('btnD'),
            bS=document.getElementById('btnS'), revWarn=document.getElementById('revWarn');

      const st={{up:false,left:false,right:false,down:false}};
      let timer=null, hasThrottle=true;

      const setA=(el,on)=>el.classList.toggle('active',!!on);
      const paint=()=>{{ setA(bU,st.up); setA(bL,st.left); setA(bR,st.right); setA(bD,st.down); }};

      function post(path, body, cb){{
        const ctrl=new AbortController(); const id=setTimeout(()=>ctrl.abort(), TIMEOUT);
        fetch(API_BASE+path,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body),signal:ctrl.signal}})
          .then(res=>{{ cb && cb(res.ok, res.status); }})
          .catch(()=>{{ cb && cb(false, 0); }})
          .finally(()=>clearTimeout(id));
      }}

      function sendThrottle(val){{
        if(!hasThrottle){{
          if (val===0) post('/cmd/pwm', {{duty:0}});
          return;
        }}
        post('/cmd/throttle', {{val:val}}, (ok, status)=>{{
          if(!ok && (status===404 || status===405)){{
            hasThrottle=false; revWarn.style.display='block';
            if (val===0) post('/cmd/pwm', {{duty:0}});
          }}
        }});
      }}

      function tick(){{
        if (st.up)    sendThrottle(+PWM);
        if (st.down)  sendThrottle(-PWM);
        if (st.left)  post('/cmd/steer', {{dir:'left'}});
        if (st.right) post('/cmd/steer', {{dir:'right'}});
        if (!st.up && !st.down && !st.left && !st.right){{ clearInterval(timer); timer=null; }}
      }}
      function start(){{ if (!timer) timer=setInterval(tick, INTERVAL); }}
      function stopAll(){{
        st.up=st.left=st.right=st.down=false; paint();
        sendThrottle(0);
        if (timer){{ clearInterval(timer); timer=null; }}
      }}

      function bindHold(el, key, action){{
        const down=(e)=>{{ e.preventDefault();
          if (action==='stop'){{ stopAll(); el.classList.add('active'); setTimeout(()=>el.classList.remove('active'),120); return; }}
          st[key]=true; paint(); tick(); start();
        }};
        const up=(e)=>{{ e.preventDefault();
          if (action!=='stop'){{ st[key]=false; paint(); if (SEND_ZERO && (key==='up' || key==='down')) sendThrottle(0); }}
        }};
        el.addEventListener('mousedown',down); el.addEventListener('mouseup',up); el.addEventListener('mouseleave',up);
        el.addEventListener('touchstart',down,{{passive:false}}); el.addEventListener('touchend',up,{{passive:false}});
      }}
      bindHold(bU,'up'); bindHold(bL,'left'); bindHold(bR,'right'); bindHold(bD,'down'); bindHold(bS,null,'stop');

      box.addEventListener('keydown',(e)=>{{
        if (['ArrowUp','ArrowLeft','ArrowRight','ArrowDown',' ','Enter'].includes(e.key)){{
          e.preventDefault();
          if (e.key==='ArrowUp') st.up=true;
          if (e.key==='ArrowLeft') st.left=true;
          if (e.key==='ArrowRight') st.right=true;
          if (e.key==='ArrowDown') st.down=true;
          if (e.key===' ' || e.key==='Enter'){{ stopAll(); bS.classList.add('active'); setTimeout(()=>bS.classList.remove('active'),120); return; }}
          paint(); tick(); start();
        }}
      }});
      box.addEventListener('keyup',(e)=>{{
        if (['ArrowUp','ArrowLeft','ArrowRight','ArrowDown'].includes(e.key)){{
          e.preventDefault();
          if (e.key==='ArrowUp') st.up=false;
          if (e.key==='ArrowLeft') st.left=false;
          if (e.key==='ArrowRight') st.right=false;
          if (e.key==='ArrowDown') st.down=false;
          paint(); if (SEND_ZERO && (e.key==='ArrowUp' || e.key==='ArrowDown')) sendThrottle(0);
        }}
      }});

      document.addEventListener('visibilitychange', ()=>{{ if (document.hidden) stopAll(); }});
      box.addEventListener('blur', stopAll);
      setTimeout(()=>box.focus(), 100);
    </script>
    """
    components.html(html, height=offset_px + 420)

# ──────────────────────────────────────────────────────────────────────────────
# (B) Live Cam
# ──────────────────────────────────────────────────────────────────────────────
def render_live_cam():
    st.subheader("📷 Live Cam")
    if cam_mode == "데모(가상 영상)":
        html_demo = """
        <style>
        .camwrap { position:relative; width:100%; height:360px; border:1px solid #ddd; border-radius:12px; overflow:hidden; background:#111;}
        .badge   { position:absolute; left:12px; top:12px; background:#fff3; color:#fff; padding:4px 10px; border-radius:999px; font-weight:700; letter-spacing:1px;}
        canvas   { width:100%; height:100%; display:block; }
        </style>
        <div class="camwrap">
          <div class="badge">DEMO</div>
          <canvas id="c"></canvas>
        </div>
        <script>
        const can = document.getElementById('c'); const ctx = can.getContext('2d');
        function resize() { can.width = can.clientWidth; can.height = can.clientHeight; }
        window.addEventListener('resize', resize); resize();
        function draw(t) {
          const w = can.width, h = can.height;
          const g = ctx.createLinearGradient(0,0,0,h);
          g.addColorStop(0,'#1b2735'); g.addColorStop(1,'#090a0f');
          ctx.fillStyle = g; ctx.fillRect(0,0,w,h);
          const r = 40 + 10*Math.sin(t*0.002);
          const cx = (w/2) + Math.sin(t*0.0015)*w*0.3;
          const cy = h*0.35 + Math.sin(t*0.001)*10;
          ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI*2);
          ctx.fillStyle = '#ffcc33'; ctx.fill();
          ctx.beginPath();
          for (let x=0; x<w; x++) {
            const y = h*0.6 + Math.sin((x*0.02)+(t*0.006))*8 + Math.sin((x*0.04)-(t*0.004))*5;
            if (x===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
          }
          ctx.strokeStyle = '#2ec4b6'; ctx.lineWidth = 2; ctx.stroke();
          ctx.fillStyle = '#fff'; ctx.font = '12px sans-serif';
          const ts = new Date().toLocaleTimeString();
          ctx.fillText('SIMULATED FEED — '+ts, 12, h-12);
          requestAnimationFrame(draw);
        }
        requestAnimationFrame(draw);
        </script>
        """
        components.html(html_demo, height=380)
        st.caption("가상(데모) 화면입니다. Pi 연결 시 ‘MJPEG 주소’로 전환하세요.")
    elif cam_mode == "노트북 웹캠(브라우저)":
        html_local_cam = """
        <style>
        .camwrap { position:relative; width:100%; height:360px; border:1px solid #ddd; border-radius:12px; overflow:hidden; background:#000; }
        .camwrap video { width:100%; height:100%; object-fit:cover; display:block; }
        .badge { position:absolute; left:12px; top:12px; background:#0008; color:#fff; padding:4px 10px; border-radius:999px; font-weight:700; letter-spacing:1px;}
        .stat { margin-top:6px; font-size:12px; color:#666; }
        </style>
        <div class="camwrap">
          <div class="badge">LOCAL CAM</div>
          <video id="v" autoplay playsinline muted></video>
        </div>
        <div class="stat">상태: <span id="st">권한 대기…</span></div>
        <script>
        const v = document.getElementById('v'); const st = document.getElementById('st');
        let localStream = null;
        async function start() {
          try {
            const constraints = { video: { width: {ideal: 1280}, height: {ideal: 720}, facingMode: "user" } };
            localStream = await navigator.mediaDevices.getUserMedia(constraints);
            v.srcObject = localStream; st.textContent = "🟢 카메라 연결됨";
          } catch (e) { console.error(e); st.textContent = "🔴 권한 거부 / 장치 없음 / 보안 정책 문제"; }
        }
        function stop() { if (localStream) { localStream.getTracks().forEach(t => t.stop()); localStream = null; st.textContent = "⏹️ 중지됨"; } }
        document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
        window.addEventListener('beforeunload', stop);
        start();
        </script>
        """
        components.html(html_local_cam, height=420)
        st.caption("처음 실행 시 브라우저 카메라 권한을 허용하세요.")
    else:
        html_mjpeg = f"""
        <style>
        .camwrap {{ position:relative; width:100%; height:360px; border:1px solid #ddd; border-radius:12px; overflow:hidden; background:#000; }}
        .camwrap img {{ width:100%; height:100%; object-fit:cover; display:block; }}
        .stat {{ margin-top:6px; font-size:12px; color:#666; }}
        </style>
        <div class="camwrap">
          <img id="cam" src="{cam_url}">
        </div>
        <div class="stat">상태: <span id="st">연결 시도 중…</span></div>
        <script>
        const img = document.getElementById('cam'); const st  = document.getElementById('st');
        img.onload  = ()=>{{ st.textContent='🟢 연결됨'; }};
        img.onerror = ()=>{{ st.textContent='🔴 연결 실패 (주소/서버/CORS 확인)'; }};
        </script>
        """
        components.html(html_mjpeg, height=420)

# ──────────────────────────────────────────────────────────────────────────────
# (C) 지도 & 경로
# ──────────────────────────────────────────────────────────────────────────────
def render_map():
    try:
        from streamlit_folium import st_folium
        import folium
    except Exception:
        st.warning("지도 기능: pip install streamlit-folium folium 설치 필요")
        return

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0088
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*R*math.asin(math.sqrt(a))

    if "pos" not in st.session_state:
        st.session_state.pos = {"lat": 35.1796, "lng": 129.0756}
    if "dst" not in st.session_state:
        st.session_state.dst = {"lat": 35.1700, "lng": 129.1300}

    st.subheader("🗺️ 지도 & 경로(직선 최단)")
    c1, c2, c3 = st.columns(3)
    pos_lat = c1.number_input("현재 위도", value=st.session_state.pos["lat"], format="%.6f")
    pos_lng = c2.number_input("현재 경도", value=st.session_state.pos["lng"], format="%.6f")
    speed_kn = c3.number_input("선속(노트)", value=max(0.0, round((pwm/100)*6.0, 1)), step=0.1)

    d1, d2 = st.columns(2)
    dst_lat = d1.number_input("목적지 위도", value=st.session_state.dst["lat"], format="%.6f")
    dst_lng = d2.number_input("목적지 경도", value=st.session_state.dst["lng"], format="%.6f")

    st.session_state.pos = {"lat": float(pos_lat), "lng": float(pos_lng)}
    st.session_state.dst = {"lat": float(dst_lat), "lng": float(dst_lng)}

    dist_km = haversine_km(pos_lat, pos_lng, dst_lat, dst_lng)
    if speed_kn > 0:
        eta_h = dist_km / (speed_kn * 1.852)
        h, m = int(eta_h), int(round((eta_h - int(eta_h)) * 60))
        eta_text = f"{h}h {m}m"
    else:
        eta_text = "—"

    center = [(pos_lat + dst_lat)/2, (pos_lng + dst_lng)/2]
    m = folium.Map(location=center, zoom_start=12, tiles="OpenStreetMap")
    folium.Marker([pos_lat, pos_lng], tooltip="현재 위치",
                  icon=folium.Icon(color="blue", icon="ship", prefix="fa")).add_to(m)
    folium.Marker([dst_lat, dst_lng], tooltip="목적지",
                  icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(m)
    folium.PolyLine([[pos_lat,pos_lng],[dst_lat,dst_lng]], color="#22c55e", weight=5, opacity=0.9,
                    tooltip=f"거리 {dist_km:.2f} km, ETA {eta_text}").add_to(m)
    folium.LatLngPopup().add_to(m)

    out = st_folium(m, height=430, use_container_width=True)
    if out and out.get("last_clicked"):
        st.session_state.dst = {"lat": out["last_clicked"]["lat"], "lng": out["last_clicked"]["lng"]}
        try:
            st.rerun()
        except Exception:
            pass
    st.caption(f"거리: {dist_km:.2f} km | 선속: {speed_kn:.1f} km | ETA: {eta_text}  (직선 경로)")

# ──────────────────────────────────────────────────────────────────────────────
# (D) LiDAR 패널(자율운항 모드에서 리모컨 자리에 표시)
#  - 더미/실시간 모드 선택
# ──────────────────────────────────────────────────────────────────────────────
def _simulate_lidar_scan(t: float, n: int, rmax: float, sigma: float,
                         dropout_rate: float, moving_obstacles: bool) -> Tuple[np.ndarray, np.ndarray]:
    theta = np.linspace(0, 2*np.pi, n, endpoint=False)
    base = 6.5 + 0.9*np.cos(theta - 0.3) + 0.6*np.cos(2*theta + 0.6) + 0.25*np.sin(3*theta + 0.5*t)
    r = base + np.random.normal(0.0, sigma, size=n)
    if moving_obstacles:
        ang_a = (0.8*t) % (2*np.pi); idx_a = int(ang_a / (2*np.pi) * n)
        for k in range(-2, 3): r[(idx_a + k) % n] = 1.6 + 0.2*np.random.randn()
        ang_b = (0.8*t + np.pi) % (2*np.pi); idx_b = int(ang_b / (2*np.pi) * n)
        for k in range(-3, 4): r[(idx_b + k) % n] = 3.0 + 0.2*np.random.randn()
    if dropout_rate > 0:
        mask = np.random.rand(n) < (dropout_rate / 100.0); r[mask] = np.nan
    r = np.clip(r, 0.2, rmax)
    return theta, r

def _render_polar(theta: np.ndarray, r: np.ndarray, rmax: float, title: str):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(6.2, 6.2))
    ax = fig.add_subplot(111, projection="polar")
    ax.set_theta_zero_location("E"); ax.set_theta_direction(-1); ax.set_rmax(rmax)
    ax.grid(True, alpha=0.35)
    ax.set_rticks([rmax*0.25, rmax*0.5, rmax*0.75, rmax])
    ax.scatter(theta, r, s=9, c="#1f77b4", alpha=0.9)
    ax.set_title(title, pad=20, fontsize=14, fontweight="bold")
    st.pyplot(fig, clear_figure=True); plt.close(fig)

def _fetch_real_frame(api_base: str, timeout: float) -> Optional[Tuple[np.ndarray, np.ndarray, float]]:
    try:
        r = requests.get(f"{api_base}/lidar/latest", timeout=timeout)
        if r.status_code != 200: return None
        js = r.json()
        if isinstance(js, dict):
            if "theta" in js and "r" in js:
                th = np.array(js["theta"], dtype=float); rr = np.array(js["r"], dtype=float)
            elif "angles_deg" in js and "ranges_m" in js:
                th = np.deg2rad(np.array(js["angles_deg"], dtype=float)); rr = np.array(js["ranges_m"], dtype=float)
            else:
                return None
        elif isinstance(js, list) and js and isinstance(js[0], dict):
            ang = [it.get("ang_deg", it.get("angle_deg", 0.0)) for it in js]
            rng = [it.get("r", it.get("range_m", np.nan)) for it in js]
            th = np.deg2rad(np.array(ang, dtype=float)); rr = np.array(rng, dtype=float)
        else:
            return None
        ts = time.time()
        return th, rr, ts
    except Exception:
        return None

def render_lidar_panel_center(api_base: str):
    st.subheader("📡 LiDAR")

    # 사이드바: 실시간 on/off + 갱신 주기만 노출
    with st.sidebar.expander("자율운항 ▸ LiDAR", expanded=True):
        run = st.toggle("실시간 수신 시작", value=False, key="lidar_run5")
        hz_l = st.slider("갱신 주기(Hz)", 1, 30, 10, key="lidar_hz5")

    # 고정 파라미터(실제 센서처럼 보이는 기본값)
    POINTS      = 360     # 스캔 해상도(포인트 수) 고정
    R_MAX       = 20.0    # 최대거리(m) 고정
    SIGMA       = 0.06    # 노이즈 표준편차(m) 고정
    DROPOUT     = 3       # 드롭아웃(%) 고정
    SHOW_OBS    = True    # 이동 물체 표현 고정

    placeholder = st.empty()
    stats = st.empty()

    def draw_once():
        t = time.time()
        th, rr = _simulate_lidar_scan(t, POINTS, R_MAX, SIGMA, DROPOUT, SHOW_OBS)
        _render_polar(th, rr, R_MAX, "실시간 LiDAR")
        stats.caption(f"프레임: {time.strftime('%H:%M:%S')} | pts={POINTS}, Rmax={R_MAX:.1f}m")

    if run:
        # 최초 1프레임
        with placeholder.container():
            draw_once()
        # 주기 갱신 루프
        interval = 1.0 / max(1, hz_l)
        while st.session_state.get("lidar_run5", False):
            time.sleep(interval)
            with placeholder.container():
                draw_once()
    else:
        # 정지 상태에서도 한 프레임은 보여줌
        with placeholder.container():
            draw_once()

# ──────────────────────────────────────────────────────────────────────────────
# 3-열 배치: 왼쪽=Live Cam / 가운데=리모컨 또는 LiDAR / 오른쪽=지도
# ──────────────────────────────────────────────────────────────────────────────
col_cam, col_mid, col_map = st.columns([0.34, 0.32, 0.34], gap="large")

with col_cam:
    render_live_cam()

with col_mid:
    if mode == "수동조작 모드":
        st.subheader("🕹️ 리모컨")
        render_big_controller(
            offset_px=60,
            api_base=API_BASE,
            pwm_val=pwm,
            hz_val=hz,
            timeout_sec=timeout_s,
            send_zero=send_zero_on_release,
        )
    else:
        render_lidar_panel_center(API_BASE)

with col_map:
    render_map()


# ──────────────────────────────────────────────────────────────────────────────
# 페이지 하단 컨트롤 패널 (상단 3열 아래, 맨 끝)
# ──────────────────────────────────────────────────────────────────────────────

with st.container():
    st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)

    st.markdown(
            f'<div class="card-header"><div class="card-title">⚙️ 제어 설정</div></div>',
            unsafe_allow_html=True,
        )
    # ▶ Row 1: API / 카메라 모드 / MJPEG URL (3열 고정폭 → 정렬 깔끔)
    r1c1, r1c2, r1c3 = st.columns([0.34, 0.32, 0.34])
    with r1c1:
        st.text_input("제어 API 주소", st.session_state["api_input"], key="api_input")
    with r1c2:
        st.selectbox("카메라 모드", ["데모(가상 영상)", "노트북 웹캠(브라우저)", "MJPEG 주소"], key="cam_mode")
    with r1c3:
        # 사용자가 직접 수정한 적 없으면 API_BASE 변화에 맞춰 기본값 갱신
        if "cam_url_user_touched" not in st.session_state:
            st.session_state.cam_url = f'{st.session_state["api_input"]}/cam/mjpeg'
        cam_changed = st.text_input("카메라 MJPEG URL", st.session_state["cam_url"], key="cam_url")
        # 사용자가 직접 손댔는지 플래그
        st.session_state.cam_url_user_touched = True

    # ▶ Row 2: 운항 모드 / 전송주기 & 타임아웃 / 체크박스 (3열 동일폭 → 정렬 깔끔)
    r2c1, r2c2, r2c3 = st.columns([0.34, 0.32, 0.34])
    with r2c1:
        st.radio("운항 모드", ["수동조작 모드", "자율운항 모드"], key="mode")
    with r2c2:
        c21, c22 = st.columns(2)
        with c21:
            st.slider("전송 주기(Hz)", 5, 30, st.session_state["hz"], key="hz")
        with c22:
            st.slider("요청 타임아웃(s)", 0.2, 3.0, st.session_state["timeout_s"], 0.1, key="timeout_s")
    with r2c3:
        st.checkbox("키에서 손 떼면 정지(0%) 전송", value=st.session_state["send_zero_on_release"], key="send_zero_on_release")

    st.markdown('</div>', unsafe_allow_html=True)
