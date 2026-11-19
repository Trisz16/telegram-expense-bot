import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db  # noqa: E402


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    db.init_db(path)
    return path


def test_tambah_dan_ambil(db_path):
    db.tambah_transaksi(1, "keluar", 15000, "makan siang", db_path)
    db.tambah_transaksi(1, "masuk", 50000, "uang saku", db_path)

    rows = db.ambil_transaksi(1, db_path=db_path)

    assert [r["keterangan"] for r in rows] == ["uang saku", "makan siang"]  # terbaru dulu
    assert rows[1]["jumlah"] == 15000


def test_data_antar_user_terpisah(db_path):
    db.tambah_transaksi(1, "keluar", 1000, "a", db_path)
    db.tambah_transaksi(2, "keluar", 2000, "b", db_path)

    assert len(db.ambil_transaksi(1, db_path=db_path)) == 1
    assert db.ambil_transaksi(2, db_path=db_path)[0]["keterangan"] == "b"


def test_hapus_terakhir_hanya_milik_user_sendiri(db_path):
    db.tambah_transaksi(1, "keluar", 1000, "lama", db_path)
    db.tambah_transaksi(1, "keluar", 2000, "baru", db_path)
    db.tambah_transaksi(2, "keluar", 3000, "orang lain", db_path)

    assert db.hapus_transaksi_terakhir(1, db_path) is True

    assert [r["keterangan"] for r in db.ambil_transaksi(1, db_path=db_path)] == ["lama"]
    assert len(db.ambil_transaksi(2, db_path=db_path)) == 1


def test_hapus_saat_kosong_mengembalikan_false(db_path):
    assert db.hapus_transaksi_terakhir(99, db_path) is False


def test_tipe_atau_jumlah_tidak_valid_ditolak(db_path):
    with pytest.raises(sqlite3.IntegrityError):
        db.tambah_transaksi(1, "transfer", 1000, "", db_path)
    with pytest.raises(sqlite3.IntegrityError):
        db.tambah_transaksi(1, "keluar", 0, "", db_path)
