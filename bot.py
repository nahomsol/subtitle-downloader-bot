from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, check_config
from subtitles import search_movie, get_imdb_id
from opensubtitles import search_subtitles


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

    await update.message.reply_text("🔎 Searching...")

    result = search_movie(movie_name)

    if not result:
        await update.message.reply_text("❌ Movie not found.")
        return

    media_type = result.get("media_type")
    tmdb_id = result.get("id")

    imdb_id = get_imdb_id(media_type, tmdb_id)

    title = result.get("title") or result.get("name")
    year = ""

    if result.get("release_date"):
        year = result["release_date"][:4]

    elif result.get("first_air_date"):
        year = result["first_air_date"][:4]

    subtitles = search_subtitles(imdb_id)

    if not subtitles:
        await update.message.reply_text(
            f"✅ Found\n\n"
            f"Title: {title}\n"
            f"Year: {year}\n\n"
            "❌ No subtitles found."
        )
        return

    languages = []

    for sub in subtitles:
        lang = sub.get("language")

        if lang and lang not in languages:
            languages.append(lang)

    message = (
        f"✅ Found\n\n"
        f"Title: {title}\n"
        f"Year: {year}\n\n"
        "🌍 Available subtitle languages:\n\n"
    )

    for lang in languages[:20]:
        message += f"• {lang}\n"

    await update.message.reply_text(message)


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
