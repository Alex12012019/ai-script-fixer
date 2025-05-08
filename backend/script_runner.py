import subprocess
from rich.console import Console
from typing import Optional
from fixer import call_llm

console = Console()
SCRIPT_PATH = "../scripts/SelfConfiguring-FaissCache.ps1"

import subprocess
from rich.console import Console
from typing import Optional
from fixer import call_llm
import os
import chardet

console = Console()

SCRIPT_PATH = "../scripts/SelfConfiguring-FaissCache.ps1"

def read_script_with_encoding(script_path):
    """Автоматически определяет кодировку и читает содержимое скрипта"""
    if not os.path.exists(script_path):
        console.print(f"[red][-] Скрипт не найден: {script_path}[/red]")
        return ""

    with open(script_path, "rb") as f:
        raw_data = f.read()

    result = chardet.detect(raw_data)
    encoding = result['encoding'] or 'utf-8'

    try:
        return raw_data.decode(encoding)
    except UnicodeDecodeError:
        console.print("[yellow][!] Не удалось прочитать с основной кодировкой, пробую latin-1...[/yellow]")
        return raw_data.decode("latin-1", errors="replace")

def run_script(script_path: str = SCRIPT_PATH) -> Optional[str]:
    console.log(f"[*] Запуск скрипта: {script_path}")
    try:
        result = subprocess.run(
            ["pwsh", "-File", script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        console.print(result)
        console.print("[green][+] Скрипт выполнен успешно![/green]")
        return None
    except subprocess.CalledProcessError as e:
        console.print(f"[red][-] Ошибка при выполнении:[/red]\n{e.stderr}")
        return e.stderr

def fix_script(error: str, script_path: str = SCRIPT_PATH) -> bool:
    with open(script_path, 'r', encoding='utf-8') as f:
        original_script = f.read()

    context = {
        "os": "Windows 10",
        "ps_version": "$PSVersionTable.PSVersion",
        "purpose": "Подготовка кэша FAISS-GPU"
    }

    prompt = f"""
Вы эксперт по PowerShell.
Следующий скрипт завершился с ошибкой:

Скрипт:
    
    {original_script}
    

    Ошибка:
    {error}

    Контекст:
    {context}

    Пожалуйста, исправьте скрипт так, чтобы он работал.
    Верните только исправленный код, без объяснений.
    """

    fixed_script = call_llm(prompt, model="Qwen3-8B-Instruct")
    if fixed_script.strip():
        console.print("[green][+] Получен исправленный скрипт[/green]")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(fixed_script)
        return True
    else:
        console.print("[-] Не удалось получить исправление от ИИ", style="red")
        return False


def auto_fix_loop(max_retries: int = 5, script_path: str = SCRIPT_PATH) -> bool:
    for i in range(max_retries):
        error = run_script(script_path)
        if error is None:
            return True
        console.print(f"[yellow][!] Попытка #{i+1} исправить скрипт...[/yellow]")
        if not fix_script(error, script_path):
            console.print("[-] ИИ не смог исправить скрипт.", style="red")
            break
    return False