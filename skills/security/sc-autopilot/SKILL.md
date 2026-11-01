---
name: sc-autopilot
description: Master Orchestrator Whitehat Adversarial Lintas-Rantai - Jalankan siklus penuh (Fase 1 Recon -> Fase 2 10-Method Counter-Auditor Hunt -> Fase 3 Local Fork Simulation -> Fase 4 Verdict Judge & 04-09 Reporting) secara otonom via delegate_task
version: 5.1.0
metadata:
  hermes:
    tags: [security, web3, whitehat, adversarial, orchestrator, autopilot, delegation, multichain]
    category: security
    requires_toolsets: [terminal]
---

# Autonomous Whitehat Adversarial Audit Orchestrator (sc-autopilot)

## When to Use
Gunakan skill ini saat pengguna meminta eksekusi audit whitehat adversarial menyeluruh dari awal hingga akhir tanpa intervensi manual (*Full Autopilot*), mengorkestrasi Fase 1 s/d Fase 4 menggunakan struktur 10 file murni (audit/00 s/d audit/09) dan standar hakim /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md.

## Pitfalls & Hukum Mutlak Orchestrator
- JAGA KONTEKS PARENT TETAP RINGAN: Gunakan delegate_task (max_concurrent_children: 1 secara sekuensial) agar setiap Subagent bekerja dengan konteks 0 token yang bersih.
- PATUHI KONSTITUSI `workspace/AGENTS.md` PADA SETIAP `delegate_task`: Sertakan Path Absolut Proyek, Paradigma Rantai, Core Invariants, Path File audit/00 s/d 09, instruksi skill_view, serta perintah agar Subagent mengembalikan ringkasan maksimal 12 baris saja.
- JAGA PEMISAHAN 6 FILE HASIL (`04` s/d `09` — 1 File = 1 Domain Murni):
  * `04-code-guarded.md` -> Murni hipotesis Fase 2 yang terhalang `require`/`assert!` (umpan Putaran 2 *Guard-Inversion* / Metode 5).
  * `05-raw-leads.md` -> Murni antrean aktif Fase 1 & 2 menuju Fase 3 (wajib memuat Metode Pencarian 1–10 / `[POV-XX]` dan Delta State).
  * `06-refuted-invalid.md` -> Murni hipotesis gugur permanen (gagal Langkah 0/1 *Pre-PoC Fact Gate*, gagal simulasi PoC, atau melanggar **Pernyataan Ketat Mutlak #1–#6** beserta sub-kasus ketat #7a/#8a/#9a/#10a di `VERDICT.md`).
  * `07-needs-next-step.md` -> Murni kandidat *unproven* (`NEXT_EXPLORE` / `NEXT_MAINNET` / `TOOL_BLOCKED`), termasuk klaim `HEAD-only` (gagal Pernyataan #2).
  * `08-valid-not-eligible.md` -> Murni temuan valid dalam batasan toleransi (`LOW_NUISANCE`: *DoS no fund loss*, *minor capped damage*, *griefing* — #10b; `ADMIN_ONLY` — #8b; atau `PRE_LIVE_SCOPE` — #7b).
  * `09-confirmed-findings.md` -> Murni `VALID_ELIGIBLE` (Simulasi Local Fork PASS + Bahaya Finansial Nyata + Lolos 10 Pernyataan `verify/VERDICT.md`).
- WAJIB JALANKAN TAHAP 4 (`VERDICT.md` GATE): Orchestrator DILARANG melaporkan temuan sebagai Confirmed sebelum Tahap 4 mengadilinya dengan /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md.
- DILARANG MEMANGGIL `skill_manage` ATAU `memory`.

---

## Procedure (Autonomous 4-Stage Adversarial Pipeline)

Saat pengguna memicu eksekusi otonom pada /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/, jalankan 4 tahapan orkestrasi berikut secara berurutan.

### Tahap Orkestrasi 1: Threat-First Recon (sc-phase1-recon)
1. Periksa apakah audit/00-project-map.md s/d audit/03-attack-surface-queue.md sudah ada.
2. Jika BELUM ADA: Panggil delegate_task untuk menugaskan Subagent Recon:
   - Goal: "Jalankan prosedur lengkap sc-phase1-recon pada proyek <nama-proyek> untuk menghasilkan 00-project-map.md, 01-threat-and-env.md, 02-state-and-var-matrix.md, 03-attack-surface-queue.md, dan menginisialisasi 05-raw-leads.md."
   - Context Wajib: Path Absolut Proyek /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek> dan instruksi: "Wajib panggil skill_view('sc-phase1-recon'), petakan 3 Kasta Realitas Aset, siklus hidup produksi, serta Patch-Scar dan View-vs-Write matrix, jangan ubah kode sumber, dan kembalikan ringkasan maksimal 12 baris."
3. Setelah selesai, baca audit/00-project-map.md dan audit/03-attack-surface-queue.md menggunakan read_file.

### Tahap Orkestrasi 2: Two-Stage Counter-Auditor Hunting (sc-phase2-hunt)
1. **Putaran 1 (Mikro Unit Antrean — Metode 1, 2, 3, 6, 7 + Katalog POV):**
   - Ambil unit antrean prioritas dari audit/03-attack-surface-queue.md.
   - Panggil delegate_task satu per satu untuk setiap unit antrean:
     * Goal: "Bedah unit antrean [NamaTarget] menggunakan prosedur Putaran 1 (Fondasi + Metode 1, 2, 3, 6, 7 -> Tahap B Katalog POV -> Tahap C) di sc-phase2-hunt."
     * Context Wajib: Sertakan Path Absolut Proyek, Paradigma Rantai, Core Invariants dari 00-project-map.md, path ke 01-threat-and-env.md & 02-state-and-var-matrix.md, serta instruksi: "Wajib panggil skill_view('sc-phase2-hunt') dan panggil skill_view pada modul references/ sesuai tag [LOAD: ...]. Terapkan Metode 1 (Backward Sink), Metode 2 (State-Transition Differential), Metode 3 (2-Wallet Sybil), Metode 6 (Memory Cache Overwrite & Duplicate-Array [A,A]), dan Metode 7 (Split-vs-Bulk). Tulis lead terbuka ke audit/05-raw-leads.md lengkap dengan kolom Metode Pencarian & Delta State, tulis hipotesis yang terhalang guard kode murni ke audit/04-code-guarded.md, dan kembalikan ringkasan maksimal 12 baris."
2. **Putaran 2 (Makro Lintas-Jalur — Metode 4, 5, 8, 9, 10):**
   - Periksa isi audit/05-raw-leads.md dan audit/04-code-guarded.md.
   - Tugaskan Subagent khusus untuk menjalankan 5 metode makro di `sc-phase2-hunt`:
     * **Metode 4:** Bedah *Patch-Scar*, jalur sampingan (migrate/rescue/sweep/batch), dan asimetri rumus View vs Write dari 02-state-and-var-matrix.md.
     * **Metode 5 (*Guard-Inversion*):** Bongkar seluruh daftar guard di 04-code-guarded.md dengan melacak fungsi publik pengubah variabel pembentuk guard.
     * **Metode 8 (*Caller-Callee Seam & Direct Bypass*):** Uji celah lempar tanggung jawab Router <-> Pool/Vault/Strategy dan panggilan langsung melompati Router.
     * **Metode 9 (*Suspended Lifecycle State*):** Uji siklus multi-tahap yang dihentikan pada status *pending/menggantung* lalu dipanggilkan transfer/borrow/delegate.
     * **Metode 10 (*Live On-Chain Residue & Upgrade Drift*):** Identifikasi peluang penyedotan *allowance*/saldo mengendap di kontrak perantara atau variabel proxy yang belum diinisialisasi pasca-upgrade.

### Tahap Orkestrasi 3: Method-Routed Pre-PoC Gate & Local Fork Simulation (sc-phase3-verify-and-poc)
1. **Simulasi & Pembuktian Seluruh Raw Leads (`05-raw-leads.md`):**
   - Untuk setiap lead aktif di audit/05-raw-leads.md, panggil delegate_task untuk menugaskan Subagent Verifier:
     * Goal: "Uji Lead [ID_Lead] dengan Langkah 0 (Routing Metode 1-10 / POV) & Langkah 1 (Saringan Fakta Pra-PoC) lalu jalankan simulasi eksploitasi pada Local Fork sesuai sc-phase3-verify-and-poc."
     * Context Wajib: Path Absolut Proyek, detail lead dari 05-raw-leads.md, dan instruksi: "Wajib panggil skill_view('sc-phase3-verify-and-poc'). Jalankan Langkah 0 (uji cepat sesuai Metode Pencarian 1-10 / POV) dan 4 Saringan Fakta Pra-PoC terlebih dahulu. Saat menulis kode simulasi PoC, gunakan kontrak asli (larangan Fantasy Mock), hanya vm.prank(attacker) tanpa vm.store/vm.etch, gunakan worker tunggal (-j 1), wajib jalankan simulasi transaksi pada Local Fork produksi bila RPC tersedia, dan distribusikan hasilnya secara murni ke: 09-confirmed-findings.md (Simulasi Fork PASS + dampak nyata), 07-needs-next-step.md (NEXT_EXPLORE / NEXT_MAINNET / TOOL_BLOCKED), atau 06-refuted-invalid.md (gagal saringan fakta / simulasi PoC revert). Kembalikan maksimal 12 baris."
2. **Fuzzing Invarian Stateful & Simetri** (untuk kandidat di `07-needs-next-step.md` berlabel `NEXT_EXPLORE`):
   - Tugaskan 1 Subagent Fase 3 untuk menjalankan Handler Stateful Invariant Fuzzing (Tier 2), Differential/Split-vs-Bulk Fuzzing (Tier 3), atau Symbolic Proving Halmos (Tier 5) terhadap kandidat NEXT_EXPLORE di 07-needs-next-step.md dan Core Invariants dari 00-project-map.md.

### Tahap Orkestrasi 4: Final Verdict Judging & Laporan 6 File (sc-phase4-report)
1. **WAJIB jalankan Hakim Akhir (`verify/VERDICT.md`) sebelum melapor:**
   Panggil delegate_task dengan instruksi: "Wajib panggil skill_view('sc-phase4-report') dan baca /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md. Jalankan **Langkah 0 (Rekonsiliasi Identitas Deployment)** lebih dulu: cocokkan kode yang dikutip dengan source terverifikasi explorer / `sha256`; klaim yang hanya berlaku di HEAD wajib ditandai `HEAD-only` dan maksimal berada di 07. Lalu adili setiap kandidat di audit/09-confirmed-findings.md dengan 10 Pernyataan Wajib VERDICT.md: (a) CABUT kandidat yang melanggar Pernyataan Ketat Mutlak #1–#6 beserta sub-kasus #7a/#8a/#9a/#10a lalu pindahkan ke 06-refuted-invalid.md; (b) CABUT kandidat yang masuk Pernyataan Berbatas Toleransi #10b (DoS with no fund loss, minor capped economic damage, nuisance griefing), #8b (admin-only bug tanpa jalur eksternal), atau #7b (belum live) lalu pindahkan ke 08-valid-not-eligible.md; (c) CABUT kandidat #9b yang belum disimulasikan di fork karena kendala RPC/tooling lalu pindahkan ke 07-needs-next-step.md; (d) Setiap vonis wajib memuat `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH`. Rapikan format keenam file (04 s/d 09) dan kembalikan maksimal 12 baris."
2. Baca hasil akhir di 09, 08, 07, 06, dan 04, lalu sajikan laporan eksekutif kepada pengguna.

---

## Verification
Pastikan di akhir eksekusi keenam file laporan (`04` s/d `09`) berada dalam kondisi rapi dan konsisten, kode sumber asli tidak berubah, dan tidak ada file test rusak yang tertinggal di repositori proyek. Laporkan jumlah item per file beserta daftar kandidat yang dicabut oleh Hakim `VERDICT.md` — DILARANG menyembunyikan pencabutan.
