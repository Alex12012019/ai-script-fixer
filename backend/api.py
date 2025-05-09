# backend/api.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rich.console import Console
import os
import sys
import json
from backend.script_runner import auto_fix_loop, SCRIPT_PATH
import chardet
from typing import Optional

console = Console()

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(project_root, "scripts")
sys.path.append(project_root)

# Добавляем SCRIPT_PATH
SCRIPT_PATH = os.path.join(scripts_dir, "SelfConfiguring-FaissCache.ps1")

# Инициализируем шаблонизатор
templates = Jinja2Templates(directory=os.path.join(project_root, "templates"))

app = FastAPI(
    title="AI Script Fixer",
    description="Автономная система автоисправления скриптов через ИИ",
    version="0.3.2"
)

class ScriptRequest(BaseModel):
    script_path: str
    script_content: Optional[str] = None
    max_retries: int = 5


history_file = os.path.join(project_root, "logs", "history.json")


def save_to_history(data):
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            f.write("[]")

    with open(history_file, "r") as f:
        history = json.load(f)

    history.append(data)

    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)


@app.post("/run")
def execute_script(req: ScriptRequest):
    result = {"script": req.script_path, "retries": req.max_retries}
    success = auto_fix_loop(req.max_retries, req.script_path)
    result["status"] = "success" if success else "failed"

    save_to_history(result)
    return result


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if not os.path.exists(history_file):
        history = []
    else:
        with open(history_file, "r") as f:
            history = json.load(f)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "script_path": SCRIPT_PATH,
        "history": history
    })


@app.get("/history")
def get_history():
    if not os.path.exists(history_file):
        return {"history": [], "error": "История не найдена"}

    with open(history_file, "r") as f:
        history = json.load(f)

    return {"history": history}

@app.get("/script/edit")
def edit_script(request: Request, script_path: str = SCRIPT_PATH):
    try:
        with open(script_path, "rb") as f:
            raw = f.read()

        result = chardet.detect(raw)
        encoding = result['encoding'] or 'utf-8'

        try:
            content = raw.decode(encoding)
        except UnicodeDecodeError:
            content = raw.decode("latin-1", errors="replace")

        return templates.TemplateResponse("script_edit.html", {
            "request": request,
            "script_path": script_path,
            "script_content": content
        })
    except Exception as e:
        console.print(f"[red][-] Ошибка при загрузке скрипта: {e}[/red]")
        return {"error": str(e)}

@app.get("/script/list")
def list_scripts(request: Request):
    scripts_dir = os.path.join(project_root, "scripts")
    script_files = [f for f in os.listdir(scripts_dir) if f.endswith((".ps1", ".sh", ".bat", ".py"))]

    return templates.TemplateResponse("script_list.html", {
        "request": request,
        "scripts": script_files
    })

@app.get("/script/load")
def load_script(name: str):
    path = os.path.join(project_root, "scripts", name)
    if not os.path.exists(path):
        return {"error": "Файл не найден"}

    print("load ", path)
    with open(path, "rb") as f:
        raw = f.read()
    print("loaded ", path)

    result = chardet.detect(raw)
    encoding = result['encoding'] or 'utf-8'

    try:
        content = raw.decode(encoding)
        print("encoded ", path, " to utf-8")
    except UnicodeDecodeError:
        content = raw.decode("latin-1", errors="replace")
        print("err encoded to utf-8. encoded ", path, " latin-1")

    return {"script_path": path, "content": content}

@app.post("/script/save")
async def save_script(request: ScriptRequest):
    with open(request.script_path, 'w', encoding='utf-8') as f:
        f.write(request.script_content)
    console.print(f"[green][+] Скрипт сохранён: {request.script_path}[/green]")
    return {"status": "saved", "path": request.script_path}