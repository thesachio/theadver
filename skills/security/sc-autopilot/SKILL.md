---
name: sc-autopilot
description: Master Orchestrator Whitehat Adversarial Lintas-Rantai - Jalankan siklus penuh (Fase 1 Recon -> Fase 2 10-Method Counter-Auditor Hunt -> Fase 3 Local Fork Simulation -> Fase 4 Verdict Judge & 04-09 Reporting) secara otonom via delegate_task
version: 6.0.0
metadata:
  hermes:
    tags: [security, web3, whitehat, adversarial, orchestrator, autopilot, delegation, multichain]
    category: security
    requires_toolsets: [terminal]
---

# Autonomous Whitehat Adversarial Audit Orchestrator (sc-autopilot)

## When to Use
Gunakan skill ini saat pengguna meminta eksekusi audit whitehat adversarial menyeluruh dari awal hingga akhir tanpa intervensi manual (*Full Autopilot*), mengorkestrasi Fase 1 s/d Fase 4 menggunakan struktur 10 file murni (audit/00 s/d audit/09) dan standar hakim /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md.

---

## LANGKAH −1 — PRE-FLIGHT RESUME CHECK (WAJIB SEBELUM APA PUN)

Dijalankan pada setiap sesi baru, instruksi "lanjutkan/resume", atau setelah kompresi konteks. **Mengalahkan seluruh Tahap Orkestrasi 1–4 di bawah.**

### 1. Cek `audit/STATE.md`
- **BELUM ADA** -> mulai Fase 1 Langkah 0 dan **segera buat `audit/STATE.md`**. Audit tanpa STATE.md DILARANG melewati Fase 1.
- **SUDAH ADA** -> **MODE RESUME**. **DILARANG mengulang dari Fase 1.** Lanjutkan dari `CURRENT_ACTIVE_ITEM`.

### 2. Booting Hemat-Konteks
- **A** — Baca **HANYA** `audit/STATE.md` lebih dulu.
- **B** — Baca `CURRENT_ACTIVE_ITEM` dan `Working Memory Scratchpad`.
- **C** — Buka file antrean **hanya pada baris item aktif**: `03-attack-surface-queue.md` (Fase 2) atau `05-raw-leads.md` (Fase 3), via `grep -n` atau baca sebagian. DILARANG memuat file penuh.
- **D** — **DILARANG KERAS** membaca ulang kode unit di `Completed Units`, dan **DILARANG menguji ulang** lead di `06-refuted-invalid.md` / `08-valid-not-eligible.md` / `Do-Not-Reopen List`.

### 3. Write-Ahead Checkpoint
**DILARANG** pindah `S-n` -> `S-(n+1)` atau `LEAD-x` -> `LEAD-(x+1)` sebelum memperbarui `CURRENT_ACTIVE_ITEM`, `Domain Coverage Meter`, dan `Do-Not-Reopen List` di `audit/STATE.md`. Checkpoint ditulis **sebelum** unit berikutnya dimulai.

### 4. Skema Wajib `audit/STATE.md`
```
# STATE — <proyek>
PHASE: <1|2|3|4>
CURRENT_ACTIVE_ITEM: <S-n | LEAD-x | null>
LAST_UPDATED: <ISO-8601>

## Domain Coverage Meter
| Domain | Berkas | LEAD | ATTESTED | BELUM | % |

## Completed Units
- S1 ... (selesai: <ringkas 1 baris>)
- S2 ...

## Do-Not-Reopen List
- LEAD-x — <kelas vonis> — <alasan 1 baris>

## Working Memory Scratchpad
- Keputusan penting, temuan, catatan alat, path harness
```

### 5. Aturan Delegasi
Setiap `delegate_task` **WAJIB** menyertakan instruksi: *"Baca `audit/STATE.md` lebih dulu. Jangan sentuh `Completed Units` atau `Do-Not-Reopen List`. Sebelum keluar, laporkan apa yang harus ditulis ke STATE.md (CURRENT_ACTIVE_ITEM, coverage, do-not-reopen)."* Subagent DILARANG menulis STATE.md sendiri — Parent yang menulis setelah menerima ringkasan.

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

Saat pengguna memicu eksekusi otonom pada /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/, jalankan 4 tahapan orkestrasi berikut secara berurutan — **diawali Tahap Orkestrasi 0 yang wajib dan tidak boleh dilewati**.

### Tahap Orkestrasi 0: Pre-Flight Checkpoint & Auto-Resume Gate (WAJIB PALING AWAL)

