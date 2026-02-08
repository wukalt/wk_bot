from fastapi import APIRouter, Request, HTTPException
from handlers.text import handle_text
from handlers.voice import handle_voice
from config import ALLOWED_USER_IDS


router = APIRouter()


@router.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    msg = data.get("message", {})
    chat_id = msg.get("chat", {}).get("id")

    if chat_id not in ALLOWED_USER_IDS:
        raise HTTPException(status_code=403)

    if "text" in msg:
        handle_text(chat_id, msg["text"])
    elif "voice" in msg:
        handle_voice(chat_id, msg["voice"])

    return {"status": "ok"}
