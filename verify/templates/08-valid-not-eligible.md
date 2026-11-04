# 08 — Valid but Not Eligible (Terbukti Secara Mekanis, Terkendala Eligibilitas / Pre-Live / Low)

Mekanisme **nyata dan terbukti** lewat eksekusi simulasi PoC (`[PASS]`), tetapi dipisahkan oleh Hakim Fase 4 (`verify/VERDICT.md`) agar tidak masuk `09` karena berada dalam batas eligibilitas:

- **`PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` (#2 & #7b):** Kerentanan berdampak finansial nyata (Critical/High/Medium) yang PoC eksploitasinya terbukti `[PASS]` pada kode repositori (`Mode Uji: FORK_DEPLOYED_HEAD` atau `LOKAL`), tetapi kontrak/fitur tersebut belum *live* di mainnet, berbeda dari bytecode produksi saat ini (`HEAD-only`), atau belum terdaftar di halaman alamat Bug Bounty.
- **`ADMIN_ONLY` (#8b):** Bug mekanis nyata pada fungsi khusus admin, tanpa jalur eksploitasi eksternal.
- **`LOW_NUISANCE` (#10b):** DoS tanpa kehilangan dana, kerugian kecil terbatas (*capped*), atau griefing non-finansial (Severity Low / S4).

> **Gerbang masuk:**
> 1. Kata "nyata dan terbukti" bersifat **harfiah** (`[PASS]` di simulator). Wadah ini **bukan** tempat menyimpan lead yang belum diuji (lead belum teruji wajib di `07` dengan `PERCOBAAN:`, Pernyataan #11b).
> 2. Wadah `08` ini **HANYA** boleh diisi oleh **Hakim Fase 4**, bukan oleh Subagent Fase 3.

## Field wajib per entri

```
ID                 : <L-xx / LEAD-xxx>
VERDICT            : VALID_NOT_ELIGIBLE
LOW_CLASS          : PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN) | ADMIN_ONLY | LOW_NUISANCE
TARGET_FILE        : 08-valid-not-eligible.md
TANGGA_BUKTI       : A-HEAD | B          (A -> seharusnya 09; C/D tidak sah di sini)
DEPLOYMENT_MATCH   : LIVE_MATCH | HEAD-only (PROVEN_ON_REPO_HEAD) | UNVERIFIED
Mode Uji           : FORK_LIVE (chain, block, RPC) | FORK_DEPLOYED_HEAD (chain, block, RPC) | LOKAL (alasan)
BUKTI MEKANISME    : <PoC [PASS] — file test + nama fungsi test, bukan dugaan>
DAMPAK KUANTITATIF : <angka dari log: dana hilang/beku/gas, bukan kategori kualitatif>
ALASAN             : <mengapa masuk batas toleransi, rujuk #2/#7b/#8b/#10b>
```

**`BUKTI MEKANISME` dan `DAMPAK KUANTITATIF` wajib berisi angka atau hasil eksekusi.** Menulis *"dampaknya kecil"* tanpa angka = entri ditolak dan lead kembali ke `07`.

**Khusus `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`:** kode PoC **utuh** + log `[PASS]` + perhitungan dampak **wajib dipertahankan** di dalam entri. DILARANG dipangkas, DILARANG dipindah ke `07`.

## Kelas yang sah

| `LOW_CLASS` | Arti | Pernyataan |
|---|---|---|
| `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` | PoC `[PASS]` di `FORK_DEPLOYED_HEAD`/`LOKAL`, tetapi kontrak belum live, berbeda dari bytecode produksi, atau di luar daftar alamat bounty | #2, #7b |
| `ADMIN_ONLY` | Bug mekanis nyata pada fungsi khusus admin, tanpa jalur eksploitasi eksternal | #8b |
| `LOW_NUISANCE` | DoS tanpa kehilangan dana, kerugian kecil terbatas, atau griefing non-finansial | #10b |

**Bukan kelas yang sah di sini:** hipotesis yang gagal diuji (→ `07` dengan `PERCOBAAN:`), hipotesis gugur mutlak (→ `06`), dan temuan berdampak finansial nyata yang sudah live (`LIVE_MATCH`) (→ `09`).
