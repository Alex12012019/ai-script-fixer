import requests
from rich.console import Console

console = Console()

def call_llm(prompt: str, model="Qwen3-14B-Instruct", host="http://localhost:1234/v1/chat/completions") -> str:
    console.log(f"[*] Отправляем запрос в {model}...")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Вы эксперт по PowerShell. Возвращайте только исправленный скрипт, без объяснений."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 2048,
        "stream": False
    }

    try:
        response = requests.post(host, json=payload, timeout=60)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            console.log(f"[green][+] ИИ вернул результат ({model})[/green]")
            return content
        else:
            console.log(f"[red][-] Ошибка от модели: {response.text}[/red]")
            return ""
    except Exception as e:
        console.print(f"[red][-] Не удалось подключиться к модели: {e}[/red]")
        return ""