Sebelum menjalankan Tahap 1, 2, 3, atau 4, Parent Orchestrator **WAJIB** memeriksa keberadaan `audit/STATE.md`.

#### 1. `audit/STATE.md` SUDAH ADA — Mode Resume Otomatis
- Baca `audit/STATE.md` lebih dulu dengan `read_file`, dan patuhi prinsip: **"Baca `audit/STATE.md` dan lanjutkan audit dari posisi kursor terakhir."**
- **DILARANG mengulang** tahap, putaran, unit antrean (`S-n`), atau lead (`LEAD-n`) yang sudah tercatat di `Completed Units`, `Dead-End Leads (06)`, atau `Verified Leads (08)` pada `audit/STATE.md`.
- **Langsung lompat** ke `Active Phase`, `Active Sub-Stage`, dan `CURRENT_ACTIVE_ITEM` yang tertulis di `audit/STATE.md`. Jangan menjalankan ulang tahap sebelumnya "untuk memastikan".
- Saat memanggil `delegate_task` untuk melanjutkan, **sertakan isi `Working Memory Scratchpad` dan daftar `Do-Not-Reopen List`** ke dalam Context Wajib Subagent. Subagent tidak boleh menebak konteks unit aktif.

#### 2. `audit/STATE.md` BELUM ADA — Mode Fresh Start
- Buat `audit/STATE.md` dengan `Active Phase: PHASE_1_RECON` dan `CURRENT_ACTIVE_ITEM: STEP_0_INVENTORY`, memakai `templates/STATE.md` sebagai skema.
- Baru setelah itu mulai dari Tahap Orkestrasi 1.

#### 3. Kewajiban Update Kursor Setiap Selesai 1 `delegate_task`
Setiap kali satu panggilan `delegate_task` selesai (baik **1 Unit `S-n`** di Tahap 2 maupun **1 Batch/Lead** di Tahap 3) dan mengembalikan ringkasan 12 baris, Parent Orchestrator **WAJIB langsung memperbarui `audit/STATE.md` SEBELUM memanggil `delegate_task` berikutnya**:
1. geser `CURRENT_ACTIVE_ITEM` ke item berikutnya,
2. tambahkan unit/lead yang baru selesai ke `Completed Units` (atau `Do-Not-Reopen List` bila gugur),
3. perbarui tabel `Domain Coverage Meter`.

> Aturan ini bersifat **write-ahead**: checkpoint ditulis sebelum pekerjaan berikutnya dimulai. Bila proses terhenti di tengah jalan, `STATE.md` harus sudah menunjukkan posisi yang benar.

---

### Tahap Orkestrasi 1: Threat-First Recon (sc-phase1-recon)
0. **Pre-flight:** bila `audit/STATE.md` belum ada, buat lebih dulu (lihat Langkah −1), lalu set `PHASE: 1`.
1. Periksa apakah audit/00-project-map.md s/d audit/03-attack-surface-queue.md sudah ada.
2. Jika BELUM ADA: Panggil delegate_task untuk menugaskan Subagent Recon:
   - Goal: "Jalankan prosedur lengkap sc-phase1-recon pada proyek <nama-proyek>: Langkah 0 (inventaris `00b-file-inventory.md`, klasifikasi PERILAKU bukan ambang baris), lalu Langkah 1–6 (termasuk Flow-Cluster <=40 Unit dan Coverage Gate >=80% per domain) untuk menghasilkan 00-project-map.md, 01-threat-and-env.md, 02-state-and-var-matrix.md, 03-attack-surface-queue.md, dan menginisialisasi 05-raw-leads.md."
   - Context Wajib: Path Absolut Proyek, path `audit/STATE.md`, dan instruksi: "Wajib panggil skill_view('sc-phase1-recon') dan baca `audit/STATE.md` lebih dulu. Petakan 3 Kasta Realitas Aset, siklus hidup produksi, Patch-Scar, dan View-vs-Write matrix. DILARANG mengubah kode sumber. Laporkan data yang harus ditulis ke STATE.md. Kembalikan ringkasan maksimal 12 baris."
3. Setelah selesai, **perbarui `audit/STATE.md`** (PHASE, Domain Coverage Meter, antrean), lalu baca audit/00-project-map.md dan audit/03-attack-surface-queue.md menggunakan read_file.

