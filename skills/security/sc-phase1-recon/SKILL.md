---
name: sc-phase1-recon
description: Phase 0 & 1 — Domain-Agnostic Recon, Production Environment Fact Mapping, Counter-Auditor Surface Discovery, and State-Mutation Matrix.
version: 6.0.0
---

# Phase 0 & 1: Domain-Agnostic Recon & Production Fact Mapping

Di Fase 0 dan Fase 1, peran Anda murni sebagai Pemeta Fakta Objektif (*Cartographer*) — bukan Hakim Penolak. DILARANG menyaring/membuang anomali secara prematur, dan DILARANG mendelegasikan pekerjaan Fase 1 ke subagent lain (Fase 1 dikerjakan oleh agent yang menerimanya; bila `sc-autopilot` yang menugaskan, pekerjaan berhenti di sini — jangan pecah lagi).
Buat direktori `audit/notes/` dan hasilkan 5 file fondasi di `audit/` (`00`, `00b`, `01` s/d `03`, serta inisialisasi `05-raw-leads.md`).

---

## Langkah 0: Enumerasi Fisik & Partisi Domain (WAJIB SEBELUM LANGKAH 1)

**Gerbang keras:** DILARANG memilih sampel, merumuskan hipotesis, atau menulis `03-attack-surface-queue.md` sebelum seluruh peta fisik repositori tertulis di `audit/00b-file-inventory.md`. Jika berkas itu belum ada, pekerjaan Fase 1 berhenti di sini.

### 1. Hitung Populasi Penuh
Jalankan enumerasi seluruh berkas kontrak di dalam scope. Abaikan `test/`, `mock/`, `script/`. Untuk setiap berkas ukur:
- **LOC** efektif (baris bukan kosong/komentar)
- **Jumlah fungsi eksternal/publik yang mengubah state**
- **Path relatif** terhadap akar repo

Wajib mencetak TOTAL populasi di kepala berkas: `N berkas | M LOC | K fungsi state-changing`. Angka ini menjadi pembanding tetap untuk seluruh fase berikutnya.

**Deduplikasi wajib:** salinan terverifikasi (`verified-deployed/`, `spoke-verified/`, `v5-verified/`) yang SHA-256-nya identik dengan berkas kanonik **dihitung sekali**. Tanpa dedup, populasi membengkak puluhan persen dengan kode yang sama.

### 2. Kelompokkan ke Domain Arsitektur
Pecah hasil enumerasi ke dalam domain/modul. Penamaan mengikuti arsitektur proyek; contoh generik:
- `D1: Hub-Pool` — kolam pusat, akuntansi lintas-rantai
- `D2: Spoke-Pools` — kolam per-rantai, penyimpanan dana
- `D3: Chain-Adapters` — adapter rantai, jembatan pesan
- `D4: Periphery-Mintburn` — mint/burn, OFT, CCTP
- `D5: Periphery-Counterfactual` — deposit counterfactual
- `D6: SVM/Solana` — program Solana
- `D7: TRON` — kontrak TRON
- `D8: Periphery-Umum` — pintu masuk pengguna, multicall, handler
- `Dn: …` — domain tambahan sesuai proyek

### 3. Klasifikasi Status Cakupan per Berkas
Setiap berkas di `00b-file-inventory.md` **WAJIB** diberi tepat satu label. **DILARANG memakai ambang baris kaku** (mis. ">200 LOC") sebagai penentu: router/adapter tipis 60 baris yang merutekan dana sama kritisnya dengan kontrak 900 baris.
- `[MUST-AUDIT]` — **salah satu** terpenuhi: mengubah state, memegang/merutekan dana, memvalidasi pesan lintas-rantai, mengeksekusi alur (router/adapter/executor/handler), atau melakukan panggilan eksternal/CPI. **Penentunya perilaku, bukan ukuran.**
- `[STATELESS/INTERFACE]` — murni tipe data, konstanta, `interface`/`IDL` tanpa isi, atau berkas deklarasi. Wajib diverifikasi silang bila dipanggil oleh `[MUST-AUDIT]`: berkas tanpa state yang menjadi hitungan dana (`Math`, `FixedPoint`, `SafeCast`) tetap masuk cakupan uji tidak langsung.

