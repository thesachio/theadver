# SCHEMA — MANIFEST.json (v1)

Satu-satunya file yang wajib dibaca mesin dari repo inbox. Semua klaim harus
machine-checkable; yang tidak bisa diperiksa skrip akan menggugurkan klaim itu sendiri.

```json
{
  "version": 1,
  "project": "<slug>",
  "upstream": { "agent": "<nama>", "date": "YYYY-MM-DD", "submitted_to_program": false },
  "sources": [
    { "name": "relay-settlement",
      "url": "https://github.com/relayprotocol/relay-settlement",
      "commit": "<SHA-40 atau 12 char pertama>" }
  ],
  "findings": [ { ...lihat bawah... } ]
}
```

## Field per finding

| Field | Tipe | Wajib | Aturan |
|---|---|---|---|
| `id` | string | ya | unik dalam manifest |
| `title` | string | ya | satu baris |
| `file` | string | ya | path relatif terhadap root inbox, harus ada |
| `lines` | [int,int] | ya | `1 <= start <= end <= jumlah baris file` |
| `snippet` | string | disarankan | harus benar-benar muncul di rentang itu (whitespace dinormalkan) |
| `claim` | string | ya | satu kalimat mekanis |
| `impact` | enum | ya | `theft` · `grief` · `dos` · `design` · `none` |
| `victim` | enum | ya | `sponsor` · `user` · `protocol` · `third-party` · `none` |
| `actor` | enum | ya | `unprivileged` · `solver` · `oracle` · `admin` |
| `live` | bool | ya | true hanya bila kode ter-deploy di produksi |
| `poc` | string | ya | path file test, harus ada |
| `cmd` | string | ya | perintah persis untuk menjalankan PoC |
| `severity_claimed` | enum | ya | `S1`–`S4` |
| `not_verified` | [string] | disarankan | hal yang TIDAK dicek penulis |

## Aturan penyaringan

Skrip `ingest.py` menggugurkan klaim **tanpa biaya model** bila:

1. field wajib hilang / enum tidak dikenal
2. `lines` tidak valid, atau melebihi jumlah baris file
3. `snippet` tidak ditemukan di rentang yang diklaim
4. file target tidak ada
5. file PoC tidak ada
6. `cmd` kosong
7. `id` duplikat
8. `commit` sumber tidak cocok dengan HEAD repo yang di-clone (peringatan)

Klaim yang gugur **tidak pernah sampai ke penilai**. Itu inti penghematannya.
