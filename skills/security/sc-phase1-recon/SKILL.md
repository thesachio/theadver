---
name: sc-phase1-recon
description: Phase 0 & 1 — Domain-Agnostic Recon, 100% Physical Repo Population Inventory, Production Environment Fact Mapping, Counter-Auditor Surface Discovery, and State-Mutation Matrix.
version: 6.4.0
---

# Phase 0 & 1: Domain-Agnostic Recon & Production Fact Mapping

Di Fase 0 dan Fase 1, peran Anda murni sebagai Pemeta Fakta Objektif (*Cartographer*) — bukan Hakim Penolak. DILARANG menyaring/membuang anomali secara prematur, dan DILARANG mendelegasikan pekerjaan Fase 1 ke subagent lain (Fase 1 dikerjakan oleh agent yang menerimanya; bila `sc-autopilot` yang menugaskan, pekerjaan berhenti di sini — jangan pecah lagi).
Buat direktori `audit/notes/` dan hasilkan 5 file fondasi di `audit/` (`00`, `00b`, `01` s/d `03`, serta inisialisasi `05-raw-leads.md`).

**GERBANG TULIS (WAJIB):** sebelum menulis satu byte pun ke `audit/*.md`, baca **`workspace/AGENTS.md` Pasal 1.3 (Protokol Anti-Truncate & Metode Write)**. `open(path,"w")` dan `>` shell **DILARANG** untuk seluruh `audit/*.md` — keduanya memotong file ke 0 byte saat dibuka. Gunakan `write_file`/`patch`/`append`, atau skrip dengan pola `.tmp` → `fsync` → `os.replace()`.

---

## Pra-Langkah 0: Baca `audit/INTEL.md` (Fase 0 — bila ada)

Periksa keberadaan `audit/INTEL.md` (hasil Fase 0 `sc-project-intel`).

- **Jika ada** → baca lebih dulu dengan `read_file`, tangkap dua hal:
  (a) daftar repositori/kontrak **in-scope** dari link Bug Bounty (Bagian 3 INTEL) — dipakai untuk memberi **tag metadata eligibilitas** (`[LIVE_BOUNTY]` vs `[REPO_STAGED]`) pada `00b-file-inventory.md` (**DILARANG** dipakai untuk membuang/mengecualikan kontrak repo dari `00b`!),
  (b) daftar **laporan audit masa lalu** (Bagian 4 INTEL) — dipakai memandu pelacakan *Patch-Scar* di Langkah 2.
- **Jika belum ada** → Fase 1 berjalan normal dari Langkah 0 tanpa berhenti (INTEL opsional, bukan gerbang pemangkas).

---

## Langkah 0: Enumerasi Fisik 100% Populasi Repo & Partisi Domain (WAJIB SEBELUM LANGKAH 1)

**Gerbang keras:** DILARANG memilih sampel, mengecualikan kontrak karena "belum ada di halaman bounty", merumuskan hipotesis, atau menulis `03-attack-surface-queue.md` sebelum **100% peta fisik repositori** tertulis di `audit/00b-file-inventory.md`. Jika berkas itu belum ada, pekerjaan Fase 1 berhenti di sini.

### 1. Hitung Populasi Penuh (100% Kontrak Fisik Repo)
Jalankan enumerasi **seluruh** berkas kontrak di dalam repositori target. Hanya abaikan folder pengujian/skrip murni (`test/`, `tests/`, `mock/`, `mocks/`, `script/`, `scripts/`, `lib/` pihak ketiga standar). Untuk setiap berkas kontrak di repositori, ukur:
- **LOC efektif** (baris bukan kosong/komentar)
- **Jumlah fungsi eksternal/publik yang mengubah state**
- **Path relatif** terhadap akar repo
- **Tag Status Deployment/Bounty (Metadata Fase 4):** `[LIVE_BOUNTY]` (bila terkonfirmasi aktif di produksi/bounty) atau `[REPO_STAGED]` (bila belum ada di daftar bounty / masih HEAD-only). **Ingat: baik `[LIVE_BOUNTY]` maupun `[REPO_STAGED]` tetap dihitung penuh di dalam populasi!**

