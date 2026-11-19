import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

HELP_TEXT = (
    "Cara pakai:\n"
    "keluar 15000 makan siang\n"
    "masuk 50000 uang saku\n\n"
    "Perintah:\n"
    "/start - sapaan\n"
    "/help - bantuan ini"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Saya bot pencatat pemasukan dan pengeluaran harianmu.\n"
        "Ketik /help untuk melihat cara pakai."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN belum diisi di .env")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()


if __name__ == "__main__":
    main()
