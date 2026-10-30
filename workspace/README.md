# theadver — Whitehat Adversarial Security Agent Setup

Konfigurasi lengkap untuk **Hermes Agent profile `adv`**: persona, konstitusi operasional,
dan 4 skill audit smart-contract lintas-rantai (Fase 1–3 + orchestrator).

Repo ini berisi **setup agent**, bukan kode proyek audit. Tidak ada source code target
di sini, dan tidak ada secret.

## Isi

```
├── SOUL.md                      Persona: Principal Whitehat Adversarial Researcher
├── workspace/
│   ├── AGENTS.md                Konstitusi operasional (mengikat parent + subagent)
│   ├── .env.rpc                 Endpoint RPC publik, no-key, read-only fork
│   ├── RPC-STATUS.md            Hasil verifikasi tiap endpoint (dengan bukti)
│   └── projects/                Tempat proyek target (kosong, di-.gitignore)
└── skills/security/
    ├── sc-autopilot/            Orchestrator 4-tahap via delegate_task
    ├── sc-phase1-recon/         Threat-first reconnaissance
    ├── sc-phase2-hunt/          3-layer adversarial hunting + 7 referensi
    └── sc-phase3-verify/        6-tier testing lab + 2 referensi
```

## Arsitektur

| Fase | Skill | Keluaran |
|---|---|---|
| 0–1 | `sc-phase1-recon` | `audit/00-project-map.md`, `01-threat-and-env.md`, `02-state-and-var-matrix.md`, `03-attack-surface-queue.md`, `06-raw-leads.md` |
| 2 | `sc-phase2-hunt` | `audit/06-raw-leads.md`, `07-rejected-hypotheses.md`, `audit/notes/` |
| 3 | `sc-phase3-verify` | `audit/04-verified-findings.md`, `05-potential-candidates.md`, dll. |
| Semua | `sc-autopilot` | Orkestrasi Fase 1 → 2 → 3 tanpa intervensi |

**Pemisahan 4 laporan adalah aturan keras** — temuan valid, kandidat potensial, jejak
mentah, dan hipotesis tertolak tidak boleh dicampur dalam satu file.

## Prinsip Inti

1. **Threat-first, bukan name-first.** Fungsi dikenali dari mutasi state, bukan dari namanya.
2. **3 lapis eksplorasi.** Radius 0–2 lifecycle → variable-centric & permutasi 3 langkah → guard-bypass & math deep-dive.
3. **Kejujuran sandbox.** Dilarang `vm.prank` sebagai admin, `vm.store`, `vm.warp` dekade. Wajib buktikan net profit nyata.
4. **3 paradigma rantai.** Atomic account/storage (EVM/Tron/Solana), object/capability & PTB (Sui/Aptos Move), async actor (TON).

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
