import streamlit as st
import time, random, os
from datetime import datetime
from textwrap import dedent
import base64
from streamlit.components.v1 import html
import os

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="Eco-friendShip 통합 대시보드",
    page_icon="🚢",
    layout="wide",
)

# --- 세션 상태 초기화 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = 0.0
if 'weather' not in st.session_state:
    # 기본 초기값 (실제 데이터 연결 시 여기를 교체)
    st.session_state['weather'] = {"irradiance": 750.0, "wind": 5.2, "wave": 0.8, "ts": time.time()}




# --- 스타일: 헤더/카드/이미지 강조 ---
st.markdown(""" 
<style>
/* HERO */
.hero {
    padding: 26px;
    border-radius: 12px;
    background: linear-gradient(90deg, rgba(3,169,244,0.06), rgba(13,110,253,0.03));
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:18px;
    box-shadow: 0 6px 18px rgba(8,30,50,0.04);
}
.h-title { font-size: 32px; font-weight:800; color:#0b3b66; margin:0; }
.h-sub { font-size:16px; color:#356; margin-top:6px; opacity:0.85; }

/* ship card */
.ship-card {
    border-radius:12px;
    overflow:hidden;
    box-shadow:0 8px 22px rgba(0,0,0,0.08);
    background:white;
    padding:8px;
    text-align:center;
}
.ship-card img { width:100%; height:auto; border-radius:8px; display:block; }
.ship-cta { margin-top:8px; font-weight:600; }

/* compact menu */
.menu-compact {
    display:flex;
    gap:12px;
    flex-direction:column;
}
.menu-item {
    padding:14px;
    border-radius:10px;
    background:#fff;
    border:1px solid #eee;
    display:flex;
    justify-content:space-between;
    align-items:center;
    transition: transform .12s ease, box-shadow .12s ease;
}
.menu-item:hover { transform: translateY(-6px); box-shadow:0 10px 26px rgba(8,30,50,0.06); }
.menu-left { display:flex; gap:12px; align-items:center; }
.menu-icon { font-size:22px; }
.menu-title { font-weight:700; font-size:16px; color:#1b3b57; }
.menu-sub { color:#6b7280; font-size:13px; }

/* status badge */
.badge {
    padding:6px 10px;
    border-radius:999px;
    font-weight:700;
    font-size:13px;
    border: 1px solid rgba(0,0,0,0.04);
}
.badge.good { background:#e6f7ea; color:#0b6b2d; }
.badge.warn { background:#fff7e0; color:#b36b00; }
.badge.bad { background:#fdecea; color:#b91c1c; }

/* prediction card */
.pred-card {
    padding:12px;
    border-radius:10px;
    background: linear-gradient(180deg,#ffffff, #f7fbff);
    border:1px solid #e8f0ff;
    box-shadow: 0 6px 16px rgba(14,45,90,0.03);
}
.small-muted { color:#6b7280; font-size:13px; }
            
/* 모든 a 태그와 하위 요소의 밑줄 제거, 색상 상속 강제 */
a.menu-link, a.menu-link:link, a.menu-link:visited, a.menu-link:hover, a.menu-link:active {
  text-decoration: none !important;
  color: inherit !important;
  border-bottom: none !important;
  display: block !important;
}

/* 하위요소까지 확실히 적용 */
a.menu-link * {
  text-decoration: none !important;
  color: inherit !important;
}

/* 포커스는 약하게 표시 (접근성 유지) */
a.menu-link:focus {
  outline: 3px solid rgba(13,110,253,0.12);
  outline-offset: 3px;
  border-radius: 8px;
}

/* ---------- 섹션 블럭 스타일 (소제목 카드형) ---------- */
.section-block {
  background: linear-gradient(180deg,#ffffff,#fbfdff);
  border-radius:12px;
  padding:14px;
  margin-bottom:14px;
  border:1px solid rgba(14,45,90,0.06);
  box-shadow: 0 10px 30px rgba(8,30,50,0.04);
  transition: transform .12s ease, box-shadow .12s ease;
}
.section-heading {
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:12px;
  margin-bottom:10px;
}
.section-title {
  font-weight:800;
  font-size:16px;
  color:#0b3b66;
}
.section-sub {
  font-size:13px;
  color:#6b7280;
}

/* 작은 액센트 배지 (섹션 우측에 넣기 좋음) */
.section-badge {
  padding:6px 10px;
  border-radius:999px;
  font-weight:700;
  font-size:13px;
  border:1px solid rgba(0,0,0,0.04);
  background:#fff;
}

/* HERO 우측 팀정보 영역 (간결) */
.hero-meta { text-align:right; font-size:13px; color:#233; }
.hero-meta .team-name { font-weight:800; font-size:14px; color:#0b3b66; }
.hero-meta .team-members { margin-top:6px; color:#556; font-size:13px; }
            
/* ---------- 예측 카드: 강조된 점수, 위험 배지, 컬러 지표 ---------- */
.visual-pred {
  background: linear-gradient(180deg,#ffffff,#fbfdff);
  border-radius:12px;
  padding:14px;
  border:1px solid rgba(14,45,90,0.06);
  box-shadow: 0 14px 30px rgba(8,30,50,0.04);
}

.visual-header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-bottom:10px;
}

.big-score {
  font-size:38px;
  font-weight:900;
  line-height:1;
  color:#0b3b66;
  letter-spacing:-0.5px;
}

.risk-pill {
  padding:8px 12px;
  border-radius:999px;
  font-weight:800;
  font-size:13px;
  display:inline-flex;
  align-items:center;
  gap:8px;
  box-shadow: 0 6px 18px rgba(11,107,45,0.04);
}

.risk-good { background:#e6f7ea; color:#0b6b2d; border:1px solid rgba(11,107,45,0.08); }
.risk-warn { background:#fff7e0; color:#b36b00; border:1px solid rgba(179,107,0,0.08); }
.risk-bad  { background:#fdecea; color:#b91c1c; border:1px solid rgba(185,28,28,0.08); }

/* 권장조치 텍스트 (작게) */
.recommend { font-size:13px; color:#455; margin-top:6px; font-weight:700; }

/* 메트릭 카드 행 */
.metrics-row {
  display:grid;
  grid-template-columns: 1fr;
  gap:12px;
  margin-top:10px
}
.metrics-row.metrics-stacked .metric{
            width:100%;}
.metric {
  flex:1;
  min-width:90px;
  background:#fff;
  border-radius:10px;
  padding:10px;
  border:1px solid #eef2f7;
  display:flex;
  gap:10px;
  align-items:center;
  box-shadow: 0 6px 18px rgba(10,30,60,0.02);
}
.metric .icon {
  width:44px; height:44px; border-radius:8px;
  display:flex; align-items:center; justify-content:center;
  font-size:20px; color: #fff; font-weight:800;
}
.metric .meta { font-size:15px; color:#6b7280; }
.metric .val { font-weight:900; font-size:20px; color:#0b3b66; }

/* 색상별 아이콘 배경 */
.icon-sun   { background: linear-gradient(90deg,#ffd27a,#ffb84d); }
.icon-wind  { background: linear-gradient(90deg,#9ad1ff,#56a6ff); }
.icon-wave  { background: linear-gradient(90deg,#b6f0e6,#43d2b6); }

/* 반응형: 좁은 화면이면 세로 스택 */
@media (max-width:640px) {
  .visual-header { flex-direction:column; align-items:flex-start; gap:8px; }
  .metrics-row { flex-direction:column; }
  .big-score { font-size:32px; }
}
            
.ship-card img { max-height: 450px; object-fit: cover; }

/* --- Subheader Pill --- */
.sh-pill{
  display:flex; align-items:center; gap:10px;
  padding:14px 16px; margin:4px 0 8px 0;
  background:linear-gradient(180deg,#e3f7fc,#f7fbff);
  width: 100%
  border:2px solid #e8eef8; border-radius:999px;
  box-shadow:0 8px 22px rgba(8,30,50,.06);
}
.sh-icon{
  width:28px; height:28px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:16px; color:#fff; font-weight:800;
  background:linear-gradient(90deg,#9ad1ff,#56a6ff);
}
.sh-title{ font-weight:900; font-size:22px; letter-spacing:-.2px; color:#0b3b66; }
                      
</style>
""", unsafe_allow_html=True)


