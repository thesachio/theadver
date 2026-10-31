# verify/ — jalur verifikasi hemat token

Pemisahan tugas:

```
AGENT HULU (murah)          SKRIP (gratis)           PENILAI (mahal)
discovery + laporan   →   ingest.py: saringan   →   hanya klaim MECH-OK
                          mekanis, nol token         jalankan PoC + gate 10 poin
```

## Pakai

```bash
# clone + validasi + saring
python3 ingest.py https://github.com/<user>/<inbox-repo>.git

# atau repo lokal
python3 ingest.py /path/ke/inbox

# uji internal tanpa jaringan
python3 ingest.py --selftest
```

Keluaran: tabel ringkas + `<inbox>/.verify/queue.json`.

## Kenapa hemat

| Tahap | Biaya |
|---|---|
| clone repo inbox | 0 token |
| saringan mekanis (ingest.py) | 0 token |
| baca manifest 10 klaim | ~500 token |
| jalankan PoC 10 klaim | ~2.000 token |
| baca 50 baris per klaim | ~6.000 token |
| **total** | **~10.000 token untuk 10 klaim** |

Bandingkan dengan audit mandiri: ~28 juta token untuk repo 113 MB.

## Batas yang harus disadari

- Verifikasi **tidak** menemukan bug baru — hanya mengesahkan/menggugurkan yang ada.
- Klaim yang gugur mekanis tidak pernah dinilai; kalau hulu ceroboh, kita kehilangan
  klaim yang sebenarnya valid.
- Kalau agent hulu sudah submit ke program lebih dulu, hasil verifikasi tidak bernilai
  payout (aturan "first submission gets the full payout").
