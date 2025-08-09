from utils.telegram_utils import send_text, send_photo, send_video
from ai.helpers import ask_gpt_with_memory, translate_fa_to_en, generate_image, transcribe_voice
from services.instagram import download_instagram_post_with_cookies
from services.youtube import download_youtube_video
from services.pinterest import download_pinterest_image

extract_mode = {}
sessions = {}

def handle_voice(chat_id, file_id):
    file_url = send_text.get_file_link(file_id)
    transcript = transcribe_voice(file_url)
    if not transcript:
        send_text(chat_id, "نتونستم ویس رو تبدیل کنم ❌")
        return
    if extract_mode.get(chat_id, False):
        send_text(chat_id, f"🗣 متن ویس:\n\n{transcript}")
    else:
        reply = ask_gpt_with_memory(chat_id, transcript)
        send_text(chat_id, reply)


def handle_text(chat_id, text):
    text = text.strip()
    if text == "/start":
        send_text(chat_id, "سلام. من wk assist هستم چطور کمکتون کنم؟")

    elif text == "/image":
        sessions[chat_id] = "image"
        send_text(chat_id, "چه تصویری می‌خواهی درست کنم برات؟")
        
    elif text == "/extract":
        current = extract_mode.get(chat_id, False)
        extract_mode[chat_id] = not current
        status = "فعال" if not current else "غیرفعال"
        send_text(chat_id, f"حالت استخراج متن از ویس اکنون {status} است.")

    elif "pinterest.com" in text:
        send_text(chat_id, "در حال دانلود تصویر از Pinterest... ⏳")
        try:
            filename, data = download_pinterest_image(text)
            if data:
                send_photo(chat_id, data)
            else:
                send_text(chat_id, "❌ نتونستم تصویر رو از پینترست بگیرم.")
        except Exception as e:
            send_text(chat_id, f"🚫 خطا: {str(e)}")

    elif text.startswith("https://www.instagram.com/"):
        send_text(chat_id, "در حال دانلود از Instagram... ⏳")
        try:
            media_files = download_instagram_post_with_cookies(text)
            if media_files:
                for filename, data in media_files:
                    if filename.endswith(".mp4"):
                        send_video(chat_id, data)
                    else:
                        send_photo(chat_id, data)
            else:
                send_text(chat_id, "🔴 نتونستم فایل رو پیدا کنم یا دانلود کنم.")
        except Exception as e:
            send_text(chat_id, f"🚫 خطا در دانلود: {str(e)}")

    elif "youtube.com" in text or "youtu.be" in text:
        send_text(chat_id, "در حال دانلود از Youtube... ⏳")
        try:
            title, video_data = download_youtube_video(text)
            if video_data:
                send_video(chat_id, video_data)
            else:
                send_text(chat_id, "❌ نتونستم ویدیو رو دانلود کنم.")
        except Exception as e:
            send_text(chat_id, f"🚫 خطا: {str(e)}")

    elif text == "/clear":
        send_text(chat_id, "حافظه پاک شد.")
        from ai.helpers import chat_memory
        chat_memory[chat_id].clear()
      
    elif sessions.get(chat_id) == "image":
        sessions.pop(chat_id)
        prompt = translate_fa_to_en(text)
        img = generate_image(prompt)
        if img:
            send_photo(chat_id, img)
        else:
            send_text(chat_id, "متاسفم، نتونستم تصویر تولید کنم.")

    else:
        reply = ask_gpt_with_memory(chat_id, text)
        send_text(chat_id, reply)
