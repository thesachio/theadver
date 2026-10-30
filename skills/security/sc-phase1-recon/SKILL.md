---
name: sc-phase1-recon
description: Fase 0 dan Fase 1 Whitehat Adversarial Reconnaissance - Adaptive intake, threat and actor modeling, state-variable read/write matrix, deployment script inspection, dan attack-surface queue
version: 4.0.0
metadata:
  hermes:
    tags: [security, web3, whitehat, adversarial, recon, threat-model, multichain, phase1]
    category: security
    requires_toolsets: [terminal]
---

# Phase 0 & 1: Threat-First Whitehat Adversarial Reconnaissance

## When to Use
Gunakan skill ini setiap kali memulai proyek baru di /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/ (atau ketika audit/00-project-map.md belum tersedia). Skill ini membangun model ancaman adversarial, memetakan variabel state beserta seluruh pembaca/penulisnya, memeriksa konfigurasi deployment, dan menyusun antrean permukaan serangan.

## Pitfalls (Larangan Keras di Fase 0 & 1)
- DILARANG MEMBUAT `AGENTS.md` DI DALAM FOLDER PROYEK: Seluruh output wajib disimpan di /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/audit/.
- DILARANG MENGUBAH KODE SUMBER PROYEK: Folder src/, contracts/, programs/, dan sources/ bersifat 100% Read-Only.
- DILARANG MENGANDALKAN NAMA FUNGSI: Kenali fungsi murni dari mutasi state (+=, -=, delete), pencetakan/penghancuran objek, aliran nilai, dan kata kunci bahasa.
- DILARANG MEMBACA SELURUH REPOSITORI SEKALIGUS: Gunakan search_files (rg -n) dan baca deklarasi state/konfigurasi secara terarah.
- ADAPTIF TERHADAP KETIADAAN DOKUMENTASI: Jika docs, website, atau halaman bounty tidak tersedia, tandai sebagai N/A dan ekstrak klaim dari README.md serta komentar kode (@notice, @dev, ///).
- DILARANG MEMANGGIL `skill_manage` ATAU `memory`.

---

## Output Wajib Fase 0 & 1 di audit/
Pastikan folder /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/audit/ dibuat terlebih dahulu, lalu hasilkan 5 file berikut:
1. 00-project-map.md (Peta utama proyek, perintah test/fork lokal -j 1, dan Core Invariants).
2. 01-threat-and-env.md (Klaim protokol, konfigurasi compiler/rantai, parameter deployment, dan Model Aktor Adversarial).
3. 02-state-and-var-matrix.md (Kamus 5 kategori state + Matriks Lacak-Balik seluruh fungsi pembaca dan penulis variabel kritis).
4. 03-attack-surface-queue.md (Antrean fungsi berbasis mutasi state, kandidat urutan 3-langkah, dan tag [LOAD: ref-...]).
5. 06-raw-leads.md (Catatan indikasi awal / kecurigaan mentah yang ditemukan selama pemetaan awal untuk dibedah di Fase 2).

---

## Procedure (6 Langkah Berurutan)

### Langkah 1: Adaptive Intake, Scope Pruning, Git Diff, & Inspeksi Skrip Deployment
1. Pemangkasan Scope (Scope Pruning):
   - Cari seluruh file kode sumber utama di dalam folder proyek (.sol, .vy, .rs, .move, .fc, .tact, .tolk).
   - Abaikan folder lib/, node_modules/, dan mock//mocks/.
   - Hitung baris kode (wc -l) tiap file kontrak untuk membedakan Core Contracts/Modules dari Periphery/Router/Libraries.
2. Jejak Perubahan Kode (Git History):
   - Jika terdapat .git, jalankan git log -n 10 --oneline dan git diff --stat pada commit terakhir untuk menandai area kode yang baru dimodifikasi.
3. Inspeksi Terarah Skrip Deployment & Konfigurasi (`script/` / `deploy/`):
   - Jangan abaikan skrip deployment! Gunakan rg atau baca file di script//deploy/ untuk memeriksa: parameter constructor/initializer, nilai desimal awal, pemasangan alamat oracle/router, dan apakah hak admin/deployer menyisakan celah salah konfigurasi (*misconfiguration*).
4. Ekstraksi Klaim & Janji Ekonomi:
   - Ekstrak janji mekanika dari README.md, docs/, atau komentar NatSpec (@notice, @dev, ///). Jika tidak ada, catat N/A.
### Langkah 2: Deteksi Paradigma Rantai, Compiler, & Lingkungan Eksekusi
Periksa file konfigurasi (foundry.toml, hardhat.config.*, Cargo.toml, Anchor.toml, Move.toml, blueprint.config.*, .env.example) untuk mendata:
1. Paradigma Rantai & Tag Modul Rantai Wajib:
   - Paradigma A — Atomic Account/Storage (EVM, Tron TVM, Solana):
     * Jika Solidity/Vyper (EVM atau Tron TVM 1 TRX = 10^6 SUN) -> Tag: [LOAD: ref-chain-evm-tron.md]
     * Jika Rust Anchor/Native (Solana SVM; cek overflow-checks = true di Cargo.toml) -> Tag: [LOAD: ref-chain-solana.md]
   - Paradigma B — Object/Capability & PTB (Sui, Aptos Move):
     * Lacak UID, Shared vs Owned Object, Capability, dan struct *Hot Potato* -> Tag: [LOAD: ref-chain-sui-move.md]
   - Paradigma C — Asynchronous Actor & Message Passing (TON FunC/Tact/Tolk):
     * Lacak send_raw_message, recv_internal, handler bounced (batas 256-bit), dan Jetton Wallet -> Tag: [LOAD: ref-chain-ton-async.md]
2. Ketersediaan Local Sandbox & Local Read-Only Fork:
   - Periksa perintah test standar (forge test -j 1, cargo test -j 1, sui move test, npx blueprint test) dan apakah ada konfigurasi RPC untuk *Local State Forking* (otomatis aktif di Mode Standar tanpa broadcast).
3. Matriks Arsitektur, Token, Oracle, & Bridge:
   - Gunakan rg untuk mendeteksi penggunaan Proxy/Upgradeability, Multicall + payable, perilaku token non-standar (desimal 6/8, fee-on-transfer, hooks, blacklist), pembacaan Oracle (latestRoundData, slot0, TWAP, Pyth), dan tanda tangan/jembatan lintas rantai (ecrecover, permit, MerkleProof, relayer).

### Langkah 3: Penyusunan Model Ancaman & Aktor (Adversarial Threat Model)
Tulis ke dalam audit/01-threat-and-env.md:
1. Daftar Aset & Hak Klaim Target: Dana brankas/pool, *shares/LP*, agunan, pendapatan bunga/fee, objek Capability, atau ketersediaan sistem (DoS/freeze).
2. Profil Kemampuan Aktor Tanpa Hak Istimewa (Attacker Capabilities):
   - *Permissionless User / Multi-Account Attacker* (bisa membuat banyak akun, memecah transaksi, menggunakan flash liquidity, dan merangkai PTB/batch call).
   - *Malicious Callback / Token Contract* (bisa memicu reentrancy atau mengembalikan data abnormal).
   - *Keeper / Liquidator / Relayer Eksternal*.
   - *(Catatan Keras: Aktor penyerang TIDAK memiliki kunci owner/admin kecuali ditemukan jalur pengambilalihan otoritas di kode).*
3. Core Invariants (Target Hukum yang Akan Diuji/Dipatahkan):
   - Rumuskan 5–8 hukum matematis dan state mutlak (misal: Total Klaim Shares <= Total Aset Riil, Debt hanya berkurang sebesar nilai pembayaran sah, Object Position wajib terikat pada Pool ID yang sama, Pesan gagal di TON wajib memulihkan state pengirim via bounce).

### Langkah 4: Pemetaan Data-First & Matriks Lacak-Balik Variabel (audit/02-state-and-var-matrix.md)
1. Baca deklarasi penyimpanan di kontrak/modul inti dan kelompokkan ke dalam 5 Kategori State:
   - (1) State Akuntansi & Saldo/Shares, (2) State Waktu & Indeks Akrual, (3) State Keamanan & Nonce/Replay, (4) State Otoritas & Capability, (5) State Pengunci Siklus & Status Asinkron.
2. Matriks Pembaca & Penulis Variabel Kritis (Variable Read/Write Matrix):
   - Untuk variabel-variabel akuntansi, indeks, dan otoritas paling kritis, gunakan rg -n "<nama_variabel>" di seluruh kontrak inti.
   - Catat untuk setiap variabel kritis:
     * Lokasi deklarasi (File:Baris)
     * Seluruh fungsi yang MENULIS/MENGUBAH (+=, -=, =, delete)
     * Seluruh fungsi yang MEMBACA (untuk menghitung batas pinjaman, harga, atau syarat require)
     * Invarian terkait yang mengikat variabel tersebut.
### Langkah 5: Penyusunan Antrean Permukaan Serangan (audit/03-attack-surface-queue.md)
Cari seluruh titik masuk (external, public, pub fn, public entry fun, recv_internal) beserta fungsi di pustaka matematika kustom (libraries//math/). Susun ke dalam audit/03-attack-surface-queue.md dengan format setiap item mencakup:
- ID & Lokasi: NamaFile:Baris
- Peran Perilaku Mutasi: (Inflow/Penambah Hak +=, Outflow/Pengurang Hak -=, Transfer/Split/Merge, Akrual Waktu, Penerus Eksternal/Callback, atau Handler Bounce/Error).
- Pasangan Siklus Hidup & Kandidat Urutan 3-Langkah: Sandingkan fungsi masuk dengan fungsi keluarnya, serta catat kandidat urutan Langkah A (Masuk) -> Langkah C (Transfer/Ubah Konfigurasi/Split) -> Langkah B (Keluar/Likuidasi).
- Target Invarian & Aktor: Invarian mana yang diincar melalui jalur ini.
- Tag Wajib `[LOAD: ...]` untuk Fase 2:
  * Wajib 1 Tag Modul Rantai ([LOAD: ref-chain-evm-tron.md], [LOAD: ref-chain-solana.md], [LOAD: ref-chain-sui-move.md], atau [LOAD: ref-chain-ton-async.md]).
  * Wajib 1 atau lebih Tag Modul Universal:
    - [LOAD: ref-math-and-vaults.md] (Operasi bagi/kali, shares/vault, unchecked, downcasting, bitwise/tick math).
    - [LOAD: ref-calls-tokens-reentrancy.md] (Transfer token/aset, pengiriman native coin, callback, panggilan eksternal).
    - [LOAD: ref-defi-oracles-liquidation.md] (Pembacaan harga oracle, swap AMM, akrual bunga/reward, likuidasi/bad debt).
- Status Awal: [QUEUED]

### Langkah 6: Pembuatan Peta Utama (00-project-map.md) & Inisialisasi Raw Leads (06-raw-leads.md)
1. Tulis ringkasan eksekutif (maksimal 90 baris) ke dalam audit/00-project-map.md yang berisi: Identitas proyek, Paradigma Rantai, Perintah Kompilasi/Test dengan flag -j 1, Daftar Kontrak In-Scope, Daftar Core Invariants, dan Indeks File audit/.
2. Buat audit/06-raw-leads.md untuk menampung indikasi anomali awal yang terlihat selama pemetaan (tanpa mengklaimnya sebagai temuan valid sebelum dibedah di Fase 2 dan diuji di Fase 3).

---

## Verification
Sebelum menyelesaikan tugas Fase 1, pastikan:
1. Kelima file di audit/ (00-project-map.md, 01-threat-and-env.md, 02-state-and-var-matrix.md, 03-attack-surface-queue.md, dan 06-raw-leads.md) telah tertulis lengkap.
2. Tidak ada file AGENTS.md yang dibuat di dalam folder proyek dan kode sumber asli kontrak tidak berubah.
3. Setiap item di 03-attack-surface-queue.md dikelompokkan berdasarkan mutasi state dan memiliki tag [LOAD: ref-...] yang valid.
