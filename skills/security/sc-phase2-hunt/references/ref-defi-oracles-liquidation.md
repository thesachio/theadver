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

### [POV-03] Multi-Identity Self-Liquidation & Bad-Debt Socialization Arbitrage

- **Kondisi Prasyarat (State Condition):**
  Protokol memiliki mekanisme penalti, likuidasi, slashing, atau sosialisasi utang macet (*bad debt*) ketika nilai kewajiban sebuah akun melampaui nilai jaminannya.

- **Kacamata Attacker (Gejala di Kode):**
  Saat akun jatuh ke kondisi rugi/insolven (`debt > collateral`), fungsi likuidasi tetap memberikan bonus likuidator penuh dari kolam umum, atau menghapus sisa utang (*bad debt*) tanpa menyita seluruh jaminan yang tersisa di sub-akun lain, atau mengizinkan peminjam meminjam/menarik agunan tepat di batas harga yang dimanipulasi sesaat.

- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang menyiapkan **dua identitas/akun/objek/kapabilitas yang ia kendalikan** — identitas pertama sebagai Kambing Hitam (posisi yang akan gagal bayar), identitas kedua sebagai Pemburu Bonus / Posisi Lawan. Tidak harus dua EOA: bisa dua akun pada pool yang sama, dua posisi, dua objek, atau dua capability.
  2. **[Pemicu Asimetri]** Identitas pertama membuka posisi maksimum pada batas risiko ekstrem hingga menyisakan utang macet atau memicu syarat likuidasi.
  3. **[Ekstraksi Nilai]** Identitas kedua mengeksekusi likuidasi/klaim terhadap identitas pertama — secara atomik atau dalam jendela eksekusi yang sama — untuk mengantongi bonus likuidasi atau menyedot cadangan asuransi protokol yang nilainya lebih besar daripada modal yang sengaja dikorbankan.

- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor selalu mengasumsikan Borrower (peminjam) dan Liquidator (pelikuidasi) adalah dua pihak yang saling bermusuhan, sehingga auditor tidak pernah menghitung bahwa jika keduanya dikendalikan satu penyerang, kerugian di satu identitas bisa menghasilkan keuntungan lebih besar di identitas lain atas beban kolam protokol.

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika `total Collateral_Tersita >= Bonus_Liquidator + Utang_Dihapus` pada setiap kondisi batas (sehingga keuntungan identitas kedua selalu lebih kecil dari kerugian identitas pertama — *Negative-EV*).

---

### [POV-06] Valuation-Source vs Execution-Venue Asymmetry (Oracle-to-Market Seam)

- **Kondisi Prasyarat (State Condition):**
  Kontrak menggunakan Sumber A (seperti Oracle eksternal atau rata-rata harga waktu/TWAP) untuk memvalidasi kesehatan posisi atau nilai aset, tetapi mengeksekusi penukaran aset, pelepasan jaminan, atau penyeimbangan portofolio secara langsung di Sumber B (kolam likuiditas spot atau pasar internal).

- **Kacamata Attacker (Gejala di Kode):**
  Fungsi yang memicu eksekusi ke Sumber B dapat dipanggil oleh publik (atau dipicu secara tidak langsung oleh pengguna), sedangkan batas penerimaan minimumnya (*minimum output / slippage guard*) bernilai 0, diambil dari parameter pemanggil, atau dihitung dari cadangan spot Sumber B saat transaksi berlangsung (bukan diturunkan secara ketat dari harga acuan Sumber A).

- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang menyiapkan modal atau *flashloan* pada pasangan aset di kolam likuiditas Sumber B.
  2. **[Pemicu Asimetri]** Dalam satu transaksi atomik, penyerang memindahkan rasio likuiditas di Sumber B secara ekstrem (sementara harga di Sumber A tetap statis), lalu memanggil fungsi protokol yang mengeksekusi transaksi ke Sumber B.
  3. **[Ekstraksi Nilai]** Kontrak protokol mengeksekusi penukaran/pelepasan aset pada harga Sumber B yang sedang terdistorsi, lalu penyerang memulihkan posisi Sumber B untuk mengekstrak selisih nilai dari protokol.

- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor berhenti memeriksa risiko manipulasi harga begitu melihat kontrak membaca harga acuan dari Oracle yang tahan manipulasi satu blok (Sumber A), tanpa memeriksa ke mana eksekusi riil dikirim (Sumber B) dan bagaimana batas *slippage* pada eksekusi tersebut dihitung.

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika fungsi pemicu dikunci hanya untuk operator tepercaya melalui jalur transaksi privat, ATAU jika batas hasil minimum pada Sumber B dihitung langsung dari harga Sumber A dengan deviasi maksimum yang lebih kecil daripada dua kali biaya pertukaran (*2x swap fee*) di Sumber B.

---

<!-- Sisipkan [POV-07], [POV-08], dst. di BAWAH baris ini, urut menaik -->
