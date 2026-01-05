from flask import Flask, render_template, request

app = Flask(__name__)

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
            # ✅ 지금은 AI 대신 "서버가 처리했다"는 걸 보여주기 위해 간단히 가공
            result = f"입력한 글자 수: {len(text)}"
        else:
            result = "텍스트를 입력해 주세요."

    return render_template("tools.html", result=result, text=text)

@app.route("/history")
def history():
    return render_template("history.html")

if __name__ == "__main__":
    app.run(debug=True)