Wajib mencetak TOTAL populasi di kepala berkas: `N berkas | M LOC | K fungsi state-changing`. Angka ini menjadi **penyebut tetap** untuk seluruh fase berikutnya.

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
- `[MUST-AUDIT]` — **salah satu** terpenuhi: mengubah state, memegang/merutekan dana, memvalidasi pesan lintas-rantai, mengeksekusi alur (router/adapter/executor/handler), melakukan panggilan eksternal/CPI, **ATAU merupakan berkas `library` / modul `pure`/`view` internal yang berisi logika perhitungan matematika/proporsi/bitwise (`Math`, `FullMath`, `TickMath`, `SqrtPriceMath`, `FixedPoint`), verifikasi kriptografi/merkle/signature, atau dekode byte/pesan kustom!** Penentunya adalah **keberadaan logika eksekusi/perhitungan di dalam berkas**, **BUKAN** apakah ia memiliki variabel storage sendiri dan **BUKAN** apakah sudah masuk halaman Bug Bounty (`[LIVE_BOUNTY]` maupun `[REPO_STAGED]` **tetap wajib `[MUST-AUDIT]`**).
- `[STATELESS/INTERFACE]` — **HANYA** untuk berkas yang murni deklarasi interface/trait/IDL tanpa isi implementasi, definisi tipe data/struct/enum murni, error kustom, atau konstanta alamat statis tanpa logika perhitungan. **DILARANG KERAS melabeli library matematika, dekoder payload, atau validator signature sebagai `[STATELESS/INTERFACE]` hanya karena tidak memiliki fungsi state-changing!**

**LOC hanya penanda prioritas relatif, bukan gerbang.** Tidak ada berkas yang lolos dari audit karena kecil.

### 3b. Kolom Identitas Deployment di `00b` (WAJIB — Gerbang Siklus Awal)

`00b-file-inventory.md` **WAJIB** memuat tabel identitas deployment di bagian atas, agar auditor tidak masuk Fase 3 tanpa tahu siklus hidup kontrak target:

| Kontrak | Alamat Live | `Siklus` | `Pola` | Sumber |
|---|---|---|---|---|
| `Nexus.sol` | `0x0000B1c0…8a5B` | `P3_LIVE_PARTIAL` | `fallback-router` | `cast code` |

- **`Siklus`** — salah satu dari `P1_PRE_DEPLOY` / `P2_TESTNET_ONLY` / `P3_LIVE_PARTIAL` / `P4_LIVE_FULL` / `P0_UNKNOWN`. Diisi dari `verify/tools/deploy_parity.py` atau minimal satu perintah `cast code` / `getAccountInfo`.
- **`Pola`** — `plain` / `proxy-eip1967` / `beacon` / `fallback-router` / `delegatecall` / `multi-kontrak` / `unknown`. Diisi bila terdeteksi; `unknown` sah bila belum diperiksa.
- **Alamat Live** boleh kosong untuk `P1_PRE_DEPLOY` — **jangan dikarang**.

**DILARANG** menyimpulkan siklus dari nama file/versi di `package.json`; siklus ditentukan oleh **keberadaan objek di rantai**, bukan oleh isi repo (repo bisa v1.2.1 sementara live v1.3.3).

### 4. Aturan Anti-Bias Pintu Masuk
**DILARANG** menyusun antrean hanya dari satu folder/domain. Setiap domain `D1..Dn` yang memiliki berkas `[MUST-AUDIT]` **WAJIB** terwakili.

