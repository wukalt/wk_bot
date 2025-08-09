from flask import Flask, request, jsonify
from handlers.message_handlers import handle_text, handle_voice
from config import ALLOWED_USER_IDS
from utils.telegram_utils import send_text

app = Flask(__name__)

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
