import sqlite3

import pytest

import db


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


def test_total_periode_memfilter_rentang_dan_user(db_path):
    db.tambah_transaksi(1, "masuk", 50000, "saku", db_path, created_at="2026-11-18T10:00:00")
    db.tambah_transaksi(1, "keluar", 15000, "makan", db_path, created_at="2026-11-18T12:00:00")
    db.tambah_transaksi(1, "keluar", 7000, "kemarin", db_path, created_at="2026-11-17T23:59:59")
    db.tambah_transaksi(2, "keluar", 9999, "orang lain", db_path, created_at="2026-11-18T09:00:00")

    masuk, keluar = db.total_periode(1, "2026-11-18T00:00:00", "2026-11-19T00:00:00", db_path)

    assert (masuk, keluar) == (50000, 15000)


def test_total_periode_batas_akhir_eksklusif(db_path):
    db.tambah_transaksi(1, "keluar", 1000, "x", db_path, created_at="2026-11-19T00:00:00")

    assert db.total_periode(1, "2026-11-18T00:00:00", "2026-11-19T00:00:00", db_path) == (0, 0)


def test_saldo(db_path):
    db.tambah_transaksi(1, "masuk", 50000, "saku", db_path)
    db.tambah_transaksi(1, "keluar", 15000, "makan", db_path)

    assert db.saldo(1, db_path) == 35000
    assert db.saldo(404, db_path) == 0


def test_total_per_keterangan_gabung_huruf_besar_kecil(db_path):
    db.tambah_transaksi(1, "keluar", 15000, "Makan", db_path)
    db.tambah_transaksi(1, "keluar", 10000, "makan", db_path)
    db.tambah_transaksi(1, "keluar", 30000, "bensin", db_path)
    db.tambah_transaksi(1, "masuk", 99999, "saku", db_path)  # bukan pengeluaran

    assert db.total_per_keterangan(1, db_path=db_path) == [("bensin", 30000), ("makan", 25000)]
