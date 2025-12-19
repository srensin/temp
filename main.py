import re
import os
import shutil
from datetime import datetime
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = ""

BASE_DIR = "downloads"
LOG_FILE = "users.txt"

os.makedirs(BASE_DIR, exist_ok=True)

def is_youtube_link(text):
    return re.match(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+", text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    username = user.username or f"user_{user.id}"
    user_id = user.id or "N/A"

    # log user
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | ID: {user_id} | Username: {username}\n")

    if not is_youtube_link(text):
        await update.message.reply_text(
            "Provide youtube link\n\nThank you for using my bot"
        )
        return

    user_folder = os.path.join(BASE_DIR, username)
    os.makedirs(user_folder, exist_ok=True)

    await update.message.reply_text("Downloading and converting to MP3... 🎵")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(user_folder, "%(title)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])

        mp3_file = next(
            f for f in os.listdir(user_folder) if f.endswith(".mp3")
        )

        mp3_path = os.path.join(user_folder, mp3_file)

        await update.message.reply_audio(
            audio=open(mp3_path, "rb"),
            caption="Thank you for using my bot"
        )

    except Exception as e:
        await update.message.reply_text(
            "Failed to convert audio.\n\nThank you for using my bot"
        )
        print("ERROR:", e)

    finally:
        shutil.rmtree(user_folder, ignore_errors=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()