#======== 사이드바 ========
# ======== Sidebar (robust links) ========
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
          for path in candidates:
              if os.path.exists(path):
                  if path.endswith(".py"):
                      st.sidebar.page_link(path, label=label)
                  elif path.endswith(".html"):
                      try:
                          with open(path, "rb") as f:
                              b64 = base64.b64encode(f.read()).decode()
                          data_url = f"data:text/html;base64,{b64}"
                          st.sidebar.markdown(
                              f"""
                              <a href="{data_url}" target="_blank"
                                style="display:block;margin:4px 0;padding:10px 12px;
                                        border-radius:8px;text-decoration:none;
                                        color:#fff;background:rgba(255,255,255,0.08);
                                        border:1px solid rgba(255,255,255,0.15);">
                                {label}
                              </a>
                              """,
                              unsafe_allow_html=True,
                          )
                      except Exception as e:
                          st.sidebar.caption(f"{label} 로드 오류: {e}")
                  return True
          st.sidebar.caption(f"'{label}' 파일을 찾지 못했습니다.")
          return False

    st.sidebar.markdown('<div class="sb-title">Eco-Friendship Dashboard</div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sb-link">', unsafe_allow_html=True)

    # 🏠 엔트리포인트(홈)
    page_link_if_exists(["Home.py"], "🏠 홈")

    # 🧭 메인 컨트롤
    page_link_if_exists([
        "pages/1_1. 메인_컨트롤.py",
        "pages/1_1.메인_컨트롤.py",
    ], "🧭 메인 컨트롤")

    # 🛰️ 위치 모니터링 LiDAR
    page_link_if_exists([
        "pages/1_2. 위치_모니터링_LiDAR.py",
        "pages/1_2.위치_모니터링_LiDAR.py",
    ], "🛰️ 위치 모니터링 LiDAR")
    
    # ⚡ 에너지 모니터링
    page_link_if_exists([
        "pages/2_2. 에너지_모니터링.py",
        "pages/2_2.에너지_모니터링.py",
    ], "⚡ 에너지 모니터링")

    # 🚢 autopilot
    page_link_if_exists([
        "pages/autopilot.py",
        # "static/autopilot.html",
    ], "🚢 autopilot")

    # 🌿 waypoint_generator
    page_link_if_exists([
        "pages/waypoint_generator.py",
        # "static/waypoint_generator.html",
    ], "🌿 waypoint_generator")


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