**DILARANG memakai kuota "minimal N lead per domain".** Kuota lead memicu pembuatan lead sampah pada modul yang memang aman (hukum Goodhart). Penggantinya adalah kewajiban jejak di Fase 2: **100% berkas `[MUST-AUDIT]` per domain harus berstatus `LEAD_GENERATED` atau `ATTESTED_CLEAN`** (`0 BELUM`, `0 DEFERRED`) — modul aman dipenuhi dengan *Negative Attestation* jujur, bukan lead palsu.

**DILARANG pendalaman dini:** DILARANG membelanjakan lebih dari 1 putaran penuh Fase 2 pada satu berkas sebelum setiap domain `D1..Dn` memiliki minimal satu jejak (lead atau atestasi).

**Berkas `[MUST-AUDIT]` terbesar per domain wajib dibuka.** Status setiap berkas dicatat: `BELUM` / `DIBACA` / `LEAD_GENERATED` / `ATTESTED_CLEAN`.

---

## Langkah 1: Environment, Production Lifecycle, & Build Sanity -> `audit/00-project-map.md`
1. **Deteksi Bahasa, Paradigma Rantai, & Build Ringan:**
   - Identifikasi ekosistem proyek: Paradigma A (Atomic EVM/Tron/Solana), Paradigma B (Object/Move Sui/Aptos), atau Paradigma C (Async Actor TON).
   - **Hierarki Deteksi Rantai 3-Level (WAJIB — rujuk `sc-phase2-hunt/references/ref-attacker-pov.md` Bagian 3):** jangan menyimpulkan rantai dari ekstensi berkas saja.
     - **Level 1 — Ekstensi Berkas:** `.sol`/`.vy`/`.yul` · `.rs` · `.move` · `.fc`/`.func`/`.tact`/`.tolk`.
     - **Level 2 — Manifes Build (wajib cek):** `foundry.toml`/`hardhat.config.*` vs `Cargo.toml` (**pastikan ada `anchor-lang`/`solana-program`/`pinocchio` sebelum menyimpulkan Solana**) vs `Move.toml` (`Sui` vs `AptosFramework`) vs `blueprint.config.ts`/`tact.config.json`.
     - **Level 3 — Sinyal Kode Spesifik:** `msg.value`/`delegatecall` vs `#[derive(Accounts)]`/`invoke_signed` vs `UID`/`TxContext` vs `recv_internal`/`send_raw_message`.
     - **Aturan Anti-Tebak (`CHAIN: AMBIGUOUS`):** bila berkas `.rs` **bukan** program Solana (CosmWasm, NEAR, Substrate, daemon off-chain), WAJIB tulis `CHAIN: AMBIGUOUS (<nama_runtime>)` di `00-project-map.md` dan **DILARANG** memasang tag `[LOAD: ref-chain-solana.md]`.
   - Uji kompilasi/tes awal dengan worker tunggal: FOUNDRY_JOBS=1 (forge test -j 1), CARGO_BUILD_JOBS=1, atau RAYON_NUM_THREADS=1.
   - Periksa ketersediaan konfigurasi RPC di ./rpc-env.sh / .env.rpc untuk kebutuhan simulasi *Local Fork* di Fase 3.
   - **Build lintas-arsitektur:** untuk program non-EVM (Solana SBF/eBPF), build lokal yang sah HANYA lewat `cargo-build-sbf`. `cargo build --release` menghasilkan shared object host (aarch64/x86_64) yang **tidak sebanding** dengan bytecode on-chain. Wajib cek `file` pada kedua binari sebelum membandingkan ukuran.
