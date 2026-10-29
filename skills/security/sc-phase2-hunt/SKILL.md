---
name: sc-phase2-hunt
description: Fase 2 Whitehat Adversarial Hunting - Eksplorasi 3 Lapis (Radius 0-2 Lifecycle, Variable-Centric & 3-Step Sequence Permutation, serta Guard-Bypass & Library Deep-Dive) dengan pemuatan referensi dinamis
version: 4.0.0
metadata:
  hermes:
    tags: [security, web3, whitehat, adversarial, vulnerability-hunting, multichain, phase2]
    category: security
    requires_toolsets: [terminal]
---

# Phase 2: 3-Layer Whitehat Adversarial Vulnerability Hunting

## When to Use
Gunakan skill ini setelah Fase 1 selesai (setelah `.audit/00-project-map.md`, `.audit/01-threat-and-env.md`, `.audit/02-state-and-var-matrix.md`, dan `.audit/03-attack-surface-queue.md` tersedia). Skill ini membedah permukaan serangan menggunakan 3 Lapis Eksplorasi Adversarial untuk menemukan jalur manipulasi state dan pelanggaran invarian.

## Pitfalls (Larangan Keras di Fase 2)
- **DILARANG MEMERIKSA BANYAK TARGET SEKALIGUS DALAM SATU PIKIRAN:** Jika menjalankan eksplorasi atas antrean di `.audit/03-attack-surface-queue.md`, Parent WAJIB menggunakan `delegate_task` (`max_concurrent_children: 1`) agar setiap Subagent fokus membedah 1 unit antrean (1 fungsi kompleks, 1 pasang fungsi siklus hidup, atau 1 variabel kritis) dengan konteks bersih.
- **WAJIB MEMANGGIL `skill_view` PADA KAMUS REFERENSI:** Jangan mengandalkan ingatan umum. Panggil `skill_view("sc-phase2-hunt", "references/<nama-file>.md")` sesuai tag `[LOAD: ...]` pada item antrean!
- **DILARANG BERHENTI HANYA KARENA MELIHAT `require()` ATAU `assert!()`:** Setiap penjaga (guard) harus diinterogasi apakah variabel pembentuknya bisa dimanipulasi (Lapis 3).
- **DISIPLIN PEMISAHAN LAPORAN & BATAS 12 BARIS SUBAGENT:**
  * Simpan catatan kerja rinci per tugas di `.audit/notes/<nama-tugas>.md`.
  * Skenario serangan yang lolos saringan skeptis ditulis ke `.audit/06-raw-leads.md` (siap diuji di Fase 3).
  * Hipotesis yang terbukti gugur oleh pengaman yang tidak bisa ditembus ditulis ke `.audit/07-rejected-hypotheses.md` (lengkap dengan lokasi `NamaFile:Baris` guard yang menggagalkannya).
  * Subagent hanya boleh mengembalikan ringkasan maksimal 12 baris ke Parent Agent.
- **DILARANG MENGUBAH KODE SUMBER PROYEK & DILARANG MEMANGGIL `skill_manage` / `memory`.**

---

## Procedure (3 Lapis Eksplorasi Adversarial)

Pastikan kamu bekerja pada `/home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/`. Buat folder `.audit/notes/` jika belum ada (`mkdir -p .audit/notes`).

