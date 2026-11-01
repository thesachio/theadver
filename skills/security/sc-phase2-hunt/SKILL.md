---
name: sc-phase2-hunt
description: Phase 2 — Counter-Auditor Adversarial Hunting (10 Non-Standard Lenses + First-Principles Foundation + Generalized Attacker POV) with Pure Code-Guard Separation (04 vs 05).
version: 5.1.0
---

# Phase 2: Counter-Auditor Two-Stage Adversarial Hunting

Tujuan Fase 2 adalah menemukan kerentanan yang luput dari mata auditor standar. Jangan membaca kode secara pasif dari baris atas ke bawah seperti auditor biasa; gunakan Fondasi First-Principles dan 10 Metode Counter-Auditor di bawah ini tanpa melakukan penghakiman kelayakan ekonomi secara prematur.

---

## Aturan Orkestrasi Subagent (delegate_task)
Jika dijalankan melalui delegasi, berikan paket tugas berisi:
1. Daftar 1 Kelompok Fungsi Siklus Hidup (2–4 fungsi) dari audit/03-attack-surface-queue.md beserta tag [LOAD: ...].
2. Instruksi wajib membaca audit/00-project-map.md, audit/01-threat-and-env.md (3 Kasta Aset & Jejak *Patch-Scar*), dan audit/02-state-and-var-matrix.md.
3. Pembagian Putaran Eksplorasi:
   - Putaran 1 (Mikro Unit Antrean): Jalankan Fondasi Batas & 5 Primitif + Metode 1, 2, 3, 6, 7 -> Tahap B (Analogi & Katalog POV) -> Tahap C (`04` vs `05`).
   - Putaran 2 (Makro Lintas-Jalur & Guard-Inversion): Jalankan Metode 4, 5, 8, 9, 10 menggunakan 02-state-and-var-matrix.md, 05-raw-leads.md, dan daftar guard di 04-code-guarded.md.

---

## TAHAP A: Fondasi First-Principles & 10 Metode "Counter-Auditor" (WAJIB Sebelum Membaca Referensi!)

Jangan memeriksa fungsi secara terisolasi. Uji fondasi batas & 5 primitif universal berikut, lalu terapkan 10 Metode Counter-Auditor dan tulis perhitungannya di audit/notes/:

### Fondasi Wajib: 4 Kondisi Batas Konkret & 5 Primitif Universal
Saat membedah setiap fungsi di unit antrean, selalu substitusikan 4 Kondisi Batas (1. Likuiditas realistis tanpa ilusi `totalSupply == 0` pada pool live; 2. Batas bawah 0, 1 wei, `min - 1`; 3. Blok/waktu sama $\Delta t = 0$; 4. Entitas kembar `sender == recipient` / `target == address(this)`) terhadap 5 Primitif Universal: (1) Kuantisasi Proporsi, (2) Transisi Paksa & Sabotase DoS, (3) Replay Otoritas/Signature, (4) Penyerahan Kontrol Eksekusi, dan (5) Lompatan Mesin Status.

---

### Kelompok Putaran 1 — Lensa Mikro Fungsi & Matematika (Metode 1, 2, 3, 6, 7)

### Metode 1 — Backward Sink-to-Source Tracing (Kebalikan Arah Baca Auditor)
Auditor membaca dari baris pertama fungsi (require) ke bawah sehingga mudah terhipnotis bahwa fungsi sudah aman. Anda WAJIB membaca dari bawah ke atas:
1. Cari Titik Kritis di Bawah (*The Sink*): baris pengiriman token/koin/NFT, pencetakan hak/share, penghapusan utang/kewajiban, atau penyitaan jaminan.
2. Lacak mundur ke atas (*backward*) setiap variabel pembentuk jumlah di *Sink* tersebut: *"Bagaimana cara memperbesar angka yang keluar di Sink sambil memperkecil pengorbanan di Source menggunakan input yang diizinkan pada 3 Kasta Aset di 01-threat-and-env.md?"*

