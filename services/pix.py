import mercadopago
import base64
import discord

from io import BytesIO
from config import MP_ACCESS_TOKEN

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

def criar_pix(user_id, aposta_id, valor):

    try:
        p = sdk.payment().create({
            "transaction_amount": float(valor),
            "description": f"Aposta {aposta_id}",
            "payment_method_id": "pix",
            "external_reference": f"{user_id}|{aposta_id}",
            "payer": {"email": "teste@teste.com"}
        })["response"]

        if "point_of_interaction" not in p:
            return None

        return p

    except Exception as e:
        print(e)
        return None


def gerar_qr(base64_string):
    return discord.File(
        BytesIO(base64.b64decode(base64_string)),
        filename="qr.png"
    )