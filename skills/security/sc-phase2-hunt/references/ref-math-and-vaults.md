# Checklist Universal: Matematika, Pembulatan, & Akuntansi Vault/Shares

Periksa setiap operasi aritmatika dan pencetakan/pembakaran hak (*shares/LP*) terhadap 6 vektor berikut:

1. **Arah Pembulatan Terbalik (Rounding Direction Vulnerability):**
   - Aturan mutlak: Pembulatan WAJIB selalu menguntungkan Protokol/Pool dan merugikan pemanggil.
   - **Fungsi Penambah Hak / Masuk:** Saat menghitung *shares* yang diterima pengguna dari jumlah aset masuk, wajib bulatkan ke BAWAH (`Down`). Saat menghitung aset yang harus disetor untuk jumlah *shares* tertentu, wajib bulatkan ke ATAS (`Up`).
   - **Fungsi Pengurang Hak / Keluar:** Saat menghitung *shares* yang harus dibakar untuk menarik sejumlah aset, wajib bulatkan ke ATAS (`Up`). Saat menghitung aset yang keluar dari penukaran *shares*, wajib bulatkan ke BAWAH (`Down`).
   - *Uji Eksploitasi:* Apakah pemanggil bisa memutar transaksi masuk-keluar berulang kali atau memecah nilai transaksi (*dust splitting*) untuk mencuri selisih pembulatan?

2. **Pembagian Menjadi Nol (Precision Loss to Zero):**
   - Apakah ada pembagian `A / B` di mana `A < B` menghasilkan `0` tanpa memicu `revert`?
   - Periksa apakah kondisi hasil `0` ini memungkinkan pemanggil: (a) mencetak posisi/hak tanpa membayar biaya (*zero fee*), (b) menghindari penalti/bunga, atau (c) memperbarui indeks akrual waktu tanpa menambah nilai (`lastUpdateTime = now` saat `reward == 0`).

3. **Pembagian Sebelum Perkalian (Divide Before Multiply):**
   - Cari pola `(a / b) * c` di mana hasil pembagian integer dipotong sebelum dikalikan kembali, yang merusak presisi perhitungan bunga atau distribusi hadiah.

4. **Inflasi Pendeposit Pertama / Manipulasi Donasi (Vault Share Inflation):**
   - Saat total saham (`totalSupply` / `totalShares`) bernilai `0` atau sangat kecil, apakah rumus pencetakan saham menggunakan rasio `amount * totalShares / totalAssets` tanpa proteksi *virtual shares/offset* atau *dead shares*?
   - Apakah `totalAssets` membaca saldo token kontrak secara langsung (`balanceOf`) sehingga dapat dimanipulasi lewat transfer langsung (*donation*) untuk membuat pendeposit berikutnya menerima `0 shares` akibat pembulatan ke bawah?

5. **Penyempitan Tipe Integer & Blok Tak Terperiksa (Unsafe Downcasting & Unchecked):**
   - Cari konversi tipe yang menyempit (`uint128(x)`, `uint96(x)`, `u64`, atau konversi `uint256` ke `int256`) tanpa pemeriksaan batas maksimum. Jika nilai melampaui batas tipe target, angka akan terpotong (*silent truncation*) dan merusak pencatatan utang/likuiditas.
   - Di dalam blok `unchecked`, pastikan pengurangan `a - b` memiliki jaminan mutlak `a >= b` di semua cabang eksekusi.

6. **Kesalahan Batas Iterator & Indeks Bitwise:**
   - Pada manipulasi *bitmap*, *tick*, atau perulangan array: periksa pergeseran bit (`<<`, `>>`), urutan rantai iterator (misal `.skip(1).enumerate()` vs `.enumerate().skip(1)`), serta batas `<` vs `<=`.

---

## Katalog Generalized Attacker POV & Auditor Blindspots (Diisi Bertahap)

Entri di bawah ini adalah pola eksploitasi nyata yang telah digeneralisasi. Pakai pada Tahap B Fase 2: cocokkan **Kondisi Prasyarat** dan **Gejala di Kode** dengan fungsi yang sedang dibedah.
Indeks seluruh POV lintas file: `references/ref-attacker-pov.md`.

### [POV-MATH-01] Desinkronisasi Indeks Akrual pada Transfer/Mutasi Pokok

- **Kondisi Prasyarat (State Condition):**
  Kontrak melacak pertumbuhan hak/bunga/kewajiban menggunakan indeks global (`globalIndex`) dan titik catat per akun (`userIndex[u]`), serta memiliki fungsi pemindahan saldo/posisi antar-akun (pemindahan, delegasi, migrasi, atau penggabungan posisi) di luar fungsi masuk/keluar tunggal.