### Metode 2 — State-Transition Differential Analysis (Expected vs. Actual Delta)
Untuk setiap aksi atau pasangan aksi (Masuk/Buat vs Keluar/Batal/Transfer/Sita dari 02-state-and-var-matrix.md), bandingkan perubahan state yang seharusnya terjadi secara ekonomi vs yang benar-benar tertulis di kode:
- Catat di audit/notes/ dengan kerangka:
  State Awal -> Aksi -> Delta Ekspektasi (Hak vs Kewajiban) vs Delta Aktual di Kode -> Selisih Variabel yang Tidak Sinkron.
- Periksa apakah ada variabel global yang berubah tanpa memperbarui variabel user (atau sebaliknya), indeks akrual yang terlambat disinkronkan satu langkah, atau operasi batal/klaim sebagian yang lupa me-reset salah satu field struct.

### Metode 3 — Irrational 2-Wallet Sybil & Zero-Time Loop (Aksi "Tidak Masuk Akal" bagi Pengguna Normal)
Auditor menguji alur pengguna waras. Anda WAJIB menguji perilaku "tidak rasional" menggunakan 2 Dompet Milik 1 Penyerang (`Attacker_A` dan `Attacker_B`) dalam 1 transaksi atomik ($\Delta t = 0$):
1. **Self-Transfer & Ping-Pong Loop:** Apa yang terjadi jika Attacker_A mentransfer/mendelegasikan hak ke dirinya sendiri (from == to) atau memantulkannya Attacker_A -> Attacker_B -> Attacker_A berulang kali di blok yang sama?
2. **Self-Liquidation / Self-Penalty Arbitrage:** Apa yang terjadi jika Attacker_A sengaja membuat posisinya terkena likuidasi/slashing/lelang/bad-debt, sementara Attacker_B bertindak sebagai likuidator/penawar yang memanen bonus atau mengalihkan kerugian (*bad debt socialization*) ke kolam publik?
3. **Zero / 1-Wei Boundary & Dust Amplification:** Masukkan nilai 0, 1 wei, atau batas_minimum - 1 untuk menguji apakah biaya/penalti terpotong jadi 0 karena pembulatan dan dapat di-loop dalam satu transaksi batch/multicall.

### Metode 6 — Memory-vs-Storage Cache Overwrite & Duplicate-Array Aliasing (`[A, A]`)
Auditor membaca variabel memori (`Struct memory s = map[user]`) seolah-olah selalu sinkron dengan storage, dan menguji parameter array dengan elemen unik (`[1, 2, 3]`):
1. **Stale Memory Cache Overwrite:** Cari fungsi yang menyalin struct/saldo ke variabel lokal (`memory` di EVM, atau akun sebelum `.reload()` pasca-CPI di Solana), lalu di tengah fungsi memanggil sub-fungsi/callback/transfer yang memodifikasi storage yang sama, dan di akhir fungsi menulis balik `map[user] = s` — sehingga mutasi di tengah jalan terhapus oleh cache memori basi.
2. **Duplicate-Array Input (`[ID_1, ID_1]`):** Pada setiap fungsi yang menerima array (`ids[]`, `pools[]`, `orders[]`, `recipients[]`, `remaining_accounts`), uji input elemen kembar `[A, A]`. Periksa apakah validasi atau pembacaan saldo dilakukan sebelum pengurangan state di dalam loop, sehingga elemen yang sama diproses/diklaim dua kali.

### Metode 7 — Metamorphic Split-vs-Bulk Asymmetry ($f(a + b) \neq f(a) + f(b)$)
Auditor menguji rumus dengan 1 angka tunggal. Anda WAJIB menguji apakah rumus bersifat non-linear ketika input dipecah atau digabung dalam 1 transaksi:
1. **Salami Slicing (Pecah Jadi $N$ Potongan Kecil):** Bandingkan 1 panggilan `aksi(1000)` vs 100 panggilan `aksi(10)`. Jika biaya/utang/share yang dibakar menggunakan pembulatan ke bawah (*round down*), memecah transaksi dapat membuat kewajiban terpotong menjadi 0 di setiap iterasi.
2. **Bulk Consolidation (Gabung via Flashloan Lalu Pecah):** Bandingkan eksekusi terpisah vs menggabungkan likuiditas/posisi sesaat pada titik perhitungan bagi-hasil/reward/tier, lalu memecahnya kembali di blok yang sama.

