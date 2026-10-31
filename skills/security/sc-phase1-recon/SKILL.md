---
name: sc-phase1-recon
description: Phase 0 & 1 — Domain-Agnostic Recon, 8-Gate Reality Baseline, and State-Mutation Matrix.
version: 4.4.0
---

# Phase 0 & 1: Domain-Agnostic Recon & Reality Baseline

Anda memegang kendali penuh atas Fase 0 dan Fase 1. DILARANG menggunakan delegate_task pada fase ini.
Buat direktori audit/notes/ dan hasilkan 5 file di audit/ (00 s/d 03, plus inisialisasi 05-raw-leads.md).

---

## Langkah 1: Environment, Production Lifecycle, & Build Sanity -> audit/00-project-map.md
1. Deteksi Bahasa & Build Ringan: Identifikasi ekosistem dan jalankan kompilasi dengan FOUNDRY_JOBS=1, CARGO_BUILD_JOBS=1, atau RAYON_NUM_THREADS=1.
2. Pemetaan Siklus Hidup Produksi (Mencegah Kondisi Istimewa #2 & #3):
   - Periksa skrip deploy/, script/, migrations/, dan konstruktor/factory.
   - Catat apakah initialize() dipanggil secara atomik saat pembuatan kontrak, apakah ada pencetakan *dead shares* awal, dan apakah kontrak target sudah memiliki TVL *live* (sehingga kondisi totalSupply == 0 tidak mungkin tercapai secara alami).
   - Pisahkan kontrak yang Aktif In-Scope dari kontrak *mock*, *script*, atau modul *deprecated*.
3. 5 Core System Invariants (Bebas Domain): Rumuskan hukum-hukum mutlak yang tidak boleh dilanggar oleh mesin status proyek ini.

---
## Langkah 2: Threat Surface & Baseline Realitas Produksi -> audit/01-threat-and-env.md
Jangan menyalin kode mentah. Tulis analisis ancaman tajam yang WAJIB mengunci Baseline Realitas Produksi:
1. Klasifikasi 3 Kasta Realitas Aset (Mencegah Kondisi Istimewa #1 & #5):
   - Kasta 1 — Token/Entitas Internal & Deterministik (LP Token, Share/Receipt Token, Token Protokol, WETH): Kodenya adalah ERC-20 standar. DILARANG KERAS mengasumsikan Kasta 1 memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau gagal mengembalikan bool ala USDT!
   - Kasta 2 — Token Eksternal Whitelist Produksi: Daftar aset yang diizinkan Admin/konfigurasi produksi. Catat sifat aslinya saja (misal: USDT punya 6 desimal, *blacklist*, dan tanpa return bool, tetapi biaya transfernya 0 / BUKAN *Fee-on-Transfer* aktif).
   - Kasta 3 — Input/Token Permissionless: Jika pengguna bebas memasukkan alamat token/pool/hook, tandai bahwa bug HANYA VALID jika bisa mencuri dana dari pool/pengguna lain yang sah (bukan merusak pool milik penyerang sendiri).
2. Batas Kepercayaan Peran & Infrastruktur (Mencegah Kondisi Istimewa #4):
   - Petakan fungsi onlyOwner/Admin/DAO/Keeper. Tandai bahwa seluruh peran berizin diasumsikan **Jujur & Waras (Honest & Sane)** — kesalahan input parameter oleh Admin bukanlah bug.
   - Petakan fungsi yang dapat dipanggil pengguna tak berizin (`unprivileged`), termasuk eksekusi batch/self-call (`address(this)`) dan validasi signature/session-key.
3. **Fisika Rantai & Delta Modifikasi** (Mencegah Kondisi Istimewa #8): Catat keunikan rantai target (aturan gas, L2 sequencer, desimal) serta bagian kode standar yang dimodifikasi secara kustom oleh developer.

---

## Langkah 3: State-Mutation & Variable Matrix -> audit/02-state-and-var-matrix.md
Gunakan search_files (rg) untuk memetakan seluruh variabel state/storage (mapping, struct, array, *accounts*):
1. Buat tabel matriks: Nama Variabel/Field | Fungsi Penulis (Mutators) | Fungsi Pembaca Kritis (Guards) | Pasangan Siklus Hidup (Masuk vs Keluar).
2. Deteksi Dini Asimetri State: Tandai variabel/field yang diubah saat entitas masuk, tetapi tidak dikurangi/dihapus secara simetris saat entitas keluar/dibatalkan/disita.

---

## Langkah 4: Primitive-Based Attack Surface Queue -> audit/03-attack-surface-queue.md
Susun antrean fungsi eksternal/publik yang mengubah state (abaikan fungsi murni konfigurasi Admin) ke dalam Unit Eksekusi Siklus Hidup (2-4 fungsi per kelompok), urutkan prioritasnya ([P1-CRITICAL], [P2-HIGH], [P3-MEDIUM]), dan tempelkan tag primitif mekanis:
- [LOAD: ref-math-and-vaults.md] -> Fungsi dengan pembagian/perkalian proporsi, rasio, biaya, kuota, atau akrual waktu.
- [LOAD: ref-calls-tokens-reentrancy.md] -> Fungsi dengan panggilan eksternal, pemindahan aset/NFT, eksekusi batch/self-call, atau verifikasi signature/izin.
- [LOAD: ref-defi-oracles-liquidation.md] -> Fungsi transisi paksa berbasis ambang batas (likuidasi, lelang, penyitaan, slashing) atau pembacaan data eksternal.
- Tambahkan tepat 1 modul rantai: [LOAD: ref-chain-evm-tron.md], [LOAD: ref-chain-solana.md], [LOAD: ref-chain-sui-move.md], atau [LOAD: ref-chain-ton-async.md].

---

## Langkah 5: Inisialisasi audit/05-raw-leads.md
Buat file audit/05-raw-leads.md untuk menampung hipotesis kerentanan potensial yang lolos saringan awal realitas produksi.
