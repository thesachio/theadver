---
name: sc-phase2-hunt
description: Phase 2 — Counter-Auditor Adversarial Hunting (10 Non-Standard Lenses + First-Principles Foundation + Generalized Attacker POV) with Pure Code-Guard Separation (04 vs 05).
version: 6.0.0
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

---

## Aturan Anti-Tunnel-Vision: Rotasi Domain & Clean-Unit Attestation

Kuota "minimal N lead per domain" **DILARANG** dipakai: memaksa jumlah lead mendorong agen mengarang hipotesis lemah hanya untuk memenuhi angka (hukum Goodhart). Yang dipaksa adalah **Penyapuan Merata (Breadth-First Sweep)** plus **bukti bahwa unit benar-benar diperiksa**.

### 1. Rotasi Domain Wajib
Pada Putaran 1 dan Putaran 2, eksekusi Unit Alur Eksekusi secara **bergilir lintas domain** (`D1 -> D2 -> D3 -> … -> D1`), **BUKAN** menghabiskan satu folder lalu berhenti. Satu putaran penuh = setiap domain ber-`[MUST-AUDIT]` mendapat giliran sebelum domain mana pun mendapat giliran kedua. Pelanggaran rotasi = putaran dibatalkan dan diulang.

### 2. Kewajiban Jejak Audit (Lead ATAU Negative Attestation)
Setiap berkas `[MUST-AUDIT]` dan setiap Unit Alur `S-n` **tidak boleh dilewati tanpa jejak**. Pilih tepat satu hasil:
- **`LEAD_GENERATED`** — ditemukan celah potensial: tulis ke `audit/05-raw-leads.md` (template penuh).
- **`ATTESTED_CLEAN`** — setelah diuji dengan 10 Metode tidak ditemukan celah: tulis **1 baris Negative Attestation** di tabel cakupan `audit/03-attack-surface-queue.md`.

**Format Negative Attestation (wajib 4 unsur — tanpa keempatnya, atestasi ditolak):**
```
<Berkas>: <jumlah> fungsi mutasi dicek dengan Metode <X, Y, Z> —
  mengapa invariant bertahan: <alasan teknis konkret>
  jalur eksternal yang diuji: <daftar jalur/callback/CPI yang benar-benar disentuh>
  jalur yang TIDAK diuji: <daftar, atau "tidak ada">
```

**Larangan atestasi kosong.** Kalimat berikut **DILARANG** dan otomatis ditolak: *"sudah diperiksa, aman"*, *"kode standar"*, *"tidak ada masalah ditemukan"*, *"mengikuti OpenZeppelin/Anchor"*. Atestasi wajib menyebut **nama fungsi yang diperiksa**, **nomor Metode**, dan **mekanisme konkret** yang membuat invariant bertahan.

**Atestasi tidak boleh lebih murah daripada lead.** Bila alasan yang bisa ditulis hanyalah "tidak ada yang mencurigakan", itu tanda unit **BELUM** benar-benar diperiksa — kembalikan ke `BELUM` dan jalankan Metode yang belum dipakai.

### 3. Gate Keluar Fase 2
Agen **DILARANG** pindah ke Fase 3 sebelum **>= 80% berkas `[MUST-AUDIT]` di SETIAP domain** berstatus `LEAD_GENERATED` **atau** `ATTESTED_CLEAN`.

| Metrik | Ambang |
|---|---|
| Berkas `[MUST-AUDIT]` berjejak **per domain** | **>= 80%** (setiap domain, tanpa kecuali) |
| Berkas `[MUST-AUDIT]` terbesar per domain | wajib != `BELUM` |
| Berkas berstatus `BELUM` di domain mana pun | **0** |

**DILARANG memakai kuota "minimal N lead per domain" sebagai metrik kelulusan.** Kelulusan diukur dari **jejak per berkas**, bukan banyaknya hipotesis — agar modul yang memang aman tidak dipaksa melahirkan lead palsu; *Negative Attestation* yang jujur justru bukti cakupan yang sah.

Gagal satu sel tabel = Fase 2 **DITOLAK**, kembali ke rotasi domain.

**Pencatat status:** hasil atestasi ditulis ke `audit/03-attack-surface-queue.md` sebagai tabel cakupan per domain, direkonsiliasi dengan `audit/00b-file-inventory.md`. Status sah: `BELUM` / `DIBACA` / `LEAD_GENERATED` / `ATTESTED_CLEAN`.

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

