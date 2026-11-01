# Indeks Katalog Attacker POV ([POV-XX])

Katalog **isi** berada di bagian bawah masing-masing file referensi domain, bukan di file ini.
File ini hanya **indeks** agar Anda dapat menemukan lokasi sebuah POV tanpa membuka tujuh file.

**Aturan penomoran:** satu nomor `[POV-XX]` hanya boleh dipakai sekali di seluruh katalog, urut menaik
sesuai urutan pencatatan. DILARANG memakai nomor yang belum terdaftar di tabel ini (larangan halusinasi).

**Cara menambah entri baru:**
1. Pilih file referensi domain yang paling dekat dengan mekanismenya.
2. Sisipkan entri lengkap (5 field wajib) di bagian `## Katalog Generalized Attacker POV & Auditor Blindspots`
   pada file tersebut, di bawah penanda sisipan.
3. Tambahkan satu baris ke tabel di bawah ini dan ke peta cepat.

**Field wajib per entri:** Kondisi Prasyarat (State Condition) · Kacamata Attacker (Gejala di Kode) ·
Rangkaian Peristiwa Serangan · Mengapa Lolos dari Auditor Biasa (Auditor Blindspot) · Batas Realitas (Kapan Gugur).

---

## Tabel Indeks

| Nomor | Judul | Lokasi Entri | Rujukan Domain |
|---|---|---|---|
| `[POV-01]` | Desinkronisasi Indeks Akrual Melalui Self-Transfer atau Mutasi 2-Aktor | `ref-math-and-vaults.md` | indeks akrual, share, mutasi 2-aktor |
| `[POV-02]` | Cross-Contract / Read-Only State Desync Saat Callback di Tengah Operasi | `ref-calls-tokens-reentrancy.md` | CEI, `nonReentrant` lokal, mid-tx state |
| `[POV-03]` | Multi-Identity Self-Liquidation & Bad-Debt Socialization Arbitrage | `ref-defi-oracles-liquidation.md` | bonus likuidasi, bad debt, asuransi |
| `[POV-04]` | Exact-Input vs Exact-Output Rounding Asymmetry & Multi-Hop Truncation | `ref-math-and-vaults.md` | exact-in vs exact-out, intermediate division |
| `[POV-05]` | Isolated Subcall (try/catch / Low-Level Call) State-Divergence & Returnbombing | `ref-calls-tokens-reentrancy.md` | try/catch fallback, selective revert, returnbomb |
| `[POV-06]` | Valuation-Source vs Execution-Venue Asymmetry (Oracle-to-Market Seam) | `ref-defi-oracles-liquidation.md` | oracle vs spot venue, forced swap/rebalance |
| `[POV-07]` | Context-Persisting Batch (delegatecall / multicall / Transient Storage) Value & State Reuse | `ref-chain-evm-tron.md` | msg.value per-tx, TSTORE bocor, batch reuse |
| `[POV-08]` | Cross-Account Parameter Aliasing & Post-CPI Stale Deserialization | `ref-chain-solana.md` | akun kembar, `remaining_accounts`, `.reload()` |
| `[POV-09]` | PTB Cross-Object Receipt/Position Spoofing & Custom Bit-Shift Mask Overflow | `ref-chain-sui-move.md` | object::id binding, Hot Potato, `<<` truncation |

---

## Peta Cepat per Tag `[LOAD: ...]`

- `[LOAD: ref-math-and-vaults.md]` -> `[POV-01]`, `[POV-04]`
- `[LOAD: ref-calls-tokens-reentrancy.md]` -> `[POV-02]`, `[POV-05]`
- `[LOAD: ref-defi-oracles-liquidation.md]` -> `[POV-03]`, `[POV-06]`
- `[LOAD: ref-chain-evm-tron.md]` -> `[POV-07]`
- `[LOAD: ref-chain-solana.md]` -> `[POV-08]`
- `[LOAD: ref-chain-sui-move.md]` -> `[POV-09]`
- `[LOAD: ref-chain-ton-async.md]` -> *(belum ada entri)*

---

## Catatan Penomoran

Penomoran mengikuti urutan pencatatan, **bukan** urutan file. `[POV-01]` tercatat lebih dulu (indeks akrual)
sehingga menempati nomor 1, meski entri berikutnya yang masuk adalah pola reentrancy. Jangan menomori ulang
entri lama saat menambah entri baru — cukup lanjutkan dari nomor terakhir di tabel.
