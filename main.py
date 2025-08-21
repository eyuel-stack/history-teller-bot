from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters,
    MessageHandler,
    CallbackQueryHandler,
)
import logging
import datetime
from history_fetcher import HistoryFetcher
from random import randint
import re


fetcher = HistoryFetcher()


logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)


async def get_msg_type(update: Update):
    if update.message:
        return update.message
    if update.callback_query and update.callback_query.message:
        return update.callback_query.message
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await get_msg_type(update)
    if not msg:
        return

    btns = [
        [InlineKeyboardButton("Today In History", callback_data="today")],
        [InlineKeyboardButton("Random History", callback_data="random")],
    ]

    username = update.effective_user.first_name
    text = f"Hi {username}! I'm AbyssiniaTimes.\nI can tell history\n use /help command to see all commands"

    await msg.reply_text(text, reply_markup=InlineKeyboardMarkup(btns))


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await get_msg_type(update)
    if not msg:
        return

    text = (
        "Commands:\n"
        "/start to see buttons\n"
        "/help to get this text\n"
        "/today history for today\n"
        "/random pick random history\n"
        "/date MM-DD to get specific date history (e.g: /date 03-01)\n"
    )

    await msg.reply_text(text)


async def err_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await get_msg_type(update)
    if not msg:
        return

    text = "Invalid command! please use /help"

    await msg.reply_text(text)


def format_summary(summary: dict):
    parts = []
    for category, items in summary.items():
        emoji = "🎯" if category == "events" else "🎂" if category == "births" else "🪦"
        block = f"{emoji} {category.capitalize()}:\n" + "\n".join(items)

        parts.append(block)

    return "\n\n".join(parts)


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await get_msg_type(update)
    if not msg:
        return

    today = datetime.datetime.today()
    month = today.month
    day = today.day

    loading = await msg.reply_text("⏳ Wait a moment....")
    summery = fetcher.summary(month, day)
    title = f"====== History for {month:02d}-{day:02d} ======\n\n"
    await loading.edit_text(title + format_summary(summery))


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await get_msg_type(update)
    if not msg:
        return
    loading = await msg.reply_text("⏳ Wait a moment....")
    month = randint(1, 12)
    day = randint(1, 30)
    summary = fetcher.summary(month, day)
    title = f"====== History for {month:02d}-{day:02d} ======\n\n"
    await loading.edit_text(title + format_summary(summary))


async def date_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await get_msg_type(update)
    if not msg:
        return

    text = msg.text.strip()
    if text.startswith("/date"):
        parts = text.split(maxsplit=1)
        text = parts[1] if len(parts) > 1 else ""
    m = re.match(r"^\s*(\d{1,2})[/-](\d{1,2})\s*$", text)
    if not m:
        await msg.reply_text("Invalid date format use like this /date 03-01 or 3/1")
        return

    month, day = int(m.group(1)), int(m.group(2))
    if not (1 <= month <= 12 and 1 <= day <= 31):
        await msg.reply_text("Invalid Month or Day !")
        return

    loading = await msg.reply_text("⏳ Wait a moment...")
    summary = fetcher.summary(month, day)
    title = f"====== History for {month:02d}-{day:02d} ======\n\n"
    await loading.reply_text(title + format_summary(summary))


async def button_handller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q:
        return
    await q.answer()
    if q.data == "today":
        await today(update, context)
    elif q.data == "random":
        await random(update, context)


def main():
    TOKEN = "Your_Token_Here"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("random", random))
    app.add_handler(CommandHandler("date", date_history))
    app.add_handler(CallbackQueryHandler(button_handller))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, err_msg))

    app.run_polling()


if __name__ == "__main__":
    main()
