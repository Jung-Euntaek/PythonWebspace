import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # ✅ .env 읽기

app = Flask(__name__)

def summarize_with_gemini(text: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "서버에 GEMINI_API_KEY가 설정되지 않았습니다. (.env 확인)"

    genai.configure(api_key=api_key)

    # ✅ 우선 안정적으로 2.5-flash 사용
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"다음 글을 한국어로 핵심만 간결하게 요약해줘.\n\n{text}"

    resp = model.generate_content(prompt)
    return resp.text.strip()

@app.route("/")
def home():
    username = "User"
    return render_template("index.html", name=username)

@app.route("/tools", methods=["GET", "POST"])
def tools():
    result = None
    text = ""

    if request.method == "POST":
        text = request.form.get("text", "").strip()

        if text:
            try:
                result = summarize_with_gemini(text)
            except Exception as e:
                result = f"Gemini 호출 중 오류가 발생했습니다: {e}"
        else:
            result = "텍스트를 입력해 주세요."

    return render_template("tools.html", result=result, text=text)

@app.route("/history")
def history():
    return render_template("history.html")

if __name__ == "__main__":
    app.run(debug=True)
