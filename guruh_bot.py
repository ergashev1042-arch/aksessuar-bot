#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import tempfile
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from groq import Groq

TOKEN = "8503206701:AAHms14tr7t2Y2qx74QaoOCZn74I104J_n0"
OWNER_ID = 1407125509
GROQ_API_KEY = "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"

# Guruh va kanal ro'yxati
TARGETS = [
    "@asakaakfaaksessuar",  # 1-guruh
    "@tayhu_asaka",          # 2-guruh
    "@windoorline_asaka",    # Kanal
]

groq_client = Groq(api_key=GROQ_API_KEY)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot ishga tushdi!\n\n📝 Matn yuboring → guruhga jo'nataman\n🎙 Ovozli xabar → matnga o'girib guruhga jo'nataman\n🖼 Rasm → guruhga jo'nataman\n🎥 Video → guruhga jo'nataman")

async def matn_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    for target in TARGETS:
        try:
            await context.bot.send_message(chat_id=target, text=update.message.text)
        except Exception as e:
            await update.message.reply_text(f"❌ Xato ({target}): {e}")
    await update.message.reply_text("✅ Xabar hammaga jo'natildi!")

async def ovoz_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("🎙 Matnga o'girilmoqda...")
    try:
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name
        await voice_file.download_to_drive(tmp_path)
        with open(tmp_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=("audio.ogg", audio_file.read()),
                model="whisper-large-v3",
                language="uz",
                response_format="text"
            )
        os.unlink(tmp_path)
        matn = transcription.strip()
        if not matn:
            await update.message.reply_text("❌ Ovozdan matn aniqlanmadi.")
            return
        for target in TARGETS:
            try:
                await context.bot.send_message(chat_id=target, text=f"🎙 Ovozli xabar:\n\n{matn}")
            except Exception as e:
                await update.message.reply_text(f"❌ Xato ({target}): {e}")
        await update.message.reply_text(f"✅ Hammaga jo'natildi!\n\n📝 Matn:\n{matn}")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def rasm_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    for target in TARGETS:
        try:
            await context.bot.send_photo(chat_id=target, photo=update.message.photo[-1].file_id, caption=update.message.caption or "")
        except Exception as e:
            await update.message.reply_text(f"❌ Xato ({target}): {e}")
    await update.message.reply_text("✅ Rasm hammaga jo'natildi!")

async def video_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    for target in TARGETS:
        try:
            await context.bot.send_video(chat_id=target, video=update.message.video.file_id, caption=update.message.caption or "")
        except Exception as e:
            await update.message.reply_text(f"❌ Xato ({target}): {e}")
    await update.message.reply_text("✅ Video hammaga jo'natildi!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, matn_qabul))
    app.add_handler(MessageHandler(filters.VOICE, ovoz_qabul))
    app.add_handler(MessageHandler(filters.PHOTO, rasm_qabul))
    app.add_handler(MessageHandler(filters.VIDEO, video_qabul))
    print("✅ Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
