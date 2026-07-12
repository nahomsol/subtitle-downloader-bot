
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, check_config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Welcome!\n\n"
        "Send me a movie or TV show name.\n"
        "I'll search for available subtitles."
    )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text.strip()

    if not movie_name:
        await update.message.reply_text("Please send a movie name.")
        return

    await update.message.reply_text(
        f"🔎 Searching for:\n\n{movie_name}"
    )


def main():
    check_config()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, search)
    )

    print("Bot started...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
