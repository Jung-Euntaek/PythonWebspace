import os

import pandas as pd
import streamlit as st


st.title("실행 이력")
st.write("텍스트 도구에서 실행된 요약/번역/피드백 결과를 확인하고 검색할 수 있습니다.")

if not st.session_state.get("logged_in", False):
    st.error("비밀번호를 먼저 입력해야 합니다. 홈에서 로그인 후 다시 시도하세요.")
    st.stop()

HISTORY_PATH = "history.csv"

if not os.path.exists(HISTORY_PATH):
    st.info("아직 저장된 실행 이력이 없습니다. 텍스트 도구에서 실행 후 다시 확인하세요.")
    st.stop()

try:
    df = pd.read_csv(HISTORY_PATH, encoding="utf-8")
except Exception as exc:
    st.error(f"history.csv를 불러오는 데 실패했습니다: {exc}")
    st.stop()

search = st.text_input("검색어를 입력하세요 (action, input, output, model에서 검색)")
if search:
    mask = (
        df["action"].astype(str).str.contains(search, case=False, na=False)
        | df["input"].astype(str).str.contains(search, case=False, na=False)
        | df["output"].astype(str).str.contains(search, case=False, na=False)
        | df["model"].astype(str).str.contains(search, case=False, na=False)
    )
    df = df[mask]

if df.empty:
    st.info("검색 결과가 없습니다.")
else:
    df_sorted = df.sort_values("timestamp", ascending=False)
    st.dataframe(df_sorted, use_container_width=True)
