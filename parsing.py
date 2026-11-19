import re
from dataclasses import dataclass

TIPE_VALID = ("masuk", "keluar")
MAKS_JUMLAH = 1_000_000_000_000
MAKS_KETERANGAN = 200

# Angka polos (15000) atau berpemisah ribuan (15.000 / 15,000).
POLA_JUMLAH = re.compile(r"^(\d+|\d{1,3}([.,]\d{3})+)$")

CONTOH = "Contoh: keluar 15000 makan siang"


class ParseError(ValueError):
    """Pesan tidak sesuai format. Isi pesannya aman ditampilkan ke pengguna."""


@dataclass(frozen=True)
class Transaksi:
    tipe: str
    jumlah: int
    keterangan: str


def parse_jumlah(teks: str) -> int:
    if not POLA_JUMLAH.match(teks):
        raise ParseError(f"'{teks}' bukan jumlah yang valid. Pakai angka saja, misal 15000 atau 15.000.")
    jumlah = int(teks.replace(".", "").replace(",", ""))
    if jumlah <= 0:
        raise ParseError("Jumlah harus lebih dari 0.")
    if jumlah > MAKS_JUMLAH:
        raise ParseError("Jumlah terlalu besar.")
    return jumlah


def parse_transaksi(teks: str) -> Transaksi:
    """Ubah 'keluar 15000 makan siang' menjadi Transaksi, atau raise ParseError."""
    bagian = teks.strip().split(maxsplit=2)
    if len(bagian) < 2:
        raise ParseError(f"Formatnya: masuk|keluar <jumlah> <keterangan>. {CONTOH}")

    tipe = bagian[0].lower()
    if tipe not in TIPE_VALID:
        raise ParseError(f"Awali pesan dengan 'masuk' atau 'keluar'. {CONTOH}")

    jumlah = parse_jumlah(bagian[1])
    keterangan = bagian[2].strip() if len(bagian) == 3 else ""
    if len(keterangan) > MAKS_KETERANGAN:
        raise ParseError(f"Keterangan maksimal {MAKS_KETERANGAN} karakter.")

    return Transaksi(tipe=tipe, jumlah=jumlah, keterangan=keterangan)
