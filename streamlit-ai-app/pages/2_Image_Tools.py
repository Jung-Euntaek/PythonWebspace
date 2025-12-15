import streamlit as st


st.title("이미지 도구")
st.write("이미지 관련 도구가 여기에 추가될 예정입니다.")

if not st.session_state.get("logged_in", False):
    st.error("비밀번호를 먼저 입력해야 합니다. 홈에서 로그인 후 다시 시도하세요.")
    st.stop()

# 기본 첫 항목(app)을 숨기고 HOME 링크 추가
st.sidebar.page_link("app.py", label="HOME", icon="🏠")
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] ul li:nth-of-type(1) {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
