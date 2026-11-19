# Bot Telegram Pencatat Keuangan Harian

Bot Telegram untuk mencatat pemasukan dan pengeluaran lewat chat biasa, lalu melihat rekap harian, mingguan, dan saldo.

## Masalah yang diselesaikan

Mencatat uang masuk dan keluar di aplikasi khusus sering terasa merepotkan, jadi akhirnya tidak dilakukan. Bot ini memindahkan pencatatan ke tempat yang sudah dibuka setiap hari: chat Telegram. Cukup ketik satu baris.

## Fitur

- Catat transaksi dengan format natural:
  - `keluar 15000 makan siang`
  - `masuk 50000 uang saku`
  - Jumlah boleh memakai pemisah ribuan (`15.000`).
- `/hari_ini` dan `/minggu_ini` menampilkan pemasukan, pengeluaran, dan selisih (minggu dihitung Senin sampai Minggu).
- `/saldo` menampilkan total pemasukan dikurangi pengeluaran, seluruh waktu.
- `/kategori` menampilkan pengeluaran terbesar per keterangan.
- `/hapus_terakhir` menghapus transaksi terakhir kalau salah ketik.
- Pesan yang salah format dibalas dengan petunjuk dan contoh, bukan error.
- Data tiap pengguna terpisah (berdasarkan `user_id` Telegram).

## Tech stack

Python 3.15, [python-telegram-bot](https://python-telegram-bot.org/) (async), SQLite (`sqlite3` bawaan), python-dotenv, pytest.

## Cara menjalankan

1. Buat bot lewat [@BotFather](https://t.me/BotFather) dengan `/newbot`, lalu salin token.
2. Siapkan environment:

   ```powershell
   git clone <url-repo-ini>
   cd <nama-folder>
   py -3.15 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Salin `.env.example` menjadi `.env`, lalu isi token:

   ```
   BOT_TOKEN=token_dari_botfather
   ```

4. Jalankan:

   ```powershell
   python bot.py
   ```

5. Buka bot di Telegram, kirim `/start`.

## Menjalankan tes

```powershell
python -m pytest
```

Tes mencakup parser pesan, query database (memakai file SQLite sementara), dan perhitungan rentang tanggal serta format rupiah.

## Struktur proyek

```
bot.py        handler Telegram dan entry point
parsing.py    ubah teks pesan menjadi data terstruktur (tanpa dependensi Telegram)
db.py         akses SQLite: tambah, ambil, hapus, total per periode
rekap.py      rentang tanggal dan format teks rekap
tests/        tes pytest
```

Logika (`parsing`, `db`, `rekap`) dipisah dari handler Telegram supaya bisa dites tanpa koneksi internet.

## Keputusan desain

- **Jumlah disimpan sebagai `INTEGER`**, bukan `float`: rupiah tidak punya sen, dan float bisa menghasilkan angka tidak presisi saat dijumlahkan.
- **Semua query memakai placeholder `?`**, sehingga teks dari pengguna tidak bisa menyisipkan SQL.
- **`CHECK` constraint di tabel** menolak tipe atau jumlah yang tidak valid walau parser salah.
- **Token hanya di `.env`** (ada di `.gitignore`). Logger `httpx` diturunkan ke level WARNING karena URL request Telegram memuat token.

## Keterbatasan

- Waktu transaksi memakai jam lokal mesin yang menjalankan bot.
- Akses SQLite bersifat sinkron di dalam handler async. Ini cukup untuk bot pribadi, tetapi bukan untuk trafik tinggi.
- Bot memakai polling, jadi harus terus berjalan di satu mesin.

## Tampilan percakapan

<!-- TODO: ganti dengan screenshot percakapan asli -->
![Contoh percakapan dengan bot](docs/screenshot.png)
