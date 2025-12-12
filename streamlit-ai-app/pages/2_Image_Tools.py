import streamlit as st


st.title("이미지 도구")
st.write("이미지 관련 도구가 여기에 추가될 예정입니다.")

if not st.session_state.get("logged_in", False):
    st.error("비밀번호를 먼저 입력해야 합니다. 홈에서 로그인 후 다시 시도하세요.")
    st.stop()
