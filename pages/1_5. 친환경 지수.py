# pages/1_친환경_지수.py

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 세션 상태 초기화 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- 사이드바 로그인/로그아웃 기능 (기능은 그대로 유지) ---
if not st.session_state['logged_in']:
    st.sidebar.subheader("관리자 로그인")
    username = st.sidebar.text_input("사용자 이름", key="eco_user")
    password = st.sidebar.text_input("비밀번호", type="password", key="eco_pass")
    if st.sidebar.button("로그인", key="eco_login"):
        if username == "admin" and password == "1234":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.sidebar.error("정보가 일치하지 않습니다.")

if st.session_state['logged_in']:
    st.sidebar.success("admin 계정으로 로그인됨")
    if st.sidebar.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- '친환경 지수' 페이지 메인 컨텐츠 ---
st.title("🌍 친환경 지수 (Eco-Friendly Index)")
st.markdown("---")

# 👇 로그인 확인 조건문(if/else)을 제거하여 항상 컨텐츠가 보이도록 수정
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("탄소 배출 저감량 (tCO₂)")
    saved_co2 = 125.7 + np.random.rand()
    st.metric(label="누적 저감량", value=f"{saved_co2:.2f} tCO₂", delta="지난 항차 대비 +2.5 tCO₂")
    st.progress(int(saved_co2 % 100))
    st.caption("동일 체급 디젤 선박 대비 누적 CO₂ 절감량입니다.")

with col2:
    st.subheader("에너지 사용 비율 (%)")
    labels = ['수소 연료 전지', '태양광']
    values = [75 + np.random.randint(-5, 5), 25 + np.random.randint(-5, 5)]
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=['#00BFFF', '#FFD700'])])
    fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

with col3:
    st.subheader("선박 탄소 집약도 지수 (CII)")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=2.85 + (np.random.rand() * 0.1),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "현재 CII 등급", 'font': {'size': 20}},
        delta={'reference': 3.0, 'increasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 12], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#2E8B57"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 4], 'color': 'green'},
                {'range': [4, 7], 'color': 'yellow'},
                {'range': [7, 12], 'color': 'red'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 11.5}}))
    fig_gauge.update_layout(margin=dict(t=30, b=0, l=30, r=30))
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")
st.subheader("오염물질 배출량 실시간 현황")
col_nox, col_sox, col_pm = st.columns(3)
col_nox.metric("질소산화물 (NOx)", "0 ppm")
col_sox.metric("황산화물 (SOx)", "0 ppm")
col_pm.metric("미세먼지 (PM)", "0 µg/m³")