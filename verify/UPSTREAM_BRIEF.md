# BRIEF UNTUK AGENT HULU (discovery)

Kamu adalah tahap **discovery**. Biaya modelmu rendah, jadi tugasmu menyisir luas.
Penilai hilir mahal dan hanya akan melihat klaim yang lolos saringan mekanis.

**Konsekuensinya: laporan yang kabur lebih mahal daripada tidak melapor sama sekali.**
Klaim tanpa lokasi presisi memaksa penilai mencari sendiri — itu justru biaya yang
ingin kita hindari.

## Wajib

1. **Pin commit.** Catat SHA repo sumber yang kamu audit. Tanpa ini nomor baris
   bergeser dan seluruh verifikasi jadi berburu.
2. **`file` + `lines` presisi.** Rentang sekecil mungkin yang masih memuat bukti.
   `PoolResolverBase.sol:388-397`, bukan "fungsi shortfall".
3. **`snippet`** — 1–3 baris kode yang membuktikan klaim. Penilai memakainya untuk
   memastikan nomor baris tidak meleset.
4. **PoC runnable** + `cmd` persis. Tanpa PoC, klaim S2+ otomatis tidak dapat dinilai.
5. **Deklarasikan `actor`, `victim`, `live`** dengan jujur.
   - `actor: admin`/`oracle`/`solver` = kemungkinan besar tidak eligible. Katakan apa adanya.
   - `live: false` bila kode belum ter-deploy. Itu bukan kegagalan — itu informasi.
6. **`not_verified`** — sebutkan apa yang TIDAK kamu periksa. Kejujuran ini yang membuat
   penilai tahu batas keyakinanmu.

## Dilarang

- Klaim tanpa lokasi (`"ada bug di resolver"`)
- `victim: user` tanpa bukti angka
- `impact: theft` padahal pelaku merugi sendiri
- PoC dengan `vm.prank` sebagai admin/owner/pool, `vm.store`, `vm.etch`, atau `vm.warp` lintas dekade
- Menyembunyikan bahwa kode belum live

## Layout repo inbox

```
MANIFEST.json
poc/AdvVerify_<ID>.t.sol
<source-repo>/            (clone sumber, commit dipin)
```

Setelah selesai: jalankan `python3 ingest.py .` dan pastikan semua klaimmu
berstatus `MECH-OK`. Kalau ada yang `GUGUR`, perbaiki sendiri — jangan kirim
ke penilai dalam keadaan gugur.
