from datetime import datetime

import pytest

import rekap


def test_rentang_hari_ini():
    mulai, sampai = rekap.rentang_hari_ini(datetime(2026, 11, 19, 15, 30))
    assert (mulai, sampai) == ("2026-11-19T00:00:00", "2026-11-20T00:00:00")


def test_rentang_minggu_ini_dimulai_senin():
    # 19 Nov 2026 hari Kamis -> Senin 16 Nov
    mulai, sampai = rekap.rentang_minggu_ini(datetime(2026, 11, 19, 15, 30))
    assert (mulai, sampai) == ("2026-11-16T00:00:00", "2026-11-23T00:00:00")


def test_rentang_minggu_ini_saat_hari_senin_dan_minggu():
    assert rekap.rentang_minggu_ini(datetime(2026, 11, 16, 0, 0))[0] == "2026-11-16T00:00:00"
    assert rekap.rentang_minggu_ini(datetime(2026, 11, 22, 23, 59))[0] == "2026-11-16T00:00:00"


def test_rentang_hari_ini_lintas_bulan():
    assert rekap.rentang_hari_ini(datetime(2026, 11, 30, 8, 0))[1] == "2026-12-01T00:00:00"


@pytest.mark.parametrize(
    "angka, hasil",
    [(0, "Rp0"), (500, "Rp500"), (15000, "Rp15.000"), (1500000, "Rp1.500.000"), (-5000, "-Rp5.000")],
)
def test_format_rupiah(angka, hasil):
    assert rekap.format_rupiah(angka) == hasil


def test_format_rekap_menghitung_selisih():
    teks = rekap.format_rekap("Hari ini", 50000, 15000)
    assert "Rp35.000" in teks and "Hari ini" in teks


def test_format_kategori_kosong_dan_tanpa_keterangan():
    assert "Belum ada" in rekap.format_kategori([])
    assert "(tanpa keterangan)" in rekap.format_kategori([("", 1000)])
