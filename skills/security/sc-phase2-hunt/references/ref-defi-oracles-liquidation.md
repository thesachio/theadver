# Checklist Universal: Oracle Harga, AMM/DEX, Akrual Waktu, & Mekanika Likuidasi

Periksa setiap pembacaan harga, perhitungan bunga, dan penyitaan agunan terhadap 6 vektor berikut:

1. **Manipulasi Harga Spot dalam Satu Transaksi (Flash Loan Spot Manipulation):**
   - Apakah protokol menghitung nilai agunan, harga aset, atau rasio pencetakan menggunakan saldo/cadangan instan dari pool AMM saat ini (`getReserves`, `slot0`, atau rasio saldo pool) tanpa rata-rata waktu (TWAP)?
   - Semua harga *spot* on-chain dapat dimanipulasi secara ekstrem dalam satu transaksi atomik menggunakan *Flash Loan*.

2. **Validasi Oracle Eksternal yang Cacat (Chainlink / Pyth / TWAP):**
   - Jika membaca data Oracle (seperti `latestRoundData` atau Pyth price feed), pastikan kode memvalidasi:
     *(a)* Harga `> 0` dan interval kepercayaan (*confidence interval* pada Pyth) tidak terlalu lebar.
     *(b)* Kesegaran data: `updatedAt >= currentTime - MAX_STALENESS` (pastikan nilai *heartbeat* sesuai dengan feed asetnya).
     *(c)* Jika di jaringan Layer-2 EVM: apakah memeriksa status **L2 Sequencer Uptime Feed** beserta masa tenggang (*grace period*) setelah sequencer pulih?

3. **Ketiadaan Slippage & Deadline yang Efektif (MEV Sandwich Attack):**
   - Jika kontrak mengeksekusi pertukaran (*swap*) atau menambah/menarik likuiditas di DEX secara otomatis:
   - Apakah batas minimum penerima (`amountOutMin`) disetel ke `0` atau dihitung secara on-chain dari harga spot yang sudah dimanipulasi?
   - Apakah batas waktu (`deadline`) disetel ke `block.timestamp` (yang berarti transaksi dapat ditahan di mempool tanpa kedaluwarsa)?

4. **Perubahan State Sebelum Akrual Waktu (Missing Interest / Reward Accrual):**
   - Pada sistem pinjaman, staking, atau pembagian hasil: apakah indeks akrual waktu (`accrueInterest` / `updatePool`) WAJIB dijalankan paling awal sebelum saldo pengguna atau total pasokan diubah?
   - Jika ada satu jalur fungsi (misal fungsi transfer internal, klaim, atau penarikan darurat) yang mengubah saldo tanpa memperbarui indeks waktu terlebih dahulu, pengguna dapat mencuri porsi hasil masa lalu atau menghindari beban bunga.

5. **Kegagalan Mekanika Likuidasi & Penanganan Bad Debt:**
   - **Insolvency / Bad Debt:** Jika nilai agunan jatuh di bawah nilai utang, apakah likuidator masih memiliki insentif ekonomi untuk melikuidasi, dan apakah sisa utang tanpa agunan (*bad debt*) dibersihkan/disosialisasikan agar tidak merusak akuntansi protokol?
   - **Posisi Debu (Dust Positions):** Apakah ada batas pinjaman minimum agar biaya gas likuidasi tidak lebih mahal daripada nilai agunan yang disita?
   - **Self-Liquidation & Pause Freeze:** Apakah peminjam bisa melikuidasi dirinya sendiri dengan keuntungan tidak sah? Apakah status `paused` memblokir fungsi pelunasan (`repay`) atau likuidasi sehingga memicu gagal bayar massal?

---

## Katalog Generalized Attacker POV & Auditor Blindspots (Diisi Bertahap)

Entri di bawah ini adalah pola eksploitasi nyata yang telah digeneralisasi. Pakai pada Tahap B Fase 2: cocokkan **Kondisi Prasyarat** dan **Gejala di Kode** dengan fungsi yang sedang dibedah.
Indeks seluruh POV lintas file: `references/ref-attacker-pov.md`.

### [POV-03] 2-Wallet Self-Liquidation & Bad-Debt Socialization Arbitrage

- **Kondisi Prasyarat (State Condition):**
  Protokol memiliki mekanisme penalti, likuidasi, slashing, atau sosialisasi utang macet (*bad debt*) ketika nilai kewajiban sebuah akun melampaui nilai jaminannya.

- **Kacamata Attacker (Gejala di Kode):**
  Saat akun jatuh ke kondisi rugi/insolven (`debt > collateral`), fungsi likuidasi tetap memberikan bonus likuidator penuh dari kolam umum, atau menghapus sisa utang (*bad debt*) tanpa menyita seluruh jaminan yang tersisa di sub-akun lain, atau mengizinkan peminjam meminjam/menarik agunan tepat di batas harga yang dimanipulasi sesaat.

- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang mendanai dua dompet independen: Attacker_A (Kambing Hitam) dan Attacker_B (Pemburu Bonus / Posisi Lawan).
  2. **[Pemicu Asimetri]** Attacker_A membuka posisi maksimum pada batas risiko ekstrem hingga menyisakan utang macet atau memicu syarat likuidasi.
  3. **[Ekstraksi Nilai]** Dalam transaksi yang sama, Attacker_B mengeksekusi likuidasi/klaim terhadap Attacker_A untuk mengantongi bonus likuidasi atau menyedot cadangan asuransi protokol yang nilainya lebih besar daripada modal Attacker_A yang sengaja dikorbankan.

- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor selalu mengasumsikan Borrower (peminjam) dan Liquidator (pelikuidasi) adalah dua pihak yang saling bermusuhan, sehingga auditor tidak pernah menghitung bahwa jika Borrower dan Liquidator adalah orang yang sama, kerugian di kantong kiri bisa menghasilkan keuntungan lebih besar di kantong kanan atas beban kolam protokol.

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika `total Collateral_Tersita >= Bonus_Liquidator + Utang_Dihapus` pada setiap kondisi batas (sehingga `Profit_Attacker_B` selalu lebih kecil dari `Kerugian_Attacker_A` — *Negative-EV*).

---

<!-- Sisipkan [POV-04], [POV-05], dst. di BAWAH baris ini, urut menaik -->
