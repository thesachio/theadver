---
name: sc-phase1-recon
description: Phase 0 & 1 — Domain-Agnostic Threat-First Recon, State-Mutation Matrix, and Primitive-Based Attack Queue.
version: 4.1.0
---

# Phase 0 & 1: Domain-Agnostic Threat-First Recon & State-Mutation Matrix

Anda memegang kendali penuh atas Fase 0 dan Fase 1. DILARANG menggunakan delegate_task pada fase ini.
Metode ini 100% Bebas Domain (Domain-Agnostic): jangan pernah mengkotak-kotakkan kontrak hanya dari label bisnisnya (DeFi, Wallet, NFT, Game, Governance, dll.), melainkan bedah sebagai Mesin Status Komputasi.
Buat direktori audit/notes/ dan hasilkan 5 file di audit/ (00 s/d 03, plus inisialisasi 05-raw-leads.md).

---

## Langkah 1: Environment & Build Sanity -> audit/00-project-map.md
1. Deteksi Bahasa & Framework: Identifikasi ekosistem (EVM/Foundry/Hardhat, Solana/Anchor, Sui/Aptos Move, TON/Func/Tact) dan jalankan build/compile ringan dengan pembatasan thread (FOUNDRY_JOBS=1, CARGO_BUILD_JOBS=1, atau RAYON_NUM_THREADS=1).
2. Pemetaan Kontrak Inti (In-Scope): Daftar seluruh file sumber utama (abaikan test/, mock/, script/), urutkan berdasarkan kompleksitas mutasi state, dan petakan alur interaksi antar-modul.
3. 5 Core System Invariants (Bebas Domain): Rumuskan hukum mutlak yang TIDAK BOLEH dilanggar oleh mesin status proyek ini dalam kondisi apa pun (mencakup: kekekalan nilai/entitas, keabsahan otoritas, urutan transisi status, konsistensi agregat vs individual, dan jaminan kelangsungan eksekusi/liveness).

---

## Langkah 2: Threat Surface & Environment Quirks -> audit/01-threat-and-env.md
Jangan menyalin kode mentah. Tulis analisis ancaman tajam mengenai:
1. Entitas & Aset yang Dipertaruhkan: Identifikasi semua jenis nilai atau hak di dalam sistem (baik token fungible ERC-20, aset diskrit NFT ERC-721/1155, saldo native, hak kepemilikan Smart Wallet/Session Key, bobot suara, maupun status pesanan/escrow) beserta titik masuk dan titik keluarnya.
2. Keunikan Rantai, Standar Eksternal, & Titik Sambungan Kustom:
   - Catat keunikan rantai target (EVM L2, Tron, Solana, Move, TON) atau standar khusus (ERC-4337/EIP-7702/EIP-1271, callback ERC-721/1155, hook eksternal).
   - Deteksi Delta Modifikasi (Fork-Diff): Jika kontrak mengadopsi standar umum (seperti ERC-4626, Uniswap, OpenZeppelin, Safe), tandai bagian mana yang merupakan modifikasi kustom buatan developer proyek ini sebagai target kecurigaan utama.
3. Batas Otoritas & Input Eksternal: Petakan siapa yang berhak mengubah konfigurasi, fungsi mana yang menerima tanda tangan/bukti eksternal, dan fungsi mana yang mengizinkan panggilan ke dirinya sendiri (address(this)) atau eksekusi batch.

---

## Langkah 3: State-Mutation & Variable Matrix -> audit/02-state-and-var-matrix.md
Gunakan search_files (rg) untuk memetakan seluruh variabel state/storage (termasuk mapping, struct, array, *shared objects*, atau *accounts*):
1. Buat tabel matriks yang memuat:
   - Nama Variabel State / Struct Field
   - Fungsi Penulis (Mutators: =, +=, -=, delete)
   - Fungsi Pembaca Kritis (Guards / Perhitungan Keluar)
   - Pasangan Siklus Hidup (Lifecycle Pair: Masuk vs Keluar / Buat vs Hapus / Kunci vs Buka)
2. Deteksi Dini Asimetri State: Tandai variabel atau field di dalam struct yang diperbarui saat entitas masuk/dibuat, tetapi TIDAK diperbarui/dihapus secara simetris saat entitas keluar, ditransfer, dibatalkan, atau dieksekusi paksa.

---

## Langkah 4: Primitive-Based Attack Surface Queue -> audit/03-attack-surface-queue.md
Susun antrean fungsi yang dapat dipanggil dari luar (external/public/entry functions) yang mengubah state atau memindahkan nilai/otoritas.
1. Kelompokkan ke dalam Unit Eksekusi Siklus Hidup (fungsi fungsi yang saling terkait per kelompok).
2. Urutkan berdasarkan prioritas risiko ([P1-CRITICAL], [P2-HIGH], [P3-MEDIUM]).
3. Penempelan Tag Referensi Berbasis Primitif Komputasi (Bukan Nama Domain!):
   Jangan melihat apa bisnis proyeknya, tetapi lihat Primitif Mekanis apa yang terjadi di dalam fungsi tersebut:
   - [LOAD: ref-math-and-vaults.md] -> Tempelkan pada SETIAP fungsi yang melakukan pembagian/perkalian angka, konversi proporsi/rasio, perhitungan biaya/kuota/bobot, atau akrual berbasis waktu/blok (berlaku untuk Vault, Staking, maupun Royalti NFT, Vesting, Voting, dan Game).
   - [LOAD: ref-calls-tokens-reentrancy.md] -> Tempelkan pada SETIAP fungsi yang melakukan panggilan eksternal, pemindahan aset (ERC-20/721/1155/Native), eksekusi batch/multicall, delegasi/self-call (address(this)), atau verifikasi otoritas/signature/session-key.
   - [LOAD: ref-defi-oracles-liquidation.md] -> Tempelkan pada SETIAP fungsi yang mengeksekusi transisi paksa saat ambang batas tercapai (likuidasi, lelang, penyitaan agunan, pencabutan sewa, slashing, pembatalan paksa) ATAU mengandalkan data/bukti harga/kondisi dari luar.
   - Tempelkan tepat 1 Modul Spesifik Rantai sesuai target: [LOAD: ref-chain-evm-tron.md], [LOAD: ref-chain-solana.md], [LOAD: ref-chain-sui-move.md], atau [LOAD: ref-chain-ton-async.md].

---

## Langkah 5: Inisialisasi audit/05-raw-leads.md
Buat file audit/05-raw-leads.md dengan header standar untuk menampung hipotesis kerentanan potensial dari Fase 1 dan Fase 2. Jika saat menyusun matriks di Langkah 3 Anda sudah melihat anomali asimetri state atau celah logika kustom, langsung tuliskan sebagai Lead pertama (LEAD-001) di audit/05-raw-leads.md.