### Tahap Orkestrasi 2: Two-Stage Counter-Auditor Hunting (sc-phase2-hunt)
0. **Pre-flight:** set `PHASE: 2`. **Rotasi domain wajib**: unit dieksekusi bergilir `D1 -> D2 -> ... -> Dn -> D1`, bukan menghabiskan satu folder. Setiap unit **wajib** menghasilkan `LEAD_GENERATED` atau `ATTESTED_CLEAN` (4 unsur: fungsi, Metode, mekanisme tahan, jalur tidak diuji) sebelum pindah unit — perbarui STATE.md lebih dulu (Write-Ahead). Gate keluar: >=80% berkas `[MUST-AUDIT]` berjejak di SETIAP domain. DILARANG memakai kuota "minimal N lead per domain".
1. **Putaran 1 (Mikro Unit Antrean — Metode 1, 2, 3, 6, 7 + Katalog POV):**
   - Ambil unit antrean prioritas dari audit/03-attack-surface-queue.md.
   - Panggil delegate_task satu per satu untuk setiap unit antrean:
     * Goal: "Bedah unit antrean [NamaTarget] menggunakan prosedur Putaran 1 (Fondasi + Metode 1, 2, 3, 6, 7 -> Tahap B Katalog POV -> Tahap C) di sc-phase2-hunt."
     * Context Wajib: Sertakan Path Absolut Proyek, Paradigma Rantai, Core Invariants dari 00-project-map.md, path ke 01-threat-and-env.md & 02-state-and-var-matrix.md, serta instruksi: "Wajib panggil skill_view('sc-phase2-hunt') dan panggil skill_view pada modul references/ sesuai tag [LOAD: ...]. Terapkan Metode 1 (Backward Sink), Metode 2 (State-Transition Differential), Metode 3 (Multi-Identity Sybil), Metode 6 (Stale Snapshot Write-Back & Duplicate Reference [A,A]), dan Metode 7 (Split-vs-Bulk). Tulis lead terbuka ke audit/05-raw-leads.md lengkap dengan kolom Metode Pencarian & Delta State, tulis hipotesis yang terhalang guard kode murni ke audit/04-code-guarded.md, dan kembalikan ringkasan maksimal 12 baris."
2. **Putaran 2 (Makro Lintas-Jalur — Metode 4, 5, 8, 9, 10):**
   - Periksa isi audit/05-raw-leads.md dan audit/04-code-guarded.md.
   - Tugaskan Subagent khusus untuk menjalankan 5 metode makro di `sc-phase2-hunt`:
     * **Metode 4:** Bedah *Patch-Scar*, jalur sampingan (migrate/rescue/sweep/batch), dan asimetri rumus View vs Write dari 02-state-and-var-matrix.md.
     * **Metode 5 (*Guard-Inversion*):** Bongkar seluruh daftar guard di 04-code-guarded.md dengan melacak fungsi publik pengubah variabel pembentuk guard.
     * **Metode 8 (*Caller-Callee Seam & Direct Bypass*):** Uji celah lempar tanggung jawab Router <-> Pool/Vault/Strategy dan panggilan langsung melompati Router.
     * **Metode 9 (*Suspended Lifecycle State*):** Uji siklus multi-tahap yang dihentikan pada status *pending/menggantung* lalu dipanggilkan transfer/borrow/delegate.
     * **Metode 10 (*Live On-Chain Residue & Upgrade Drift*):** Identifikasi peluang penyedotan *allowance*/saldo mengendap di kontrak perantara atau variabel proxy yang belum diinisialisasi pasca-upgrade.

