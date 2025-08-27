# dashboard.py

import streamlit as st

# 페이지 기본 설정 (가장 먼저 나와야 합니다)
# set_page_config는 메인 스크립트나 각 페이지에 한 번만 사용할 수 있습니다.
# 보통 메인 스크립트에 설정합니다.
st.set_page_config(
    page_title="Eco-friendShip 대시보드",
    page_icon="🚢",
    layout="wide",
)

# --- 세션 상태 초기화 ---
# 로그인 상태를 저장하기 위해 session_state를 초기화합니다.
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 메인 페이지 컨텐츠 ---
st.title("🚢 Eco-friendShip 대시보드")
st.markdown("---")

st.header("✨ 시작하기")
st.info("좌측 사이드바에서 원하는 메뉴를 선택하여 각 대시보드를 확인하세요.")

st.subheader("메뉴 안내")
st.markdown("""
- **친환경 지수**: 선박의 탄소 배출 저감량, 에너지 효율 등 친환경 성능을 모니터링합니다.
- **안전/경보**: 주요 시스템 상태를 확인하고 경보 발생 이력을 조회합니다.
- **로그인**: **로그인 후** 선박의 주요 기능을 원격으로 제어합니다. (관리자용)
""")

# 로그인 폼을 메인 페이지에 둘 수도 있습니다.
if not st.session_state['logged_in']:
    st.sidebar.subheader("관리자 로그인")
    username = st.sidebar.text_input("사용자 이름", key="main_user")
    password = st.sidebar.text_input("비밀번호", type="password", key="main_pass")
    if st.sidebar.button("로그인", key="main_login"):
        if username == "admin" and password == "1234":
            st.session_state['logged_in'] = True
            st.rerun() # 로그인 성공 시 새로고침
        else:
            st.sidebar.error("정보가 일치하지 않습니다.")

# 로그아웃 버튼
if st.session_state['logged_in']:
    st.sidebar.success("admin 계정으로 로그인됨")
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun() # 로그아웃 시 새로고침