**LOC hanya penanda prioritas relatif, bukan gerbang.** Tidak ada berkas yang lolos dari audit karena kecil.

### 4. Aturan Anti-Bias Pintu Masuk
**DILARANG** menyusun antrean hanya dari satu folder/domain. Setiap domain `D1..Dn` yang memiliki berkas `[MUST-AUDIT]` **WAJIB** terwakili.

**DILARANG memakai kuota "minimal N lead per domain".** Kuota lead memicu pembuatan lead sampah pada modul yang memang aman (hukum Goodhart). Penggantinya adalah kewajiban jejak di Fase 2: >= 80% berkas `[MUST-AUDIT]` per domain harus berstatus `LEAD_GENERATED` **atau** `ATTESTED_CLEAN` — modul aman dipenuhi dengan *Negative Attestation* jujur, bukan lead palsu.

**DILARANG pendalaman dini:** DILARANG membelanjakan lebih dari 1 putaran penuh Fase 2 pada satu berkas sebelum setiap domain `D1..Dn` memiliki minimal satu jejak (lead atau atestasi).

**Berkas `[MUST-AUDIT]` terbesar per domain wajib dibuka.** Status setiap berkas dicatat: `BELUM` / `DIBACA` / `LEAD_GENERATED` / `ATTESTED_CLEAN`.

---

## Langkah 1: Environment, Production Lifecycle, & Build Sanity -> `audit/00-project-map.md`
1. **Deteksi Bahasa, Paradigma Rantai, & Build Ringan:**
   - Identifikasi ekosistem proyek: Paradigma A (Atomic EVM/Tron/Solana), Paradigma B (Object/Move Sui/Aptos), atau Paradigma C (Async Actor TON).
   - Uji kompilasi/tes awal dengan worker tunggal: FOUNDRY_JOBS=1 (forge test -j 1), CARGO_BUILD_JOBS=1, atau RAYON_NUM_THREADS=1.
   - Periksa ketersediaan konfigurasi RPC di ./rpc-env.sh / .env.rpc untuk kebutuhan simulasi *Local Fork* di Fase 3.
   - Unduh/ekstrak toolchain besar: **DILARANG ke `/tmp`** bila `df -h /tmp` menunjukkan tmpfs. Ekstraksi >500 MB wajib ke disk nyata (mis. `~/.tools`), lalu set `CARGO_TARGET_DIR` ke disk yang sama.
   - **Build lintas-arsitektur:** untuk program non-EVM (Solana SBF/eBPF), build lokal yang sah HANYA lewat `cargo-build-sbf`. `cargo build --release` menghasilkan shared object host (aarch64/x86_64) yang **tidak sebanding** dengan bytecode on-chain. Wajib cek `file` pada kedua binari sebelum membandingkan ukuran.
2. **Pemetaan Fakta Siklus Hidup Produksi** (Data Faktual untuk Fase 3 & 4):
   - Periksa skrip deploy/, script/, migrations/, dan konstruktor/factory.
   - Catat secara faktual: (a) apakah fungsi `initialize()` sudah dieksekusi secara atomik saat deployment, (b) apakah kontrak mencetak *dead shares* awal atau sudah memiliki TVL *live* di produksi (sehingga `totalSupply == 0` sudah terlewati), dan (c) mana kontrak yang Aktif In-Scope, mana yang masih Pre-Live / Paused, serta mana yang *mock/deprecated*.
3. **5–8 Core System Invariants (General-Deterministic):**
   - Rumuskan 5–8 hukum kekekalan nilai dan konsistensi state mutlak dari proyek ini (misal: Total Klaim <= Total Aset Riil, Keluar(Masuk(x)) <= x, atau Setiap perubahan kewajiban wajib diikuti sinkronisasi indeks).

---

