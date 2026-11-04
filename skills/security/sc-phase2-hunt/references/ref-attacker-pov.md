# Dynamic Symptom Router: Katalog Attacker POV (`[POV-XX]`) & 3-Level Chain Detector

Berkas ini adalah **Router Gejala Kode (Symptom Router)** untuk memanggil pola eksploitasi on-chain yang telah digeneralisasi secara **hemat token (Lazy-Load)**.
- **Checklist Prinsip Dasar** tetap berada di `ref-math-and-vaults.md`, `ref-calls-tokens-reentrancy.md`, `ref-defi-oracles-liquidation.md`, dan `ref-chain-*.md` (selalu tipis < 60 baris).
- **Detail 8 Field Katalog POV** berada di modul terpisah: `ref-pov-math.md`, `ref-pov-call.md`, `ref-pov-defi.md`, dan `ref-pov-chain.md`.

---

## 1. Prosedur Pemakaian Hemat-Token di Fase 2 (Tahap B) & Fase 3 (Langkah 1b)

1. **Jangan Membuka Semua File `ref-pov-*.md` Sekaligus!**
2. Baca kolom **Gejala Pemicu di Kode (Trigger Symptom)** pada Tabel Router di Bagian 2 di bawah ini.
3. **Gejala Kode Adalah Satu-Satunya Pemicu (Lintas-Kelas):** Kolom **Kelas Entitas** hanya menunjukkan topologi **tipikal**, **BUKAN pembatas!** Apabila unit `[CLASS-A]` (kontrak monolitik tunggal) memiliki gejala pemicu di kode (misal: fungsi transfer ber-indeks akrual atau `liquidate` internal), Anda **WAJIB** tetap membuka berkas `ref-pov-*.md` yang ditunjuk untuk membaca 8 field lengkapnya (termasuk *Auditor Blindspot* dan *Routing Simulasi Fase 3*).
4. **Larangan Halusinasi Nomor POV:** DILARANG memakai nomor `[POV-XX]` yang belum terdaftar di tabel ini. Jika menemukan pola baru yang belum ada di katalog, gunakan analogi mekanis bebas dari `ref-method-registry.md` (`M-001`..`M-010`).

---

## 2. Tabel Router Gejala Kode (`[POV-XX]`)

| Nomor POV | Judul Pola Serangan | Kelas Entitas Tipikal | Metode Terkait | Gejala Pemicu di Kode (Kapan Wajib Dibuka?) | Lokasi File Katalog |
|---|---|---|---|---|---|
| `[POV-MATH-01]` | Desinkronisasi Indeks Akrual pada Transfer/Mutasi Pokok | `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]` | `M-002`, `M-003`, `M-006` | Ada `globalIndex`/`userIndex` + fungsi pemindah saldo/posisi 2-akun (`transfer`/`delegate`/`migrate`/`merge`) | `ref-pov-math.md` |
| `[POV-MATH-02]` | Inverse-Function Rounding & Multi-Hop Fee Truncation | `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]` | `M-001`, `M-004`, `M-007` | Pasangan konversi 2 arah (*Exact-Input* vs *Exact-Output*: `deposit` vs `mint`) atau pembagian proporsi/fee $\ge 2$ tahap | `ref-pov-math.md` |
| `[POV-CALL-01]` | State Desynchronization pada Penyerahan Kontrol | `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]` | `M-002`, `M-006`, `M-008` | Panggilan keluar / transfer ETH / hook NFT / CPI terjadi saat variabel pertama sudah berubah tapi variabel pasangannya belum | `ref-pov-call.md` |
| `[POV-CALL-02]` | Subcall Success/Failure State Divergence | `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]` | `M-002`, `M-008`, `M-009` | Subcall dibungkus `try/catch` atau `.call()` tanpa `require(success)` dengan mutasi state berbeda antara cabang sukses vs gagal | `ref-pov-call.md` |
| `[POV-DEFI-01]` | Multi-Identity Self-Liquidation & Bad-Debt Socialization | `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]` | `M-002`, `M-003`, `M-005` | Ada likuidasi/slashing/penalti yang memberi bonus likuidator atau sosialisasi *bad debt* saat `debt > collateral` | `ref-pov-defi.md` |
| `[POV-DEFI-02]` | Valuation Source vs Execution Sink Mismatch | `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]` | `M-001`, `M-005`, `M-008` | Valuasi posisi membaca Sumber A (Oracle/TWAP), tetapi eksekusi swap/likuidasi dikirim ke Sumber B (pool spot) | `ref-pov-defi.md` |
| `[POV-EVM-01]` | Multicall Context Reuse & Residual Authority | `[CLASS-A]`, `[CLASS-B]` | `M-003`, `M-007`, `M-010` | Kontrak punya `Multicall` (`delegatecall`), loop batch, atau `TSTORE`/`TLOAD` + fungsi pembaca `msg.value` / flag sementara | `ref-pov-chain.md` |
| `[POV-SOL-01]` | Cross-CPI Stale AccountInfo & Duplicate Writable Alias | `[CLASS-B]`, `[CLASS-C]` | `M-003`, `M-006` | Instruksi Solana punya $\ge 2$ akun `mut`/`remaining_accounts` setipe tanpa `key() !=` atau baca akun pasca-CPI tanpa `.reload()?` | `ref-pov-chain.md` |
| `[POV-MOVE-01]` | PTB Capability & Object Splitting | `[CLASS-B]`, `[CLASS-C]` | `M-006`, `M-007`, `M-008` | Fungsi Move menerima $\ge 2$ objek (`Pool` + `Position`/`Receipt`) tanpa cek `object::id`, atau memakai geser bit `<<` kustom | `ref-pov-chain.md` |
| `[POV-TON-01]` | Async Message Interleaving & Bounce Payload Truncation | `[CLASS-C]` | `M-002`, `M-007`, `M-009` | Kontrak TON mengubah state lalu mengirim pesan keluar dengan handler `bounced` (>224 bit / `ref`) atau tanpa *pending lock* | `ref-pov-chain.md` |

