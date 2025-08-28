# login_app.py
import streamlit as st
import random
import string
from datetime import datetime, timedelta

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="Streamlit 로그인", page_icon="🔐", layout="centered")

# -----------------------------
# 세션 스토리지 (데모용)
# -----------------------------
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "1234", "email": "admin@example.com", "is_active": True}
    }

if "pw_reset" not in st.session_state:
    st.session_state.pw_reset = {}

st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", None)
st.session_state.setdefault("view", "login")

# 실시간 검증 플래그 기본값
st.session_state.setdefault("forgot_mismatch", False)
st.session_state.setdefault("admin_mismatch", False)

ADMIN_KEY = "ADMIN-KEY-CHANGE-ME"

# -----------------------------
# 유틸
# -----------------------------
def gen_code(n=6):
    return "".join(random.choices(string.digits, k=n))

def send_reset_code(username: str):
    code = gen_code()
    st.session_state.pw_reset[username] = {
        "code": code,
        "expire_at": datetime.utcnow() + timedelta(minutes=10),
    }
    return code

def verify_reset_code(username: str, code: str) -> bool:
    item = st.session_state.pw_reset.get(username)
    if not item:
        return False
    if datetime.utcnow() > item["expire_at"]:
        return False
    return item["code"] == code

def user_exists(username: str) -> bool:
    return username in st.session_state.users

def check_password(username: str, password: str) -> bool:
    user = st.session_state.users.get(username)
    return bool(user and user["is_active"] and user["password"] == password)

def create_or_activate_user(username: str, password: str, email: str):
    st.session_state.users[username] = {
        "password": password,
        "email": email,
        "is_active": True,
    }

def nav_to(view: str):
    st.session_state["view"] = view
    st.rerun()

# -----------------------------
# 콜백: 비밀번호 일치 여부 실시간 체크
# -----------------------------
def check_match(scope: str):
    """scope: 'forgot' 또는 'admin'"""
    if scope == "forgot":
        pw = st.session_state.get("pw_new", "")
        pw2 = st.session_state.get("pw_new2", "")
        st.session_state["forgot_mismatch"] = bool(pw and pw2 and pw != pw2)
    elif scope == "admin":
        pw = st.session_state.get("ad_pw", "")
        pw2 = st.session_state.get("ad_pw2", "")
        st.session_state["admin_mismatch"] = bool(pw and pw2 and pw != pw2)

