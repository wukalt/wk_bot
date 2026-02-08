from services.telegram import send_text
from services.ai import ask_gpt


def handle_voice(chat_id, transcript):
    send_text(chat_id, ask_gpt(chat_id, transcript))
