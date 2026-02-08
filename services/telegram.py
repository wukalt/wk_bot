import requests
from config import TELEGRAM_API


def send_text(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )


def send_photo(chat_id, image_bytes):
    requests.post(
        f"{TELEGRAM_API}/sendPhoto",
        data={"chat_id": chat_id},
        files={"photo": ("image.jpg", image_bytes)}
    )


def send_video(chat_id, video_bytes):
    requests.post(
        f"{TELEGRAM_API}/sendVideo",
        data={"chat_id": chat_id},
        files={"video": ("video.mp4", video_bytes)}
    )


def get_file_link(file_id):
    res = requests.get(
        f"{TELEGRAM_API}/getFile",
        params={"file_id": file_id}
    ).json()
    return f"https://api.telegram.org/file/bot{TELEGRAM_API}/{res['result']['file_path']}"
