import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import db
import rekap
from parsing import ParseError, parse_transaksi

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
# httpx mencatat URL request di level INFO, dan URL Telegram memuat token bot.
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

HELP_TEXT = (
    "Cara mencatat (kirim sebagai pesan biasa):\n"
    "keluar 15000 makan siang\n"
    "masuk 50000 uang saku\n\n"
    "Perintah:\n"
    "/start - sapaan\n"
    "/help - bantuan ini\n"
    "/hari_ini - rekap hari ini\n"
    "/minggu_ini - rekap minggu ini (Senin-Minggu)\n"
    "/saldo - total saldo semua waktu\n"
    "/kategori - pengeluaran terbesar per keterangan\n"
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


async def _kirim_rekap(update: Update, judul: str, rentang: tuple[str, str]) -> None:
    masuk, keluar = db.total_periode(update.effective_user.id, *rentang)
    await update.message.reply_text(rekap.format_rekap(judul, masuk, keluar))


async def hari_ini(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _kirim_rekap(update, "Rekap hari ini", rekap.rentang_hari_ini())


async def minggu_ini(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _kirim_rekap(update, "Rekap minggu ini", rekap.rentang_minggu_ini())


async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Saldo: {rekap.format_rupiah(db.saldo(update.effective_user.id))}"
    )


async def kategori(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = db.total_per_keterangan(update.effective_user.id)
    await update.message.reply_text(rekap.format_kategori(data))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tangkap error yang lolos dari handler: catat ke log, beri pesan ramah."""
    logger.error("Error saat memproses update", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Maaf, terjadi kesalahan di sisi bot. Coba lagi sebentar lagi."
        )


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("BOT_TOKEN belum diisi di .env")
    db.init_db()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hapus_terakhir", hapus_terakhir))
    app.add_handler(CommandHandler("hari_ini", hari_ini))
    app.add_handler(CommandHandler("minggu_ini", minggu_ini))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("kategori", kategori))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catat))
    app.add_error_handler(error_handler)
    logger.info("Bot berjalan. Tekan Ctrl+C untuk berhenti.")
    app.run_polling()


if __name__ == "__main__":
    main()
