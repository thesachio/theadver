# 04 — Code-Guarded (Khusus Guard Statis / Struktural — Umpan Metode 5 Putaran 2)

Wadah murni untuk hipotesis Fase 2 yang berhenti di **guard izin atau struktural statis** (`onlyOwner`, `onlyRole`, `msg.sender == router`, `nonReentrant`, `whenNotPaused`, atau pengecekan alamat `address != address(0)`).

> **GERBANG PEMISAHAN GUARD STATIS VS DINAMIS (WAJIB):**
> - **Guard Statis (Masuk ke `04` ini):** Guard yang variabel pembentuknya hanya berupa alamat pemanggil (`msg.sender`), role/whitelist tetap, atau flag mutex/boolean sederhana.
> - **Guard Dinamis / Matematis (DILARANG masuk `04` — WAJIB masuk `05-raw-leads.md`!):** Apabila ekspresi `require` / `if (...) revert` / `assert!` melibatkan perhitungan aritmetika, pembulatan (`mulDiv`), saldo token (`balanceOf`), rasio pool (`totalAssets`/`totalSupply`), akumulator waktu/indeks, batas LTV/likuidasi, atau panjang array, hipotesis tersebut **DILARANG diparkir di `04`**! Masukkan langsung ke `05-raw-leads.md` (dengan tag `M-005`) agar diuji secara mekanis menggunakan fuzzer di Fase 3.

## Field wajib per entri

```
ID                  : <R-001>
File:Baris          : <path:Kontrak:Fungsi:Lbaris>
Ekspresi Guard      : <ekspresi perbandingan apa adanya, mis. msg.sender == configuredRouter>
Variabel Pembentuk  : <daftar variabel state di dalam ekspresi guard>
Penulis Variabel    : <fungsi yang dapat mengubah tiap variabel — rujuk 02-state-and-var-matrix.md>
Hipotesis Dihentikan: <apa yang ingin dilakukan penyerang dan mengapa guard statis ini menghentikannya>
Status Putaran 2    : TERSANGKAL | TEMBUS | BELUM
```

- **`TERSANGKAL`** — variabel guard terbukti hanya bisa diubah admin sah.
- **`TEMBUS`** — ada jalur tidak langsung untuk mengubah variabel guard → **dipromosikan ke `05`**.
- **`BELUM`** — belum diperiksa; memblokir penandaan unit `[HUNTED]`.

**Aturan:** guard tanpa `Variabel Pembentuk` dan `Penulis Variabel` tidak dapat diuji di Putaran 2 — lengkapi sebelum menandai unit `[HUNTED]`. Jangan menyalin kode utuh; cukup ekspresi guard dan jalan masuknya.
