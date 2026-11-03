# Katalog Generalized Attacker POV — Domain DeFi, Oracle, AMM, & Likuidasi (`[POV-DEFI-XX]`)

Berkas ini menyimpan pola eksploitasi on-chain nyata pada mekanisme valuasi oracle, eksekusi DEX/AMM, dan likuidasi/bad-debt.
- **Indeks & Router Gejala:** `references/ref-attacker-pov.md`
- **Checklist Prinsip Dasar:** `references/ref-defi-oracles-liquidation.md`

---

### [POV-DEFI-01] Multi-Identity Self-Liquidation & Bad-Debt Socialization
- **Target Kelas:** `[CLASS-C]` *(Multi-Entity Long Flow: Identitas 1 Borrower + Identitas 2 Liquidator + Pool + Oracle/Insurance)*, `[CLASS-B]`
- **Metode Terkait:** `M-002` (State-Transition Differential), `M-003` (Irrational Multi-Identity Sybil), `M-005` (Guard-Inversion)
- **Gejala Pemicu di Kode (Trigger Symptom):** Protokol memiliki fungsi likuidasi/slashing/penalti yang memberikan bonus likuidator ATAU menghapus sisa utang tak beragunan (*bad debt socialization*) ketika `debt > collateral`.
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
- **Batas Realitas (Kapan Pola Ini GUGUR) & Routing Uji Cepat Fase 3:**
  - *Batas Realitas:* Gugur jika `total Collateral_Tersita >= Bonus_Liquidator + Utang_Dihapus` pada setiap kondisi batas (sehingga keuntungan identitas kedua selalu lebih kecil dari kerugian identitas pertama — *Negative-EV*).
  - *Routing Uji Cepat Fase 3:* Sebelum menulis PoC, hitung pertidaksamaan `total Collateral_Tersita >= Bonus_Liquidator + Utang_Dihapus` memakai angka parameter live (LTV, liquidation threshold, liquidation bonus, reserve factor). Jika ruas kiri selalu menang di seluruh kondisi batas -> lead *Negative-EV*, langsung buang ke `06` tanpa menulis PoC.

---

### [POV-DEFI-02] Valuation Source vs Execution Sink Mismatch
- **Target Kelas:** `[CLASS-C]` *(Multi-Entity Long Flow: Kontrak Protokol + Sumber Valuasi A [Oracle] + Venue Eksekusi B [DEX/AMM Spot])*
- **Metode Terkait:** `M-001` (Backward Sink-to-Source), `M-005` (Guard-Inversion), `M-008` (Caller-Callee Seam)
- **Gejala Pemicu di Kode (Trigger Symptom):** Kontrak membaca harga acuan dari Sumber A (Oracle/TWAP), tetapi mengeksekusi swap/rebalance/likuidasi ke Sumber B (pool spot) dengan `amountOutMin == 0`, parameter pemanggil, atau dihitung dari spot reserve Sumber B.
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
- **Batas Realitas (Kapan Pola Ini GUGUR) & Routing Uji Cepat Fase 3:**
  - *Batas Realitas:* Gugur jika fungsi pemicu dikunci hanya untuk operator tepercaya melalui jalur transaksi privat, ATAU jika batas hasil minimum pada Sumber B dihitung langsung dari harga Sumber A dengan deviasi maksimum yang lebih kecil daripada dua kali biaya pertukaran (*2x swap fee*) di Sumber B.
  - *Routing Uji Cepat Fase 3:* Cek modifier akses fungsi pemicu dan rumus batas output minimum (`amountOutMin`). Jika fungsi hanya bisa dipanggil operator tepercaya ATAU batas output dikunci ke harga Oracle Sumber A dengan toleransi $< 2\times$ biaya swap Sumber B -> langsung ke `06`.

---

## Penanda Sisipan Entri Baru (`[POV-DEFI-03]` .. `[POV-DEFI-NN]`)
*(Tambahkan entri baru di atas baris ini dengan 8 field wajib, lalu daftarkan 1 baris di `references/ref-attacker-pov.md`).*
