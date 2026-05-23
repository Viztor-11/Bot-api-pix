from fastapi import FastAPI, Request
import mercadopago

app = FastAPI()

MP_ACCESS_TOKEN = "MP TOKEN"
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# armazenamento em memória
pagamentos = {}

# ================= STATUS =================
@app.get("/status")
async def status():
    return pagamentos

# ================= WEBHOOK =================
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    try:
        if "data" in data:
            payment_id = data["data"]["id"]

            pagamento = sdk.payment().get(payment_id)["response"]

            if pagamento["status"] == "approved":
                ref = pagamento["external_reference"]

                user_id, aposta_id = ref.split("|")
                user_id = int(user_id)

                if aposta_id not in pagamentos:
                    pagamentos[aposta_id] = []

                if user_id not in pagamentos[aposta_id]:
                    pagamentos[aposta_id].append(user_id)

                print(f"Pagamento aprovado: {user_id} | {aposta_id}")

    except Exception as e:
        print("Erro webhook:", e)

    return {"ok": True}