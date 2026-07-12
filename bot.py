from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, check_config
from subtitles import search_movie, get_imdb_id
from opensubtitles import search_subtitles, download_subtitle
LANGUAGE_NAMES = {
    "en": "🇬🇧 English",
    "fr": "🇫🇷 French",
    "de": "🇩🇪 German",
    "es": "🇪🇸 Spanish",
    "it": "🇮🇹 Italian",
    "pt": "🇵🇹 Portuguese",
    "pt-PT": "🇵🇹 Portuguese (Portugal)",
    "pt-BR": "🇧🇷 Portuguese (Brazil)",
    "ar": "🇸🇦 Arabic",
    "tr": "🇹🇷 Turkish",
    "ko": "🇰🇷 Korean",
    "ja": "🇯🇵 Japanese",
    "zh-CN": "🇨🇳 Chinese (Simplified)",
    "zh-TW": "🇹🇼 Chinese (Traditional)",
    "zh-CA": "🇭🇰 Chinese (Cantonese)",
    "ru": "🇷🇺 Russian",
    "pl": "🇵🇱 Polish",
    "nl": "🇳🇱 Dutch",
    "ro": "🇷🇴 Romanian",
    "vi": "🇻🇳 Vietnamese",
    "bn": "🇧🇩 Bengali",
    "el": "🇬🇷 Greek",
    "sr": "🇷🇸 Serbian",
    "sk": "🇸🇰 Slovak",
    "fa": "🇮🇷 Persian",
    "hi": "🇮🇳 Hindi",
    "sv": "🇸🇪 Swedish",
    "da": "🇩🇰 Danish",
    "fi": "🇫🇮 Finnish",
    "no": "🇳🇴 Norwegian",
    "cs": "🇨🇿 Czech",
    "hu": "🇭🇺 Hungarian",
}


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

    # Create inline buttons for languages (2 per row)
    keyboard = []

for i in range(0, len(subtitles[:20]), 2):
    row = []

    for j in range(2):
        if i + j < len(subtitles[:20]):

            sub = subtitles[i + j]

            language_name = LANGUAGE_NAMES.get(
                sub["language"],
                sub["language"]
            )

            row.append(
                InlineKeyboardButton(
                    language_name,
                    callback_data=f'download_{sub["file_id"]}'
                )
            )

    keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_lang = query.data.replace("download_", "")
    language_name = LANGUAGE_NAMES.get(selected_lang, selected_lang)

    await query.edit_message_text(
        text=f"✅ You selected: {language_name}\n\n"
        f"🔗 Downloading subtitles...\n"
        f"(Subtitle download functionality coming soon!)"
    )


def main():
    check_config()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, search)
    )

    print("Bot started...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
