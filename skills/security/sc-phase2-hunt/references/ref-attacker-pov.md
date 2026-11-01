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
| `[POV-01]` | Desinkronisasi Indeks Akrual Melalui Self-Transfer atau Mutasi 2-Aktor | `ref-math-and-vaults.md` | indeks akrual, share, sinkron 1-argumen |
| `[POV-02]` | Cross-Contract / Read-Only State Desync Saat Callback di Tengah Operasi | `ref-calls-tokens-reentrancy.md` | CEI, `nonReentrant` lokal, mid-tx state |
| `[POV-03]` | 2-Wallet Self-Liquidation & Bad-Debt Socialization Arbitrage | `ref-defi-oracles-liquidation.md` | bonus likuidasi, bad debt, asuransi |
| `[POV-04]` | Exact-Input vs Exact-Output Rounding Asymmetry & Multi-Hop Truncation | `ref-math-and-vaults.md` | exact-output, fee truncation, split-vs-bulk |

---

## Peta Cepat per Tag `[LOAD: ...]`

- `[LOAD: ref-math-and-vaults.md]` -> `[POV-01]`, `[POV-04]`
- `[LOAD: ref-calls-tokens-reentrancy.md]` -> `[POV-02]`
- `[LOAD: ref-defi-oracles-liquidation.md]` -> `[POV-03]`
- `[LOAD: ref-chain-*]` -> *(belum ada entri)*

---

## Catatan Penomoran

Penomoran mengikuti urutan pencatatan, **bukan** urutan file. `[POV-01]` tercatat lebih dulu (indeks akrual)
sehingga menempati nomor 1, meski entri berikutnya yang masuk adalah pola reentrancy. Jangan menomori ulang
entri lama saat menambah entri baru — cukup lanjutkan dari nomor terakhir di tabel.