2. **Pemetaan Fakta Siklus Hidup Produksi & Rencana Dual-Mode Fork** (Data Faktual untuk Fase 3 & 4):
   - Periksa skrip `deploy/`, `script/`, `migrations/`, dan konstruktor/factory.
   - Catat secara faktual di `00-project-map.md`:
     (a) apakah fungsi `initialize()` sudah dieksekusi secara **atomik** saat deployment (baik pada proxy maupun implementation `_disableInitializers()`),
     (b) apakah kontrak mencetak *dead shares* awal atau sudah memiliki TVL *live* di produksi (serta apakah ada fungsi `Factory.create*` permissionless atau jalur penarikan penuh yang memungkinkan pool kembali ke `totalSupply == 0`),
     (c) **pemetaan alamat on-chain** untuk setiap kontrak: mana yang dapat diuji langsung dengan **`FORK_LIVE`** (kontrak aktif di mainnet) dan mana yang harus diuji di Fase 3 menggunakan **`FORK_DEPLOYED_HEAD`** (deploy kode repo HEAD di atas fork mainnet karena kontrak berstatus `[REPO_STAGED]` / HEAD-only / belum di-upgrade).
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
## [S-n] <Nama Alur Eksekusi> — <Domain D1..Dn>
- Berkas tercakup: <daftar path relatif>
- LOC total: <angka> | Fungsi state-changing: <angka>
- Topologi Entitas: [CLASS-A | CLASS-B | CLASS-C] — Entitas Utama: <...> | Entitas Berinteraksi: <...> | Panjang Alur: <1 / 2 / >=3>
- Titik masuk unprivileged: <daftar fungsi>
- [LOAD: ref-method-registry.md, ref-<domain>.md, ref-chain-<paradigma>.md, ref-attacker-pov.md]
- Status: BELUM / DIBACA / LEAD_GENERATED / ATTESTED_CLEAN
```

**Kelas Topologi Entitas (WAJIB — tepat satu label per unit; rujuk `sc-phase2-hunt/references/ref-method-registry.md` Bagian 1):**

| Label | Definisi Boundary |
|---|---|
| `[CLASS-A]` | **Single-Entity Flow** — satu entitas mandiri memproses state, validasi guard, kalkulasi, dan transisi alur secara tertutup tanpa ketergantungan panggilan ke entitas lain yang menjadi bagian jalur serangan. |
| `[CLASS-B]` | **Dual-Entity Interaction** — dua entitas berinteraksi langsung dalam satu jalur/jendela eksekusi (Kontrak Hulu ↔ Hilir, Kontrak ↔ Callback, Program ↔ Target CPI, atau Akun A ↔ Akun B). |
| `[CLASS-C]` | **Multi-Entity Long On-Chain Flow** — tiga atau lebih entitas berinteraksi berantai dalam alur on-chain panjang, lintas-domain, multi-hop (`User -> Router -> Pool -> Strategy -> Oracle/DEX/Bridge`), PTB multi-objek, atau rantai pesan asinkron. |

> **CLASS-A/B/C adalah router metode berdasarkan topologi entitas, BUKAN indikator severity atau EV.**
> Kontrak `[CLASS-A]` tunggal dapat memegang 100% TVL — label ini menentukan *paket metode* di Fase 2, bukan prioritas atau nilai uang.

**Aturan agregasi:**
1. Setiap berkas `[MUST-AUDIT]` **wajib** muncul di **tepat satu** unit — tidak boleh hilang, tidak boleh ganda. Verifikasi jumlah berkas di antrean terhadap `00b-file-inventory.md`.
2. Cluster hanya boleh menggabungkan berkas yang **saling memanggil** atau berada dalam satu alur nilai; DILARANG menggabung sekadar karena satu folder.
3. Bila total unit masih >40 setelah clustering awal, Anda **DILARANG** menandai berkas `[MUST-AUDIT]` sebagai `DEFERRED`! Anda **WAJIB merapatkan pengelompokan** (*re-cluster*) berkas-berkas yang berada dalam satu domain/alur hingga **100% berkas `[MUST-AUDIT]`** masuk ke dalam $\le 40$ unit aktif (`0 DEFERRED`, `0 BELUM`).
4. **Seluruh berkas `[MUST-AUDIT]`** (100% populasi `[MUST-AUDIT]` dari `00b-file-inventory.md`, baik yang berlabel `[LIVE_BOUNTY]` maupun `[REPO_STAGED]`) **wajib menjadi anggota unit aktif `S-n`**.

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

Buat file `audit/05-raw-leads.md` dan catat setiap indikasi awal anomali mutasi state, *Patch-Scar*, ketidaksinkronan View vs Write, atau **guard aritmetika/dinamis mencurigakan** yang ditemukan selama Langkah 0–4 **tanpa melakukan penghakiman kelayakan ekonomi (EV) atau penyaringan `HEAD-only` terlebih dahulu**.

> **Guard dinamis JANGAN diparkir di `04`.** Guard yang ekspresinya melibatkan aritmetika, `mulDiv`, `balanceOf`, rasio `totalAssets`/`totalSupply`, akumulator waktu/indeks, batas LTV/likuidasi, atau panjang array **wajib masuk `05`** (tag `M-005`) agar di-fuzz di Fase 3. Lihat `verify/templates/04-code-guarded.md`.

> ⚠️ **`05` ADALAH ANTREAN, BUKAN RIWAYAT — DILARANG MEMBENGKAK.**
> `05` dibaca **berulang** setiap resume, triage, dan perpindahan lead; ia adalah file paling sering dibuka sepanjang audit. Isi `05` dibatasi **hanya** untuk hal yang dibutuhkan saat memilih lead berikutnya.
>
> **Wajib ada per lead (ringkas, maks ~10 baris):** ID · `File:Baris` · hipotesis **satu baris** · metode (`M-xxx`/`[POV-xx]`) · EV kasar · status.
>
> **DILARANG ada di `05`:**
> - kutipan kode panjang, trace, atau salinan log terminal → taruh di `audit/notes/lead-<id>.md`
> - analisis berlapis / riwayat koreksi → taruh di `audit/notes/lead-<id>.md`
> - **atestasi `ATTESTED_CLEAN`** → taruh di `audit/03` (1 baris di tabel cakupan) + detail di `audit/notes/attest-<unit>.md`
> - blok bukti hasil uji → wadah hasilnya (`06`/`07`/`08`/`09`)
>
> **Patokan ukuran:** rata-rata **≤ 250 B per lead**. `05` dengan 50 lead sehatnya **≤ 15 KB**. File > 25 KB adalah tanda riwayat sudah bocor ke antrean — pindahkan sebelum menambah lead baru.
>
> **Aturan pemindahan (dua arah, jangan dipisah):** sebelum memangkas detail dari `05`, **WAJIB** sudah ada `audit/notes/lead-<id>.md` yang memuat detail itu. Memangkas tanpa memindah = data hilang permanen.
>
> **Bedakan dari wadah hasil:** `06`/`07`/`08`/`09` **DILARANG** diringkas — isinya bukti eksekusi yang menjadi syarat sah laporan (`BUKTI_SIMULASI`, `PERCOBAAN`, PoC `[PASS]`). Yang dipadatkan hanya `05`, karena `05` memuat **rencana**, bukan **bukti**.

**Fase 1 adalah penulis SAH `05`** — skill ini secara eksplisit melarang delegasi ("DILARANG mendelegasikan pekerjaan Fase 1 ke subagent lain"), sehingga tidak ada Subagent yang bersaing menulis. Aturan staging hanya mengikat ketika pekerjaan didelegasikan (Fase 2/3). Tetap patuhi `workspace/AGENTS.md` Pasal 1.3: `write_file` awal lalu `append`, **DILARANG** `open(path,"w")` / `>`.

---

## Langkah 6: Gerbang Cakupan PEMETAAN ANTREAN (QUEUE MAPPING GATE) — WAJIB sebelum menutup Fase 1

**Fase 1 hanya memetakan, belum berburu.** Karena itu gerbang keluar Fase 1 **tidak menguji hasil Fase 2** (`LEAD_GENERATED`/`ATTESTED_CLEAN` belum ada saat Fase 1 ditutup). Yang diuji: apakah berkas `[MUST-AUDIT]` dari `00b-file-inventory.md` sudah **terpetakan masuk ke Unit Alur `S-n`** di `03-attack-surface-queue.md`.

Status yang sah di Fase 1: `BELUM` (belum masuk unit) -> `TERPETAKAN_DI_UNIT` (sudah tercakup di dalam unit aktif `S-n`). Status `DEFERRED` **DILARANG** untuk berkas `[MUST-AUDIT]` — seluruh berkas `[MUST-AUDIT]` wajib **100%** masuk ke dalam $\le 40$ unit `S-n`!

Hitung dan tulis ke bagian akhir `05-raw-leads.md`:

| Metrik | Rumus | Ambang LULUS |
|---|---|---|
| **Ketercakupan antrean penuh** | berkas `[MUST-AUDIT]` berstatus `TERPETAKAN_DI_UNIT` ÷ total `[MUST-AUDIT]` | **= 100%** (0 `BELUM`, 0 `DEFERRED`) |
| **Cakupan domain** | domain `D1..Dn` dengan **100%** berkas `[MUST-AUDIT]` berstatus `TERPETAKAN_DI_UNIT` ÷ total domain ber-`[MUST-AUDIT]` | **= 100%** |
| **Berkas raksasa** | berkas `[MUST-AUDIT]` terbesar per domain | **wajib `TERPETAKAN_DI_UNIT`** |
| **Ukuran antrean** | jumlah Unit Alur Eksekusi | **<= 40** (rapatkan cluster bila >40) |
| **Integritas agregasi** | berkas di antrean unik | **0 hilang, 0 ganda** vs `00b` |

> **Gerbang 100% Tanpa Celah (`0 BELUM, 0 DEFERRED`):** Seluruh berkas `[MUST-AUDIT]` wajib **100% terpetakan** masuk ke dalam $\le 40$ Unit Alur Eksekusi `S-n`. Tidak boleh ada berkas `[MUST-AUDIT]` yang ditinggalkan sebagai `BELUM` maupun ditunda sebagai `DEFERRED`.

> **DILARANG memakai "jumlah lead per domain" sebagai metrik kelulusan.** Kelulusan diukur dari **keterpetakan per berkas**, bukan banyaknya hipotesis — agar modul yang memang aman tidak dipaksa melahirkan lead palsu.

Bila **salah satu** ambang gagal: Fase 1 **DITOLAK**, kembali ke Langkah 0/4 dan perluas enumerasi atau clustering. DILARANG melanjutkan ke Fase 2 dengan gerbang gagal.

**Pembagian tanggung jawab gerbang — jangan tertukar:**

| Fase | Gerbang | Yang diuji | Ambang |
|---|---|---|---|
| **1** (Langkah 6) | Queue Mapping Gate | berkas `[MUST-AUDIT]` masuk Unit `S-n` | 100% terpetakan, 0 `BELUM`, 0 `DEFERRED`, domain 100%, unit <= 40 |
| **2** (Gate Keluar) | Trace Gate | berkas per domain berstatus `LEAD_GENERATED` / `ATTESTED_CLEAN` | = 100% **per domain** (0 `BELUM`, 0 `DIBACA`, 0 `DEFERRED`) |
| **4** (Langkah 0a) | Dual Gate | keduanya diperiksa ulang | (1) + (2) |

**Catatan pengukuran:** pengukur cakupan (`00b-file-inventory.md`) WAJIB dieksklusi dari populasi yang diukur. Tanpa eksklusi, setiap berkas "disebut" oleh inventarisnya sendiri dan cakupan selalu tampak 100%.

**Alasan aturan ini:** tanpa pengukuran, agen akan menyusut ke satu jalur yang paling menarik perhatian dan menyebutnya "audit mendalam". Sampling yang tidak diakui sebagai sampling adalah kegagalan yang tidak terdeteksi.
