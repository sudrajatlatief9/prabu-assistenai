import os
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def home():
    return {"status": "PRABU Asisten AI Online!"}

# Endpoint Webhook Penerima Pesan Chat (WA / Telegram)
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("Pesan masuk:", data)
    
    # Di sini tempat memasukkan logika Agen Hermes nantinya
    
    return {"status": "success", "message": "Pesan diproses"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
