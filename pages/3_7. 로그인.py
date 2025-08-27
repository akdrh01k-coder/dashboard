# login_app.py

import streamlit as st

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="Streamlit 로그인",
    page_icon="🔐",
    layout="centered"
)

# --- 로그인 상태를 관리하기 위한 세션 상태 초기화 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 로그인 페이지 함수 ---
def show_login_page():
    st.title("🔐 로그인")

    # 로그인 폼 생성
    with st.form("login_form"):
        username = st.text_input("사용자 이름", placeholder="admin")
        password = st.text_input("비밀번호", type="password", placeholder="1234")
        submitted = st.form_submit_button("로그인")

        # 로그인 버튼을 눌렀을 때
        if submitted:
            # 실제 앱에서는 데이터베이스나 st.secrets를 사용해 안전하게 인증해야 합니다.
            if username == "admin" and password == "1234":
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()  # 로그인 성공 시 페이지를 새로고침하여 메인 페이지로 이동
            else:
                st.error("사용자 이름 또는 비밀번호가 올바르지 않습니다.")

# --- 로그인 성공 후 보여줄 메인 페이지 함수 ---
def show_main_page():
    st.title("🎉 환영합니다!")
    st.write(f"**{st.session_state['username']}**님, 성공적으로 로그인했습니다.")
    st.write("이제 여기에 원하는 애플리케이션 내용을 추가할 수 있습니다.")

    # 로그아웃 버튼
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state.pop('username', None) # 사용자 이름 정보 삭제
        st.rerun() # 로그아웃 시 페이지를 새로고침하여 로그인 페이지로 이동

# --- 메인 로직 ---
# 로그인 상태에 따라 보여줄 페이지 결정
if st.session_state['logged_in']:
    show_main_page()
else:
    show_login_page()