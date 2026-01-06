import csv
from datetime import datetime
import os
from flask import Flask, flash, render_template, request, redirect, session, url_for
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # ✅ .env 읽기

app = Flask(__name__)
app.secret_key = "dev-secret-key"

def summarize_with_gemini(text: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "서버에 GEMINI_API_KEY가 설정되지 않았습니다. (.env 확인)"

    genai.configure(api_key=api_key)

    # ✅ 우선 안정적으로 2.5-flash 사용
    model_name = "gemini-2.5-flash"
    model = genai.GenerativeModel(model_name)
    prompt = f"다음 글을 한국어로 핵심만 간결하게 요약해줘.\n\n{text}"

    resp = model.generate_content(prompt)
    return resp.text.strip(), model_name

HISTORY_PATH = "history.csv"

def append_history(action: str, input_text: str, output_text: str, model_name: str) -> None:
    """요약 결과를 CSV에 누적 저장."""
    is_new_file = not os.path.exists(HISTORY_PATH)
    with open(HISTORY_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "action", "model", "input_preview", "output_preview"],
        )
        if is_new_file:
            writer.writeheader()

        writer.writerow(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "action": action,
                "model": model_name,
                "input_preview": (input_text[:120] + "…") if len(input_text) > 120 else input_text,
                "output_preview": (output_text[:120] + "…") if len(output_text) > 120 else output_text,
            }
        )

def read_history(limit: int = 50):
    """CSV에서 최근 기록을 읽어 리스트로 반환."""
    if not os.path.exists(HISTORY_PATH):
        return []

    with open(HISTORY_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    rows.reverse()  # 최신이 위로 오게
    return rows[:limit]


@app.route("/")
def home():
    username = "User"
    return render_template("index.html", name=username)

@app.route("/tools", methods=["GET", "POST"])
def tools():
    if request.method == "POST":
        text = request.form.get("text", "").strip()

        if not text:
            flash("텍스트를 입력해 주세요.", "error")
            session["text"] = ""
            return redirect(url_for("tools"))

        try:
            summary, model_used = summarize_with_gemini(text)

            session["result"] = summary
            session["text"] = text

            if summary and "오류" not in summary:
                append_history("summary", text, summary, model_used)
                flash("요약이 완료되었습니다.", "success")
            else:
                flash("요약은 되었지만 오류 메시지가 포함되어 있습니다.", "error")

        except Exception as e:
            session["result"] = f"Gemini 호출 중 오류가 발생했습니다: {e}"
            session["text"] = text
            flash("Gemini 호출에 실패했습니다.", "error")

        return redirect(url_for("tools"))

    result = session.pop("result", None)
    text = session.pop("text", "")

    return render_template("tools.html", result=result, text=text)

@app.route("/history")
def history():
    rows = read_history(limit=50)
    return render_template("history.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
