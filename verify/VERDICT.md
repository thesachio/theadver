# PROTOKOL PENILAI (tahap verifikasi)

Penilai hanya menerima klaim dari `.verify/queue.json` (sudah lolos saringan mekanis).
Penilai **tidak** menyisir kode untuk mencari bug baru — itu tugas hulu.

## Empat langkah wajib per klaim

1. **Jalankan PoC mereka sendiri** dengan `cmd` yang diberikan. Kalau tidak PASS →
   `REJECTED_POC_FAILS`. Jangan baca kodenya lebih jauh.
2. **Audit PoC-nya.** Cari `vm.prank` sebagai admin/owner/pool, `vm.store`, `vm.etch`,
   `vm.warp` tidak wajar. Kalau ada → `REJECTED_CHEATCODE`.
3. **Baca hanya rentang `lines`** (+ guard di sekitarnya) untuk memastikan klaim sesuai kode.
4. **Jalankan gate 10 poin** di bawah.

## Gate 10 poin (satu gagal = tidak valid)

1. Baca seluruh rules program (Scope, OOS, Eligibility, Severity, PoC requirements)
2. Tunjukkan pasal yang membuat ini In Scope
3. Tunjukkan ini TIDAK masuk Out of Scope / Exclusion
4. Semua syarat eligible terpenuhi, bukan sebagian
5. Impact end-to-end: trigger → proses → dampak nyata
6. Live & reproducible, bukan teoritis
7. Severity sesuai impact terbukti, tanpa overclaim
8. Impact publik / tidak terbatas pada satu akun
9. Ceklis satu per satu
10. Baru boleh `VALID & ELIGIBLE`

## Kelas verdict

| Verdict | Arti |
|---|---|
| `VALID_ELIGIBLE` | lolos 10 poin, layak submit ke matriks |
| `VALID_NOT_ELIGIBLE` | mekanisme nyata, tapi gagal scope (belum live / aktor privilese) → kanal hardening |
| `REJECTED_BY_DESIGN` | perilaku didokumentasikan sebagai disengaja |
| `REJECTED_NO_VICTIM` | pelaku merugi sendiri / tidak ada pihak dirugikan |
| `REJECTED_POC_FAILS` | PoC tidak jalan di sandbox bersih |
| `REJECTED_CHEATCODE` | PoC bergantung pada cheatcode terlarang |
| `REJECTED_MISMATCH` | kode di `lines` tidak mendukung klaim |

## Format keluaran

```
ID          : <id>
VERDICT     : <kelas>
ALASAN      : <1–2 kalimat, sebut pasal/baris>
BUKTI       : <output test / nama file:baris>
BIAYA-BACA  : <jumlah baris yang dibaca>
```