### Metode 3 — Irrational Multi-Identity Sybil & Zero-Time Loop (Aksi "Tidak Masuk Akal" bagi Pengguna Normal)

**Prinsip:** Auditor menguji alur pengguna waras. Anda WAJIB menguji perilaku "tidak rasional" yang hanya mungkin bila **dua atau lebih identitas/akun/objek/kapabilitas yang dikendalikan satu penyerang** berinteraksi secara atomik atau dalam jendela eksekusi yang sama ($\Delta t = 0$). Kerugian di satu identitas boleh terjadi asal keuntungan di identitas lain lebih besar — penyerang tidak peduli "kantong" mana yang rugi.

**Contoh EVM:** dua EOA milik penyerang (`Attacker_A`, `Attacker_B`) dalam 1 transaksi.

**Padanan non-EVM:** **Solana** — dua signer, atau satu signer + account alias/duplicate account · **Move** — dua capability atau dua object milik satu owner · **TON** — dua actor, atau dua jalur message dari actor yang sama.

**Langkah uji:**
1. **Self-Transfer & Ping-Pong Loop:** Apa yang terjadi jika identitas pertama memindahkan/mendelegasikan hak ke dirinya sendiri (`from == to`) atau memantulkannya A -> B -> A berulang kali dalam jendela eksekusi yang sama?
2. **Self-Liquidation / Self-Penalty Arbitrage:** Apa yang terjadi jika identitas pertama sengaja membuat posisinya terkena likuidasi/slashing/lelang/bad-debt, sementara identitas kedua bertindak sebagai likuidator/penawar yang memanen bonus atau mengalihkan kerugian (*bad debt socialization*) ke kolam publik?
3. **Zero / Boundary & Dust Amplification:** Masukkan nilai 0, 1 unit terkecil, atau `batas_minimum - 1` untuk menguji apakah biaya/penalti terpotong jadi 0 karena pembulatan dan dapat di-loop dalam satu batch/multicall.

### Metode 6 — Stale Local-Snapshot Write-Back & Duplicate-Reference Aliasing (`[A, A]`)

**Prinsip A — Snapshot basi ditulis balik:** Sebuah salinan state dibuat lokal, lalu di tengah eksekusi terjadi interaksi eksternal (callback/panggilan ke modul lain) yang mengubah state persisten yang sama, dan di akhir salinan lokal ditulis kembali — sehingga perubahan terbaru terhapus senyap. Yang dicari bukan nama tipe atau kata kunci bahasanya, melainkan **urutan baca-lokal -> mutasi-persisten -> tulis-balik**.

**Contoh EVM:** `Struct memory s = map[user]` -> panggil callback yang mengubah `map[user]` -> `map[user] = s`.

**Padanan non-EVM:** **Solana** — account data dibaca sebelum CPI, ditulis balik tanpa `.reload()` · **Move** — objek di-*unpack*, dipakai lintas call, lalu di-*pack* ulang dengan nilai lama · **TON** — `c4`/`c5` dibaca sebelum mengirim pesan, lalu disimpan setelahnya.

**Prinsip B — Referensi kembar diproses dua kali:** Satu referensi yang sama muncul lebih dari sekali dalam satu input dan diproses berulang, karena validasi/pembacaan saldo terjadi sebelum mutasi di dalam loop.

**Contoh EVM:** `claim([1, 1])`; dedup biasanya `ids[i] < ids[i+1]` atau bitmap.

**Padanan non-EVM:** duplicate account, repeated `remaining_accounts`, duplicate recipient, resource/object reference kembar.

**Langkah uji:**
1. Cari fungsi yang menyalin struktur/saldo ke variabel lokal, memanggil keluar, lalu menulis balik ke state persisten di akhir.
2. Pada setiap fungsi ber-parameter daftar, uji input dengan elemen kembar `[A, A]`. Periksa apakah ada deduplikasi sebelum mutasi.

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

### Metode 8 — Caller-Callee Assumption Seam & Direct Downstream Bypass (Celah Lempar Tanggung Jawab)

**Prinsip:** Dua lapisan komponen (hulu dan hilir) masing-masing menganggap lapisan lain sudah memvalidasi. Yang menentukan bukan nama modifier, melainkan dua pertanyaan: **(a) apakah jalur hilir benar-benar membatasi caller yang sah, dan (b) apakah jalur hilir mengulang seluruh validasi kritis** — atau hanya mempercayai bahwa pemanggil hulu sudah melakukannya.

**Contoh EVM:** hulu `Router/Gateway/Manager`, hilir `Pool/Vault/Strategy`; pembatasan lazim `onlyRouter` / `onlyManager`.

