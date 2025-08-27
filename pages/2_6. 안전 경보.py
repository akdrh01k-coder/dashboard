# safety_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="안전/경보 대시보드",
    page_icon="⚠️",
    layout="wide",
)

st.title("⚠️ 안전/경보 (Safety/Alarm)")
st.markdown("---")

# --- 더미 데이터 생성 ---
def create_alarm_data():
    """시뮬레이션을 위한 경보 로그 데이터를 생성합니다."""
    now = datetime.now()
    alarm_data = {
        '시간': [(now - timedelta(minutes=np.random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(10)],
        '경보 종류': np.random.choice(['수소 압력 낮음', '연료전지 온도 높음', 'ESS 배터리 과열', '빌지 수위 높음', 'GPS 신호 없음'], 10),
        '심각도': np.random.choice(['주의', '경고', '위험'], 10, p=[0.5, 0.3, 0.2]),
        '처리 상태': np.random.choice(['확인', '미확인'], 10, p=[0.7, 0.3])
    }
    return pd.DataFrame(alarm_data)

# --- 실시간 시스템 상태 ---
st.subheader("실시간 시스템 상태")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<h5 style='text-align: center;'>수소 연료 전지</h5>", unsafe_allow_html=True)
    st.success("● 정상", icon="✅")
    st.info(f"온도: {65 + np.random.rand():.1f}°C")
    st.info(f"압력: {700 + np.random.rand():.1f} bar")

with col2:
    st.markdown("<h5 style='text-align: center;'>ESS/배터리</h5>", unsafe_allow_html=True)
    st.warning("● 주의", icon="⚠️")
    st.info(f"충전율 (SoC): {85 + np.random.rand():.1f}%")
    st.warning(f"온도: {42 + np.random.rand():.1f}°C (권장 범위 초과)")

with col3:
    st.markdown("<h5 style='text-align: center;'>화재 감지기</h5>", unsafe_allow_html=True)
    st.success("● 정상", icon="✅")
    st.info("기관실: 정상")
    st.info("조타실: 정상")

with col4:
    st.markdown("<h5 style='text-align: center;'>침수(빌지) 센서</h5>", unsafe_allow_html=True)
    st.success("● 정상", icon="✅")
    st.info("선수: 5%")
    st.info("선미: 8%")

# --- 경보 발생 로그 ---
st.markdown("---")
st.subheader("경보 발생 로그")
alarm_df = create_alarm_data()

# 심각도에 따라 DataFrame 스타일 적용
def highlight_severity(row):
    color = ''
    if row['심각도'] == '위험':
        color = 'background-color: #ff4b4b; color: white'
    elif row['심각도'] == '경고':
        color = 'background-color: #ffc44b;'
    return [color] * len(row)

st.dataframe(alarm_df.style.apply(highlight_severity, axis=1), use_container_width=True)
if st.button("전체 경보 확인 처리"):
    st.toast("모든 경보를 '확인' 상태로 변경했습니다.")