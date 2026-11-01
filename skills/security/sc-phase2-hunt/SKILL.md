---
name: sc-phase2-hunt
description: Phase 2 — Counter-Auditor Adversarial Hunting (5 Non-Standard Lenses + Generalized Attacker POV) with Pure Code-Guard Separation (04 vs 05).
version: 5.0.0
---

# Phase 2: Counter-Auditor Two-Stage Adversarial Hunting

Tujuan Fase 2 adalah menemukan kerentanan yang luput dari mata auditor standar. Jangan membaca kode secara pasif dari baris atas ke bawah seperti auditor biasa; gunakan 5 Metode Counter-Auditor di bawah ini tanpa melakukan penghakiman kelayakan ekonomi secara prematur.

---

## Aturan Orkestrasi Subagent (delegate_task)
Jika dijalankan melalui delegasi, berikan paket tugas berisi:
1. Daftar 1 Kelompok Fungsi Siklus Hidup (2–4 fungsi) dari audit/03-attack-surface-queue.md beserta tag [LOAD: ...].
2. Instruksi wajib membaca audit/00-project-map.md, audit/01-threat-and-env.md (3 Kasta Aset & Jejak *Patch-Scar*), dan audit/02-state-and-var-matrix.md.
3. Instruksi menjalankan Tahap A (5 Metode Counter-Auditor First-Principles) -> Tahap B (Analogi & Katalog Attacker POV) -> Tahap C (Pemisahan Murni `04-code-guarded.md` vs `05-raw-leads.md`).

---

## TAHAP A: 5 Metode Pencarian "Counter-Auditor" (WAJIB Sebelum Membaca Referensi!)

Jangan memeriksa fungsi secara terisolasi. Terapkan kelima lensa berlawanan-arah berikut dan tulis perhitungannya di audit/notes/:

### Metode 1 — Backward Sink-to-Source Tracing (Kebalikan Arah Baca Auditor)
Auditor membaca dari baris pertama fungsi (require) ke bawah sehingga mudah terhipnotis bahwa fungsi sudah aman. Anda WAJIB membaca dari bawah ke atas:
1. Cari Titik Kritis di Bawah (*The Sink*): baris pengiriman token/koin/NFT, pencetakan hak/share, penghapusan utang/kewajiban, atau penyitaan jaminan.
2. Lacak mundur ke atas (*backward*) setiap variabel pembentuk jumlah di *Sink* tersebut: *"Bagaimana cara memperbesar angka yang keluar di Sink sambil memperkecil pengorbanan di Source menggunakan input yang diizinkan pada 3 Kasta Aset di 01-threat-and-env.md?"*

### Metode 2 — State-Transition Differential Analysis (Expected vs. Actual Delta)
Untuk setiap aksi atau pasangan aksi di kelompok fungsi ini, bandingkan perubahan state yang seharusnya terjadi secara ekonomi vs yang benar-benar tertulis di kode:
- Catat di audit/notes/ dengan kerangka:
  State Awal -> Aksi -> Delta Ekspektasi (Hak vs Kewajiban) vs Delta Aktual di Kode -> Selisih Variabel yang Tidak Sinkron.
- Periksa apakah ada variabel global yang berubah tanpa memperbarui variabel user (atau sebaliknya), indeks akrual yang terlambat disinkronkan satu langkah, atau operasi batal/klaim sebagian yang lupa me-reset salah satu field struct.

### Metode 3 — Irrational 2-Wallet Sybil & Zero-Time Loop (Aksi "Tidak Masuk Akal" bagi Pengguna Normal)
Auditor menguji alur pengguna waras. Anda WAJIB menguji perilaku "tidak rasional" menggunakan 2 Dompet Milik 1 Penyerang (`Attacker_A` dan `Attacker_B`) dalam 1 transaksi atomik ($\Delta t = 0$):
1. **Self-Transfer & Ping-Pong Loop:** Apa yang terjadi jika Attacker_A mentransfer/mendelegasikan hak ke dirinya sendiri (from == to) atau memantulkannya Attacker_A -> Attacker_B -> Attacker_A berulang kali di blok yang sama?
2. **Self-Liquidation / Self-Penalty Arbitrage:** Apa yang terjadi jika Attacker_A sengaja membuat posisinya terkena likuidasi/slashing/lelang/bad-debt, sementara Attacker_B bertindak sebagai likuidator/penawar yang memanen bonus atau mengalihkan kerugian (*bad debt socialization*) ke kolam publik?
3. **Zero / 1-Wei Boundary & Dust Amplification:** Masukkan nilai 0, 1 wei, atau batas_minimum - 1 untuk menguji apakah biaya/penalti terpotong jadi 0 karena pembulatan dan dapat di-loop dalam satu transaksi batch/multicall.