---

### Kelompok Putaran 2 — Lensa Makro Lintas-Jalur, Guard, & On-Chain (Metode 4, 5, 8, 9, 10)

### Metode 4 — Patch-Scar, Periphery, & View-vs-Write Asymmetry (Menyerang Titik Lelah Auditor)
1. **Bedah *Patch-Scar* (Bekas Tambalan):** Jika fungsi utama memiliki `if`/`require` khusus yang terlihat seperti tambalan audit (lihat 01-threat-and-env.md), periksa apakah jalur sampingan (transfer, migrate, rescue, sweep, emergencyWithdraw, batch, onERC721Received) yang menyentuh variabel yang sama lupa dipasang tambalan tersebut.
2. **Desinkronisasi Rumus `View` vs `Write`:** Bandingkan baris demi baris rumus di fungsi view/preview dengan fungsi tulis pasangannya di 02-state-and-var-matrix.md (misal: perbedaan arah pembulatan `mulDivDown` vs `mulDivUp`, atau biaya yang dihitung di preview tetapi tidak dipotong di fungsi eksekusi).

### Metode 5 — Guard-Inversion (Membalik Guard Kode Menjadi Target Manipulasi)
Setiap kali menemukan `require(Kondisi_X >= Kondisi_Y)` atau `if (...) revert`:
- Jangan langsung berhenti! Tanyakan: *"Variabel apa yang menyusun Kondisi_X dan Kondisi_Y? Berdasarkan 02-state-and-var-matrix.md, bisakah fungsi publik lain (atau flashloan/donasi/callback) mengubah nilai X atau Y sesaat sebelum baris require ini dieksekusi?"*
- *(Pada Putaran 2, gunakan metode ini secara khusus untuk membongkar seluruh daftar guard yang terkumpul di audit/04-code-guarded.md).*

### Metode 8 — Caller-Callee Assumption Seam & Direct Pool Bypass (Celah Lempar Tanggung Jawab)
Auditor memeriksa Kontrak_A (Router/Gateway/Manager) dan Kontrak_B (Pool/Vault/Strategy/Engine) secara terpisah dan menganggap keduanya aman:
1. **Unvalidated Seam:** Periksa titik panggilan Kontrak_A -> Kontrak_B. Apakah Kontrak_A meneruskan parameter (`receiver`, `from`, `onBehalfOf`, `token`, `data`) tanpa validasi karena mengira Kontrak_B akan memvalidasinya, sementara Kontrak_B percaya buta karena panggilan datang dari Kontrak_A?
2. **Direct Downstream Bypass:** Jika validasi keamanan (slippage, whitelist, fee, access check) ditaruh di Router/Periphery, periksa apakah penyerang dapat memanggil fungsi publik di kontrak inti (Pool/Vault/Strategy) secara langsung tanpa melewati Router.

### Metode 9 — Half-Baked / Suspended Lifecycle State (Menyerang Saat Status "Menggantung")
Auditor menguji siklus hidup yang selesai tuntas (Request -> Finalize). Anda WAJIB menguji siklus yang sengaja dihentikan di tengah jalan:
- Mulai Langkah 1 dari proses multi-tahap (misal: `requestWithdraw`, `initiateCooldown`, `createOrder`, `startAuction`, `propose`, atau kirim pesan async tahap pertama).
- JANGAN jalankan langkah penyelesaiannya. Saat akun/objek masih berada dalam status *"Pending / Menggantung"* tersebut, panggil fungsi jalur lain (transfer, delegate, borrow, liquidate, emergencyWithdraw, atau cancel berulang) untuk memeriksa apakah saldo/jaminan yang sedang menggantung belum dikunci sehingga bisa dipakai dua kali (*double-spend*).

