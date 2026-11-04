# theadver — Whitehat Adversarial Security Agent Setup (v6.2.0 Simulation-First)

Konfigurasi lengkap untuk **Hermes Agent profile `adv`**: persona, konstitusi operasional
(`workspace/AGENTS.md`), standar Hakim Akhir (`verify/VERDICT.md`), dan **6 skill** audit
smart-contract lintas-rantai (Fase 0–4 + orchestrator `sc-autopilot`).

Repo ini berisi **setup agent**, bukan kode proyek audit. Tidak ada source code target
di sini, dan tidak ada secret.

## Isi

```
├── SOUL.md                            Persona: Principal Whitehat Adversarial Researcher
├── config.yaml                        Gate workflow (write_approval, delegation, cwd)
├── sync.sh                            Sinkronisasi profil → repo git ini
├── verify/
│   ├── VERDICT.md                     Standar Hakim Akhir (11 Pernyataan + Gate Cakupan + #11e)
│   ├── ingest.py                      Pipeline verifikasi inbox mekanis
│   ├── templates/                     Template skema murni (STATE, INTEL, 04 s/d 09)
│   └── tools/verify07.py              Validator mekanis bukti usaha untuk 07
├── workspace/
│   ├── AGENTS.md                      Konstitusi operasional (mengikat parent + subagent)
│   ├── README.md                      Ringkasan alur Fase 0–4 (v6.2.0)
│   ├── .env.rpc                       Endpoint RPC publik, no-key, read-only fork
│   ├── rpc-free-tier.md               Daftar endpoint RPC gratis cadangan lintas-rantai
│   ├── RPC-STATUS.md                  Hasil verifikasi tiap endpoint (dengan bukti)
│   ├── .gitignore                     Blokir secret + folder proyek/audit
│   └── projects/                      Tempat proyek target (kosong, di-.gitignore)
└── skills/security/
    ├── sc-autopilot/                  Orchestrator 5-tahap (Fase 0 → 1 → 2 → 3 → 4)
    ├── sc-project-intel/              Fase 0: Pengumpul tautan referensi & metadata INTEL.md
    ├── sc-phase1-recon/               Fase 1: Inventaris 100% (00b), peta proyek, & antrean (00–03)
    ├── sc-phase2-hunt/                Fase 2: Counter-Auditor hunting + Method Registry & POV
    ├── sc-phase3-verify-and-poc/      Fase 3: Simulation-First Lab (Dual-Mode Fork + 3-Stage Fuzz)
    └── sc-phase4-report/              Fase 4: Hakim Akhir VERDICT.md & pemisahan 09 vs 08
```

Laporan audit hidup di `<proyek>/audit/` — folder terlihat, bukan folder tersembunyi.
Isinya data klien dan **tidak pernah** masuk repo ini.

## Arsitektur 5-Tahap & Skema 6-File Hasil (`04`–`09`)

