# Draf postingan LinkedIn

Minggu ini saya membuat bot Telegram untuk mencatat pemasukan dan pengeluaran harian, hanya dengan mengetik satu baris di chat, misalnya "keluar 15000 makan siang".

Fitur utamanya: pencatatan lewat chat, rekap harian dan mingguan, saldo, pengeluaran terbesar per keterangan, dan hapus transaksi terakhir.

Yang saya pelajari:

- Memisahkan logika dari framework. Parser pesan, query database, dan format rekap berdiri sendiri, jadi bisa dites dengan pytest tanpa koneksi ke Telegram.
- Keamanan dasar. Semua query SQL memakai placeholder, token hanya ada di .env, dan saya baru sadar log HTTP bisa membocorkan token lewat URL, jadi level log-nya saya turunkan.
- Hal kecil yang menentukan akurasi. Jumlah uang disimpan sebagai integer, bukan float, dan rentang "minggu ini" dihitung dari hari Senin dengan batas akhir eksklusif supaya transaksi tengah malam tidak dihitung dua kali.

Stack: Python, python-telegram-bot (async), SQLite, pytest.

Kode lengkap dan cara menjalankannya ada di sini: <GANTI_DENGAN_TAUTAN_REPO>

#Python #Telegram #SQLite #Pytest #BackendDevelopment