### Metode 10 — Live On-Chain Residue, Router Allowance, & Upgrade Storage Drift
Auditor menguji pada *sandbox* kosong (`setUp()` bersih), sedangkan kontrak di produksi memiliki residu state nyata:
1. **Unspent Allowance & Stranded Balance Arbitrage:** Periksa apakah kontrak Router/Helper/Migrator/Adapter memiliki fungsi panggilan eksternal terbuka (`call`, `transferFrom`, `sweep`, `swap` dengan parameter alamat bebas) yang dapat disalahgunakan untuk menarik saldo token yang mengendap di kontrak atau menyedot allowance pengguna aktif di mainnet.
2. **Proxy Upgrade & Uninitialized Re-Config Drift:** Jika kontrak menggunakan Proxy/Upgradeable, periksa apakah ada variabel state baru pada versi implementasi saat ini yang berasumsi sudah terisi di konstruktor, padahal pada state proxy produksi nilainya masih 0 (atau berbenturan dengan nilai lama dari versi sebelumnya).

---

## TAHAP B: Pengayaan Analogi Mekanis & Katalog Attacker POV ([POV-XX])
Panggil skill_view("sc-phase2-hunt", "<nama-file-ref>") sesuai tag [LOAD: ...]:
1. Terjemahkan konsep di dalam referensi domain sebagai Pola Mekanis Abstrak lintas domain.
2. Buka bagian `## Katalog Generalized Attacker POV & Auditor Blindspots` di **file referensi domain yang baru Anda muat** (mis. `ref-math-and-vaults.md`). Cocokkan apakah **Kondisi Prasyarat** terpenuhi dan **Gejala di Kode** pada item `[POV-XX]` hadir pada fungsi yang sedang Anda bedah — terutama kolom *Auditor Blindspot*, karena di situlah peluangnya berada. Untuk mencari POV yang tidak ada di file tersebut, lihat indeks lokasi di `references/ref-attacker-pov.md`.
   - **Fallback wajib:** bila tidak ada POV yang cocok di seluruh katalog, JANGAN mengarang nomor POV. Turunkan ke analogi mekanis bebas (butir 1) dan catat di `audit/notes/` bahwa katalog untuk pola tersebut belum tersedia. *(Katalog POV diisi bertahap — ketiadaannya bukan cacat, jangan "diperbaiki" dengan entri karangan.)*

---

## TAHAP C: Pemisahan Murni (04-code-guarded.md vs 05-raw-leads.md)
Di Fase 2, Anda adalah Pemburu (Hunter), bukan Hakim Ekonomi. Jangan membuang anomali hanya karena terlihat kecil sendirian (karena akan dirangkai menjadi *attack chain* di Putaran 2 atau diuji amplifikasinya di simulasi Fase 3):
1. **Dua Larangan Fakta Dasar Kode:** Jangan mengarang sifat palsu pada Token Kasta 1 (LP/Share token = ERC-20 standar, bukan *Fee-on-Transfer*/USDT) dan jangan mengasumsikan penyerang bisa memanggil fungsi onlyOwner secara langsung.
2. **Jika Ditemukan Anomali yang Tidak Dihentikan Guard** (atau Guard Bisa Ditembus via Metode 5):
   Tulis langsung ke `audit/05-raw-leads.md` sesuai template `verify/templates/05-raw-leads.md` lengkap dengan: Metode Pencarian (Metode 1..Metode 10 dan/atau `[POV-XX]`), File:Kontrak:Fungsi (Baris), Delta State (Expected vs Actual), Urutan Eksploitasi, dan Potensi Rantai Serangan (Chaining).
3. **Jika Hipotesis Benar-Benar Dihentikan oleh Guard Kode** (`require` / `if (...) revert` / `assert!`):
   Tulis langsung ke `audit/04-code-guarded.md` sesuai template `verify/templates/04-code-guarded.md` lengkap dengan: File:Baris, Ekspresi Guard, Variabel Pembentuk, Penulis Variabel (rujuk 02-state-and-var-matrix.md), Hipotesis yang Dihentikan, dan Status Putaran 2: `BELUM`.
4. Tandai kelompok fungsi di audit/03-attack-surface-queue.md menjadi [HUNTED].
