# theadver — Whitehat Adversarial Security Agent Setup

Konfigurasi lengkap untuk **Hermes Agent profile `adv`**: persona, konstitusi operasional,
dan 5 skill audit smart-contract lintas-rantai (Fase 0–4 + orchestrator).

Repo ini berisi **setup agent**, bukan kode proyek audit. Tidak ada source code target
di sini, dan tidak ada secret.

## Isi

```
├── SOUL.md                      Persona: Principal Whitehat Adversarial Researcher
├── config.yaml                  Gate workflow (write_approval, delegation, cwd)
├── workspace/
│   ├── AGENTS.md                Konstitusi operasional (mengikat parent + subagent)
│   ├── README.md                Ringkasan alur Fase 0–4
│   ├── .env.rpc                 Endpoint RPC publik, no-key, read-only fork
│   ├── RPC-STATUS.md            Hasil verifikasi tiap endpoint (dengan bukti)
│   ├── .gitignore               Blokir secret + folder proyek/audit
│   └── projects/                Tempat proyek target (kosong, di-.gitignore)
└── skills/security/
    ├── sc-autopilot/            Orchestrator 4-tahap via delegate_task
    ├── sc-phase1-recon/         Recon + baseline realitas produksi
    ├── sc-phase2-hunt/          Two-stage hunting + 7 referensi
    ├── sc-phase3-verify-and-poc/ Triage 8 gerbang + PoC + 2 referensi
    └── sc-phase4-report/        Quality gate final + format 04–07
```

Laporan audit hidup di `<proyek>/audit/` — folder terlihat, bukan folder tersembunyi.
Isinya data klien dan **tidak pernah** masuk repo ini. Skrip watchdog yang terikat pada
satu proyek juga tidak masuk sini.

## Arsitektur

| Fase | Skill | Keluaran |
|---|---|---|
| 0–1 | `sc-phase1-recon` | `audit/00-project-map.md`, `01-threat-and-env.md`, `02-state-and-var-matrix.md`, `03-attack-surface-queue.md`, inisialisasi `05-raw-leads.md` |
| 2 | `sc-phase2-hunt` | `audit/05-raw-leads.md`, `audit/04-rejected-hypotheses.md`, `audit/notes/` |
| 3 | `sc-phase3-verify-and-poc` | `audit/07-confirmed-findings.md`, `06-unproven-needs-review.md`, `04-rejected-hypotheses.md` |
| 4 | `sc-phase4-report` | Quality gate final: cabut temuan yang lolos palsu, rapikan format 04–07 |
| Semua | `sc-autopilot` | Orkestrasi Fase 1 → 2 → 3 → 4 tanpa intervensi |

**Pemisahan 4 laporan adalah aturan keras**, urut kronologis di `audit/`:

```
04-rejected-hypotheses.md      gugur oleh guard, atau melanggar 8 Gerbang Realitas
05-raw-leads.md                hipotesis menunggu pembuktian PoC
06-unproven-needs-review.md    logis & lolos 8 gerbang, tapi tooling/state eksternal menghalangi
07-confirmed-findings.md       lolos 8 gerbang + PoC nyata (fork) — tidak ada yang lain
```

## Prinsip Inti

1. **Domain-agnostic, threat-first.** Kontrak dibedah sebagai mesin status, bukan dari label bisnisnya.
2. **Two-stage hunt.** Tahap A first-principles (backward sink tracing, 4 kondisi konkret, 3 lapis mutasi) sebelum Tahap B analogi referensi, ditutup Tahap C saringan 8 gerbang.
3. **8 Gerbang Realitas Bounty.** Fantasy mock, ilusi pool kosong, kode mati, admin bunuh diri, sabotase diri, debu 1 wei, negative-EV, dan fiksi fisika blockchain — satu saja terlanggar, temuan wajib ke `04`.
4. **Fork untuk 07.** Entri `07` wajib punya bukti `Mode Uji: FORK (chain, block, RPC)`. Chain tanpa RPC → turun ke `06`, bukan dipaksakan jadi confirmed.
5. **Kejujuran sandbox.** Dilarang `vm.store`, `vm.etch`, `vm.prank(admin)`, `deal` pada state protokol, dan `vm.warp` dekade.
6. **3 paradigma rantai.** Atomic account/storage (EVM/Tron/Solana), object/capability & PTB (Sui/Aptos Move), async actor (TON).

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
berjalan — repo ini adalah salinan setup, bukan worktree kerja.

## Peringatan

Endpoint RPC di `.env.rpc` **gratis tanpa SLA**. Publik dan rate-limited. Hanya untuk
fork lokal read-only. Dilarang `--broadcast`, `cast send`, atau transaksi apa pun yang
mengubah state jaringan publik.

Sui public JSON-RPC sudah deprecated (migrasi ke gRPC). `sui move test` tidak terdampak;
hanya fork state Sui nyata yang butuh endpoint sendiri.

## Atribusi

Konsep skala Tier, paradigma rantai, dan pola pengujian disusun untuk keperluan audit
whitehat defensif. Pelajari `workspace/AGENTS.md` sebelum menjalankan apa pun.
