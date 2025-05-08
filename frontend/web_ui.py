import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="AI Script Fixer", layout="wide")
st.title("🧠 AI-Powered Script Fixer")
st.markdown("Запуск скриптов, автоисправление через ИИ и история фиксов")

SCRIPT_PATH = "../scripts/SelfConfiguring-FaissCache.ps1"
API_URL = "http://localhost:8000/run"

# === Форма запуска скрипта ===
with st.form("run_script_form"):
    st.subheader("▶️ Запустить скрипт")
    script_path = st.text_input("Путь к скрипту", value=SCRIPT_PATH)
    max_retries = st.slider("Максимум попыток", min_value=1, max_value=10, value=5)
    submit = st.form_submit_button("Запустить")

    if submit:
        with st.spinner("Запуск скрипта..."):
            data = {"script_path": script_path, "max_retries": max_retries}
            response = requests.post(API_URL, json=data)
            result = response.json()
            st.success("✅ Скрипт выполнен")
            st.code(json.dumps(result, indent=2, ensure_ascii=False))

# === История фиксов ===
st.sidebar.header("📁 История фиксов")
history_path = os.path.join("..", "logs", "history.json")

if os.path.exists(history_path):
    with open(history_path, "r", encoding="utf-8") as f:
        history = json.load(f)
    for idx, item in enumerate(history):
        st.sidebar.info(f"{idx+1}. [{item.get('status', 'unknown')}] {item.get('script', '')}")
else:
    st.sidebar.warning("🚫 История пуста")