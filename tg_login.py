import asyncio
import json
import os
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")
PASSWORD = os.getenv("TELEGRAM_PASSWORD", "")
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_session")

STATUS_FILE = "telegram_login_status.json"

async def step1_send_code():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    
    if await client.is_user_authorized():
        print("ALREADY_AUTHORIZED")
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"status": "authorized"}, f)
        await client.disconnect()
        return

    result = await client.send_code_request(PHONE)
    phone_code_hash = result.phone_code_hash
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "status": "code_sent",
            "phone_code_hash": phone_code_hash
        }, f)
    print("CODE_SENT_SUCCESS")
    await client.disconnect()

async def step2_sign_in(code):
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()

    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    phone_code_hash = data.get("phone_code_hash")
    try:
        await client.sign_in(phone=PHONE, code=code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        print("PASSWORD_NEEDED")
        await client.sign_in(password=PASSWORD)
    
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"LOGIN_SUCCESS:{me.first_name}:{me.id}")
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"status": "authorized", "user_id": me.id, "name": me.first_name}, f)
    else:
        print("LOGIN_FAILED")

    await client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "send_code":
        asyncio.run(step1_send_code())
    elif len(sys.argv) > 2 and sys.argv[1] == "sign_in":
        code = sys.argv[2]
        asyncio.run(step2_sign_in(code))