# --- HERO SECTION (상단 강조영역) ---
st.markdown(f"""
<div class="hero" style="padding:22px; border-radius:12px; margin-bottom:18px;">
  <div class="left">
    <div class="h-title">🚢 Eco-friendShip — 통합 관제 대시보드</div>
    <div class="h-sub">H2호의 안전 운항을 위한 실시간 모니터링 · 예측 · 제어가 가능한 대시보드입니다.</div>
  </div>

  <!-- 오른쪽: 마지막 갱신 대신 팀 정보 노출 -->
  <div style="min-width:260px; text-align:right;" class="hero-meta">
    <div class="team-name">Team: Eco-friendShip </div>
    <div class="team-members">팀원: 정민교 · 전영준 · 박재림</div>
    <div class="team-mentor" style="margin-top:6px; color:#6b7280;">신승훈 멘토님</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")  # spacing

# --- NEW LAYOUT: left (narrow menu) / center (ship image) / right (prediction) ---
menu_col, center_col, pred_col = st.columns([1.0, 1.1, 1.0])

# ---------- LEFT: 주요 기능 (좁게) ----------
with menu_col:
    # --- 항해 상태 요약 카드 (메뉴 위) ---
    # 위치: with menu_col: 블록 맨 위에 붙여넣어 주세요.

    sailing_status = st.session_state.get('sailing_status', "안전 항해")
    speed_kn = st.session_state.get('speed_kn', 15.2)
    heading_deg = st.session_state.get('heading_deg', 95)

    st.markdown("""
    <style>
    .nav-summary {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding:10px;
    border-radius:10px;
    background: linear-gradient(180deg,#c6fc9f,#ecfce6);
    border:1px solid #e7f0fb;
    box-shadow: 0 6px 16px rgba(10,30,60,0.03);
    margin-bottom:12px;
    width:100%;
    box-sizing:border-box;
    }

    /* 상태 박스: 너비 축소(메뉴 폭 기준으로 적절하게 보이도록) */
    .nav-status {
    display:flex;
    align-items:center;
    gap:10px;
    padding:10px 12px;
    border-radius:10px;
    width:48%;             /* <-- 상태 박스 너비 (조정 가능) */
    min-width:140px;
    background: linear-gradient(180deg,##dee3fa,#e9f8ee);
    color:#0b6b2d;

    }
    .nav-status .icon {
    font-size:18px;
    background: rgba(11,107,45,0.12);
    border-radius:8px;
    padding:6px;
    display:flex;
    align-items:center;
    justify-content:center;
    }
    .status-text { display:flex; flex-direction:column; line-height:1; }
    .status-label { font-size:12px; color:#25606a; opacity:0.95; }
    .status-value { font-size:19px; font-weight:700; margin-top:2px; color:#132904; }

    /* 중앙: 속도 카드 (작은 카드 스타일) */
    .nav-center {
    width:22%;     
    min-width:90px;
    display:flex;
    flex-direction:column;
    align-items:flex-start;
    gap:4px;
    box-sizing:border-box;
    }
    .center-box {
    border:1px solid #eef4f8;
    padding:8px 10px;
    border-radius:8px;
    width:100%;
    text-align:left;
    background: linear-gradient(180deg, #ecfceb, #f7fff4);
    }
    .center-label { font-size:12px; color:#6b7280f; }
    .center-value { font-size:22px; font-weight:900; color:#12324b; }

    @media (max-width: 720px) {
    .nav-summary { flex-direction:column; align-items:stretch; gap:8px; }
    .nav-status, .nav-center, .nav-heading { width:100%; }
    .nav-status { justify-content:flex-start; }
    }
    </style>
    """, unsafe_allow_html=True)

    # 상태 아이콘 선택
    status_icon = "✅" if "안전" in sailing_status else ("⚠️" if "주의" in sailing_status else "🚨")

    st.markdown(f"""
    <div class="nav-summary" role="region" aria-label="항해 상태 요약">
    <div class="nav-status" aria-live="polite">
        <div class="icon">{status_icon}</div>
        <div class="status-text">
        <div class="status-label">항해 상태</div>
        <div class="status-value">{sailing_status}</div>
        </div>
    </div>

    <div class="nav-center">
        <div class="center-box">
        <div class="center-label">현재 속도</div>
        <div class="center-value">{speed_kn:.1f} <span style="font-size:12px; font-weight:700; color:#566;">kn</span></div>
        </div>
    </div>

    <div class="nav-center">
        <div class="center-box">
        <div class="center-label">침로</div>
        <div class="center-value">{heading_deg}°</div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
          <div class="sh-pill" role="heading" aria-level="2">
        <div class="sh-icon">📊</div>        
      <div class="sh-title">주요 기능 바로 가기</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="menu-compact">', unsafe_allow_html=True)

    st.markdown(f"""
    <a class="menu-link" href="1._메인_컨트롤" target="_self">
        <div class="menu-item">
        <div class="menu-left">
            <div class="menu-icon">🕹️</div>
            <div>
            <div class="menu-title">메인 컨트롤</div>
            <div class="menu-sub">실시간 원격 제어 · 운항 모드 변경</div>
            </div>
        </div>
        <div><span class="badge good">양호</span></div>
        </div>
    </a>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <a class="menu-link" href="2._에너지_모니터링" target="_self" style="text-decoration:none; color:inherit; display:block;">
    <div class="menu-item" role="button" aria-label="에너지 모니터링으로 이동">
        <div class="menu-left">
        <div class="menu-icon">⚡</div>
        <div>
            <div class="menu-title">에너지 모니터링</div>
            <div class="menu-sub">배터리 · 태양광 · 연료전지 상태 확인</div>
        </div>
        </div>
        <div><span class="badge warn">원활</span></div>
    </div>
    </a>
    """, unsafe_allow_html=True)


    st.markdown(f"""
    <a class="menu-link" href="4._친환경_지표" target="_self" style="text-decoration:none; color:inherit; display:block;">
    <div class="menu-item" role="button" aria-label="친환경 지표로 이동">
        <div class="menu-left">
        <div class="menu-icon">🌱</div>
        <div>
            <div class="menu-title">친환경 지표</div>
            <div class="menu-sub">탄소 감축량 · 효율 지수</div>
        </div>
        </div>
        <div><span class="badge bad">A등급</span></div>
    </div>
    </a>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    # keep compact: remove the earlier prediction summary from left (we move it to right)

# ---------- CENTER: 선박 이미지 (크게, 중앙) ----------
with center_col:
    st.markdown('<div class="ship-card">', unsafe_allow_html=True)
    def get_image_base64(path):
      with open(path, "rb") as img_file:
          return base64.b64encode(img_file.read()).decode()

  # 1. 표시할 선박 이미지 4개의 파일 경로를 여기에 입력하세요.
  # (전, 후, 좌, 우 순서)
    image_paths = [
      "your_ship_image.png", 
      "image1.png", 
      "image2.png", 
      "image3.png"
  ]
    image_sources = []
  # 모든 로컬 이미지가 존재하는지 확인
    if all(os.path.exists(p) for p in image_paths):
      # 존재하면 Base64로 인코딩하여 리스트에 추가
      for path in image_paths:
          ext = os.path.splitext(path)[1][1:] # 확장자 추출 (e.g., 'png')
          image_sources.append(f"data:image/{ext};base64,{get_image_base64(path)}")

  # 3. HTML, CSS, JavaScript를 사용하여 슬라이드 쇼 컴포넌트 생성
    slideshow_html = f"""
    <style>
      /* 슬라이드 쇼 컨테이너 */
      .slideshow-container {{
          max-width: 1000px;
          position: relative;
          margin: auto;
          border-radius: 8px;
          overflow: hidden; /* 둥근 모서리 적용을 위해 */
      }}
      /* 각 슬라이드(이미지) */
      .mySlides {{
          display: none; /* 기본적으로 모든 슬라이드 숨김 */
      }}
      .mySlides img {{
          vertical-align: middle;
          width: 100%;
      }}
      /* 페이드 인/아웃 애니메이션 */
      .fade {{
          animation-name: fade;
          animation-duration: 1.5s;
      }}
      @keyframes fade {{
          from {{opacity: .4}}
          to {{opacity: 1}}
      }}
    </style>

    <div class="slideshow-container">
      <div class="mySlides fade">
          <img src="{image_sources[0]}">
      </div>
      <div class="mySlides fade">
          <img src="{image_sources[1]}">
      </div>
      <div class="mySlides fade">
          <img src="{image_sources[2]}">
      </div>
      <div class="mySlides fade">
          <img src="{image_sources[3]}">
      </div>
    </div>

    <script>
      let slideIndex = 0;
      showSlides(); // 스크립트 시작 시 함수 호출

      function showSlides() {{
          let i;
          let slides = document.getElementsByClassName("mySlides");
          // 모든 슬라이드를 숨김
          for (i = 0; i < slides.length; i++) {{
              slides[i].style.display = "none";
          }}
          slideIndex++;
          // 인덱스가 슬라이드 개수를 넘어가면 처음으로 리셋
          if (slideIndex > slides.length) {{slideIndex = 1}}
          // 현재 인덱스의 슬라이드만 표시
          slides[slideIndex-1].style.display = "block";
          // 2초 후에 다시 showSlides 함수 호출 (재귀)
          setTimeout(showSlides, 3000); 
      }}
    </script>
  """
    
    html(slideshow_html, height=450)
    st.markdown('</div>', unsafe_allow_html=True)


# ---------- RIGHT: 오늘의 운항 예측 (시각적 카드) ----------

from textwrap import dedent  # 상단 import에 추가돼 있어야 함

with pred_col:
    
# 컴팩트 모드(여백/폰트 축소)
  w = st.session_state['weather'] 
  AUTO_INTERVAL = 30 
  if time.time() - st.session_state.get('last_refresh', 0) > AUTO_INTERVAL:
       w['irradiance'] = max(0.0, w['irradiance'] + random.uniform(-80, 80))
       w['wind'] = max(0.0, w['wind'] + random.uniform(-1.2, 1.2)) 
       w['wave'] = max(0.0, w['wave'] + random.uniform(-0.3, 0.3)) 
       w['ts'] = time.time() 
       st.session_state['weather'] = w 
       st.session_state['last_refresh'] = time.time() 
       
       # 점수 계산 (원래 로직 유지) 
       score = (min(w['wind'] / 12.0, 1.0) * 50.0) + (min(w['wave'] / 3.0, 1.0) * 40.0) + ((1 - min(w['irradiance'] / 1000.0, 1.0)) * 10.0) 
       score = max(0.0, min(100.0, score)) 
       score_int = int(score) 
      
  if score < 30: 
            risk_label = "양호"
            risk_class = "good"
            pill_class = "risk-good" 
  elif score < 60: 
            risk_label = "주의"
            risk_class = "warn"
            pill_class = "risk-warn" 
  else: 
            risk_label = "위험"
            risk_class = "bad"
            pill_class = "risk-bad"

        # 추천 조치 (간단 문구) 
  recommendation = "평상 운항" if risk_label == "양호" else ("감속·주의 항해" if risk_label == "주의" else "항로 변경 또는 정박 검토")    
  st.markdown("""
    <style>
      .visual-pred{ padding:12px; }
      .visual-header{ margin-bottom:6px; }
      .big-score{ font-size:32px; }   /* 38 -> 32 */
      .metric{ padding:8px 10px; }
      .metric .val{ font-size:15px; }
      .metric-sun { background-color: #fce2b8; border-color: #fcd79a; }
      .metric-wind { background-color: #d0ebff; border-color: #a6d4ff; }
      .metric-wave { background-color: #d0f0ed; border-color: #a6e1d9; }
    </style>
    """, unsafe_allow_html=True)

  st.markdown(dedent(f"""
    <div class="sh-pill" role="heading" aria-level="2">
      <div class="sh-icon">📈</div>
      <div class="sh-title">오늘의 운항 예측</div>
      <span class="sh-badge {'good' if risk_label=='양호' else ('warn' if risk_label=='주의' else 'bad') }">{risk_label}</span>
    </div>  
      <div class="visual-pred">
        <div class="visual-header">
          <div>
            <div class="big-score">{score_int}/100</div>
            <div style="color:#6b7280; font-size:13px; margin-top:6px;">종합 운항 위험도</div>
          </div>
          <div style="text-align:right;">
            <div class="risk-pill {pill_class}">{risk_label}</div>
            <div class="recommend">추천 조치: {recommendation}</div>
            <div style="font-size:13px; color:#9aa; margin-top:6px;">
              마지막 갱신: {datetime.fromtimestamp(w['ts']).strftime('%H:%M:%S')}
            </div>
          </div>
        </div>
        <div class="metrics-row metrics-stacked">
          <div class="metric metric-sun" aria-label="일사량">
            <div class="icon icon-sun">☀️</div>
            <div><div class="meta">일사량</div><div class="val">{int(w['irradiance'])} W/m²</div></div>
          </div>
          <div class="metric metric-wind" aria-label="풍속">
            <div class="icon icon-wind">🌬️</div>
            <div><div class="meta">풍속</div><div class="val">{w['wind']:.1f} m/s</div></div>
          </div>
          <div class="metric metric-wave" aria-label="파고">
            <div class="icon icon-wave">🌊</div>
            <div><div class="meta">파고</div><div class="val">{w['wave']:.2f} m</div></div>
          </div>
        </div>
      </div>
    """), unsafe_allow_html=True)



st.markdown("---")
