#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ============================================================
# SOZLAMALAR
# ============================================================

TOKEN = "8503206701:AAHms14tr7t2Y2qx74QaoOCZn74I104J_n0"
GURUH_ID = -1001210486415  # Sizning guruhingiz

# Sizning Telegram ID ingiz (bot faqat sizdan buyruq qabul qiladi)
# Quyida 0 o'rniga o'z ID ingizni yozing
# ID olish uchun @userinfobot ga /start yozing
OWNER_ID = 1407125509  # Ergashev Muxammad-Ali

# ============================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"✅ Bot ishga tushdi!\n\n"
        f"Sizning ID ingiz: `{user_id}`\n\n"
        f"Endi menga matn yoki ovozli xabar yuboring — guruhga jo'nataman!",
        parse_mode="Markdown"
    )

async def matn_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Faqat owner dan qabul qiladi
    if OWNER_ID != 0 and user_id != OWNER_ID:
        await update.message.reply_text("❌ Siz bu botdan foydalana olmaysiz.")
        return

    matn = update.message.text

    try:
        await context.bot.send_message(
            chat_id=GURUH_ID,
            text=matn
        )
        await update.message.reply_text("✅ Xabar guruhga jo'natildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def ovoz_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Faqat owner dan qabul qiladi
    if OWNER_ID != 0 and user_id != OWNER_ID:
        await update.message.reply_text("❌ Siz bu botdan foydalana olmaysiz.")
        return

    ovoz = update.message.voice

    try:
        # Ovozli xabarni guruhga jo'natish
        await context.bot.send_voice(
            chat_id=GURUH_ID,
            voice=ovoz.file_id,
            caption="🎙 Yangi ovozli xabar"
        )
        await update.message.reply_text("✅ Ovozli xabar guruhga jo'natildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def rasm_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if OWNER_ID != 0 and user_id != OWNER_ID:
        return

    rasm = update.message.photo[-1]
    caption = update.message.caption or ""

    try:
        await context.bot.send_photo(
            chat_id=GURUH_ID,
            photo=rasm.file_id,
            caption=caption
        )
        await update.message.reply_text("✅ Rasm guruhga jo'natildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def video_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if OWNER_ID != 0 and user_id != OWNER_ID:
        return

    video = update.message.video

    try:
        await context.bot.send_video(
            chat_id=GURUH_ID,
            video=video.file_id,
            caption=update.message.caption or ""
        )
        await update.message.reply_text("✅ Video guruhga jo'natildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, matn_qabul))
    app.add_handler(MessageHandler(filters.VOICE, ovoz_qabul))
    app.add_handler(MessageHandler(filters.PHOTO, rasm_qabul))
    app.add_handler(MessageHandler(filters.VIDEO, video_qabul))

    print("✅ Guruh bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