### Langkah 1: Persiapan Target, Aktor, & Pemuatan Referensi Dinamis
1. Baca `.audit/00-project-map.md` dan `.audit/01-threat-and-env.md` untuk mengunci: Paradigma Rantai (A/B/C), Kemampuan Aktor Tanpa Hak Istimewa, dan Core Invariants yang menjadi target.
2. Ambil target dari `.audit/03-attack-surface-queue.md` dan baca definisi state terkait di `.audit/02-state-and-var-matrix.md`.
3. **Panggil `skill_view` sesuai Tag `[LOAD: ...]` pada Target:**
   - **Wajib Muat 1 Modul Rantai Proyek:**
     * `references/ref-chain-evm-tron.md` (Solidity/Vyper di EVM & Tron TVM)
     * `references/ref-chain-solana.md` (Rust Anchor/Native di Solana)
     * `references/ref-chain-sui-move.md` (Move di Sui/Aptos)
     * `references/ref-chain-ton-async.md` (FunC/Tact/Tolk di TON)
   - **Wajib Muat Modul Ekonomi/Logika yang Relevan:**
     * `references/ref-math-and-vaults.md`
     * `references/ref-calls-tokens-reentrancy.md`
     * `references/ref-defi-oracles-liquidation.md`

### Langkah 2: LAPIS 1 — Bedah Mikro-ke-Makro & Pasangan Siklus Hidup (Radius 0 -> 1 -> 2)
Baca kode fungsi target menggunakan `read_file` (maksimal 120–150 baris per panggilan) dan jalankan analisis dua arah (dari mutasi kode -> dampak, dan dari target invarian -> mutasi kode):
1. **Radius 0 (Eksplorasi Tingkat Unit & Input Adversarial):**
   - **Otorisasi & Ikatan Parameter:** Apakah pemanggil tanpa hak istimewa bisa menyuplai alamat `from`/`user`, akun `remaining_accounts`, objek `UID`, atau pesan `Jetton` milik entitas lain tanpa verifikasi ikatan kepemilikan?
   - **Simetri Baca vs Tulis:** Apakah kunci indeks mapping/array atau field objek saat dibaca 100% identik dengan saat ditulis?
   - **Nilai Ekstrem & Referensi Diri:** Uji secara mental jika input bernilai `0`, `1 unit terkecil (wei/sun/lamport/mist)`, `max_uint`, alamat/objek pengirim sama dengan penerima (`from == to`, `tokenA == tokenB`), atau array berisi elemen kembar `[X, X]`.
   - **Non-Idempotency (Panggilan Berulang):** Apa yang terjadi jika fungsi dipanggil dua kali berturut-turut dalam satu blok/transaksi/PTB?
2. **Radius 1 (Pasangan Siklus Hidup / Direct-Pair Symmetry):**
   - Gunakan `search_files` (`rg -n`) untuk membuka fungsi pasangan yang melakukan mutasi kebalikan (`+=` vs `-=`/`delete`, *mint* vs *burn*, *lock* vs *unlock*, pengiriman pesan vs handler `bounced`).
   - Cari ketidaksimetrian: apakah ada variabel state, indeks akrual, atau biaya yang ditambah saat masuk tetapi lupa dikurangi/dihapus saat keluar, saat penarikan darurat, atau saat likuidasi?
3. **Radius 2 (Batas Kepercayaan Lintas Kontrak / Lintas Pesan):**
   - Lacak ke mana panggilan keluar (`.call`, CPI, PTB, `send_raw_message`) mengarah. Apakah kontrak inti bisa dipanggil langsung (*direct call*) melewati `Router` untuk menghindari validasi?
   - Khusus **Paradigma C (TON Async)**: Apa yang terjadi pada state di Kontrak Hulu jika eksekusi gagal di Kontrak Hilir? Apakah handler `bounced` memulihkan seluruh state dalam batas 256-bit?

### Langkah 3: LAPIS 2 — Pelacakan Balik Variabel & Permutasi Urutan 3 Langkah
Jika Lapis 1 belum menemukan celah langsung (atau saat melakukan eksplorasi mendalam), geser sudut pandang dari fungsi ke **Variabel & Kombinasi Urutan**:
1. **Variable-Centric Reverse Trace:**
   - Lihat matriks variabel kritis di `.audit/02-state-and-var-matrix.md` yang disentuh oleh target ini.
   - Periksa **jalur sampingan** yang juga membaca/menulis variabel tersebut: fungsi `transfer`, `claim`, `split/merge`, `migrate`, `liquidate`, atau `poke/update`. Apakah jalur sampingan tersebut mengubah saldo/posisi tanpa memperbarui indeks waktu/utang/reward?
