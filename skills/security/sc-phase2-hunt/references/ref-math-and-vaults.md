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

- **Inflasi Pendeposit Pertama & Manipulasi Donasi / `balanceOf` Skew (Pool Kosong maupun Pool Aktif `totalSupply > 0`):**
  - Saat total saham (`totalSupply` / `totalShares`) bernilai 0 atau sangat kecil (termasuk pada vault yang bisa dibuat lewat Factory atau ditarik kembali ke 0), apakah rumus pencetakan saham menggunakan rasio `amount * totalShares / totalAssets` tanpa proteksi *virtual shares/offset* atau *dead shares*?
  - Apakah `totalAssets` membaca saldo token kontrak secara langsung (`balanceOf`) sehingga dapat dimanipulasi lewat transfer langsung (*donation*) untuk membuat pendeposit berikutnya menerima 0 shares akibat pembulatan ke bawah?
  - **Donasi Penyerang pada Pool Aktif (`totalSupply > 0`):** Apakah pengiriman token langsung (`ERC20.transfer` / donasi oleh penyerang di luar fungsi deposit) dapat: (a) mematahkan asersi kesamaan ketat (`require(token.balanceOf(address(this)) == internalBalance)`) hingga memicu DoS permanen, (b) menyela alur *push-then-sync* (`mint`/`skim`/`sync` atau distribusi reward) untuk mencuri selisih saldo sebelum disinkronkan, atau (c) mendistorsi harga share/indeks akrual? **(Ingat: donasi oleh PENYERANG adalah vektor *permissionless* yang 100% VALID, bukan kesalahan korban!)**

5. **Penyempitan Tipe Integer & Blok Tak Terperiksa (Unsafe Downcasting & Unchecked):**
   - Cari konversi tipe yang menyempit (`uint128(x)`, `uint96(x)`, `u64`, atau konversi `uint256` ke `int256`) tanpa pemeriksaan batas maksimum. Jika nilai melampaui batas tipe target, angka akan terpotong (*silent truncation*) dan merusak pencatatan utang/likuiditas.
   - Di dalam blok `unchecked`, pastikan pengurangan `a - b` memiliki jaminan mutlak `a >= b` di semua cabang eksekusi.

6. **Kesalahan Batas Iterator & Indeks Bitwise:**
   - Pada manipulasi *bitmap*, *tick*, atau perulangan array: periksa pergeseran bit (`<<`, `>>`), urutan rantai iterator (misal `.skip(1).enumerate()` vs `.enumerate().skip(1)`), serta batas `<` vs `<=`.

---

---
## Katalog Generalized Attacker POV & Auditor Blindspots (Modular Lazy-Load)
Untuk mencocokkan gejala kode dengan pola serangan on-chain nyata tanpa membebani konteks:
1. Periksa **Tabel Router Gejala Kode** di `references/ref-attacker-pov.md`.
2. Jika gejala pemicunya cocok dengan fungsi yang sedang dibedah, muat katalog lengkapnya di `references/ref-pov-math.md`.
