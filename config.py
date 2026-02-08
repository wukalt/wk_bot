import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

ALLOWED_USER_IDS = {
    int(i) for i in os.getenv("ALLOWED_USER_IDS", "").split(",") if i
}
