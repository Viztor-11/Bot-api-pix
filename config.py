from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

MOD_ROLE_ID = 123456789
LOG_CHANNEL_ID = 123456789