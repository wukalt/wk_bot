import requests
from collections import defaultdict, deque
from config import OPENAI_API_KEY, HF_API_KEY

chat_memory = defaultdict(lambda: deque(maxlen=50))

def ask_gpt_with_memory(chat_id, user_text):
    history = chat_memory[chat_id]
    history.append({"role": "user", "content": user_text})
    messages = [{"role": "system", "content": "تو یک دستیار فارسی زبان هستی. پاسخ‌ها دوستانه باشند."}] + list(history)
    res = requests.post("https://api.openai.com/v1/chat/completions", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "model": "gpt-5",
        "verbosity": "low",
        "reasoning_effort": "minimal",
        "messages": messages
    }).json()
    reply = res.get("choices", [{}])[0].get("message", {}).get("content", "پاسخی دریافت نشد.")
    history.append({"role": "assistant", "content": reply})
    return reply


def translate_fa_to_en(text):
    res = requests.post("https://api.openai.com/v1/chat/completions", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "model": "gpt-5",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that translates Persian to English."},
            {"role": "user", "content": f"Translate this to English: {text}"}
        ]
    }).json()
    return res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()


def generate_image(prompt):
    res = requests.post("https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0", headers={
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "image/png"
    }, json={"inputs": prompt})
    if "image" in res.headers.get("content-type", ""):
        return res.content
    return None


def transcribe_voice(file_url):
    voice_data = requests.get(file_url)
    if not voice_data.ok:
        return None
    res = requests.post("https://api-inference.huggingface.co/models/openai/whisper-large-v3", headers={
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "audio/ogg"
    }, data=voice_data.content)
    if not res.ok:
        return None
    return res.json().get("text")
