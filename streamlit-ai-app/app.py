import openai
import pandas as pd
import streamlit as st


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
has_api_key = bool(api_key)
if not has_api_key:
    st.sidebar.warning("API Key를 입력하세요.")

client = openai.OpenAI(api_key=api_key) if has_api_key else None

uploaded_image = st.file_uploader(
    "이미지를 업로드하면 화면에 표시됩니다.",
    type=["png", "jpg", "jpeg", "webp", "bmp", "svg"],
)
if uploaded_image:
    st.image(uploaded_image, caption=f"업로드한 이미지: {uploaded_image.name}")

tab_summary, tab_translate, tab_feedback, tab_length = st.tabs(
    ["텍스트 요약", "영어 → 한국어 번역", "글쓰기 피드백", "텍스트 길이 시각화"]
)


def require_api_key():
    st.warning("API Key를 입력한 뒤 다시 시도하세요.")
    return False


with tab_summary:
    summary_text = st.text_area(
        "", height=220, key="summary_text", placeholder="텍스트를 입력하세요."
    )
    if st.button("실행", key="summary_button"):
        if not summary_text.strip():
            st.warning("텍스트를 입력하세요.")
        elif not has_api_key:
            require_api_key()
        else:
            with st.spinner("요약 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "Summarize the user's text in Korean as succinctly as possible.",
                            },
                            {"role": "user", "content": summary_text},
                        ],
                        temperature=0.3,
                        max_tokens=256,
                    )
                    summary = response.choices[0].message.content.strip()
                    st.success("요약이 완료되었습니다.")
                    st.write(summary)
                except Exception as exc:
                    st.error(f"요약 요청 처리 중 오류가 발생했습니다: {exc}")

with tab_translate:
    translate_text = st.text_area(
        "", height=220, key="translate_text", placeholder="텍스트를 입력하세요."
    )
    if st.button("실행", key="translate_button"):
        if not translate_text.strip():
            st.warning("텍스트를 입력하세요.")
        elif not has_api_key:
            require_api_key()
        else:
            with st.spinner("번역 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "Translate the user's English text into Korean. Return only the translated Korean text.",
                            },
                            {"role": "user", "content": translate_text},
                        ],
                        temperature=0.3,
                        max_tokens=256,
                    )
                    translated = response.choices[0].message.content.strip()
                    st.success("번역 결과")
                    st.write(translated)
                except Exception as exc:
                    st.error(f"번역 요청 처리 중 오류가 발생했습니다: {exc}")

with tab_feedback:
    feedback_text = st.text_area(
        "", height=220, key="feedback_text", placeholder="텍스트를 입력하세요."
    )
    if st.button("실행", key="feedback_button"):
        if not feedback_text.strip():
            st.warning("텍스트를 입력하세요.")
        elif not has_api_key:
            require_api_key()
        else:
            with st.spinner("피드백 작성 중..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a writing coach. Provide concise, constructive Korean feedback on clarity, "
                                    "tone, and structure. Include specific suggestions and an improved sample rewrite "
                                    "no longer than 3 sentences."
                                ),
                            },
                            {"role": "user", "content": feedback_text},
                        ],
                        temperature=0.4,
                        max_tokens=320,
                    )
                    feedback = response.choices[0].message.content.strip()
                    st.success("피드백 결과")
                    st.write(feedback)
                except Exception as exc:
                    st.error(f"피드백 요청 처리 중 오류가 발생했습니다: {exc}")

with tab_length:
    length_text = st.text_area(
        "", height=220, key="length_text", placeholder="텍스트를 입력하세요."
    )
    if st.button("실행", key="length_button"):
        if not length_text.strip():
            st.warning("텍스트를 입력하세요.")
        else:
            char_count = len(length_text)
            word_count = len(length_text.split())
            data = pd.DataFrame(
                {"항목": ["문자 수", "단어 수"], "값": [char_count, word_count]}
            ).set_index("항목")
            st.bar_chart(data)
            st.write(f"문자 수: {char_count}, 단어 수: {word_count}")
