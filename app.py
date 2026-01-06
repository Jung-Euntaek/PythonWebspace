import sqlite3
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

DB_PATH = "app.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict처럼 접근 가능
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          timestamp TEXT NOT NULL,
          action TEXT NOT NULL,
          model TEXT NOT NULL,
          input TEXT NOT NULL,
          output TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

def insert_history(action: str, input_text: str, output_text: str, model_name: str) -> None:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO history (timestamp, action, model, input, output)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action,
            model_name,
            input_text,
            output_text,
        ),
    )
    conn.commit()
    conn.close()

def fetch_history(limit: int = 50):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, timestamp, action, model,
               input AS input_full,
               output AS output_full
        FROM history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_history_one(history_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, timestamp, action, model, input, output
        FROM history
        WHERE id = ?
        """,
        (history_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row

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
                insert_history("summary", text, summary, model_used)
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
    rows = fetch_history(limit=50)
    return render_template("history.html", rows=rows)

@app.route("/history/<int:history_id>")
def history_detail(history_id: int):
    row = fetch_history_one(history_id)
    if row is None:
        return "해당 기록을 찾을 수 없습니다.", 404
    return render_template("history_detail.html", row=row, idx=history_id)

if __name__ == "__main__":
    app.run(debug=True)
