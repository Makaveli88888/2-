from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="JOKERAl Mini App Backend")

BOT_TOKEN = os.getenv("JOKERAL_BOT_TOKEN")
PACKS = {
    "starter": {"stars": 50, "chips": 5000, "title": "Starter Boost"},
    "standard": {"stars": 150, "chips": 16500, "title": "Standard Boost"},
    "high": {"stars": 500, "chips": 60000, "title": "High Boost"},
}

class InvoiceRequest(BaseModel):
    pack: str
    user_id: int

@app.post("/cashier/stars-invoice")
async def create_stars_invoice(req: InvoiceRequest):
    if req.pack not in PACKS:
        raise HTTPException(400, "Unknown pack")
    pack = PACKS[req.pack]
    payload = f"pack:{req.pack}:{uuid4()}"
    # W prawdziwej implementacji użyj telegram.Bot.create_invoice_link
    # Tutaj mock dla demo lokalnego
    invoice_link = f"https://t.me/invoice/mock?payload={payload}&stars={pack['stars']}"
    return {
        "invoice_link": invoice_link,
        "payload": payload,
        "stars": pack["stars"],
        "chips": pack["chips"],
        "note": "Zastąp mock prawdziwym create_invoice_link gdy token jest ustawiony"
    }

@app.get("/health")
def health():
    return {"status": "ok", "bot_token_set": bool(BOT_TOKEN)}
