from services.telegram import send_text, send_photo, send_video
from services.ai import ask_gpt
from services.downloaders import *
from state.memory import sessions, extract_mode


def handle_text(chat_id, text):
    if text == "/start":
        send_text(chat_id, "سلام 👋")

    elif text == "/clear":
        sessions.clear()
        send_text(chat_id, "حافظه پاک شد 🧹")

    else:
        send_text(chat_id, ask_gpt(chat_id, text))