**Padanan non-EVM:** **Solana** — CPI dari program lain vs instruksi yang dipanggil langsung tanpa signer · **Move** — fungsi yang menuntut capability (`RouterCap`) vs `public entry` bebas · **TON** — pesan dari kontrak resmi vs pesan eksternal.

**Langkah uji:**
1. **Unvalidated Seam:** Pada titik panggilan hulu -> hilir, apakah hulu meneruskan parameter (`receiver`, `from`, `onBehalfOf`, `token`, `data`) tanpa validasi karena mengira hilir akan memvalidasinya — sementara hilir percaya buta karena panggilan datang dari hulu?
2. **Direct Downstream Bypass:** Jika validasi keamanan (slippage, whitelist, fee, access check) hanya ada di hulu, periksa apakah penyerang dapat memanggil fungsi publik hilir secara langsung tanpa melewati hulu.

### Metode 9 — Half-Baked / Suspended Lifecycle State (Menyerang Saat Status "Menggantung")
Auditor menguji siklus hidup yang selesai tuntas (Request -> Finalize). Anda WAJIB menguji siklus yang sengaja dihentikan di tengah jalan:
- Mulai Langkah 1 dari proses multi-tahap (misal: `requestWithdraw`, `initiateCooldown`, `createOrder`, `startAuction`, `propose`, atau kirim pesan async tahap pertama).
- JANGAN jalankan langkah penyelesaiannya. Saat akun/objek masih berada dalam status *"Pending / Menggantung"* tersebut, panggil fungsi jalur lain (transfer, delegate, borrow, liquidate, emergencyWithdraw, atau cancel berulang) untuk memeriksa apakah saldo/jaminan yang sedang menggantung belum dikunci sehingga bisa dipakai dua kali (*double-spend*).

### Metode 10 — Live Residual State, Delegated Authority, & Post-Upgrade Drift

**Prinsip:** Auditor menguji pada *sandbox* bersih, sedangkan sistem di produksi membawa **state sisa yang nyata**: otorisasi tertunda yang belum terpakai, saldo/objek aset yang tertinggal, dan konfigurasi usang setelah peningkatan/migrasi. Tiga hal ini tidak muncul di `setUp()` yang kosong — harus dibaca dari state live lebih dulu.

**Contoh EVM:** `allowance`/`approve` yang belum terpakai · saldo token mengendap di Router/Helper/Migrator · slot proxy EIP-1967 dan variabel implementasi baru yang masih 0.

**Padanan non-EVM:** **Solana** — delegated authority/capability pada token account, saldo mengendap di PDA, data akun lama setelah program upgrade · **Move** — capability tertunda, object aset tertinggal, field baru yang belum terisi setelah migrasi · **TON** — saldo tersisa di kontrak perantara, konfigurasi actor yang tidak sinkron setelah upgrade.

**Tabel padanan istilah:**

| Istilah EVM | Konsep umum |
|---|---|
| `allowance` / `approve` | otorisasi tertunda yang belum terpakai |
| `cast call` / `eth_getStorageAt` | pembacaan state live sebelum menulis PoC |
| saldo mengendap di kontrak | *residual balance* / *asset object* tertinggal |
| slot proxy EIP-1967 | *storage slot* / *object field* / *account data* / *actor state* |
| konfigurasi usang pasca-upgrade | *stale configuration* setelah migrasi |

**Langkah uji:**
1. **Delegated Authority & Residual Balance:** Apakah komponen perantara (Router/Helper/Migrator/Adapter) memiliki panggilan eksternal terbuka (`call`, `transferFrom`, `sweep`, `swap` dengan parameter alamat bebas) yang dapat menarik saldo tertinggal atau menyedot otorisasi pengguna aktif?
2. **Post-Upgrade Drift:** Setelah peningkatan/migrasi, apakah ada variabel/field baru yang berasumsi sudah terisi saat inisialisasi padahal pada state produksi masih 0 — atau berbenturan dengan nilai lama dari versi sebelumnya?

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
4. Tandai kelompok fungsi di audit/03-attack-surface-queue.md menjadi `[HUNTED]`.
5. **Wajib tulis status jejak** pada tabel cakupan: `LEAD_GENERATED` (butir 2) atau `ATTESTED_CLEAN` (butir 3, dengan 4 unsur atestasi lengkap). Kelompok tanpa keduanya tetap `BELUM` dan **memblokir Gate Keluar Fase 2**.