### Metode 4 — Patch-Scar, Periphery, & View-vs-Write Asymmetry (Menyerang Titik Lelah Auditor)
1. **Bedah *Patch-Scar* (Bekas Tambalan):** Jika fungsi utama memiliki `if`/`require` khusus yang terlihat seperti tambalan audit (lihat 01-threat-and-env.md), periksa apakah jalur sampingan (transfer, migrate, emergencyWithdraw, batch, onERC721Received) yang menyentuh variabel yang sama lupa dipasang tambalan tersebut.
2. **Desinkronisasi Rumus `View` vs `Write`:** Bandingkan baris demi baris rumus di fungsi view/preview dengan fungsi tulis pasangannya di 02-state-and-var-matrix.md (misal: perbedaan arah pembulatan `mulDivDown` vs `mulDivUp`, atau biaya yang dihitung di preview tetapi tidak dipotong di fungsi eksekusi).

### Metode 5 — Guard-Inversion (Membalik Guard Kode Menjadi Target Manipulasi)
Setiap kali menemukan `require(Kondisi_X >= Kondisi_Y)` atau `if (...) revert`:
- Jangan langsung berhenti! Tanyakan: *"Variabel apa yang menyusun Kondisi_X dan Kondisi_Y? Berdasarkan 02-state-and-var-matrix.md, bisakah fungsi publik lain (atau flashloan/donasi/callback) mengubah nilai X atau Y sesaat sebelum baris require ini dieksekusi?"*
- *(Pada Putaran 2, gunakan metode ini secara khusus untuk membongkar seluruh daftar guard yang terkumpul di audit/04-code-guarded.md).*

---

## TAHAP B: Pengayaan Analogi Mekanis & Katalog Attacker POV ([POV-XX])
Panggil skill_view("sc-phase2-hunt", "<nama-file-ref>") sesuai tag [LOAD: ...]:
1. Terjemahkan konsep di dalam referensi domain sebagai Pola Mekanis Abstrak lintas domain.
2. Buka katalog terpusat `references/ref-attacker-pov.md` (bagian `## Daftar Entri`). Cocokkan apakah **Kondisi Prasyarat** terpenuhi dan **Gejala di Kode** pada item `[POV-XX]` hadir pada fungsi yang sedang Anda bedah — terutama kolom *Auditor Blindspot*, karena di situlah peluangnya berada.
   - **Fallback wajib:** bila `ref-attacker-pov.md` belum memuat POV yang cocok, JANGAN mengarang nomor POV. Turunkan ke analogi mekanis bebas (butir 1) dan catat di `audit/notes/` bahwa katalog POV untuk pola tersebut belum tersedia. *(Katalog POV diisi bertahap — ketiadaannya bukan cacat, jangan "diperbaiki" dengan entri karangan.)*

---

## TAHAP C: Pemisahan Murni (04-code-guarded.md vs 05-raw-leads.md)
Di Fase 2, Anda adalah Pemburu (Hunter), bukan Hakim Ekonomi. Jangan membuang anomali hanya karena terlihat kecil sendirian (karena akan dirangkai menjadi *attack chain* di Putaran 2 atau diuji amplifikasinya di simulasi Fase 3):
1. **Dua Larangan Fakta Dasar Kode:** Jangan mengarang sifat palsu pada Token Kasta 1 (LP/Share token = ERC-20 standar, bukan *Fee-on-Transfer*/USDT) dan jangan mengasumsikan penyerang bisa memanggil fungsi onlyOwner secara langsung.
2. **Jika Ditemukan Anomali yang Tidak Dihentikan Guard** (atau Guard Bisa Ditembus via Metode 5):
   Tulis langsung ke `audit/05-raw-leads.md` lengkap dengan: Metode Pencarian (1-5 / POV-XX), File:Kontrak:Fungsi (Baris), Delta State (Expected vs Actual), Urutan Eksploitasi, dan Potensi Rantai Serangan (Chaining).
3. **Jika Hipotesis Benar-Benar Dihentikan oleh Guard Kode** (`require` / `if (...) revert` / `assert!`):
   Tulis langsung ke `audit/04-code-guarded.md` lengkap dengan lokasi File:Baris guard, ekspresi matematika guard-nya, dan variabel pembentuknya (sebagai umpan *Guard-Inversion* Putaran 2).
4. Tandai kelompok fungsi di audit/03-attack-surface-queue.md menjadi [HUNTED].