# -----------------------------
# 로그인 화면
# -----------------------------
def show_login_page():
    st.title("🔐 로그인")

    with st.form("login_form"):
        username = st.text_input("사용자 이름", placeholder="admin")
        password = st.text_input("비밀번호", type="password", placeholder="••••")

        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            submitted = st.form_submit_button("로그인", use_container_width=True)

        if submitted:
            if check_password(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("로그인에 성공했습니다.")
                st.rerun()
            else:
                st.error("사용자 이름 또는 비밀번호가 올바르지 않습니다.")

    lcol, rcol = st.columns(2)
    with lcol:
        if st.button("🔑 비밀번호 찾기", type="secondary", use_container_width=True):
            nav_to("forgot")
    with rcol:
        if st.button("🛡️ 관리자 등록", type="secondary", use_container_width=True):
            nav_to("admin")

# -----------------------------
# 비밀번호 찾기 화면
# -----------------------------
def show_forgot_page():
    st.markdown("### 🔑 비밀번호 찾기")
    if st.button("← 로그인으로 돌아가기", type="secondary"):
        nav_to("login")

    st.write("아이디를 확인하여 **재설정 코드**를 발급받고, 아래에서 새 비밀번호로 변경하십시오.")

    # 코드 발급
    u = st.text_input("사용자 이름", placeholder="내 아이디", key="pw_user")
    email_hint = st.text_input("등록 이메일(선택)", placeholder="name@example.com", key="pw_email")
    if st.button("재설정 코드 보내기"):
        if not user_exists(u):
            st.error("해당 사용자가 없거나 비활성화 상태입니다.")
        else:
            code = send_reset_code(u)
            st.info("재설정 코드가 발급되었습니다. (데모이므로 화면에 표시합니다.)")
            with st.expander("📩 데모 코드 보기"):
                st.code(code, language="text")

    st.divider()

    # 실시간 비밀번호 확인
    u2 = st.text_input("사용자 이름(다시 입력)", placeholder="내 아이디", key="pw_user2")
    code_in = st.text_input("재설정 코드", placeholder="6자리 숫자", key="pw_code")
    new_pw = st.text_input("새 비밀번호", type="password", key="pw_new")
    new_pw2 = st.text_input("새 비밀번호 확인", type="password", key="pw_new2")

    if new_pw and new_pw2:
        if new_pw != new_pw2:
            st.markdown("<span style='color:red;'>비밀번호가 일치하지 않습니다.</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:green;'>비밀번호가 일치합니다.</span>", unsafe_allow_html=True)

    if st.button("비밀번호 재설정"):
        if not user_exists(u2):
            st.error("해당 사용자가 존재하지 않습니다.")
        elif new_pw != new_pw2:
            st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        elif not verify_reset_code(u2, code_in.strip()):
            st.error("코드가 올바르지 않거나 만료되었습니다. 다시 요청하십시오.")
        else:
            st.session_state.users[u2]["password"] = new_pw
            st.session_state.pw_reset.pop(u2, None)
            st.success("비밀번호가 재설정되었습니다. 로그인 페이지로 돌아가 로그인하십시오.")


# -----------------------------
# 관리자 등록 화면
# -----------------------------
def show_admin_page():
    st.markdown("### 🛡️ 관리자 등록(초대코드)")
    if st.button("← 로그인으로 돌아가기", type="secondary"):
        nav_to("login")

    st.caption("신규 계정은 **관리자 초대코드**로만 생성/활성화됩니다.")

    invite = st.text_input("관리자 초대코드", placeholder="ADMIN-KEY-…", key="ad_invite")
    new_user = st.text_input("새 사용자 이름", placeholder="영문/숫자 권장", key="ad_user")
    new_email = st.text_input("이메일(선택)", placeholder="name@example.com", key="ad_email")
    new_pw = st.text_input("비밀번호", type="password", key="ad_pw")
    new_pw2 = st.text_input("비밀번호 확인", type="password", key="ad_pw2")

    if new_pw and new_pw2:
        if new_pw != new_pw2:
            st.markdown("<span style='color:red;'>비밀번호가 일치하지 않습니다.</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:green;'>비밀번호가 일치합니다.</span>", unsafe_allow_html=True)

    if st.button("계정 만들기"):
        if invite != ADMIN_KEY:
            st.error("초대코드가 올바르지 않습니다.")
        elif not new_user or not new_pw:
            st.error("사용자 이름과 비밀번호를 입력하십시오.")
        elif new_pw != new_pw2:
            st.error("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        else:
            create_or_activate_user(new_user, new_pw, new_email)
            st.success("계정이 활성화되었습니다. 로그인 페이지에서 방금 만든 계정으로 로그인하십시오.")


# -----------------------------
# 로그인 이후 메인
# -----------------------------
def show_main_page():
    st.markdown(
        "<h1 style='text-align:center;'>🎉 환영합니다!</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<h3 style='text-align:center;'>{st.session_state['username']}님, 성공적으로 로그인하였습니다.</h3>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🔓 로그아웃", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["view"] = "login"
            st.rerun()

# -----------------------------
# 라우팅
# -----------------------------
if st.session_state["logged_in"]:
    show_main_page()
else:
    if st.session_state["view"] == "login":
        show_login_page()
    elif st.session_state["view"] == "forgot":
        show_forgot_page()
    elif st.session_state["view"] == "admin":
        show_admin_page()
    else:
        nav_to("login")
