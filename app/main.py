from datetime import datetime

from app.db import init_db, insert_history, list_history, get_history

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

init_db()

# static 폴더 연결 (Flask의 static과 같은 역할)
app.mount("/static", StaticFiles(directory="static"), name="static")

# templates 폴더 연결
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "name": "FastAPI"})

@app.get("/tools", response_class=HTMLResponse)
def tools_page(request: Request):
    return templates.TemplateResponse(
        "tools.html",
        {"request": request, "result": None, "error": None, "text": ""},
    )

@app.post("/tools", response_class=HTMLResponse)
def tools_submit(request: Request, text: str = Form("")):
    text = (text or "").strip()
    if not text:
        return templates.TemplateResponse(
            "tools.html",
            {"request": request, "result": None, "error": "텍스트를 입력해 주세요.", "text": ""},
        )

    # ✅ 지금은 AI 대신 '가짜 요약' (앞 200자만 보여주기)
    summary = text[:200] + ("…" if len(text) > 200 else "")

    model_used = "mock"  # 나중에 Gemini/OpenAI 붙이면 실제 모델명으로 바꿈
    insert_history(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        action="summary",
        model=model_used,
        input_text=text,
        output_text=summary,
    )

    return templates.TemplateResponse(
        "tools.html",
        {"request": request, "result": summary, "error": None, "text": text},
    )

@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request, q: str = "", action: str = "all"):
    rows = list_history(q=q, action=action, limit=50)
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "rows": rows, "q": q, "action": action},
    )

@app.get("/history/{history_id}", response_class=HTMLResponse)
def history_detail(request: Request, history_id: int):
    row = get_history(history_id)
    return templates.TemplateResponse(
        "history_detail.html",
        {"request": request, "row": row},
    )