---

## 3. Hierarki Deteksi Rantai 3-Level (3-Level Chain-Type Detection)

Gunakan tabel 3-level ini di Fase 1 (`00-project-map.md` & `03-attack-surface-queue.md`), Fase 2, dan Fase 3 agar agen tidak salah memuat cartridge (khususnya pada berkas `.rs` atau `.move`):

| Level 1: Ekstensi File | Level 2: Manifes Build (Wajib Cek!) | Level 3: Sinyal Kode Spesifik | Cartridge Checklist Fase 2 | POV Rantai (`ref-pov-chain.md`) | Referensi Mesin Uji Fase 3 |
|---|---|---|---|---|---|
| `.sol`, `.vy`, `.yul` | `foundry.toml`, `hardhat.config.*`, `truffle-config.js`, `tronbox.js` | `msg.sender`, `msg.value`, `delegatecall`, `abi.encode` (atau `SUN`/`msg.tokenvalue` untuk Tron) | `ref-chain-evm-tron.md` | `[POV-EVM-01]` | `ref-test-evm-advanced.md` |
| `.rs` | `Cargo.toml` memuat `anchor-lang`, `solana-program`, atau `pinocchio`; atau ada `Anchor.toml` | `#[program]`, `#[derive(Accounts)]`, `AccountInfo`, `invoke_signed`, `Pubkey` | `ref-chain-solana.md` | `[POV-SOL-01]` | `ref-test-multichain-advanced.md` |
| `.move` | `Move.toml` memuat `Sui` atau `AptosFramework` | `UID`, `TxContext`, `transfer::public_transfer`, `object::id`, atau `acquires` | `ref-chain-sui-move.md` | `[POV-MOVE-01]` | `ref-test-multichain-advanced.md` |
| `.fc`, `.func`, `.tact`, `.tolk` | `blueprint.config.ts`, `tact.config.json`, `wrappers/` | `recv_internal`, `send_raw_message`, `begin_cell()`, `slice` | `ref-chain-ton-async.md` | `[POV-TON-01]` | `ref-test-multichain-advanced.md` |
| `.rs` / lainnya *(Tidak cocok Level 2 & 3 di atas)* | Misal: `cosmwasm-std`, `near-sdk`, `frame-support` (Substrate), atau Rust off-chain daemon | Tidak ada `AccountInfo`/`invoke_signed` Solana | **Tandai `CHAIN: AMBIGUOUS (<nama_runtime>)`!** DILARANG memaksakan `ref-chain-solana.md`; gunakan prinsip universal di `ref-method-registry.md` | Analogi mekanis `M-001..M-010` | Harness native runtime terkait |

---

## 4. Cara Menambah Entri POV Baru (`Plug-and-Play`)
1. Pilih berkas katalog POV yang sesuai (`ref-pov-math.md`, `ref-pov-call.md`, `ref-pov-defi.md`, atau `ref-pov-chain.md`).
2. Tambahkan blok entri baru dengan **8 field wajib** di atas penanda sisipan pada berkas tersebut.
3. Tambahkan **1 baris ringkas** ke Tabel Router Gejala di Bagian 2 berkas ini. Tidak ada berkas skill utama (`SKILL.md`) yang perlu diubah!
