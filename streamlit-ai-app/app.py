import streamlit as st
import openai


st.set_page_config(page_title="AI 텍스트 요약기", page_icon="📝")
st.title("AI 텍스트 요약기")
st.write("입력한 글을 간단히 요약하거나 번역합니다.")

with st.expander("도움말 보기"):
    st.markdown(
        """
        1. 아래 텍스트 상자에 긴 글을 붙여 넣으세요.  
        2. **요약하기** 버튼을 누르면 AI가 핵심만 정리해 줍니다.  
        3. 결과는 아래에 표시됩니다.  
        """
    )

api_key = st.sidebar.text_input("OpenAI API Key", type="password")
text = st.text_area("요약·번역할 텍스트를 입력하세요.", height=220)

if not api_key:
    st.info("API Key를 입력하세요")
else:
    client = openai.OpenAI(api_key=api_key)

    action = None
    if st.button("요약하기"):
        action = "summary"
    if st.button("영어 → 한국어 번역"):
        action = "translate"

    if action:
        if not text.strip():
            st.warning("텍스트를 입력하세요.")
        else:
            with st.spinner("처리 중..."):
                try:
                    if action == "summary":
                        messages = [
                            {
                                "role": "system",
                                "content": "Summarize the user's text in Korean as succinctly as possible.",
                            },
                            {"role": "user", "content": text},
                        ]
                        title = "요약 결과"
                    else:
                        messages = [
                            {
                                "role": "system",
                                "content": "Translate the user's English text into Korean. Return only the translated Korean text.",
                            },
                            {"role": "user", "content": text},
                        ]
                        title = "번역 결과"

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=256,
                    )
                    result = response.choices[0].message.content.strip()

                    if action == "summary":
                        st.success("요약이 완료되었습니다.")
                    else:
                        st.success(title)
                    st.write(result)
                except Exception as exc:
                    st.error(f"요청 처리 중 오류가 발생했습니다: {exc}")
