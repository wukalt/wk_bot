from fastapi import FastAPI
from api.webhook import router


app = FastAPI()
app.include_router(router)


@app.get("/")
def index():
    return "Bot is running..."