| Fase | Skill | Keluaran Utama di `audit/` |
|---|---|---|
| 0 | `sc-project-intel` | `INTEL.md` (6 informasi konteks & link langsung; **penanda metadata non-destruktif**) |
| 1 | `sc-phase1-recon` | `STATE.md`, `00b-file-inventory.md` (**100% populasi fisik**), `00-project-map.md`, `01-threat-and-env.md`, `02-state-and-var-matrix.md`, `03-attack-surface-queue.md`, inisialisasi `05-raw-leads.md` |
| 2 | `sc-phase2-hunt` | `04-code-guarded.md` *(khusus guard statis)*, `05-raw-leads.md` *(anomali + guard dinamis/matematis)*, `notes/staging-*.md` |
| 3 | `sc-phase3-verify-and-poc` | Kandidat `09-confirmed-findings.md`, `07-needs-next-step.md` *(target 0 entri)*, `06-refuted-invalid.md` *(wajib log simulasi untuk #11e)* |
| 4 | `sc-phase4-report` | Vonis akhir via `verify/VERDICT.md`: memisahkan `09` (*Live Production*) vs `08-valid-not-eligible.md` (*Pre-Live `HEAD_ONLY_PROVEN` / Low / Admin-Only*), mengaudit cakupan (#11d), `07` (#11), dan `06` (#11e) |
| Semua | `sc-autopilot` | Orkestrasi otonom Fase 0 → 1 → 2 → 3 → 4 dengan checkpoint `STATE.md` |

**Pemisahan 6 wadah hasil (`04` s/d `09`) adalah aturan keras** di `audit/`:

```
04-code-guarded.md        Murni hipotesis Fase 2 yang dihentikan Guard Statis/Struktural (umpan Putaran 2)
05-raw-leads.md           Antrean aktif anomali state & Guard Dinamis/Matematis (input Fase 3)
06-refuted-invalid.md     Gugur permanen (WAJIB log eksekusi test + Strike 3 Fuzz untuk POC_FAILS/EV/DUST)
07-needs-next-step.md     Kendala komputasi/RPC ekstrem setelah 3-Step Self-Healing (Target akhir = 0 entri)
08-valid-not-eligible.md  PoC terbukti [PASS], namun berstatus Pre-Live (HEAD_ONLY_PROVEN), Admin-Only, atau Low
09-confirmed-findings.md  Lolos 11 Pernyataan VERDICT.md + Fork Live [PASS] + Bahaya Finansial Nyata
```

## Prinsip Inti (v6.2.0 Simulation-First)

1. **100% Populasi Fisik & Cakupan Berjejak (#11c & #11d).** Seluruh kontrak `[MUST-AUDIT]` di repositori terdaftar di `00b-file-inventory.md` dan wajib memiliki jejak (`LEAD_GENERATED` atau `ATTESTED_CLEAN` bersitasi `File:Baris`). `INTEL.md` tidak pernah dipakai untuk memangkas cakupan kode di hulu.
2. **Pemisahan Guard Statis vs Dinamis.** Guard izin statis masuk `04`; semua guard yang melibatkan matematika, rasio, saldo, waktu, atau array wajib masuk `05` untuk diuji dengan fuzzer di Fase 3.
3. **Simulation-First & No Paper Refutation (#11e).** Fase 3 dilarang menggugurkan lead matematika, logika, atau ekonomi hanya dengan hitungan kertas. Menolak lead dengan klaim `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, atau `REJECTED_DUST` tanpa log eksekusi test dan fuzz memicu `PAPER_REFUTATION_DETECTED`.
4. **Dual-Mode Fork (`FORK_LIVE` & `FORK_DEPLOYED_HEAD`) + Victim Seeding.** Kontrak live diuji dengan `FORK_LIVE`; kontrak repo yang belum deploy / HEAD-only diuji dengan men-deploy kode HEAD di atas fork mainnet (`FORK_DEPLOYED_HEAD`). Setiap PoC wajib menyimulasikan transaksi korban normal (*Victim Seeding*) sebelum menyimpulkan kegagalan.
5. **3-Stage Escalation (2 Manual + 1 Mandatory Fuzz).** Sebelum lead dinyatakan gagal di Fase 3, agen wajib menempuh Strike 1 (Manual + Victim Seeding), Strike 2 (Perbaikan Urutan + 3-Way EV Amplification), dan Strike 3 (1× tes Fuzz `testFuzz_` / `proptest` / `halmos`).
6. **Gerbang Deployment Eksklusif di Fase 4 (`09` vs `08`).** Fase 3 buta terhadap administrasi bounty dan fokus membuktikan mekanisme eksploitasi. Di Fase 4, Hakim `VERDICT.md` memisahkan PoC yang `[PASS]` pada kontrak produksi aktif ke `09`, dan PoC yang `[PASS]` pada kode HEAD-only / pre-live ke `08` (`PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN`).

## Toolchain yang Diuji

| Tool | Versi | Status |
|---|---|---|
| forge / cast / anvil / chisel | 1.8.5 | terverifikasi (build + test + fork) |
| halmos | 0.3.3 | terverifikasi (SMT, 4 paths PASS) |
| sui | 1.83.0 | terverifikasi (`sui move build` + `test`) |
| aptos | 9.6.0 | terverifikasi (`aptos move compile`) |
| vyper | 0.4.1 | terpasang |
| cargo / rustc | 1.99.1 | terpasang |
| node / npx | 26.7.0 / 12.0.2 | terpasang |

Solc 0.8.28 via Forge. `rg`, `jq`, `git` tersedia.

## Konfigurasi Hermes

```yaml
terminal:
  cwd: /home/ubuntu/.hermes/profiles/adv/workspace
skills:
  write_approval: true
memory:
  write_approval: true
delegation:
  max_iterations: 150
  max_concurrent_children: 1
```

`worktree_isolation` tidak diaktifkan. Tidak ada `.git` di level workspace saat agent
berjalan — repo ini adalah salinan setup, bukan worktree kerja. Gunakan `./sync.sh`
untuk menyinkronkan profil aktif `~/.hermes/profiles/adv` ke repositori git ini.

## Peringatan

Endpoint RPC di `.env.rpc` dan `workspace/rpc-free-tier.md` **gratis tanpa SLA**. Publik dan
rate-limited. Hanya untuk fork lokal read-only. Dilarang `--broadcast`, `cast send`, atau
transaksi apa pun yang mengubah state jaringan publik.

Sui public JSON-RPC sudah deprecated (migrasi ke gRPC). `sui move test` tidak terdampak;
hanya fork state Sui nyata yang butuh endpoint sendiri.

## Atribusi

Konsep skala Tier, paradigma rantai, dan arsitektur Simulation-First disusun untuk keperluan
audit whitehat defensif. Pelajari `workspace/AGENTS.md` dan `verify/VERDICT.md` sebelum
menjalankan apa pun.
