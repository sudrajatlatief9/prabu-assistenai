import os
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# Konfigurasi API Keys dari Environment Variables Cloud Run
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

@app.get("/")
def home():
    return {"status": "Asisten AI RW Online & Connected to Telegram!"}

# Endpoint Webhook khusus Telegram
@app.post("/webhook-telegram")
async def telegram_webhook(request: Request):
    if not GROQ_API_KEY or not TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="API Key belum lengkap di server.")
    
    body = await request.json()
    
    # Validasi apakah pesan teks dari Telegram
    if "message" not in body or "text" not in body["message"]:
        return {"status": "ignored"}
    
    chat_id = body["message"]["chat"]["id"]
    user_message = body["message"]["text"]
    user_name = body["message"]["from"].get("first_name", "Warga/Pengurus")
    
    try:
        # System Prompt khusus Pengurus RW
        system_instruction = (
            "Kamu adalah Asisten AI resmi untuk Pengurus RW 026 Pengasinan, Bekasi. "
            "Tugasmu adalah membantu pengurus (Sekretaris, Bendahara, Koordinator IT) dalam hal: "
            "1. Membuat draf surat, pemberitahuan, atau pengumuman warga. "
            "2. Merapikan pencatatan laporan keuangan kas RW. "
            "3. Memberikan solusi teknis pengelolaan website RW. "
            "Gunakan bahasa Indonesia yang profesional, ramah, dan ringkas."
        )

        # Memanggil AI Groq/Hermes
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b", # Pastikan model aktif
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Pengirim: {user_name}. Pesan: {user_message}"}
            ],
            temperature=0.3,
            max_tokens=1024
        )

        ai_reply = response.choices[0].message.content

        # Kirim balik jawaban AI ke Telegram Pengguna
        send_telegram_message(chat_id, ai_reply)

        return {"status": "success"}

    except Exception as e:
        print("Error:", str(e))
        send_telegram_message(chat_id, "Maaf, terjadi kendala saat memproses permintaan Anda.")
        return {"status": "error", "detail": str(e)}

def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
