import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient, events
from telethon.tl.types import User
import google.generativeai as genai

# ===================== SOZLAMALAR =====================
API_ID = 37827998
API_HASH = "087f2975b686ea86cda1baa389ae641a"
GEMINI_API_KEY = "AIzaSyAc29KOWLn35djlLAz-t_GPmtz5bzFGeyY"

YOUR_NAME = "Salom"

BOT_ACTIVE = True

KEYWORD_RESPONSES = {
    "salom": "Salom! Hozir band eman, tez orada javob beraman",
    "narx": "Narx haqida ma'lumot uchun kuting, tez orada javob beraman.",
    "qachon": "Imkon topilishi bilan albatta javob beraman!",
    "telefon": "Ish vaqtida 9:00-18:00 javob beraman.",
    "rahmat": "Arzimaydi!",
    "ok": "OK",
    "xayr": "Xayr! Yaxshi kun tilayman",
}

LOG_FILE = "xabarlar_log.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="Sen " + YOUR_NAME + " nomidan avtomatik javob beruvchi yordamchisan. " + YOUR_NAME + " hozir band. Uning nomidan samimiy va qisqa javob ber. Har doim O'zbek tilida javob ber. Juda uzun javob berma - 1-2 jumladan oshirma. Agar savol muhim bolsa, tez orada shaxsan javob beraman de."
)

client = TelegramClient('session', API_ID, API_HASH)


def log_message(sender_name, sender_id, text, reply, source):
    entry = {
        "vaqt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kimdan": sender_name,
        "id": sender_id,
        "xabar": text,
        "javob": reply,
        "turi": source
    }
    logs = []
    if Path(LOG_FILE).exists():
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            pass
    logs.append(entry)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    logger.info("Xabar: " + sender_name + ": " + text[:40] + " [" + source + "]")


def check_keywords(text):
    text_lower = text.lower()
    for keyword, response in KEYWORD_RESPONSES.items():
        if keyword in text_lower:
            return response
    return None


def get_ai_response(message_text, sender_name):
    try:
        response = gemini.generate_content(sender_name + " dan xabar keldi: " + message_text)
        return response.text.strip()
    except Exception as e:
        logger.error("Gemini xatosi: " + str(e))
        return "Hozir band eman, tez orada javob beraman!"


@client.on(events.NewMessage(incoming=True))
async def handle_message(event):
    if not BOT_ACTIVE or event.out:
        return

    sender = await event.get_sender()
    if not isinstance(sender, User):
        return

    sender_name = ((sender.first_name or '') + ' ' + (sender.last_name or '')).strip()
    text = event.message.text or ""
    if not text:
        return

   if not event.is_private:
    return source = "shaxsiy" if event.is_private else "guruh"

    keyword_reply = check_keywords(text)
    if keyword_reply:
        reply_text = keyword_reply
        reply_source = "shablon (" + source + ")"
    else:
        reply_text = get_ai_response(text, sender_name)
        reply_source = "AI (" + source + ")"

    await event.reply(reply_text)
    log_message(sender_name, sender.id, text, reply_text, reply_source)


@client.on(events.NewMessage(outgoing=True, pattern=r'^/bot (on|off)$'))
async def control_bot(event):
    global BOT_ACTIVE
    cmd = event.pattern_match.group(1)
    BOT_ACTIVE = (cmd == 'on')
    if BOT_ACTIVE:
        status = "YOQILDI"
    else:
        status = "OCHIRILDI"
    await event.reply("Bot " + status)
    logger.info("Bot holati: " + status)


async def main():
    await client.start()
    me = await client.get_me()
    logger.info("Bot ishga tushdi! Akkount: " + str(me.first_name))
    logger.info("Boshqarish: /bot on yoki /bot off")
    logger.info("AI: Gemini 2.0 Flash (bepul)")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
