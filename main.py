from flask import Flask, request, jsonify
from handlers.message_handlers import handle_text, handle_voice
from config import ALLOWED_USER_IDS
from utils.telegram_utils import send_text

app = Flask(__name__)

# === Config ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_API = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'

ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS")

# === States ===
sessions = {}
extract_mode = {}
chat_memory = defaultdict(lambda: deque(maxlen=50))

# === Telegram Utils ===
def send_text(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_photo(chat_id, image_bytes):
    requests.post(f"{TELEGRAM_API}/sendPhoto", data={
        "chat_id": chat_id
    }, files={
        "photo": ("image.jpg", image_bytes)
    })

def send_video(chat_id, video_bytes):
    requests.post(f"{TELEGRAM_API}/sendVideo", data={
        "chat_id": chat_id
    }, files={
        "video": ("video.mp4", video_bytes)
    })

def get_file_link(file_id):
    res = requests.get(f"{TELEGRAM_API}/getFile", params={"file_id": file_id}).json()
    path = res["result"]["file_path"]
    return f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{path}"

# === My Functions ===
def clear_history():
    chat_memory.clear()
    return "memory is cleared -> empty now"

def download_instagram_post_with_cookies(url):
    if os.path.exists("insta_download"):
        shutil.rmtree("insta_download")

    L = instaloader.Instaloader(dirname_pattern="insta_download", save_metadata=False, download_comments=False)

    cookie_file = "instacookies.txt" 
    if os.path.exists(cookie_file):
        L.context._session.cookies.load(cookie_file, ignore_discard=True, ignore_expires=True)
    else:
        print("کوکی فایل پیدا نشد!")

    shortcode = url.rstrip('/').split("/")[-1].split("?")[0]
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    print("Post typename:", post.typename)
    
    L.download_post(post, target="post")

    media_folder = "insta_download/post"
    media_files = sorted(os.listdir(media_folder))
    media_bytes = []
    for file in media_files:
        filepath = os.path.join(media_folder, file)
        with open(filepath, "rb") as f:
            media_bytes.append((file, f.read()))

    shutil.rmtree("insta_download")
    return media_bytes


def download_youtube_video(url):
    try:
        output_filename = "video.mp4"
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': output_filename,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'video')

        if not os.path.exists(output_filename):
            print("⚠️ فایل ویدیویی ساخته نشد.")
            return None, None

        with open(output_filename, "rb") as f:
            video_data = f.read()

        os.remove(output_filename)
        return title, video_data
    except Exception as e:
        print("Download error:", str(e))
        return None, None


def extract_pinterest_image_url(pinterest_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(pinterest_url, headers=headers)
        if res.status_code != 200:
            print(f"Failed to get Pinterest page, status: {res.status_code}")
            return None
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup.find_all("meta"):
            if tag.get("property") == "og:image":
                return tag.get("content")
        print("og:image meta tag not found")
        return None
    except Exception as e:
        print("Pinterest image extraction error:", e)
        return None

def download_pinterest_image(url):
    image_url = extract_pinterest_image_url(url)
    if not image_url:
        return None, None
    image_data = requests.get(image_url).content
    return "pinterest_image.jpg", image_data


# TODO : Make it work

# def edit_image_with_prompt(image_bytes, prompt):
#     url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5-img2img"
#     headers = {
#         "Authorization": f"Bearer {HF_API_KEY}"
#     }

#     files = {
#         "image": ("input.png", image_bytes, "image/png")
#     }

#     data = {
#         "inputs": prompt
#     }

#     response = requests.post(url, headers=headers, files=files, data=data)
#     time.sleep(15)

#     if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
#         return response.content
#     else:
#         print("⚠️ پاسخ غیرمعتبر:", response.text)
#         return None


# === AI Helpers ===
def ask_gpt_with_memory(chat_id, user_text):
    history = chat_memory[chat_id]
    history.append({"role": "user", "content": user_text})
    messages = [{"role": "system", "content": "تو یک دستیار فارسی زبان هستی. پاسخ‌ها دوستانه باشند."}] + list(history)
    res = requests.post("https://api.openai.com/v1/chat/completions", headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "model": "gpt-4o-mini",
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
        "model": "gpt-4o-mini",
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

# === Handlers ===
def handle_voice(chat_id, file_id):
    file_url = get_file_link(file_id)
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
        send_text(chat_id, "سلام. من wk assist هستم چطور کمکتون کنمم؟")

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

    # TODO : FIX THIS
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
        clear_history()
      
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

# === Webhook Routes ===
>>>>>>> parent of 7225699 (Fix: clear command)
@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")

    if chat_id not in ALLOWED_USER_IDS:
        send_text(chat_id, "شما اجازه استفاده از این ربات را ندارید.")
        return jsonify({"status": "unauthorized"})

    if "voice" in msg:
        handle_voice(chat_id, msg["voice"]["file_id"])
    elif "text" in msg:
        handle_text(chat_id, msg["text"])
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def index():
    return "Bot is running ...."


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