2. **Permutasi Urutan 3 Langkah (`Langkah A -> Langkah Transisi C -> Langkah B`):**
   - Uji skenario ketika penyerang menyisipkan aksi transisi di tengah siklus normal:
     * `Masuk (A) -> Transfer Hak / Pecah Objek / Ubah Konfigurasi Mode (C) -> Keluar / Likuidasi (B)`
     * `Donasi / Flash Loan (A) -> Panggilan Nilai 0 / Akrual Indeks (C) -> Mint / Redeem / Borrow (B)`

### Langkah 4: LAPIS 3 — Pembongkaran Penjaga (Guard-Bypass) & Pustaka Matematika
Jangan langsung menyerah ketika melihat `require()`, `assert!()`, atau `modifier` yang tampak menghalangi serangan:
1. **Interogasi Variabel Pembentuk Guard (Guard-Bypass Analysis):**
   - Untuk setiap pengecekan keamanan penting (misal `require(healthFactor >= MIN)` atau `assert!(amountOut >= minOut)`), lacak dari mana nilai di sebelah kiri dan kanan dihitung!
   - Apakah salah satu variabel pembentuknya membaca saldo `balanceOf(address(this))` secara langsung, membaca harga spot, menggunakan pembulatan ke bawah yang bisa dibuat menjadi `0`, atau membaca state yang belum di-`.reload()`?
2. **Pembedahan Pustaka Matematika & Bitwise (`libraries/` / `math/`):**
   - Jika fungsi target memanggil fungsi pembantu matematika kustom (pembagian *fixed-point*, *sqrt price*, pergeseran bit `<<` / `>>`, *tick bitmap*, atau *type casting*), buka file pustaka tersebut dan periksa batas *overflow/truncation* serta arah pembulatannya.

### Langkah 5: Saringan Devil's Advocate & Pencatatan ke File Kategori Terpisah
Evaluasi setiap kandidat skenario serangan secara objektif:
1. Apakah aktor penyerang benar-benar tidak membutuhkan kunci `admin`/`owner`?
2. Apakah ada pengaman di hulu/hilir yang membatalkan skenario ini dan terbukti TIDAK BISA dilewati lewat Lapis 3?
3. **Klasifikasi & Penulisan Output:**
   - Tulis rincian analisis ke `.audit/notes/<nama-tugas>.md`.
   - Perbarui status item di `.audit/03-attack-surface-queue.md` menjadi `[HUNTED - LEAD FOUND]` atau `[HUNTED - CLEAN]`.
   - **Jika Skenario Lolos Devil's Advocate:** Tuliskan ke **`.audit/06-raw-leads.md`** dengan format lengkap:
     * Judul & ID Lead
     * Lokasi Kode Presisi (`NamaFile:Baris`)
     * Aktor & Prasyarat Awal (*Preconditions*)
     * Urutan Aksi Eksploitasi (*Step-by-Step Sequence*)
     * Invarian yang Dilanggar & Estimasi Dampak
     * Rekomendasi Tier Pengujian Fase 3 (Tier 1 s/d Tier 6) untuk membuktikannya.
   - **Jika Skenario Gugur oleh Guard yang Sah:** Tuliskan ke **`.audit/07-rejected-hypotheses.md`** beserta lokasi eksak penjaga (`NamaFile:Baris`) dan alasan mekanis mengapa serangan gagal.

---

## Verification
Pastikan status di `.audit/03-attack-surface-queue.md` telah diperbarui, catatan kerja tersimpan di `.audit/notes/`, temuan mentah dipisahkan dengan rapi antara `.audit/06-raw-leads.md` dan `.audit/07-rejected-hypotheses.md`, serta laporan balik ke Parent Agent tidak melebihi 12 baris.
