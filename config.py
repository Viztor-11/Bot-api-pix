from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

MOD_ROLE_ID = int(os.getenv("MOD_ROLE_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))