"""Optional Telegram adapter. Run with: python telegram_bot.py"""
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from app.agent import JokerAgent
from app.database import MemoryStore

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("joker.telegram")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("JokerGodAl online. Napisz, czego potrzebujesz.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return
    agent: JokerAgent = context.application.bot_data["agent"]
    conversation_id = f"telegram:{update.effective_user.id}"
    try:
        answer = agent.respond(conversation_id, update.message.text or "")
        await update.message.reply_text(answer[:4000])
    except Exception:
        log.exception("Telegram message failed")
        await update.message.reply_text("Wystąpił błąd. Sprawdź konfigurację Jokera.")


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not token or not api_key:
        raise SystemExit("Ustaw TELEGRAM_BOT_TOKEN i OPENAI_API_KEY.")
    store = MemoryStore(os.getenv("DATABASE_PATH", "./data/joker.db"))
    agent = JokerAgent(store, api_key, os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
    application = Application.builder().token(token).build()
    application.bot_data["agent"] = agent
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()


if __name__ == "__main__":
    main()
