# 04 — Code-Guarded (Umpan Guard-Inversion / Metode 5)

Wadah murni untuk hipotesis Fase 2 yang **berhenti di guard kode** (`require` / `if (...) revert` / `assert!`).
Entri di sini bukan temuan; ia adalah umpan untuk Putaran 2.

Setiap entri wajib memuat:

- `ID` — mis. `R-001`
- `File:Baris` — lokasi guard, presisi sampai baris
- `Ekspresi Guard` — tulis ulang ekspresi perbandingannya apa adanya (mis. `amount <= liquidReserves`)
- `Variabel Pembentuk` — daftar variabel di kedua sisi perbandingan
- `Penulis Variabel` — fungsi mana saja yang dapat mengubah tiap variabel tersebut (rujuk `02-state-and-var-matrix.md`)
- `Hipotesis yang Dihentikan` — apa yang ingin dilakukan penyerang dan mengapa guard ini menghentikannya
- `Status Putaran 2` — `TERSANGKAL` (guard tidak bisa digeser) atau `TEMBUS` (ada jalur pergeseran) atau `BELUM`

Aturan: guard tanpa `Variabel Pembentuk` dan `Penulis Variabel` tidak dapat diuji di Putaran 2 — lengkapi sebelum
menandai unit `[HUNTED]`. Jangan menyalin kode utuh; cukup ekspresi guard dan jalan masuknya.
