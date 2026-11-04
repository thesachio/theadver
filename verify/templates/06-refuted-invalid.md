# 06 — Refuted / Invalid (Gugur Permanen)

Temuan yang **gugur mutlak** per `verify/VERDICT.md`. Setiap entri wajib **diawali heading `## [ID] Judul`** dan memuat:
`ID`, `VERDICT`, `Pernyataan Dilanggar (#1-#10)`, `File:Baris`, `TANGGA_BUKTI`, `DEPLOYMENT_MATCH`, `Mode Uji`, dan **`BUKTI_SIMULASI`** (atau **`BUKTI_STATIS`** khusus untuk salah baca kode literal).

(`TANGGA_BUKTI` dan `DEPLOYMENT_MATCH` wajib ada meski vonisnya gugur — tanpa keduanya, vonis dianggap belum sah dan entri harus dikembalikan ke penulisnya.)

## GERBANG ANTI-PAPER-REFUTATION (Pernyataan #11e — `PAPER_REFUTATION_DETECTED`)

Wadah `06` **DILARANG KERAS** dipakai untuk membuang lead secara malas hanya dengan hitungan kertas atau alasan teks!

Untuk kelas vonis `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, dan `REJECTED_DUST`, entri **WAJIB** menyertakan blok `BUKTI_SIMULASI:` yang berisi:

1. **Perintah eksekusi test nyata** (`$ forge test --match-test ...` / `$ cargo test ...` / `$ sui move test ...`),
2. **Ringkasan kode setup** yang membuktikan telah dilakukannya *Victim Lifecycle Seeding* dan *3-Way EV Amplification*,
3. **Log hasil Strike 3 Mandatory Fuzzing** (`testFuzz_... (runs: 256, ...)` / `proptest` / `halmos`) yang membuktikan invarian tetap tidak tertembus.

Entri `REJECTED_POC_FAILS` / `REJECTED_NEGATIVE_EV` / `REJECTED_DUST` tanpa log eksekusi test dan fuzz di atas adalah pelanggaran **Pernyataan #11e (`PAPER_REFUTATION_DETECTED`)** → **laporan DITOLAK** di Fase 4 dan lead dikembalikan ke **Fase 3**!

## Kelas yang sah di wadah ini

**Wajib `BUKTI_SIMULASI` (Log Test + Strike 3 Fuzz):**
`REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, `REJECTED_DUST`.

**Sah dengan `BUKTI_STATIS` (Kutipan Baris Kode / Dokumen Resmi / On-Chain Bytecode):**
`REJECTED_FANTASY_MOCK` (bukan quirk nyata Kasta 2 dan bukan *Cross-Whitelist Confusion*), `REJECTED_CHEATCODE`, `REJECTED_GENESIS_MIRAGE` (hanya bila pool tunggal live permanen terisi & tanpa factory/withdraw-all), `REJECTED_PRIVILEGED_FANTASY` (hanya bila menuntut admin/oracle berbuat jahat di luar pemicu *permissionless*), `REJECTED_NON_LIVE_INIT` (hanya bila proxy & implementation sudah terkunci), `REJECTED_NO_VICTIM` (bukan *attacker donation/balance-skew*), `REJECTED_BY_DESIGN` (dilarang dipakai bila menghasilkan pencurian dana Positive-EV, insolvensi, atau pembekuan dana permanen), `REJECTED_MISMATCH`, `REJECTED_UNPROVEN_DEPLOYMENT`.

## Field wajib per entri

```markdown
## [L-XX] Contoh Penolakan
ID                  : L-XX
VERDICT             : REJECTED_POC_FAILS | REJECTED_NEGATIVE_EV | REJECTED_DUST | REJECTED_MISMATCH | ...
Pernyataan Dilanggar: <#1-#6, #7a/#8a/#9a/#10a bila relevan>
File:Baris          : <path/Kontrak.sol:Baris>
TANGGA_BUKTI        : A | A-HEAD | B | C | D
DEPLOYMENT_MATCH    : LIVE_MATCH | HEAD-only (PROVEN_ON_REPO_HEAD) | UNVERIFIED
Mode Uji            : FORK_LIVE | FORK_DEPLOYED_HEAD | LOKAL | STRUKTURAL
BUKTI_SIMULASI / BUKTI_STATIS:
  $ <perintah test & log hasil Strike 1-3 + testFuzz_..., atau kutipan baris kode statis>
ALASAN              : <1-2 kalimat tegas>
```

---
