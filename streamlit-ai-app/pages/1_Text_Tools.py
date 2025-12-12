import os
from datetime import datetime

import google.generativeai as genai
import pandas as pd
import streamlit as st


st.title("텍스트 도구")
st.write("요약, 번역, 글쓰기 피드백, 텍스트 길이 시각화를 제공합니다.")

if not st.session_state.get("logged_in", False):
    st.error("비밀번호를 먼저 입력해야 합니다. 홈에서 로그인 후 다시 시도하세요.")
    st.stop()

with st.expander("도움말 보기"):
    st.markdown(
        """
        1. 아래 텍스트 상자에 긴 글을 붙여 넣으세요.  
        2. **실행** 버튼을 누르면 선택한 기능이 실행됩니다.  
        3. 결과는 아래에 표시됩니다.  
        """
    )

HISTORY_PATH = "history.csv"

api_key = st.session_state.get("gemini_api_key") or st.session_state.get("api_key", "")
has_api_key = bool(api_key)
if not has_api_key:
    st.sidebar.warning("홈에서 Gemini API Key를 입력하세요.")

AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]
selected_model = st.sidebar.selectbox("Gemini 모델 선택", AVAILABLE_MODELS, index=0)

tab_summary, tab_translate, tab_feedback, tab_length = st.tabs(
    ["텍스트 요약", "영어 → 한국어 번역", "글쓰기 피드백", "텍스트 길이 시각화"]
)


def require_api_key():
    st.warning("홈 페이지에서 Gemini API Key를 입력한 뒤 다시 시도하세요.")


def log_history(action: str, input_text: str, output_text: str, model_name: str) -> None:
    """요약/번역/피드백 결과를 CSV로 누적 저장."""
    try:
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "model": model_name,
            "input": input_text,
            "output": output_text,
        }
        df = pd.DataFrame([row])
        header_needed = not os.path.exists(HISTORY_PATH)
        df.to_csv(
            HISTORY_PATH,
            mode="a",
            header=header_needed,
            index=False,
            encoding="utf-8",
        )
    except Exception as exc:
        st.warning(f"history.csv 저장에 실패했습니다: {exc}")


def generate_with_fallback(prompt: str):
    """
    선택 모델이 404/제한 등으로 실패할 때 호환 모델로 순차 시도.
    반환: (응답 텍스트, 사용 모델명) 또는 (None, None)
    """
    if not has_api_key:
        require_api_key()
        return None, None

    errors = []
    fallback_models = []
    for name in [selected_model, "gemini-2.5-flash", "gemini-2.0-flash"]:
        if name not in fallback_models:
            fallback_models.append(name)

    for name in fallback_models:
        try:
            genai.configure(api_key=api_key)
            mdl = genai.GenerativeModel(name)
            resp = mdl.generate_content(prompt)
            st.caption(f"사용 모델: {name}")
            return resp.text, name
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            continue

    st.error("모델 호출이 모두 실패했습니다. 다른 모델을 선택하거나 google-generativeai 버전을 업데이트하세요.")
    for err in errors:
        st.error(err)
    return None, None


with tab_summary:
    summary_text = st.text_area(
        "", height=220, key="summary_text", placeholder="텍스트를 입력하세요."
    )
    if st.button("실행", key="summary_button"):
        if not summary_text.strip():
            st.warning("텍스트를 입력하세요.")
        else:
            with st.spinner("요약 중..."):
                prompt = (
                    "다음 글을 한국어로 간결하게 요약해줘. "
                    "핵심만 남기고 불필요한 예시는 제외해.\n\n"
                    f"{summary_text}"
                )
                result, model_used = generate_with_fallback(prompt)
                if result:
                    st.success("요약이 완료되었습니다.")
                    st.write(result)
                    log_history("summary", summary_text, result, model_used or "")

with tab_translate:
    translate_text = st.text_area(
        "", height=220, key="translate_text", placeholder="텍스트를 입력하세요."
    )
    if st.button("실행", key="translate_button"):
        if not translate_text.strip():
            st.warning("텍스트를 입력하세요.")
        else:
            with st.spinner("번역 중..."):
                prompt = (
                    "Translate the following English text into Korean. "
                    "Return only the translated Korean text without explanations.\n\n"
                    f"{translate_text}"
                )
                result, model_used = generate_with_fallback(prompt)
                if result:
                    st.success("번역 결과")
                    st.write(result)
                    log_history("translate", translate_text, result, model_used or "")

with tab_feedback:
    feedback_text = st.text_area(
        "", height=220, key="feedback_text", placeholder="텍스트를 입력하세요."
    )
    if st.button("실행", key="feedback_button"):
        if not feedback_text.strip():
            st.warning("텍스트를 입력하세요.")
        else:
            with st.spinner("피드백 작성 중..."):
                prompt = (
                    "You are a writing coach. Provide concise, constructive Korean feedback on clarity, tone, and "
                    "structure of the following text. Include specific suggestions and an improved sample rewrite "
                    "no longer than 3 sentences.\n\n"
                    f"{feedback_text}"
                )
                result, model_used = generate_with_fallback(prompt)
                if result:
                    st.success("피드백 결과")
                    st.write(result)
                    log_history("feedback", feedback_text, result, model_used or "")

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
