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

### [POV-01] Desinkronisasi Indeks Akrual Melalui Self-Transfer atau Mutasi Pihak Ketiga

- **Kondisi Prasyarat (State Condition):**
  Kontrak melacak hak klaim/bunga/poin menggunakan indeks global (`globalIndex`) dan titik catat per pengguna (`userIndex[u]`), serta memiliki fungsi pemindahan hak (`transfer`, `delegate`, `migrate`, `merge`) selain fungsi masuk/keluar utama.

- **Kacamata Attacker (Gejala di Kode):**
  Fungsi pemindahan memperbarui `balance[from]` dan `balance[to]` (atau menyalin saldo ke variabel memori sementara `uint256 balFrom = balance[from]`), tetapi **tidak** menyinkronkan/mengklaim hak tertunda pada KEDUA akun sebelum saldo berubah, atau tidak menolak kondisi `from == to`.

- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Attacker_A mengakumulasi hak/bunga yang belum diklaim (`globalIndex > userIndex[Attacker_A]`).
  2. **[Pemicu Asimetri]** Attacker_A memindahkan saldo ke Attacker_B (yang masih memiliki `userIndex` rendah) atau mentransfer ke dirinya sendiri (Attacker_A -> Attacker_A).
  3. **[Ekstraksi Nilai]** Attacker_B (atau Attacker_A) mengeklaim hak penuh menggunakan saldo baru dikalikan selisih indeks lama, lalu mengembalikan pokoknya untuk diulang (*loop*).

- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor memeriksa `stake()`, `unstake()`, dan `claim()` lalu melihat ketiganya sudah memanggil modifier `updateReward(msg.sender)`. Auditor lupa bahwa modifier tersebut hanya menerima 1 argumen (`msg.sender`), sehingga pada fungsi 2-aktor seperti `transfer(to, amount)`, akun `to` tidak ikut ter-update — atau variabel memori menimpa nilai saat `from == to`.

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika fungsi transfer secara eksplisit memanggil sinkronisasi indeks untuk `from` DAN `to` sebelum mengubah saldo, serta menggunakan pengurangan/penambahan langsung di storage (bukan menyalin variabel memori yang saling menimpa saat `from == to`).

---

### [POV-04] Inverse-Function Rounding Asymmetry & Multi-Hop Truncation (mint/withdraw vs deposit/redeem)

- **Asumsi Auditor Standar:** "Vault sudah aman dari *rounding exploit* karena `convertToShares` menggunakan `Rounding.Down` dan `convertToAssets` menggunakan `Rounding.Up`, serta `totalSupply == 0` sudah diproteksi dengan *virtual shares/dead shares*."

- **Realita Penyerang (Counter-Auditor):** Meskipun fungsi searah (`deposit` dan `redeem`) membulatkan ke arah yang benar, fungsi kebalikannya (`mint(shares)` atau `withdraw(assets)`) atau konversi multi-tahap (`asset -> wrappedAsset -> basePoint -> share`) sering kali melakukan pembagian integer antara (*intermediate division*) yang membulatkan ke bawah sebelum pembulatan akhir. Jika `mint(1)` atau `withdraw(x)` melewati 2 kali pembagian beruntun, pemangkasan di langkah pertama dapat mengecilkan penyebut atau pengali di langkah kedua.

- **Target Pencarian di Kode** (Kombinasi `Metode 4` & `Metode 7`):
  1. Sandingkan rumus di dalam `deposit(x)` vs `mint(y)` dan `withdraw(x)` vs `redeem(y)`. Cari apakah keduanya memanggil fungsi internal yang sama dengan flag `Rounding` berbeda, atau menulis ulang rumus sendiri.
  2. Cari rantai konversi 2 langkah atau lebih: misalnya `shares = (assets * feeBps / 10000) * totalSupply / totalAssets`. Periksa apakah bagian `(assets * feeBps / 10000)` dapat menghasilkan 0 untuk nilai `assets > 0` sementara pokok `assets` tetap dipindahkan.

- **Uji Cepat Langkah 0 (Fase 3):**
  - Substitusi matematis langsung dengan angka batas: `totalAssets = 10000e18 + 1`, `totalSupply = 10000e18`, `fee = 30 bps`. Hitung apakah `withdraw(a) + withdraw(b)` memotong share lebih sedikit daripada `withdraw(a + b)`. Jika tidak ada selisih $\ge 1\text{ wei}$ yang menguntungkan pengguna setelah dikurangi biaya transaksi/loop, langsung gugurkan.

---

<!-- Sisipkan [POV-05], [POV-06], dst. di BAWAH baris ini, urut menaik -->