## Langkah 2: Threat Surface, Fakta Lingkungan, & Jejak "Patch-Scar" -> `audit/01-threat-and-env.md`
Jangan menyalin kode mentah. Dokumentasikan fakta lingkungan produksi secara objektif sebagai acuan bersama:
1. **Klasifikasi 3 Kasta Realitas Aset:**
   - **Kasta 1 — Token/Entitas Internal & Deterministik** (LP Token, Share/Receipt Token, Token Protokol, WETH): Catat bahwa kodenya adalah kontrak internal/ERC-20 standar (tidak memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau anomali return bool ala USDT).
   - **Kasta 2 — Token Eksternal Whitelist Produksi:** Daftar aset eksternal yang benar-benar diizinkan di produksi beserta sifat nyatanya (misal: desimal 6/8, *blacklistable* pada USDC/USDT, tidak mengembalikan bool pada transfer USDT namun biaya transfernya 0).
   - **Kasta 3 — Input/Token Permissionless:** Tandai fungsi mana yang mengizinkan pengguna memasukkan alamat token/pool/hook kustom secara bebas, dan apakah ia berinteraksi dengan dana kolam bersama (*shared pool*) atau terisolasi.
2. **Peta Peran, Pintu Samping (Periphery), & Batas Otoritas:**
   - Petakan seluruh titik masuk pengguna eksternal tak berizin (unprivileged), termasuk pintu samping yang sering luput dari auditor: fitur multicall/batch, `address(this)` self-call, migrate/rescue/sweep/emergency, callback (`onERC721Received`/hooks), dan verifikasi signature/session-key.
   - Petakan fungsi khusus berizin (onlyOwner/Admin/DAO/Keeper) beserta parameter state yang dapat diubahnya.
3. **Fisika Rantai & Jejak Bekas Tambalan (*Patch-Scars / Custom Deltas*):**
   - Catat karakteristik rantai target (aturan gas, L2 sequencer, desimal native coin).
   - Deteksi *Patch-Scar*: Gunakan `git log` (jika ada) atau amati kode untuk menandai: (a) bagian library standar (ERC4626/Uniswap/Anchor/Move) yang dimodifikasi secara kustom oleh developer, dan (b) kondisi `if`/`require` khusus atau variabel pengunci tambahan yang terlihat seperti tambalan cepat di satu fungsi (untuk diperiksa di Fase 2 apakah fungsi pasangannya lupa ditambal).

---

## Langkah 3: State-Mutation & View-vs-Write Matrix -> `audit/02-state-and-var-matrix.md`
Gunakan search_files (rg -n) untuk memetakan seluruh variabel state/storage (mapping, struct, array, objek, atau akun):
1. Buat tabel matriks lacak-balik:
   Nama Variabel/Field | Fungsi Penambah (`+=`, `=`) | Fungsi Pengurang (`-=`, `delete`) | Fungsi View / Preview / Guard Pembaca.
2. Deteksi Dini 2 Titik Buta Auditor:
   - **Asimetri Mutasi Siklus Hidup:** Tandai variabel atau field struct yang dimodifikasi saat entitas masuk/dibuat, tetapi tidak di-reset/dikurangi pada jalur keluar, transfer, batal, klaim sebagian, atau likuidasi.
   - **Pasangan Rumus `View` vs `Write`:** Sandingkan fungsi view/pure penentu nilai (seperti `preview*`, `getAccountLiquidity`, `getPending*`, `getPrice`) dengan fungsi tulis yang memutasi state aslinya untuk diperiksa di Fase 2 apakah ada rumus yang tidak sinkron.

---

## Langkah 4: Primitive-Based Attack Surface Queue -> `audit/03-attack-surface-queue.md`
Susun seluruh fungsi yang mengubah state ke dalam Unit Alur Eksekusi.

### 4a. Flow-Cluster: Batas 40 Unit (WAJIB)
**DILARANG** membuat 1 Unit per 1 berkas jika hasilnya antrean meledak di atas **40 unit**. Antrean 183 unit identik dengan 183 berkas bukan audit — itu daftar berkas yang tidak akan pernah tuntas dieksekusi (bottleneck Fase 2/3).

