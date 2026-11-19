import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import db
from parsing import ParseError, parse_transaksi

load_dotenv()

HELP_TEXT = (
    "Cara mencatat (kirim sebagai pesan biasa):\n"
    "keluar 15000 makan siang\n"
    "masuk 50000 uang saku\n\n"
    "Perintah:\n"
    "/start - sapaan\n"
    "/help - bantuan ini\n"
    "/hapus_terakhir - hapus transaksi terakhir"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Saya bot pencatat pemasukan dan pengeluaran harianmu.\n"
        "Ketik /help untuk melihat cara pakai."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def catat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        transaksi = parse_transaksi(update.message.text)
    except ParseError as e:
        await update.message.reply_text(str(e))
        return

    db.tambah_transaksi(
        update.effective_user.id, transaksi.tipe, transaksi.jumlah, transaksi.keterangan
    )
    await update.message.reply_text(
        f"Tercatat: {transaksi.tipe} {transaksi.jumlah} {transaksi.keterangan}".rstrip()
    )


async def hapus_terakhir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if db.hapus_transaksi_terakhir(update.effective_user.id):
        await update.message.reply_text("Transaksi terakhir dihapus.")
    else:
        await update.message.reply_text("Belum ada transaksi yang bisa dihapus.")


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN belum diisi di .env")
    db.init_db()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hapus_terakhir", hapus_terakhir))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catat))
    app.run_polling()


if __name__ == "__main__":
    main()
