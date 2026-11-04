# Template Wadah Audit (Skema v6.2.0 Simulation-First: STATE, INTEL, `04`–`09`)

Untuk **audit baru** (keputusan v6.2.0). Audit legacy tetap memakai skema lamanya.

Salin berkas-berkas template ini ke `<proyek>/audit/` sesuai fasenya:

- **`INTEL.md`** — konteks & tautan referensi Fase 0 (maks 40 baris; **penanda metadata non-destruktif** `[LIVE_BOUNTY]` vs `[REPO_STAGED]`, **bukan** pemangkas populasi `00b`)
- **`STATE.md`** — checkpoint resume (**WAJIB** di `audit/` sejak Fase 1 Langkah 0; lihat `AGENTS.md §0`)
- **`04-code-guarded.md`** — khusus hipotesis Fase 2 yang dihentikan **Guard Statis/Struktural** (`onlyOwner`, `msg.sender == router`, `nonReentrant`) sebagai umpan Putaran 2
- **`05-raw-leads.md`** — antrean aktif menuju Fase 3: seluruh anomali mutasi state + **Guard Dinamis/Matematis** (wajib `Kelas Topologi`, `Metode Pencarian`, dan `Delta State`)
- **`06-refuted-invalid.md`** — gugur permanen (**WAJIB** blok `BUKTI_SIMULASI:` berisi log test + Strike 3 Fuzz untuk `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, dan `REJECTED_DUST` — Pernyataan #11e)
- **`07-needs-next-step.md`** — kendala komputasi/RPC ekstrem (wajib `Disposition:` + blok `PERCOBAAN:`, divalidasi `verify/tools/verify07.py`; target akhir `07` = 0 entri)
- **`08-valid-not-eligible.md`** — diisi **eksklusif oleh Hakim Fase 4**: PoC terbukti `[PASS]`, namun berstatus `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`, `ADMIN_ONLY`, atau `LOW_NUISANCE`
- **`09-confirmed-findings.md`** — bounty-ready (`VALID_ELIGIBLE`): PoC `[PASS]` + `DEPLOYMENT_MATCH: LIVE_MATCH` + bahaya finansial nyata (Critical/High/Medium)

**Aturan pengadilan:** `verify/VERDICT.md` (Langkah 0 Rekonsiliasi Deployment + Langkah 4a Gate Cakupan #11c/#11d + 11 Pernyataan + #11 `LAZY_BAILOUT` + #11e `PAPER_REFUTATION`). Setiap vonis wajib memuat `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH`.

**Sebelum menulis ke `audit/*.md`:** baca `AGENTS.md` Pasal 1.3 — `open(path,"w")` dan `>` shell **DILARANG** (memotong file ke 0 byte saat dibuka).
