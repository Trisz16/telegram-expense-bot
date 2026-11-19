import pytest

from parsing import ParseError, Transaksi, parse_jumlah, parse_transaksi


def test_keluar_normal():
    assert parse_transaksi("keluar 15000 makan siang") == Transaksi("keluar", 15000, "makan siang")


def test_masuk_normal():
    assert parse_transaksi("masuk 50000 uang saku") == Transaksi("masuk", 50000, "uang saku")


def test_huruf_besar_dan_spasi_berlebih():
    assert parse_transaksi("  KELUAR   20000   kopi  ") == Transaksi("keluar", 20000, "kopi")


def test_keterangan_boleh_kosong():
    assert parse_transaksi("masuk 1000") == Transaksi("masuk", 1000, "")


@pytest.mark.parametrize("teks", ["15.000", "15,000", "1.500.000"])
def test_jumlah_dengan_pemisah_ribuan(teks):
    assert parse_jumlah(teks) == int(teks.replace(".", "").replace(",", ""))


@pytest.mark.parametrize(
    "teks",
    [
        "",
        "   ",
        "keluar",
        "halo semua",
        "transfer 1000 teman",
        "keluar abc makan",
        "keluar -5000 makan",
        "keluar 0 makan",
        "keluar 15.5 makan",
        "keluar 15.00 makan",
        "keluar 99999999999999 makan",
        "keluar 1000 " + "x" * 201,
    ],
)
def test_input_salah_memunculkan_parse_error(teks):
    with pytest.raises(ParseError):
        parse_transaksi(teks)


def test_pesan_error_ramah_menyertakan_contoh():
    with pytest.raises(ParseError, match="Contoh"):
        parse_transaksi("halo")
