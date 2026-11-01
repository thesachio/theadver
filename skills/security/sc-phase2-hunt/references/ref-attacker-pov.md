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
| `[POV-MATH-01]` | Desinkronisasi Indeks Akrual pada Transfer/Mutasi Pokok | `ref-math-and-vaults.md` | indeks akrual, share, transfer pokok |
| `[POV-MATH-02]` | Inverse-Function Rounding & Multi-Hop Fee Truncation | `ref-math-and-vaults.md` | rounding arah balik, fee truncation |
| `[POV-CALL-01]` | State Desynchronization pada Penyerahan Kontrol | `ref-calls-tokens-reentrancy.md` | control handoff, mid-tx state |
| `[POV-CALL-02]` | Subcall Success/Failure State Divergence | `ref-calls-tokens-reentrancy.md` | try/catch cabang, returnbomb |
| `[POV-DEFI-01]` | Multi-Identity Self-Liquidation & Bad-Debt Socialization | `ref-defi-oracles-liquidation.md` | bonus likuidasi, bad debt, asuransi |
| `[POV-DEFI-02]` | Valuation Source vs Execution Sink Mismatch | `ref-defi-oracles-liquidation.md` | oracle vs spot venue, slippage |
| `[POV-EVM-01]` | Multicall Context Reuse & Residual Authority Exploitation | `ref-chain-evm-tron.md` | msg.value loop/multicall, transient slot |
| `[POV-SOL-01]` | Cross-CPI Stale AccountInfo & Duplicate Writable Alias | `ref-chain-solana.md` | duplicate account key, .reload() |
| `[POV-MOVE-01]` | Programmable Transaction Block (PTB) Capability & Object Splitting | `ref-chain-sui-move.md` | object::id binding, hot potato, << |
| `[POV-TON-01]` | Async Message Interleaving & Bounce Payload Truncation | `ref-chain-ton-async.md` | 224-bit bounce, in-flight lock |

---

## Peta Cepat per Tag `[LOAD: ...]`

- `[LOAD: ref-math-and-vaults.md]` -> `[POV-MATH-01]`, `[POV-MATH-02]`
- `[LOAD: ref-calls-tokens-reentrancy.md]` -> `[POV-CALL-01]`, `[POV-CALL-02]`
- `[LOAD: ref-defi-oracles-liquidation.md]` -> `[POV-DEFI-01]`, `[POV-DEFI-02]`
- `[LOAD: ref-chain-evm-tron.md]` -> `[POV-EVM-01]`
- `[LOAD: ref-chain-solana.md]` -> `[POV-SOL-01]`
- `[LOAD: ref-chain-sui-move.md]` -> `[POV-MOVE-01]`
- `[LOAD: ref-chain-ton-async.md]` -> `[POV-TON-01]`

---

## Catatan Penomoran

ID bersifat **per-domain**: awalan menandai berkas tempat entri tinggal
(`MATH`, `CALL`, `DEFI`, `EVM`, `SOL`, `MOVE`, `TON`) dan nomor urut lokal
di dalam berkas itu. Menambah entri baru cukup melanjutkan nomor pada domain
yang sama (mis. `[POV-MATH-03]`), tanpa menomori ulang entri lama dan tanpa
menyentuh domain lain.
