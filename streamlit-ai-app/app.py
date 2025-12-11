import streamlit as st


st.set_page_config(page_title="AI 텍스트 & 이미지 도구", page_icon="📝")
st.title("AI 텍스트 & 이미지 도구")
st.write(
    "사이드바의 페이지 메뉴에서 텍스트 도구 또는 이미지 도구를 선택하세요. "
    "홈에서 Google Gemini API Key를 입력하면 텍스트 도구의 모든 기능을 사용할 수 있습니다."
)

st.sidebar.subheader("Google Gemini 설정")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password", key="sidebar_gemini_key")
if gemini_key:
    st.session_state["gemini_api_key"] = gemini_key
    st.sidebar.success("Gemini API Key가 저장되었습니다.")
else:
    st.sidebar.info("Gemini API Key를 입력하세요. 입력 후 다른 페이지에서 그대로 사용됩니다.")

st.info("왼쪽 사이드바에서 페이지를 선택한 뒤 원하는 도구를 사용하세요.")
