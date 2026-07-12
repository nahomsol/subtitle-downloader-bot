import os
import sys
import logging
import tempfile

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

from subtitles import search_movie, get_imdb_id
from opensubtitles import search_subtitles, download_subtitle


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Send me a movie or TV series name.\n\n"
        "I'll search and let you download subtitles."
    )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    print("SEARCH FUNCTION STARTED", flush=True)
    
    if not query:
        await update.message.reply_text("Please send a movie or series name.")
        return

    msg = await update.message.reply_text("🔎 Searching...")

    try:
        movie = search_movie(query)
    except Exception as e:
        logger.exception(e)
        await msg.edit_text("❌ Failed to search movie.")
        return

    if not movie:
        await msg.edit_text("❌ No movie found.")
        return

    media_type = movie.get("media_type")
    tmdb_id = movie.get("id")

    imdb_id = get_imdb_id(media_type, tmdb_id)

    if not imdb_id:
        await msg.edit_text("❌ IMDb ID not found.")
        return

    try:
      print("IMDB ID:", imdb_id, flush=True)

      subtitles = search_subtitles(imdb_id)

    except Exception as e:
      logger.exception(e)
      await msg.edit_text("❌ Failed to search subtitles.")
      return

    if not subtitles:
        await msg.edit_text("❌ No subtitles found.")
        return

    keyboard = []

    for subtitle in subtitles[:20]:
      file_id = subtitle.get("file_id")

    language = (
        subtitle.get("language")
        or subtitle.get("lang")
        or "Unknown"
    )

    release = (
        subtitle.get("release")
        or subtitle.get("release_name")
        or ""
    )

        text = language
        if release:
            text += f" • {release[:40]}"

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"sub|{file_id}",
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await msg.edit_text(
        f"🎬 {movie.get('title')}\n\nChoose a subtitle:",
        reply_markup=reply_markup,
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data or ""

    if not data.startswith("sub|"):
        await query.edit_message_text("❌ Invalid request.")
        return

    file_id = data.split("|", 1)[1]

    try:
        await query.edit_message_text("⬇️ Downloading subtitle...")
    except Exception:
        pass

    try:
        subtitle = download_subtitle(file_id)
    except Exception as e:
        logger.exception(e)
        await query.edit_message_text("❌ Failed to download subtitle.")
        return

    if not subtitle:
        await query.edit_message_text("❌ Subtitle download failed.")
        return

    filename = (
        subtitle.get("filename")
        or subtitle.get("file_name")
        or f"{file_id}.srt"
    )

    content = (
        subtitle.get("content")
        or subtitle.get("data")
        or subtitle.get("bytes")
    )

    if content is None:
        await query.edit_message_text("❌ Invalid subtitle data.")
        return

    if isinstance(content, str):
        content = content.encode("utf-8")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as tmp:
        tmp.write(content)
        temp_path = tmp.name

    try:
        with open(temp_path, "rb") as f:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=f,
                filename=filename,
                reply_to_message_id=query.message.message_id,
            )
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    try:
        await query.edit_message_text("✅ Subtitle sent.")
    except Exception:
        pass


def main():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search,
        )
    )
    application.add_handler(
        CallbackQueryHandler(button_callback)
    )

    logger.info("Bot started...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
