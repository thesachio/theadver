# Template Wadah Audit (Skema v6.3.0: Gerbang Siklus + STATE, INTEL, `04`–`09`)

Untuk **audit baru** (keputusan v6.2.0). Audit legacy tetap memakai skema lamanya.

Salin berkas-berkas template ini ke `<proyek>/audit/` sesuai fasenya:

- **`INTEL.md`** — konteks & tautan referensi Fase 0 (maks 40 baris; **penanda metadata non-destruktif** `[LIVE_BOUNTY]` vs `[REPO_STAGED]`, **bukan** pemangkas populasi `00b`)
- **`STATE.md`** — checkpoint resume (**WAJIB** di `audit/` sejak Fase 1 Langkah 0; lihat `AGENTS.md §0`)
- **`MODEL.md`** — **Blueprint Mekanisme Proyek (fakta saja, hidup)**: 7 komponen per domain (`BERKAS`·`MEKANISME`·`CHAINING`·`DATA`·`INVARIAN`+penegak·`LINGKUNGAN` ber-tag `[chain:alamat]`·`ASUMSI`), `patch` per baris, ≤12 baris/domain, +≤3/unit. Menampung pemahaman dari eksplorasi agar Fase 3 merancang uji dari mekanisme nyata, bukan tebakan. **Dilarang** memuat hipotesis (→`05`) dan status deployment (→`deploy-parity-*.json`)
- **`04-code-guarded.md`** — khusus hipotesis Fase 2 yang dihentikan **Guard Statis/Struktural** (`onlyOwner`, `msg.sender == router`, `nonReentrant`) sebagai umpan Putaran 2
- **`05-raw-leads.md`** — antrean aktif menuju Fase 3: seluruh anomali mutasi state + **Guard Dinamis/Matematis** (wajib `Kelas Topologi`, `Metode Pencarian`, dan `Delta State`)
- **`RADAR.md`** — **sinyal celah lintas-domain (append-only)**: observasi berpresisi `File:Baris` yang **belum layak jadi lead** tetapi relevan bagi unit/domain lain di proyek yang sama. Dua lapis (Observasi + Kejadian: `PROMOTED`/`RESOLVED-*`/`TARGET-ADDED`/`REOPENED`/`EXHAUSTED`), Gerbang 3-Uji (`Presisi`/`Asimetri`/`Pemicu`), ditarik dengan `grep` berbasis **path berkas** (bukan ID unit). Sinyal yang sudah punya PoC `[PASS]` **DILARANG** diparkir di sini — wajib naik ke `05`
- **`06-refuted-invalid.md`** — gugur permanen (**WAJIB** blok `BUKTI_SIMULASI:` berisi log test + Strike 3 Fuzz untuk `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, dan `REJECTED_DUST` — Pernyataan #11e)
- **`07-needs-next-step.md`** — kendala komputasi/RPC ekstrem (wajib `Disposition:` ∈ `NEXT_EXPLORE`/`NEXT_MAINNET`/`TOOL_BLOCKED`/`ENV_ERROR` + blok `PERCOBAAN:`, divalidasi `verify/tools/verify07.py`; target akhir `07` = 0 entri)
- **`08-valid-not-eligible.md`** — diisi **eksklusif oleh Hakim Fase 4**: PoC terbukti `[PASS]` (`POC_STATUS: PASS`), namun `CYCLE`/`ELIGIBILITY` menempatkannya di luar `09` — `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`, `TESTNET_ONLY`, `ENTRYPOINT_RELOCATED`, `ADMIN_ONLY`, atau `LOW_NUISANCE`
- **`09-confirmed-findings.md`** — bounty-ready (`VALID_ELIGIBLE`): PoC `[PASS]` + `ELIGIBILITY: LIVE_MATCH` + `LIVE_IDENTITY` terukur + `DEPLOYMENT_MATCH: LIVE_MATCH` + bahaya finansial nyata (Critical/High/Medium)

> **Dua sumbu ortogonal (v6.3.0):** `SEVERITY` ditentukan **impact** saja; `CYCLE`/`ELIGIBILITY` hanya menentukan **wadah**. Temuan Critical yang `HEAD_ONLY_PROVEN` tetap ditulis **Critical** meski berada di `08`. Rujuk `verify/VERDICT.md` §0.3.

**Aturan pengadilan:** `verify/VERDICT.md` (Langkah 0 Rekonsiliasi Deployment + Langkah 4a Gate Cakupan #11c/#11d + 11 Pernyataan + #11 `LAZY_BAILOUT` + #11e `PAPER_REFUTATION`). Setiap vonis wajib memuat `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH`.

**Sebelum menulis ke `audit/*.md`:** baca `AGENTS.md` Pasal 1.3 — `open(path,"w")` dan `>` shell **DILARANG** (memotong file ke 0 byte saat dibuka).
