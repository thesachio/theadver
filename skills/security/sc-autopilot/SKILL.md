---
name: sc-autopilot
description: Master Orchestrator Whitehat Adversarial Lintas-Rantai - Jalankan siklus penuh (Fase 0 Intel -> Fase 1 Recon -> Fase 2 Class-Routed Counter-Auditor Hunt via ref-method-registry -> Fase 3 Local Fork Simulation -> Fase 4 Verdict Judge & 04-09 Reporting) secara otonom via delegate_task
version: 6.1.0
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
Blok di bawah **harus identik** dengan `verify/templates/STATE.md` (sumber kebenaran tunggal). Jangan menulis varian field sendiri.
```
# AUDIT EXECUTION STATE (CHECKPOINT)

- Target Repo: <nama_repo_atau_path>
- Last Updated: <timestamp_atau_step>
- Active Phase: PHASE_0_INTEL | PHASE_1_RECON | PHASE_2_HUNT | PHASE_3_VERIFY | PHASE_4_VERDICT
- Active Sub-Stage: STEP_0_PROJECT_INTEL | STEP_0_INVENTORY | ROUND_1_MICRO | ROUND_2_MACRO | STEP_0_BATCH | POC_EXECUTION

## 1. Cursor Position (Titik Lanjut Eksak)
- Last Completed Item: <S-n (Domain: <D>) -> hasil 1 baris>
- CURRENT_ACTIVE_ITEM: <S-n (Domain: <D>)>
- Active Files in Scope: <path berkas nyata>
- Active Strike Count (Fase 3): <0/2 atau "-" bila masih Fase 2>

## 2. Domain Coverage Meter (Syarat Gate >= 80%)
| Domain | Total [MUST-AUDIT] | Selesai (Lead/Attested) | Persentase | Status |

## 3. Working Memory Scratchpad (Maks 10 Baris — Konteks Sementara Unit Aktif)
- <maks 10 baris; temuan final pindah ke 05-raw-leads.md>

## 4. Do-Not-Reopen List (Sudah Final, Dilarang Dibaca Ulang)
- Completed Units: <S-01, S-02, ...>
- Dead-End Leads (06): <LEAD-n, ...>
- Verified Leads (08): <LEAD-n, ...>
```

**Aturan isi:** `CURRENT_ACTIVE_ITEM` hanya satu; `Active Files in Scope` wajib path nyata; angka `Domain Coverage Meter` harus reproduksibel dari `00b-file-inventory.md` + tabel cakupan `03-attack-surface-queue.md`; berkas ini maksimal **50 baris** dan bukan tempat menyimpan hasil - hanya posisi.

### 5. Aturan Delegasi
Setiap `delegate_task` **WAJIB** menyertakan instruksi: *"Baca `audit/STATE.md` lebih dulu. Jangan sentuh `Completed Units` atau `Do-Not-Reopen List`. Sebelum keluar, laporkan apa yang harus ditulis ke STATE.md (CURRENT_ACTIVE_ITEM, coverage, do-not-reopen)."* Subagent DILARANG menulis STATE.md sendiri — Parent yang menulis setelah menerima ringkasan.