### Tahap Orkestrasi 3: Method-Routed Pre-PoC Gate & Local Fork Simulation (sc-phase3-verify-and-poc)
0. **Pre-flight:** set `PHASE: 3`. **Langkah 1a wajib:** triage BATCH atas SELURUH lead di `05-raw-leads.md` (routing metode + 4 Kemustahilan Fakta) sebelum menulis satu baris PoC pun. Setelah tabel triage tuntas, urutkan PoC berdasarkan **EV tertinggi** dengan keterwakilan domain — **BUKAN FIFO**. Patuhi **2-Strike Circuit Breaker**: maksimal 2 percobaan gagal per hipotesis, lalu `REJECTED_POC_FAILS` ke `06` dan masuk `Do-Not-Reopen List`.
1. **Simulasi & Pembuktian Seluruh Raw Leads (`05-raw-leads.md`):**
   - Untuk setiap lead aktif di audit/05-raw-leads.md, panggil delegate_task untuk menugaskan Subagent Verifier:
     * Goal: "Uji Lead [ID_Lead] dengan Langkah 0 (Routing Metode 1-10 / POV) & Langkah 1 (Saringan Fakta Pra-PoC) lalu jalankan simulasi eksploitasi pada Local Fork sesuai sc-phase3-verify-and-poc."
     * Context Wajib: Path Absolut Proyek, detail lead dari 05-raw-leads.md, dan instruksi: "Wajib panggil skill_view('sc-phase3-verify-and-poc'). Jalankan Langkah 0 (uji cepat sesuai Metode Pencarian 1-10 / POV) dan 4 Saringan Fakta Pra-PoC terlebih dahulu. Saat menulis kode simulasi PoC, gunakan kontrak asli (larangan Fantasy Mock), hanya vm.prank(attacker) tanpa vm.store/vm.etch, gunakan worker tunggal (-j 1), wajib jalankan simulasi transaksi pada Local Fork produksi bila RPC tersedia, dan distribusikan hasilnya secara murni ke: 09-confirmed-findings.md (Simulasi Fork PASS + dampak nyata), 07-needs-next-step.md (NEXT_EXPLORE / NEXT_MAINNET / TOOL_BLOCKED), atau 06-refuted-invalid.md (gagal saringan fakta / simulasi PoC revert). Kembalikan maksimal 12 baris."
2. **Fuzzing Invarian Stateful & Simetri** (untuk kandidat di `07-needs-next-step.md` berlabel `NEXT_EXPLORE`):
   - Tugaskan 1 Subagent Fase 3 untuk menjalankan Handler Stateful Invariant Fuzzing (Tier 2), Differential/Split-vs-Bulk Fuzzing (Tier 3), atau Symbolic Proving Halmos (Tier 5) terhadap kandidat NEXT_EXPLORE di 07-needs-next-step.md dan Core Invariants dari 00-project-map.md.

### Tahap Orkestrasi 4: Final Verdict Judging & Laporan 6 File (sc-phase4-report)
0. **Pre-flight — Coverage Gate (Langkah 0a):** set `PHASE: 4`. Sebelum mengadili kualitas PoC, bandingkan `00b-file-inventory.md` dengan tabel cakupan di `03-attack-surface-queue.md`. Bila cakupan `[MUST-AUDIT]` **< 80%** ATAU ada domain **0%** ATAU berkas terbesar per domain masih `BELUM` -> `AUDIT_INCOMPLETE_COVERAGE_BIAS`: **TOLAK penyelesaian laporan**, kembalikan ke Fase 1/2. Temuan lama disimpan sebagai hasil sementara.
1. **WAJIB jalankan Hakim Akhir (`verify/VERDICT.md`) sebelum melapor:**
   Panggil delegate_task dengan instruksi: "Wajib panggil skill_view('sc-phase4-report') dan baca /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md. Jalankan **Langkah 0 (Rekonsiliasi Identitas Deployment)** lebih dulu: cocokkan kode yang dikutip dengan source terverifikasi explorer / `sha256`; klaim yang hanya berlaku di HEAD wajib ditandai `HEAD-only` dan maksimal berada di 07. Lalu adili setiap kandidat di audit/09-confirmed-findings.md dengan 10 Pernyataan Wajib VERDICT.md: (a) CABUT kandidat yang melanggar Pernyataan Ketat Mutlak #1–#6 beserta sub-kasus #7a/#8a/#9a/#10a lalu pindahkan ke 06-refuted-invalid.md; (b) CABUT kandidat yang masuk Pernyataan Berbatas Toleransi #10b (DoS with no fund loss, minor capped economic damage, nuisance griefing), #8b (admin-only bug tanpa jalur eksternal), atau #7b (belum live) lalu pindahkan ke 08-valid-not-eligible.md; (c) CABUT kandidat #9b yang belum disimulasikan di fork karena kendala RPC/tooling lalu pindahkan ke 07-needs-next-step.md; (d) Setiap vonis wajib memuat `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH`. Rapikan format keenam file (04 s/d 09) dan kembalikan maksimal 12 baris."
2. Baca hasil akhir di 09, 08, 07, 06, dan 04, lalu sajikan laporan eksekutif kepada pengguna.

---

## Verification
Pastikan di akhir eksekusi keenam file laporan (`04` s/d `09`) berada dalam kondisi rapi dan konsisten, kode sumber asli tidak berubah, dan tidak ada file test rusak yang tertinggal di repositori proyek. Laporkan jumlah item per file beserta daftar kandidat yang dicabut oleh Hakim `VERDICT.md` — DILARANG menyembunyikan pencabutan.
