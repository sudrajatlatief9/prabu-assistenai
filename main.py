import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# Inisialisasi klien Groq (menggunakan API Key dari environment variable Cloud Run)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# Struktur data untuk menerima pesan masuk
class MessageRequest(BaseModel):
    message: str
    sender_role: str = "pengurus" # Contoh role: sekretaris, bendahara, it

@app.get("/")
def home():
    return {"status": "Asisten AI RW Online & Connected to Hermes/Groq!"}

@app.post("/webhook-ai")
async def chat_with_agent(req: MessageRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY belum dikonfigurasi di server.")
    
    try:
        # System Prompt khusus untuk Asisten Pengurus RW
        system_instruction = (
            "Kamu adalah Asisten AI resmi untuk Pengurus RW 026 Kelurahan Pengasinan Kecamatan Rawalumbu, Kota Bekasi. "
            "Tugasmu adalah membantu pengurus (Sekretaris, Bendahara, Koordinator IT) dalam hal: "
            "1. Membuat draf surat, pemberitahuan, atau pengumuman warga. "
            "2. Merapikan pencatatan laporan keuangan kas RW. "
            "3. Memberikan solusi teknis pengelolaan website RW. "
            "Gunakan bahasa Indonesia yang profesional, ramah, dan ringkas."
        )

        # Memanggil Model AI (Menggunakan Llama-3 / Hermes-style instruction)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Model cepat & cerdas dari Groq
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Peran pengirim: {req.sender_role}. Pesan: {req.message}"}
            ],
            temperature=0.3,
            max_tokens=1024
        )

        ai_reply = response.choices[0].message.content
        return {
            "status": "success",
            "reply": ai_reply
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
