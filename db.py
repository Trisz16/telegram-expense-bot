import sqlite3
from contextlib import closing
from datetime import datetime

DB_PATH = "transaksi.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS transaksi (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    tipe       TEXT    NOT NULL CHECK (tipe IN ('masuk', 'keluar')),
    jumlah     INTEGER NOT NULL CHECK (jumlah > 0),
    keterangan TEXT    NOT NULL DEFAULT '',
    created_at TEXT    NOT NULL
)
"""


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # akses kolom lewat nama: row["jumlah"]
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(SCHEMA)


def tambah_transaksi(
    user_id: int,
    tipe: str,
    jumlah: int,
    keterangan: str = "",
    db_path: str = DB_PATH,
    created_at: str | None = None,
) -> int:
    """Simpan transaksi dan kembalikan id barisnya.

    created_at (format ISO) hanya untuk pengujian; default: waktu sekarang.
    """
    if created_at is None:
        created_at = datetime.now().isoformat(timespec="seconds")
    with closing(_connect(db_path)) as conn, conn:
        cursor = conn.execute(
            "INSERT INTO transaksi (user_id, tipe, jumlah, keterangan, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, tipe, jumlah, keterangan, created_at),
        )
        return cursor.lastrowid


def ambil_transaksi(
    user_id: int, limit: int = 10, db_path: str = DB_PATH
) -> list[sqlite3.Row]:
    """Ambil transaksi milik user_id, terbaru dulu."""
    with closing(_connect(db_path)) as conn:
        return conn.execute(
            "SELECT * FROM transaksi WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()


def total_periode(
    user_id: int,
    mulai: str = "0000",
    sampai: str = "9999",
    db_path: str = DB_PATH,
) -> tuple[int, int]:
    """Total (masuk, keluar) untuk created_at di rentang [mulai, sampai).

    Tanpa argumen rentang = seluruh waktu. String ISO bisa dibandingkan
    langsung sebagai teks, jadi tidak perlu fungsi tanggal SQLite.
    """
    with closing(_connect(db_path)) as conn:
        row = conn.execute(
            "SELECT "
            "COALESCE(SUM(CASE WHEN tipe = 'masuk'  THEN jumlah END), 0) AS masuk, "
            "COALESCE(SUM(CASE WHEN tipe = 'keluar' THEN jumlah END), 0) AS keluar "
            "FROM transaksi WHERE user_id = ? AND created_at >= ? AND created_at < ?",
            (user_id, mulai, sampai),
        ).fetchone()
    return row["masuk"], row["keluar"]


def saldo(user_id: int, db_path: str = DB_PATH) -> int:
    masuk, keluar = total_periode(user_id, db_path=db_path)
    return masuk - keluar


def total_per_keterangan(
    user_id: int, tipe: str = "keluar", limit: int = 10, db_path: str = DB_PATH
) -> list[tuple[str, int]]:
    """Total per keterangan (huruf kecil), terbesar dulu. Dasar fitur /kategori."""
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT LOWER(keterangan) AS kategori, SUM(jumlah) AS total "
            "FROM transaksi WHERE user_id = ? AND tipe = ? "
            "GROUP BY LOWER(keterangan) ORDER BY total DESC, kategori LIMIT ?",
            (user_id, tipe, limit),
        ).fetchall()
    return [(r["kategori"], r["total"]) for r in rows]


def hapus_transaksi_terakhir(user_id: int, db_path: str = DB_PATH) -> bool:
    """Hapus transaksi terbaru milik user_id. True jika ada yang terhapus."""
    with closing(_connect(db_path)) as conn, conn:
        cursor = conn.execute(
            "DELETE FROM transaksi WHERE id = "
            "(SELECT MAX(id) FROM transaksi WHERE user_id = ?)",
            (user_id,),
        )
        return cursor.rowcount > 0