Gabungkan berkas yang berada dalam **satu alur transaksi** di domain yang sama menjadi **satu Unit Alur Eksekusi `S-n`**. Contoh pola alur: `Router + Pool + Handler + Adapter`, atau `Periphery -> SpokePool -> Executor -> Adapter`, atau `program + CPI partner` (non-EVM).

**Format wajib setiap unit:**
```
## [S-n] <Nama Alur> — <Domain>
- Berkas tercakup: <daftar path [MUST-AUDIT] lengkap>
- LOC total: <n> | Fungsi state-changing: <n>
- Titik masuk unprivileged: <fungsi>
- [LOAD: ref-…md, ref-chain-…md]
- Status: BELUM / DIBACA / LEAD_GENERATED / ATTESTED_CLEAN
```

**Aturan agregasi:**
1. Setiap berkas `[MUST-AUDIT]` **wajib** muncul di **tepat satu** unit — tidak boleh hilang, tidak boleh ganda. Verifikasi jumlah berkas di antrean terhadap `00b-file-inventory.md`.
2. Cluster hanya boleh menggabungkan berkas yang **saling memanggil** atau berada dalam satu alur nilai; DILARANG menggabung sekadar karena satu folder.
3. Bila total unit masih >40 setelah clustering berbasis alur, prioritaskan cluster yang memuat dana terbesar dan tandai sisanya `DEFERRED` (bukan dihapus) beserta alasan.
4. Berkas `[MUST-AUDIT]` terbesar per domain **wajib** menjadi anggota cluster aktif — tidak boleh jadi unit tunggal yang `DEFERRED`.

### 4b. Urutan Prioritas
- `[P1-CRITICAL]` & `[P2-HIGH]`: Fungsi unprivileged (termasuk pintu samping migrate, batch, callback, dan area *Patch-Scar*) yang memindahkan nilai, menghitung proporsi/akrual, atau memicu transisi paksa.
- `[P3-ADMIN-OR-PERIPHERY]`: Fungsi operasional khusus Admin/Keeper (dicatat untuk pemeriksaan *admin-only bug* atau jalur eskalasi).

### 4c. Penempelan Tag Referensi `[LOAD: ...]` Wajib per Kelompok
- `[LOAD: ref-math-and-vaults.md]` -> Fungsi dengan operasi bagi/kali proporsi, share, pembulatan, biaya, atau akrual indeks waktu.
- `[LOAD: ref-calls-tokens-reentrancy.md]` -> Fungsi dengan panggilan eksternal, transfer token/NFT, callback, eksekusi batch/self-call, atau verifikasi signature.
- `[LOAD: ref-defi-oracles-liquidation.md]` -> Fungsi dengan pembacaan harga/oracle, swap, pinjaman, atau transisi paksa (likuidasi, lelang, penyitaan, slashing).
- Tambahkan tepat 1 tag rantai: `[LOAD: ref-chain-evm-tron.md]`, `[LOAD: ref-chain-solana.md]`, `[LOAD: ref-chain-sui-move.md]`, atau `[LOAD: ref-chain-ton-async.md]`.

---

## Langkah 5: Inisialisasi Antrean Aktif -> `audit/05-raw-leads.md`
Buat file `audit/05-raw-leads.md` dan catat setiap indikasi awal anomali mutasi state, *Patch-Scar*, atau ketidaksinkronan View vs Write yang ditemukan selama Langkah 0–4 tanpa melakukan penghakiman kelayakan ekonomi terlebih dahulu.

---

## Langkah 6: Gerbang Cakupan PEMETAAN ANTREAN (QUEUE MAPPING GATE) — WAJIB sebelum menutup Fase 1

