# 08 — Valid but Not Eligible

Mekanisme **nyata** dan terbukti, tetapi tidak layak masuk `09` karena batas toleransi:
`[PRE_LIVE_SCOPE]` (#7b), `[ADMIN_ONLY]` (#8b), `[LOW_NUISANCE]` (#10b: DoS tanpa kehilangan dana,
kerugian kecil terbatas, griefing non-finansial), atau severity diturunkan dari klaim awal (#10).

> **Gerbang masuk:** kata "nyata dan terbukti" bersifat harfiah. Wadah ini **bukan** tempat
> menyimpan lead yang belum diuji. Lead yang mekanismenya belum dibuktikan tetap di `07`
> dan wajib `PERCOBAAN:` (Pernyataan #11b).

## Field wajib per entri

```
ID                : <L-xx / LEAD-xxx>
VERDICT           : VALID_NOT_ELIGIBLE
LOW_CLASS         : <PRE_LIVE_SCOPE | ADMIN_ONLY | LOW_NUISANCE>
TARGET_FILE       : 08-valid-not-eligible.md
ALASAN            : <mengapa masuk batas toleransi, rujuk #7b/#8b/#10b>
BUKTI MEKANISME   : <apa yang membuktikan mekanismenya jalan — PoC/simulasi, bukan dugaan>
TANGGA_BUKTI      : <B | C>   (A sudah seharusnya ke 09; D tidak sah di sini)
DEPLOYMENT_MATCH  : <sha256 sama | source explorer cocok | BEDA -> HEAD-only | tidak terverifikasi>
Mode Uji          : <FORK (chain, block) | LOKAL (alasan) | STRUKTURAL>
DAMPAK KUANTITATIF: <angka dari log: dana hilang/beku/gas, bukan kategori kualitatif>
```

**`BUKTI MEKANISME` dan `DAMPAK KUANTITATIF` wajib berisi angka atau hasil eksekusi.** Menulis
*"dampaknya kecil"* tanpa angka = entri ditolak dan lead kembali ke `07`.

## Kelas yang sah

| `LOW_CLASS` | Arti | Pernyataan |
|---|---|---|
| `PRE_LIVE_SCOPE` | Mekanisme nyata tetapi kontrak/fitur belum live, paused, atau di luar scope utama | #7b |
| `ADMIN_ONLY` | Bug mekanis nyata pada fungsi khusus admin, tanpa jalur eksploitasi eksternal | #8b |
| `LOW_NUISANCE` | DoS tanpa kehilangan dana, kerugian kecil terbatas, atau griefing non-finansial | #10b |

**Bukan kelas yang sah di sini:** hipotesis yang gagal diuji (→ `07` dengan `PERCOBAAN:`),
hipotesis gugur mutlak (→ `06`), dan temuan berdampak finansial nyata (→ `09`).