- **Kacamata Attacker (Gejala di Kode):**
  Fungsi pemindahan mengubah saldo akun pengirim (`from`) dan penerima (`to`) — atau menyalin saldo ke variabel memori sementara sebelum ditulis balik — tetapi tidak menyinkronkan/mengklaim hak tertunda pada KEDUA akun sebelum saldo berubah, atau tidak menolak kondisi `from == to`.

- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Attacker_A mengakumulasi selisih indeks yang belum diklaim (`globalIndex > userIndex[Attacker_A]`), sementara Attacker_B memiliki `userIndex` lama yang rendah.
  2. **[Pemicu Asimetri]** Attacker_A memindahkan saldo pokok ke Attacker_B (atau memindahkan ke dirinya sendiri Attacker_A -> Attacker_A bila kontrak memakai variabel memori sementara).
  3. **[Ekstraksi Nilai]** Akun penerima mengeklaim hak penuh menggunakan saldo baru dikalikan selisih indeks lama, lalu mengembalikan pokoknya untuk diulang (*loop*).

- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor memeriksa fungsi masuk, keluar, dan klaim utama (1-aktor) lalu melihat ketiganya sudah memanggil modifier/fungsi penyinkron indeks untuk `msg.sender`. Auditor lupa bahwa penyinkron 1-argumen tersebut tidak memperbarui akun kedua (`to`) pada fungsi 2-aktor, atau luput melihat variabel memori yang saling menimpa saat `from == to`.

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika fungsi pemindahan secara eksplisit menyinkronkan indeks untuk `from` DAN `to` sebelum mengubah saldo, serta menggunakan pengurangan/penambahan langsung di storage tanpa penimpaan cache memori saat `from == to`.

---

### [POV-MATH-02] Inverse-Function Rounding & Multi-Hop Fee Truncation

- **Kondisi Prasyarat (State Condition):**
  Kontrak menyediakan pasangan fungsi konversi dua arah — yaitu fungsi Berbasis Input Eksak (*Exact-Input*, pemanggil menentukan jumlah yang diserahkan, kontrak menghitung hasil) dan fungsi Berbasis Target Output Eksak (*Exact-Output*, pemanggil menentukan jumlah hasil yang diminta, kontrak menghitung balik beban biayanya) — atau melakukan konversi proporsi melewati $\ge 2$ tahap pembagian integer beruntun.

- **Kacamata Attacker (Gejala di Kode):**
  Meskipun fungsi searah (*Exact-Input*, mis. setor aset atau tukar share) sudah membulatkan ke arah yang menguntungkan protokol, fungsi kebalikannya (*Exact-Output*, mis. cetak share eksak atau tarik aset eksak) atau perhitungan potongan biaya perantara `(amount * feeBps / 10000) * totalShares / totalAssets` melakukan pembagian integer yang membulatkan ke bawah di langkah tengah sebelum pembulatan akhir.

- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang mencari atau menciptakan rasio nilai tukar di mana total aset dan total pencatatan bagian (*shares/units*) tidak berkelipatan bulat sempurna.
  2. **[Pemicu Asimetri]** Penyerang memanggil fungsi *Exact-Output* berulang kali dengan nilai target kecil tepat di bawah ambang pembulatan (Metode 7 — *Split-vs-Bulk*: $f(a) + f(b) < f(a+b)$).
  3. **[Ekstraksi Nilai]** Potongan biaya atau beban bagian yang harus dibakar terpangkas menjadi 0 atau berkurang 1 wei di setiap iterasi, lalu dilipatgandakan dalam satu transaksi batch/multicall.

- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor terpaku memeriksa fungsi *Exact-Input* utama serta proteksi pendeposit pertama (`totalSupply == 0`), lalu menganggap fungsi *Exact-Output* pasangannya sudah simetris tanpa menguji apakah pembagian antara (*intermediate division*) memotong penyebut atau biaya sebelum langkah pembulatan terakhir.

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika seluruh tahap pembagian pada fungsi *Exact-Output* membulatkan beban pengguna ke atas (`Rounding.Up` / *ceil*) tanpa pemangkasan perantara, atau jika selisih maksimum setelah di-loop dalam batas gas 1 blok lebih kecil dari biaya gas + fee protokol (`REJECTED_DUST` / `REJECTED_NEGATIVE_EV`).

---

<!-- Sisipkan [POV-CALL-02], [POV-DEFI-02], dst. di BAWAH baris ini, urut menaik -->