**Fase 1 hanya memetakan, belum berburu.** Karena itu gerbang keluar Fase 1 **tidak menguji hasil Fase 2** (`LEAD_GENERATED`/`ATTESTED_CLEAN` belum ada saat Fase 1 ditutup). Yang diuji: apakah berkas `[MUST-AUDIT]` dari `00b-file-inventory.md` sudah **terpetakan masuk ke Unit Alur `S-n`** di `03-attack-surface-queue.md`.

Status yang sah di Fase 1: `BELUM` (belum masuk unit) -> `TERPETAKAN_DI_UNIT` (sudah tercakup antrean) atau `DEFERRED` (sengaja ditunda dengan alasan tertulis). `DIBACA` / `LEAD_GENERATED` / `ATTESTED_CLEAN` adalah status Fase 2 dan **tidak dipakai** sebagai ambang di sini.

Hitung dan tulis ke bagian akhir `05-raw-leads.md`:

| Metrik | Rumus | Ambang LULUS |
|---|---|---|
| **Ketercakupan antrean** | berkas `[MUST-AUDIT]` berstatus `TERPETAKAN_DI_UNIT` ÷ total `[MUST-AUDIT]` | **>= 80%** |
| **Non-DEFERRED penuh** | (`TERPETAKAN_DI_UNIT` + `DEFERRED` ber-alasan) ÷ total `[MUST-AUDIT]` | **= 100%** (tidak ada `BELUM`) |
| Cakupan domain | domain `D1..Dn` dengan >=1 berkas `TERPETAKAN_DI_UNIT` ÷ total domain ber-`[MUST-AUDIT]` | **100%** |
| Berkas raksasa | berkas `[MUST-AUDIT]` terbesar per domain | **wajib `TERPETAKAN_DI_UNIT`** |
| Ukuran antrean | jumlah Unit Alur Eksekusi | **<= 40** |
| Integritas agregasi | berkas di antrean unik | **0 hilang, 0 ganda** vs `00b` |
| **Integritas lingkungan** | `df -h` + `free -h` pada path kerja & toolchain | **disk >= 10 GB, RAM >= 4 GB** sebelum Fase 2 |

> **Dua angka, dua fungsi.** `>= 80%` adalah ambang *minimum kelayakan* pemetaan; `= 100% non-DEFERRED` memastikan tidak ada berkas yang hilang tanpa jejak — berkas yang belum masuk unit **wajib** berstatus `DEFERRED` beserta alasan, bukan dibiarkan `BELUM`.

> **DILARANG memakai "jumlah lead per domain" sebagai metrik kelulusan.** Kelulusan diukur dari **keterpetakan per berkas**, bukan banyaknya hipotesis — agar modul yang memang aman tidak dipaksa melahirkan lead palsu.

Bila **salah satu** ambang gagal: Fase 1 **DITOLAK**, kembali ke Langkah 0/4 dan perluas enumerasi atau clustering. DILARANG melanjutkan ke Fase 2 dengan gerbang gagal.

**Pembagian tanggung jawab gerbang — jangan tertukar:**

| Fase | Gerbang | Yang diuji | Ambang |
|---|---|---|---|
| **1** (Langkah 6) | Queue Mapping Gate | berkas `[MUST-AUDIT]` masuk Unit `S-n` | >= 80% terpetakan, 100% non-DEFERRED, domain 100%, unit <= 40 |
| **2** (Gate Keluar) | Trace Gate | berkas per domain berstatus `LEAD_GENERATED` / `ATTESTED_CLEAN` | >= 80% **per domain** |
| **4** (Langkah 0a) | Dual Gate | keduanya diperiksa ulang | (1) + (2) |

**Catatan pengukuran:** pengukur cakupan (`00b-file-inventory.md`) WAJIB dieksklusi dari populasi yang diukur. Tanpa eksklusi, setiap berkas "disebut" oleh inventarisnya sendiri dan cakupan selalu tampak 100%.

**Alasan aturan ini:** tanpa pengukuran, agen akan menyusut ke satu jalur yang paling menarik perhatian dan menyebutnya "audit mendalam". Sampling yang tidak diakui sebagai sampling adalah kegagalan yang tidak terdeteksi.