## Pitfalls & Hukum Mutlak Orchestrator
- JAGA KONTEKS PARENT TETAP RINGAN: Gunakan delegate_task (max_concurrent_children: 1 secara sekuensial) agar setiap Subagent bekerja dengan konteks 0 token yang bersih.
- PATUHI KONSTITUSI `workspace/AGENTS.md` PADA SETIAP `delegate_task`: Sertakan Path Absolut Proyek, Paradigma Rantai, Core Invariants, Path File audit/00 s/d 09, instruksi skill_view, serta perintah agar Subagent menulis entri lengkap ke `audit/notes/staging-<unit>.md` dan mengembalikan **manifes** maksimal 12 baris (bukan muatan entri) — lihat **3b. Protokol Staging**.
- JAGA PEMISAHAN 6 FILE HASIL (`04` s/d `09` — 1 File = 1 Domain Murni):
  * `04-code-guarded.md` -> Murni hipotesis Fase 2 yang terhalang `require`/`assert!` (umpan Putaran 2 *Guard-Inversion* / Metode 5).
  * `05-raw-leads.md` -> Murni antrean aktif Fase 1 & 2 menuju Fase 3 (wajib memuat Metode Pencarian (M-001..M-NNN / `[POV-XX]`) dan Delta State).
  * `06-refuted-invalid.md` -> Murni hipotesis gugur permanen (gagal Langkah 0/1 *Pre-PoC Fact Gate*, gagal simulasi PoC, atau melanggar **Pernyataan Ketat Mutlak #1–#6** beserta sub-kasus ketat #7a/#8a/#9a/#10a di `VERDICT.md`).
  * `07-needs-next-step.md` -> Murni kandidat *unproven* (`NEXT_EXPLORE` / `NEXT_MAINNET` / `TOOL_BLOCKED`), termasuk klaim `HEAD-only` (gagal Pernyataan #2).
  * `08-valid-not-eligible.md` -> Murni temuan valid dalam batasan toleransi (`LOW_NUISANCE`: *DoS no fund loss*, *minor capped damage*, *griefing* — #10b; `ADMIN_ONLY` — #8b; atau `PRE_LIVE_SCOPE` — #7b).
  * `09-confirmed-findings.md` -> Murni `VALID_ELIGIBLE` (Simulasi Local Fork PASS + Bahaya Finansial Nyata + Lolos 11 Pernyataan `verify/VERDICT.md`).
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
- **Jika `audit/INTEL.md` juga belum ada** → inisialisasi `audit/STATE.md` dengan `Active Phase: PHASE_0_INTEL` dan `CURRENT_ACTIVE_ITEM: STEP_0_PROJECT_INTEL`, lalu jalankan Tahap Orkestrasi 0.5.
- **Jika `audit/INTEL.md` sudah ada** → inisialisasi `audit/STATE.md` dengan `Active Phase: PHASE_1_RECON` dan `CURRENT_ACTIVE_ITEM: STEP_0_INVENTORY`, lalu langsung ke Tahap Orkestrasi 1.
- Skema disalin dari `verify/templates/STATE.md`.

#### 3. Kewajiban Update Kursor Setiap Selesai 1 `delegate_task`
Setiap kali satu panggilan `delegate_task` selesai (baik **1 Unit `S-n`** di Tahap 2 maupun **1 Batch/Lead** di Tahap 3) dan mengembalikan **manifes** 12 baris, Parent Orchestrator **WAJIB langsung memperbarui `audit/STATE.md` SEBELUM memanggil `delegate_task` berikutnya**:
1. geser `CURRENT_ACTIVE_ITEM` ke item berikutnya,
2. tambahkan unit/lead yang baru selesai ke `Completed Units` (atau `Do-Not-Reopen List` bila gugur),
3. perbarui tabel `Domain Coverage Meter`.

> Aturan ini bersifat **write-ahead**: checkpoint ditulis sebelum pekerjaan berikutnya dimulai. Bila proses terhenti di tengah jalan, `STATE.md` harus sudah menunjukkan posisi yang benar.

#### 3b. Protokol Staging: Satu Penulis per File (WAJIB)

Subagent **DILARANG** menulis ke `audit/04`–`09`. Ringkasan `≤12 baris` **bukan** tempat membawa muatan entri — satu entri butuh 15–20 baris, sedangkan unit normal menghasilkan 120–160 baris. Memaksa muatan masuk ringkasan = entri dipangkas atau ditulis tanpa pernah dibaca utuh.

**Alur wajib setiap `delegate_task`:**
1. **Subagent** menulis entri **lengkap siap-tempel** ke `audit/notes/staging-<unit>.md` (format final sudah jadi: kolom, File:Baris, guard, Delta State, blok `PERCOBAAN:`).
2. **Subagent** mengembalikan `≤12 baris` berisi **manifes saja**: `STAGING: <path> | 04: <n> | 05: <n>` (atau `06/07/08/09`) + 1 baris verdict per entri.
3. **Parent** memindahkan isi staging ke `04`–`09` memakai metode sesuai tabel `references/ref-atomic-write.md`, lalu **menghapus** file staging.

**Metode merge Parent (DILARANG `open("w")` / `>`):**

| Wadah | Metode |
|---|---|
| `06`, `08`, `09` | `append` (entri tidak diubah setelah ditulis) |
| `04`, `05`, `07` | entri baru → `append`; ubah status kemudian → `patch` |
| `STATE.md` | `patch` baris (jangan tulis ulang penuh) |

**Verifikasi merge (wajib, murah):** setelah memindahkan, jalankan `grep -c '^## \[' <file>` pada wadah tujuan dan cocokkan dengan angka manifes Subagent. Beda angka = entri hilang atau terduplikasi → perbaiki sebelum lanjut.

> **Mengapa staging, bukan izin tulis langsung.** `max_concurrent_children: 1` bersifat konfigurasi, bukan jaminan — bila dinaikkan, dua Subagent bisa menulis `05` serentak dan saling menimpa. Staging menghilangkan kelas risiko itu sepenuhnya tanpa bergantung pada setelan.

---

### Tahap Orkestrasi 0.5: Project Intelligence & Direct Reference Links (sc-project-intel)

1. Periksa apakah `audit/INTEL.md` sudah ada dan **tidak kosong**.
2. **SUDAH ADA** → lanjutkan langsung ke Tahap Orkestrasi 1.
3. **BELUM ADA** → jalankan prosedur `sc-project-intel` (atau tugaskan Subagent Intel) untuk mengumpulkan **6 informasi inti & tautan langsung** ke `audit/INTEL.md` sesuai `verify/templates/INTEL.md`:
   - Nama Proyek & organisasi
   - Overview 1–3 kalimat
   - Link UI/dApp
   - Link Repo GitHub spesifik **+ commit HEAD**
   - **Direct Link Bug Bounty Rules**
   - **Direct Links Past Audit Reports**

   Setelah selesai, perbarui `audit/STATE.md` ke `PHASE_1_RECON` (`CURRENT_ACTIVE_ITEM: STEP_0_INVENTORY`) sebelum menyentuh Tahap 1.

> `TIDAK_DITEMUKAN` adalah hasil sah (lihat hukum kejujuran `sc-project-intel`). INTEL tidak boleh memblokir audit — status `PARTIAL` tetap lanjut ke Tahap 1 dengan catatan Bagian 6 terisi.

---

### Tahap Orkestrasi 1: Threat-First Recon (sc-phase1-recon)
0. **Pre-flight:** bila `audit/STATE.md` belum ada, buat lebih dulu (lihat Langkah −1), lalu set `PHASE: 1`.
1. Periksa apakah `audit/00b-file-inventory.md` **DAN** `audit/00-project-map.md` s/d `audit/03-attack-surface-queue.md` sudah ada.
   - **Semua ada** -> lanjutkan ke butir 2 (jangan menimpa hasil yang sudah valid).
   - **Ada yang hilang** -> jalankan butir 2. Bila yang hilang hanya sebagian (mis. `00b` tidak ada tetapi `00`–`03` ada), **tetap jalankan dari Langkah 0**: inventaris adalah fondasi seluruh gerbang cakupan.

   **Proyek lama dengan audit/ sebelumnya (rebuild bersih).** Untuk proyek yang sudah pernah diaudit dengan antrean lama, **DILARANG melanjutkan di atas folder lama**:
   ```bash
   mv audit audit_old_$(date +%Y%m%d)   # arsipkan, JANGAN rm -rf
   ```
2. Panggil delegate_task untuk Subagent Recon dengan instruksi wajib:
   - **Baca `audit/INTEL.md` lebih dulu** (bila ada) untuk **menyelaraskan scope bounty** (Bagian 3) dan **riwayat laporan audit** (Bagian 4) sebelum menyusun inventaris.
   - Menerapkan **3-Level Chain Detection** (`sc-phase2-hunt/references/ref-attacker-pov.md` Bagian 3) dan menuliskannya ke `00-project-map.md`; tulis `CHAIN: AMBIGUOUS (<runtime>)` bila `.rs` bukan program Solana.
   - Menetapkan **Kelas Topologi Entitas** pada **setiap** unit `S-n` di `03-attack-surface-queue.md`: `[CLASS-A]` (Single-Entity), `[CLASS-B]` (Dual-Entity), `[CLASS-C]` (Multi-Entity Long Flow).
   - Wajib `skill_view('sc-phase1-recon')`, DILARANG mengubah kode sumber, laporkan data untuk STATE.md, kembalikan ringkasan maksimal 12 baris.
3. Setelah selesai, **perbarui `audit/STATE.md`** (PHASE, Domain Coverage Meter, antrean), lalu baca `00-project-map.md` dan `03-attack-surface-queue.md`.

---

### Tahap Orkestrasi 2: Two-Stage Counter-Auditor Hunting (sc-phase2-hunt)
0. **Pre-flight:** set `PHASE: 2`.

   **Interleaved Domain Wave & Position-Blind Fixed Quota:**
   - Rotasi berjalan lintas domain `D1 -> D2 -> ... -> Dn -> D1`. Di dalam setiap domain, unit `[CLASS-A]`, `[CLASS-B]`, dan `[CLASS-C]` dibedah **tanpa mendiskriminasi urutan bawah** — kontrak `[CLASS-A]` tunggal bisa memegang 100% TVL.
   - **1 panggilan `delegate_task` = tepat 1 Unit `S-n`.** DILARANG merapel beberapa unit di ekor antrean (*No Tail-End Compression*).
   - Prompt Subagent **DILARANG** memuat label "prioritas rendah / urutan bawah / EV kecil" (*Position-Blind*).
   - Gate keluar: >= 80% berkas `[MUST-AUDIT]` berjejak di **SETIAP** domain. DILARANG memakai kuota "minimal N lead per domain".

1. **Putaran 1 (Mikro — metode sesuai kelas topologi unit):**
   - Ambil **satu** unit dari `audit/03-attack-surface-queue.md`, panggil `delegate_task` satu per satu.
     * **Goal:** "Bedah unit `S-n` menggunakan prosedur Putaran 1 di `sc-phase2-hunt`."
     * **Context Wajib:**
       - Path Absolut Proyek, Paradigma Rantai, Core Invariants dari `00-project-map.md`, path `01-threat-and-env.md` & `02-state-and-var-matrix.md`, dan `audit/INTEL.md` bila ada.
       - Wajib `skill_view('sc-phase2-hunt')`, lalu **baca `references/ref-method-registry.md`** dan **`references/ref-attacker-pov.md`**.
       - **Jalankan paket metode `M-001..M-NNN` sesuai kelas topologi unit**:
         `[CLASS-A]` → *Single-Pass Deep Kill* (`M-005` inline saat itu juga);
         `[CLASS-B]` → *Dual-Entity* (CLASS-A + `M-003`, `M-006` Prinsip A+B, `M-008`, `M-010`);
         `[CLASS-C]` → *Multi-Entity Long Flow* (paket penuh, penekanan rantai komposisi panjang).
       - **Lazy-load `references/ref-pov-<math|call|defi|chain>.md`** HANYA bila gejala pemicu di tabel router `ref-attacker-pov.md` terpenuhi.
       - **KELUARAN:** tulis entri LENGKAP siap-tempel ke `audit/notes/staging-<unit>.md` (staging WAJIB); `03` boleh di-`patch` pada baris status; **`STATE.md` DILARANG disentuh**. Kembalikan manifes ≤ 20 baris: `STAGING: <path> | 04: <n> | 05: <n>` + 1 baris verdict per entri.
       - Entri `05` wajib memuat `Kelas Topologi`, kolom Metode Pencarian (`M-00X`/`[POV-XX]`), dan Delta State; entri `04` wajib memuat File:Baris, Ekspresi Guard, Variabel Pembentuk.

2. **Putaran 2 / Sintesis Lintas-Jalur:**
   - Bongkar **seluruh** guard di `04-code-guarded.md` **lintas-entitas** (`M-005` cross-contract, `M-008` seam, `M-009` suspended lifecycle, `M-010` residual/drift).
   - **Unified Phase 3 Gate:** DILARANG masuk Tahap Orkestrasi 3 sebelum **seluruh kelas (A, B, C)** lulus Gate Cakupan >= 80% per domain dan Putaran 2 ditutup.

---

### Tahap Orkestrasi 3: Method-Routed Pre-PoC Gate & Local Fork Simulation (sc-phase3-verify-and-poc)
0. **Pre-flight:** set `PHASE: 3`. **Langkah 1a wajib:** triage BATCH atas SELURUH lead di `05-raw-leads.md` (routing metode + 4 Kemustahilan Fakta) sebelum menulis satu baris PoC pun. Setelah tabel triage tuntas, urutkan PoC berdasarkan **EV tertinggi** dengan keterwakilan domain — **BUKAN FIFO**. Patuhi **2-Strike Circuit Breaker**: maksimal 2 percobaan gagal per hipotesis, lalu `REJECTED_POC_FAILS` ke `06` dan masuk `Do-Not-Reopen List`.
   **Juga berlaku mutlak di tahap ini:**
   - **Langkah 0c (Tangga Self-Healing):** label `TOOL_BLOCKED` DILARANG untuk masalah kompilasi dependency/remapping/versi compiler/test runner. Wajib menempuh Usaha 1 (flag & toolchain) → Usaha 2 (**Standalone Interface-Only / Minimal Harness**) → Usaha 3 (fallback RPC), lalu lampirkan log ketiganya.
   - **Langkah 0d (Do-It-Now):** `NEXT_MAINNET` DILARANG bila RPC tersedia — jalankan `cast call`/`cast storage`/`cast implementation` saat itu juga. `NEXT_EXPLORE` DILARANG bila baru 1 skenario sederhana — wajib jalankan multi-step chaining / Differential (Tier 3) / Handler Fuzzing (Tier 2) / halmos (Tier 5) hingga timeout komputasi.
1. **Simulasi & Pembuktian Seluruh Raw Leads (`05-raw-leads.md`) — Unified Cross-Class:**
   - **Kuota delegasi PoC: maksimal 1 s/d 3 Lead per Subagent**, dari urutan **pertama sampai urutan paling akhir**. DILARANG KERAS merapel 5–10 lead sisa ke satu Subagent pembersih (*No Tail-End Compression*). Prompt DILARANG melabeli lead sebagai "sisa/prioritas rendah/EV kecil".
   - Fase 3 berjalan atas **gabungan lead A + B + C** setelah semua kelas lulus Gate Cakupan Fase 2.
   - Untuk setiap lead aktif di audit/05-raw-leads.md, panggil delegate_task untuk menugaskan Subagent Verifier:
     * Goal: "Uji Lead [ID_Lead] (maks 1–3 lead per Subagent) dengan Langkah 0 (Routing dinamis `M-001..M-NNN` / `[POV-XX]` via `ref-method-registry.md` & `ref-pov-*.md`) & Langkah 1 (Saringan Fakta Pra-PoC) lalu jalankan simulasi eksploitasi pada Local Fork sesuai sc-phase3-verify-and-poc."
     * Context Wajib: Path Absolut Proyek, detail lead dari 05-raw-leads.md, path `audit/STATE.md`, dan instruksi: "Wajib panggil skill_view('sc-phase3-verify-and-poc') dan baca `audit/STATE.md` lebih dulu. Jalankan Langkah 0b (2-Strike), Langkah 0c (Tangga Self-Healing), Langkah 0d (Do-It-Now), Langkah 1a (triage batch) dan 4 Saringan Fakta Pra-PoC. Saat menulis kode simulasi PoC: gunakan kontrak asli (larangan Fantasy Mock), hanya vm.prank(attacker) tanpa vm.store/vm.etch, worker tunggal (-j 1), wajib Local Fork produksi bila RPC tersedia. **PROTOKOL 3-WAY EV AMPLIFICATION (WAJIB):** DILARANG memvonis `REJECTED_DUST` / `REJECTED_NEGATIVE_EV` sebelum ketiga pengali diuji dan angkanya dicatat di `audit/notes/` — (a) Flashloan/Capital Scaling, (b) Single-Tx Looping/Batching, (c) Cross-Lead/Cross-Class Chaining ke guard di `04-code-guarded.md`. **DISTRIBUSI:** hasil wajib tegas ke `09` (Fork PASS + dampak nyata), `08` (valid tapi Low/admin-only/pre-live), atau `06` (gugur). **KELUARAN: tulis entri LENGKAP siap-tempel ke `audit/notes/staging-<lead>.md` — staging WAJIB untuk hasil verifikasi lead; jangan menulis ke `06`/`07`/`08`/`09` langsung.** **`07` HANYA boleh dengan blok bukti `PERCOBAAN:` berisi perintah + keluaran — `NEXT_EXPLORE` wajib lampiran log fuzzer/chaining yang mentok timeout, `TOOL_BLOCKED` wajib lampiran log ketiga usaha self-healing, `NEXT_MAINNET` wajib bukti rantai tanpa RPC. Tanpa lampiran, jangan tulis 07 — kerjakan sampai tuntas.** Laporkan ke STATE.md. Kembalikan maksimal 12 baris berupa MANIFES: `STAGING: <path> | 06: <n> | 07: <n> | 08: <n> | 09: <n>` + 1 baris verdict per entri."
2. **Fuzzing Invarian Stateful & Simetri** (untuk sisa kandidat yang belum bisa dituntaskan):
   - Tugaskan 1 Subagent Fase 3 untuk menjalankan Handler Stateful Invariant Fuzzing (Tier 2), Differential/Split-vs-Bulk Fuzzing (Tier 3), atau Symbolic Proving Halmos (Tier 5). **Wajib dijalankan pada sesi ini** — bukan ditunda sebagai alasan `NEXT_EXPLORE`. Lampirkan perintah, statistik run, dan waktu timeout ke `notes/`.

### Tahap Orkestrasi 4: Final Verdict Judging & Laporan 6 File (sc-phase4-report)
0. **Pre-flight — DUA GATE:** set `PHASE: 4`.
   - **(i) Coverage Gate (Langkah 0a butir 1-3):** bandingkan `00b-file-inventory.md` dengan tabel cakupan `03-attack-surface-queue.md`. Bila cakupan `[MUST-AUDIT]` **< 80%** ATAU ada domain **0%** ATAU berkas terbesar per domain masih `BELUM` -> `AUDIT_INCOMPLETE_COVERAGE_BIAS`: **TOLAK laporan**, kembalikan ke Fase 1/2. Temuan lama disimpan sebagai hasil sementara.
   - **(ii) LAZY_BAILOUT Gate (Langkah 0a butir 3b / Pernyataan #11):** periksa **SETIAP** entri `07`. `TOOL_BLOCKED` tanpa log 3-Step Self-Healing, `NEXT_MAINNET` padahal RPC tersedia, atau `NEXT_EXPLORE` tanpa log fuzzer yang mentok timeout -> `LAZY_BAILOUT_DETECTED`: **TOLAK laporan**, kembalikan entri ke Fase 3 sampai menjadi `09`/`08`/`06`. Label basi (judul sudah pindah tapi label lama masih ada) juga dihitung tidak sah. **Target akhir `07` = 0 entri.**
1. **WAJIB jalankan Hakim Akhir (`verify/VERDICT.md`) sebelum melapor:**
   Panggil delegate_task dengan instruksi: "Wajib panggil skill_view('sc-phase4-report') dan baca /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md serta `audit/STATE.md`. Jalankan **Langkah 0 (Rekonsiliasi Identitas Deployment)** lebih dulu: cocokkan kode yang dikutip dengan source terverifikasi explorer / `sha256`; klaim yang hanya berlaku di HEAD wajib ditandai `HEAD-only` dan maksimal berada di 07. Lalu adili setiap kandidat di audit/09-confirmed-findings.md dengan **11 Pernyataan Wajib VERDICT.md** (termasuk Langkah 4a Gate Cakupan + **#11 `LAZY_BAILOUT_DETECTED`**): (a) CABUT kandidat yang melanggar Pernyataan Ketat Mutlak #1–#6 beserta sub-kasus #7a/#8a/#9a/#10a lalu pindahkan ke 06-refuted-invalid.md; (b) CABUT kandidat yang masuk Pernyataan Berbatas Toleransi #10b (DoS with no fund loss, minor capped economic damage, nuisance griefing), #8b (admin-only bug tanpa jalur eksternal), atau #7b (belum live) lalu pindahkan ke 08-valid-not-eligible.md; (c) Untuk kandidat #9b: **DILARANG memarkir ke 07 tanpa bukti percobaan** — periksa apakah `07` memuat blok `PERCOBAAN:` (perintah + keluaran) untuk `NEXT_EXPLORE`/`TOOL_BLOCKED`, dan bukti rantai tanpa RPC untuk `NEXT_MAINNET`. Bila tidak ada: jalankan sendiri `cast call`/`cast storage` bila RPC tersedia, atau kembalikan ke Fase 3. Setiap entri `07` tanpa bukti = `LAZY_BAILOUT_DETECTED`; (d) Setiap vonis wajib memuat `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH`. Rapikan format keenam file (04 s/d 09), laporkan jumlah entri `07`, dan kembalikan maksimal 12 baris."
2. Baca hasil akhir di 09, 08, 07, 06, dan 04, lalu sajikan laporan eksekutif kepada pengguna — **wajib menyertakan baris `COVERAGE:` dan `LAZY_BAILOUT:`** beserta jumlah entri `07`.

---

## Verification
Pastikan di akhir eksekusi keenam file laporan (`04` s/d `09`) berada dalam kondisi rapi dan konsisten, kode sumber asli tidak berubah, dan tidak ada file test rusak yang tertinggal di repositori proyek. Laporkan jumlah item per file beserta daftar kandidat yang dicabut oleh Hakim `VERDICT.md` — DILARANG menyembunyikan pencabutan.
