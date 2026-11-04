# 04 — Code-Guarded (Khusus Guard Statis / Struktural — Umpan Metode 5 Putaran 2)

Wadah murni untuk hipotesis Fase 2 yang berhenti di **guard izin atau struktural statis** (`onlyOwner`, `onlyRole`, `msg.sender == router`, `nonReentrant`, `whenNotPaused`, atau pengecekan alamat `address != address(0)`).

> **GERBANG PEMISAHAN GUARD STATIS VS DINAMIS (WAJIB):**
> - **Guard Statis (Masuk ke `04` ini):** Guard yang variabel pembentuknya hanya berupa alamat pemanggil (`msg.sender`), role/whitelist tetap, atau flag mutex/boolean sederhana.
> - **Guard Dinamis / Matematis (DILARANG masuk `04` — WAJIB masuk `05-raw-leads.md`!):** Apabila ekspresi `require` / `if (...) revert` / `assert!` melibatkan perhitungan aritmetika, pembulatan (`mulDiv`), saldo token (`balanceOf`), rasio pool (`totalAssets`/`totalSupply`), akumulator waktu/indeks, batas LTV/likuidasi, atau panjang array, hipotesis tersebut **DILARANG diparkir di `04`**! Masukkan langsung ke `05-raw-leads.md` (dengan tag `M-005`) agar diuji secara mekanis menggunakan fuzzer di Fase 3.

## Field wajib per entri

```markdown
## [R-001] Contoh Guard Statis
ID                  : R-001
File:Baris          : <path/Kontrak.sol:Baris>
Ekspresi Guard      : <require(msg.sender == router) / onlyRole(...)>
Variabel Pembentuk  : <router / role mapping / flag>
Penulis Variabel    : <setRouter(...) onlyOwner / konstruktor>
Hipotesis Dihentikan: <hipotesis yang terhenti di guard ini>
Status Putaran 2    : TERSANGKAL | TEMBUS | BELUM
```

- `TERSANGKAL` — variabel guard terbukti hanya bisa diubah admin sah **DAN** memenuhi kedua syarat berikut:
  1. Entitas yang diizinkan oleh guard tersebut **bukan** kontrak/program/modul hulu yang dapat dipicu oleh pengguna tak berizin (*unprivileged caller*), **DAN**
  2. Fungsi tersebut **tidak** memproses state/antrean/saldo yang dapat diracuni terlebih dahulu oleh pengguna tak berizin untuk menyabotase/membajak eksekusi rutin (seperti harvest, settle, rebalance, liquidate, atau relay).
- `TEMBUS` — meskipun variabel permission-nya sendiri tidak bisa dimanipulasi (mis. `immutable` atau dikunci admin), guard ini **TETAP DINYATAKAN `TEMBUS`** dan **WAJIB dipromosikan ke `05-raw-leads.md`** apabila memenuhi salah satu dari 3 jalur *Permissionless* berikut:
  1. **Jalur 1 (Mutasi Variabel Guard — `M-005`):** Ada jalur tak berizin untuk mengubah variabel pembentuk guard itu sendiri; **ATAU**
  2. **Jalur 2 (Pemicuan Lewat Kontrak/Modul Hulu — `M-008`):** Permission mengunci pemanggil ke suatu kontrak/program/objek hulu (Router, Manager, Hub, Vault, Forwarder), namun kontrak hulu tersebut memiliki fungsi publik yang dapat dipanggil penyerang tak berizin untuk meneruskan eksekusi/parameter ke fungsi ini; **ATAU**
  3. **Jalur 3 (*Unprivileged State Poisoning* pada Eksekusi Rutin — `M-005`/`M-009`):** Permission mengunci pemanggil ke aktor operasional rutin (Keeper, Relayer, Solver, Operator), tetapi penyerang tak berizin dapat memanipulasi state, antrean, atau saldo likuiditas di fungsi publik lain sehingga ketika aktor rutin menjalankan fungsi ini secara normal, terjadi kebocoran nilai atau *DoS revert* permanen!
- `BELUM` — belum diperiksa terhadap ketiga jalur di atas; memblokir penandaan unit `[HUNTED]`.

**Aturan:** **DILARANG menandai `TERSANGKAL` hanya karena variabel alamat (`router`/`manager`/`keeper`) bersifat `immutable` atau hanya bisa diubah oleh `onlyOwner`!** Wajib periksa **Jalur 2** (apakah entitas yang diizinkan adalah kontrak hulu yang bisa dipanggil publik) dan **Jalur 3** (apakah state yang dibaca di dalam fungsi ini bisa diracuni secara *permissionless*). Jangan menyalin kode utuh; cukup ekspresi guard dan jalan masuknya.
