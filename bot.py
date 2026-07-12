import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from subtitles import (
    search_movie,
    get_imdb_id,
)

from opensubtitles import (
    search_subtitles,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🎬 Welcome!\n\n"
        "Send me a movie or TV show name."
    )
    async def search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    movie_name = update.message.text.strip()

    if not movie_name:
        await update.message.reply_text(
            "Please send a movie name."
        )
        return

    msg = await update.message.reply_text(
        "🔎 Searching..."
    )

    try:
        movie = search_movie(movie_name)

        if not movie:
            await msg.edit_text(
                "❌ Movie not found."
            )
            return

        imdb_id = get_imdb_id(
            movie["media_type"],
            movie["id"],
        )

        if not imdb_id:
            await msg.edit_text(
                "❌ IMDb ID not found."
            )
            return

        subtitles = search_subtitles(imdb_id)

        if not subtitles:
            await msg.edit_text(
                "❌ No subtitles found."
            )
            return

    except Exception as e:
        logger.exception(e)

        await msg.edit_text(
            "❌ Something went wrong."
        )
        return

    keyboard = []

    for subtitle in subtitles[:20]:

        language = (
            subtitle.get("language")
            or "Unknown"
        )

        file_id = subtitle.get("file_id")

        keyboard.append(
            [
                InlineKeyboardButton(
                    language,
                    callback_data=f"sub|{file_id}",
                )
            ]
        )

    await msg.edit_text(
        f"🎬 {movie['title']}\n\nChoose subtitle language:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        ),
    )

async def button_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    data = query.data or ""

    if not data.startswith("sub|"):
        await query.edit_message_text(
            "❌ Invalid request."
        )
        return

    file_id = data.split("|", 1)[1]

    await query.edit_message_text(
        f"✅ Subtitle selected.\n\nFile ID: {file_id}"
    )
    def main():

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search,
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_callback
        )
    )

    print("✅ Bot started...")

    app.run_polling()

if __name__ == "__main__":
    main()
