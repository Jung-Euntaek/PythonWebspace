import streamlit as st


try:
    APP_PASSWORD = st.secrets.get("APP_PASSWORD", "changeme")
except Exception:
    APP_PASSWORD = "changeme"

st.set_page_config(page_title="AI 텍스트 & 이미지 도구", page_icon="📝")
st.title("AI 텍스트 & 이미지 도구")

# 로그인 게이트
if not st.session_state.get("logged_in", False):
    st.info("비밀번호를 입력하면 한 번 로그인으로 유지됩니다.")
    password = st.text_input("비밀번호를 입력하세요.", type="password", key="login_password")
    if st.button("로그인"):
        if password == APP_PASSWORD:
            st.session_state["logged_in"] = True
            st.success("로그인되었습니다. 왼쪽 메뉴에서 페이지를 선택하세요.")
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

st.write(
    "사이드바에서 텍스트 도구, 이미지 도구, 히스토리를 선택하세요. "
    "여기에서 Google Gemini API Key를 입력하면 텍스트 도구의 모든 기능을 사용할 수 있습니다."
)

st.sidebar.subheader("Google Gemini 설정")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password", key="sidebar_gemini_key")
if gemini_key:
    st.session_state["gemini_api_key"] = gemini_key
    st.sidebar.success("Gemini API Key가 저장되었습니다.")
else:
    st.sidebar.info("Gemini API Key를 입력하세요. 다른 페이지에서 그대로 사용됩니다.")

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

st.subheader("빠른 이동")
col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/1_Text_Tools.py", label="텍스트 도구", icon="📝")
with col2:
    st.page_link("pages/2_Image_Tools.py", label="이미지 도구", icon="🖼")
with col3:
    st.page_link("pages/3_History.py", label="히스토리", icon="📜")
