from datetime import datetime, timedelta


def _awal_hari(waktu: datetime) -> datetime:
    return waktu.replace(hour=0, minute=0, second=0, microsecond=0)


def rentang_hari_ini(sekarang: datetime | None = None) -> tuple[str, str]:
    """Rentang [00:00 hari ini, 00:00 besok) sebagai string ISO."""
    awal = _awal_hari(sekarang or datetime.now())
    return awal.isoformat(timespec="seconds"), (awal + timedelta(days=1)).isoformat(timespec="seconds")


def rentang_minggu_ini(sekarang: datetime | None = None) -> tuple[str, str]:
    """Rentang [Senin 00:00, Senin depan 00:00). weekday(): Senin = 0."""
    hari_ini = _awal_hari(sekarang or datetime.now())
    senin = hari_ini - timedelta(days=hari_ini.weekday())
    return senin.isoformat(timespec="seconds"), (senin + timedelta(days=7)).isoformat(timespec="seconds")


def format_rupiah(angka: int) -> str:
    """15000 -> 'Rp15.000'; -5000 -> '-Rp5.000'."""
    teks = f"Rp{abs(angka):,}".replace(",", ".")
    return f"-{teks}" if angka < 0 else teks


def format_rekap(judul: str, masuk: int, keluar: int) -> str:
    return (
        f"{judul}\n"
        f"Pemasukan : {format_rupiah(masuk)}\n"
        f"Pengeluaran: {format_rupiah(keluar)}\n"
        f"Selisih   : {format_rupiah(masuk - keluar)}"
    )


def format_kategori(data: list[tuple[str, int]]) -> str:
    if not data:
        return "Belum ada pengeluaran yang tercatat."
    baris = [f"{i}. {nama or '(tanpa keterangan)'}: {format_rupiah(total)}" for i, (nama, total) in enumerate(data, 1)]
    return "Pengeluaran terbesar per keterangan:\n" + "\n".join(baris)
