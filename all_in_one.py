import multiprocessing
import os
import sys
import time
from rich.console import Console

console = Console()

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

def start_backend():
    console.print("[+] Запуск FastAPI сервера...")
    backend_path = os.path.join(project_root, "backend")
    sys.path.append(backend_path)
    os.chdir(backend_path)

    from api import app
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    os.chdir(project_root)

def start_frontend():
    console.print("[+] Запуск Web интерфейса (Streamlit)...")
    frontend_path = os.path.join(project_root, "frontend")
    os.chdir(frontend_path)

    os.system("streamlit run web_ui.py")
    os.chdir(project_root)

if __name__ == "__main__":
    console.print("🚀 AI-Powered Script Fixer запущен")

    os.makedirs(os.path.join(project_root, "logs"), exist_ok=True)

    backend_process = multiprocessing.Process(target=start_backend)
    frontend_process = multiprocessing.Process(target=start_frontend)

    backend_process.start()
    time.sleep(2)
    frontend_process.start()

    try:
        backend_process.join()
        frontend_process.join()
    except KeyboardInterrupt:
        console.print("[!] Остановка всех процессов...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)