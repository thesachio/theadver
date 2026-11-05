# 08 — Valid but Not Eligible (Terbukti Secara Mekanis, Terkendala Eligibilitas / Pre-Live / Low)

Mekanisme **nyata dan terbukti** lewat eksekusi simulasi PoC (`[PASS]`), tetapi dipisahkan oleh Hakim Fase 4 (`verify/VERDICT.md`) agar tidak masuk `09` karena berada dalam batas eligibilitas:

- **`PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` (#2 & #7b):** Kerentanan berdampak finansial nyata (Critical/High/Medium) yang PoC eksploitasinya terbukti `[PASS]` pada kode repositori (`Mode Uji: FORK_DEPLOYED_HEAD` atau `LOKAL`), tetapi kontrak/fitur tersebut belum *live* di mainnet, berbeda dari bytecode produksi saat ini (`HEAD-only`), atau belum terdaftar di halaman alamat Bug Bounty.
- **`ADMIN_ONLY` (#8b):** Bug mekanis nyata pada fungsi khusus admin, tanpa jalur eksploitasi eksternal.
- **`LOW_NUISANCE` (#10b):** DoS tanpa kehilangan dana, kerugian kecil terbatas (*capped*), atau griefing non-finansial (Severity Low / S4).

> **Gerbang masuk:**
> 1. Kata "nyata dan terbukti" bersifat **harfiah** (`[PASS]` di simulator). Wadah ini **bukan** tempat menyimpan lead yang belum diuji (lead belum teruji wajib di `07` dengan `PERCOBAAN:`, Pernyataan #11b).
> 2. Wadah `08` ini **HANYA** boleh diisi oleh **Hakim Fase 4**, bukan oleh Subagent Fase 3.

## Field wajib per entri

```markdown
## [L-XX] Contoh Pre-Live/Low
ID                  : L-XX
VERDICT             : VALID_NOT_ELIGIBLE
LOW_CLASS           : PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN) | ADMIN_ONLY | LOW_NUISANCE
TARGET_FILE         : 08-valid-not-eligible.md
ALASAN              : <mengapa valid secara mekanis namun masuk batas eligibilitas 08>
BUKTI MEKANISME     : <kode PoC & log eksekusi [PASS]>
POC_STATUS          : PASS                       <- WAJIB literal PASS; selain itu -> 07
TANGGA_BUKTI        : A-HEAD | B | C            (D tidak sah di sini)
DEPLOYMENT_MATCH    : HEAD-only (PROVEN_ON_REPO_HEAD) | LIVE_MATCH | UNVERIFIED
CYCLE               : P1_PRE_DEPLOY | P2_TESTNET_ONLY | P3_LIVE_PARTIAL | P4_LIVE_FULL
ELIGIBILITY         : HEAD_ONLY_PROVEN | TESTNET_ONLY | ENTRYPOINT_RELOCATED | LIVE_MATCH
Mode Uji            : FORK_DEPLOYED_HEAD | LOKAL | FORK_LIVE
SEVERITY            : Critical | High | Medium | Low      <- DARI IMPACT, bukan dari siklus
DAMPAK KUANTITATIF  : <angka kerugian/profit terukur dari log PoC>
```

**`BUKTI MEKANISME` dan `DAMPAK KUANTITATIF` wajib berisi hasil eksekusi PoC dan angka terukur.** Khusus untuk `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`, **kode PoC dan patch perbaikan wajib disertakan secara utuh** karena temuan ini bernilai tinggi bagi tim pengembang sebelum mereka melakukan deployment/upgrade ke mainnet. Menulis *"dampaknya kecil"* tanpa angka = entri ditolak dan lead kembali ke `07`.

> **`SEVERITY` ditentukan oleh IMPACT, BUKAN oleh `CYCLE`/`ELIGIBILITY`.** Temuan yang terbukti mencuri dana tanpa syarat **tetap ditulis `Critical`** meski `CYCLE: P1_PRE_DEPLOY`. Menuliskan `Low`/`Medium` di `08` hanya karena "belum live" adalah pelanggaran `VERDICT.md` §0.3 dan akan ditolak `verify/ingest.py`.
>
> **`POC_STATUS` wajib literal `PASS`.** `08` berarti *valid tetapi tidak eligible* — bila PoC belum bisa dijalankan (RPC mati, rantai tak dikenal, toolchain absen), tempatnya **`07`**, bukan `08`.
>
> **`CYCLE` dan `ELIGIBILITY` diisi dari artefak `deploy_parity`:** `python3 verify/tools/deploy_parity.py … --out audit/notes/deploy-parity-<ID>.json`. Bila artefak tidak ada, entri `08` ditolak.

## Kelas yang sah

| `LOW_CLASS` | Arti | Pernyataan |
|---|---|---|
| `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` | Eksploitasi terbukti `[PASS]` di atas kode repo (`FORK_DEPLOYED_HEAD`/`LOKAL`), namun kontrak/fitur masih pre-live, paused, HEAD-only, atau di luar daftar alamat bounty aktif | #2 & #7b |
| `ADMIN_ONLY` | Bug mekanis nyata pada fungsi khusus admin, tanpa jalur eksploitasi eksternal | #8b |
| `LOW_NUISANCE` | DoS tanpa kehilangan dana, kerugian kecil terbatas, atau griefing non-finansial | #10b |

**Bukan kelas yang sah di sini:** hipotesis yang gagal diuji (→ `07` dengan `PERCOBAAN:`), hipotesis gugur mutlak (→ `06` dengan `BUKTI_SIMULASI:`), dan temuan berdampak finansial nyata pada kontrak produksi aktif (→ `09`).
