from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

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

    return templates.TemplateResponse(
        "tools.html",
        {"request": request, "result": summary, "error": None, "text": text},
    )
