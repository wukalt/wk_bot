import requests
from config import OPENAI_API_KEY
from state.memory import chat_memory


def ask_gpt(chat_id, text):
    history = chat_memory[chat_id]
    history.append({"role": "user", "content": text})

    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": list(history)
        }
    ).json()

    reply = res["choices"][0]["message"]["content"]
    history.append({"role": "assistant", "content": reply})
    return reply
