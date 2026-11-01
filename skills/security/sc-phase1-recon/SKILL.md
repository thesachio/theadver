---
name: sc-phase1-recon
description: Phase 0 & 1 — Domain-Agnostic Recon, Production Environment Fact Mapping, and State-Mutation Matrix.
version: 5.0.0
---

# Phase 0 & 1: Domain-Agnostic Recon & Production Fact Mapping

Di Fase 0 dan Fase 1, peran Anda murni sebagai Pemeta Fakta Objektif (*Cartographer*) — bukan Hakim Penolak. DILARANG menggunakan `delegate_task` pada fase ini dan DILARANG menyaring/membuang anomali secara prematur.
Buat direktori `audit/notes/` dan hasilkan 5 file fondasi di `audit/` (`00` s/d `03`, serta inisialisasi `05-raw-leads.md`).

---

## Langkah 1: Environment, Production Lifecycle, & Build Sanity -> `audit/00-project-map.md`
1. **Deteksi Bahasa, Paradigma Rantai, & Build Ringan:**
   - Identifikasi ekosistem proyek: Paradigma A (Atomic EVM/Tron/Solana), Paradigma B (Object/Move Sui/Aptos), atau Paradigma C (Async Actor TON).
   - Uji kompilasi/tes awal dengan worker tunggal: FOUNDRY_JOBS=1 (forge test -j 1), CARGO_BUILD_JOBS=1, atau RAYON_NUM_THREADS=1.
   - Periksa ketersediaan konfigurasi RPC di ./rpc-env.sh / .env.rpc untuk kebutuhan simulasi *Local Fork* di Fase 3.
2. **Pemetaan Fakta Siklus Hidup Produksi** (Data Faktual untuk Fase 3 & 4):
   - Periksa skrip deploy/, script/, migrations/, dan konstruktor/factory.
   - Catat secara faktual: (a) apakah fungsi `initialize()` sudah dieksekusi secara atomik saat deployment, (b) apakah kontrak mencetak *dead shares* awal atau sudah memiliki TVL *live* di produksi (sehingga `totalSupply == 0` sudah terlewati), dan (c) mana kontrak yang Aktif In-Scope, mana yang masih Pre-Live / Paused, serta mana yang *mock/deprecated*.
3. **5–8 Core System Invariants (General-Deterministic):**
   - Rumuskan 5–8 hukum kekekalan nilai dan konsistensi state mutlak dari proyek ini (misal: Total Klaim <= Total Aset Riil, Keluar(Masuk(x)) <= x, atau Setiap perubahan kewajiban wajib diikuti sinkronisasi indeks).

---

## Langkah 2: Threat Surface & Fakta Lingkungan Produksi -> audit/01-threat-and-env.md
Jangan menyalin kode mentah. Dokumentasikan fakta lingkungan produksi secara objektif sebagai acuan bersama:
1. **Klasifikasi 3 Kasta Realitas Aset:**
   - **Kasta 1 — Token/Entitas Internal & Deterministik** (LP Token, Share/Receipt Token, Token Protokol, WETH): Catat bahwa kodenya adalah kontrak internal/ERC-20 standar (tidak memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau anomali return bool ala USDT).
   - **Kasta 2 — Token Eksternal Whitelist Produksi:** Daftar aset eksternal yang benar-benar diizinkan di produksi beserta sifat nyatanya (misal: desimal 6/8, *blacklistable* pada USDC/USDT, tidak mengembalikan bool pada transfer USDT namun biaya transfernya 0).
   - **Kasta 3 — Input/Token Permissionless:** Tandai fungsi mana yang mengizinkan pengguna memasukkan alamat token/pool/hook kustom secara bebas, dan apakah ia berinteraksi dengan dana kolam bersama (*shared pool*) atau terisolasi.
2. **Peta Peran & Batas Otoritas (Actor & Privilege Map):**
   - Petakan seluruh titik masuk pengguna eksternal tak berizin (unprivileged), termasuk fitur multicall/batch, `address(this)` self-call, callback, dan verifikasi signature/session-key.
   - Petakan fungsi khusus berizin (onlyOwner/Admin/DAO/Keeper) beserta parameter state apa saja yang dapat diubah oleh peran tersebut.
3. **Fisika Rantai & Delta Modifikasi Kustom:**
   - Catat karakteristik rantai target (aturan gas, L2 sequencer, desimal native coin) serta bagian dari library standar (seperti ERC4626/Uniswap/Anchor/Move standar) yang dimodifikasi secara kustom oleh developer.

---

## Langkah 3: State-Mutation & Variable Matrix (General-Deterministic) -> audit/02-state-and-var-matrix.md
Gunakan search_files (rg -n) untuk memetakan seluruh variabel state/storage (mapping, struct, array, objek, atau akun):
1. Buat tabel matriks lacak-balik: Nama Variabel/Field | Fungsi Penulis/Penambah (`+=`, `=`) | Fungsi Pengurang/Penghapus (`-=`, `delete`) | Fungsi Pembaca Kritis (Guards/Math).
2. Deteksi Dini Asimetri Mutasi State: Tandai variabel atau field struct yang dimodifikasi saat entitas masuk/dibuat, tetapi tidak di-reset/dikurangi secara simetris saat entitas keluar, ditransfer, dibatalkan, atau dilikuidasi.

---

## Langkah 4: Primitive-Based Attack Surface Queue -> audit/03-attack-surface-queue.md
Susun seluruh fungsi yang mengubah state ke dalam Unit Eksekusi Siklus Hidup (2–4 fungsi yang menyentuh variabel yang sama per kelompok):
1. **Urutan Prioritas:**
   - `[P1-CRITICAL]` & `[P2-HIGH]`: Fungsi unprivileged yang memindahkan nilai, menghitung proporsi/akrual, melakukan panggilan eksternal, atau memicu transisi paksa.
   - `[P3-ADMIN-OR-PERIPHERY]`: Fungsi operasional khusus Admin/Keeper (tetap dicatat agar dapat diperiksa apakah ada *admin-only bug* atau jalur eskalasi).
2. **Penempelan Tag Referensi `[LOAD: ...]` Wajib per Kelompok:**
   - `[LOAD: ref-math-and-vaults.md]` -> Fungsi dengan operasi bagi/kali proporsi, share, pembulatan, biaya, atau akrual indeks waktu.
   - `[LOAD: ref-calls-tokens-reentrancy.md]` -> Fungsi dengan panggilan eksternal, transfer token/NFT, callback, eksekusi batch/self-call, atau verifikasi signature.
   - `[LOAD: ref-defi-oracles-liquidation.md]` -> Fungsi dengan pembacaan harga/oracle, swap, pinjaman, atau transisi paksa (likuidasi, lelang, penyitaan, slashing).
   - Tambahkan tepat 1 tag rantai: `[LOAD: ref-chain-evm-tron.md]`, `[LOAD: ref-chain-solana.md]`, `[LOAD: ref-chain-sui-move.md]`, atau `[LOAD: ref-chain-ton-async.md]`.

---

## Langkah 5: Inisialisasi Antrean Aktif -> audit/05-raw-leads.md
Buat file `audit/05-raw-leads.md` dan catat setiap indikasi awal anomali mutasi state atau ketidaksinkronan variabel yang ditemukan selama Langkah 1–4 tanpa melakukan penghakiman kelayakan ekonomi terlebih dahulu.
