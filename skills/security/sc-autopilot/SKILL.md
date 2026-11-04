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

### Tahap Orkestrasi 3: Simulation-First Pre-PoC Triage & Dual-Mode Fork Lab (sc-phase3-verify-and-poc)
0. **Pre-flight:** set `PHASE: 3`. **Langkah 1a wajib:** susun tabel triage **BATCH** atas **SELURUH** lead di `05-raw-leads.md` di `audit/notes/fase3-urutan-poc.md` (petakan skenario harness, kebutuhan *Victim Seeding*, dan potensi chaining lintas-kelas), lalu urutkan eksekusi PoC berdasarkan **EV tertinggi dengan keterwakilan domain** — **BUKAN FIFO**.

**Hukum Mutlak di Tahap Orkestrasi 3:**
- **Hukum *No Code, No Reject*:** DILARANG KERAS menggugurkan lead logika/matematika/ekonomi ke `06` di Langkah 1 hanya berdasarkan hitungan kertas **tanpa menulis dan menjalankan kode simulasi test**!
- **Protokol *3-Stage Escalation (2 Manual + 1 Mandatory Fuzz)*:** Lead DILARANG dibuang ke `06` sebagai `REJECTED_POC_FAILS` / `REJECTED_NEGATIVE_EV` / `REJECTED_DUST` hanya dari 2 percobaan manual; **percobaan ke-3 WAJIB** menggunakan `testFuzz_` (atau `proptest`/`halmos`) untuk mengacak parameter input sebelum boleh dinyatakan gugur dan masuk **Do-Not-Reopen List**.
- **DILARANG Menyentuh Wadah `08` di Tahap 3:** Subagent Fase 3 **buta** terhadap apakah kontrak sudah *live* di halaman bounty atau masih HEAD-only. Bila kontrak sudah live di on-chain, gunakan **`FORK_LIVE`**; bila kontrak belum deploy atau kode HEAD berbeda, gunakan **`FORK_DEPLOYED_HEAD`** (deploy kontrak repo di atas fork mainnet). **Semua PoC yang PASS membuktikan patahnya invarian wajib diajukan sebagai kandidat `09` (lewat staging)** untuk diadili di Tahap 4!
- **Langkah 0c (Tangga Self-Healing) & Langkah 0d (Do-It-Now):** Tetap mengikat mutlak sebelum label `TOOL_BLOCKED`, `NEXT_MAINNET`, atau `NEXT_EXPLORE` boleh dipakai di `07`.

1. **Simulasi & Pembuktian Seluruh Raw Leads (`05-raw-leads.md`) — Unified Cross-Class:**
   - **Kuota delegasi PoC:** maksimal **1 s/d 3 Lead per Subagent**, dari urutan **pertama sampai urutan paling akhir** (*No Tail-End Compression*, *Position-Blind*).
   - Untuk setiap batch 1–3 lead aktif di `audit/05-raw-leads.md`, panggil `delegate_task` untuk menugaskan Subagent Verifier:
     * **Goal:** "Buktikan mekanisme Lead `[ID_Lead]` (maks 1–3 lead) melalui simulasi eksekusi nyata (`FORK_LIVE`, `FORK_DEPLOYED_HEAD`, atau harness native non-EVM) dengan *Realistic Victim Seeding*, *3-Way EV Amplification*, dan *Fuzz Escalation* sesuai `sc-phase3-verify-and-poc`."
     * **Context Wajib:** Path Absolut Proyek, detail lead dari `05-raw-leads.md`, path `audit/STATE.md`, dan instruksi literal berikut:
       > "Wajib panggil `skill_view('sc-phase3-verify-and-poc')` dan baca `audit/STATE.md` lebih dulu.
       > **URUTAN WAJIB EKSEKUSI:**
       > (1) **DILARANG *Paper Refutation***: Jangan buang lead ke `06` hanya dengan hitungan kertas! Gunakan routing metode di `ref-method-registry.md` & `ref-pov-*.md` untuk **merancang kode test**.
       > (2) **Pilih Mode Simulasi Terbaik**: Jika kontrak target sudah ter-deploy di rantai ber-RPC, jalankan **`Mode Uji: FORK_LIVE`**. Jika kontrak belum ter-deploy atau kode repo (HEAD) lebih baru, **WAJIB** jalankan **`Mode Uji: FORK_DEPLOYED_HEAD`** (nyalakan `--fork-url` rantai target agar token/oracle/pool eksternal tetap asli, lalu deploy kontrak repo di atas fork tersebut). Gunakan **`LOKAL`** hanya untuk non-EVM atau rantai tanpa RPC.
       > (3) **WAJIB *Victim Lifecycle Seeding***: Jika state kontrak sedang kosong/pasif, simulasikan transaksi pengguna normal (`vm.prank(victim)` melakukan `deposit`/`borrow`/`requestWithdraw`/`createOrder`/`approve`) lebih dulu sebelum menembakkan `vm.prank(attacker)`.
       > (4) **WAJIB *3-Way EV Amplification* & *Strike 3 Fuzzing***: Sebelum memvonis `REJECTED_POC_FAILS` / `REJECTED_NEGATIVE_EV` / `REJECTED_DUST`, wajib uji ketiga pengali (Flashloan Scaling, Single-Tx Looping, Cross-Lead Chaining ke guard `04`) **DAN** wajib jalankan minimal 1× `testFuzz_` (Strike 3).
       > (5) **DISTRIBUSI MURNI 3 WADAH (`09`, `06`, `07` — DILARANG `08`!)**: Jangan pernah menargetkan `08` atau menggugurkan lead karena pre-live/HEAD-only di Fase 3! Jika simulasi eksploitasi PASS, tulis ke staging sebagai kandidat `09`. Jika gagal setelah Strike 3 Fuzz, tulis ke staging sebagai kandidat `06` (wajib lampirkan log eksekusi test/fuzz). `07` HANYA sah dengan `Disposition:` + blok `PERCOBAAN:` berisi perintah `$ ...` dan output nyata.
       > **KELUARAN:** tulis entri LENGKAP siap-tempel ke `audit/notes/staging-<id>.md` (jangan tulis ke `06`/`07`/`09` langsung). Laporkan update untuk `STATE.md`. Kembalikan maksimal 12 baris berupa MANIFES: `STAGING: <path> | 06: <n> | 07: <n> | 09: <n>` + 1 baris verdict per entri."

2. **Fuzzing Invarian Stateful & Simetri** (untuk sisa kandidat yang belum bisa dituntaskan):
   - Tugaskan 1 Subagent Fase 3 untuk menjalankan Handler Stateful Invariant Fuzzing (Tier 2), Differential/Split-vs-Bulk Fuzzing (Tier 3), atau Symbolic Proving Halmos (Tier 5) **pada sesi ini juga**, dan lampirkan log statistik run ke `notes/`.

### Tahap Orkestrasi 4: Final Verdict Judging, Deployment Gate, & Laporan 6 File (sc-phase4-report)
0. **Pre-flight — TIGA GATE INTEGRITAS:** set `PHASE: 4`.
   - **(i) Coverage Gate (Langkah 0a butir 1–3):** bandingkan `00b-file-inventory.md` dengan tabel cakupan `03-attack-surface-queue.md`. Kontrak repo yang belum tercantum di halaman Bug Bounty **tetap sah** sebagai populasi `[REPO_STAGED]` (bukan `COVERAGE_BIAS`), namun seluruh berkas `[MUST-AUDIT]` di repo wajib mencapai cakupan **>= 80% per domain** dan **0 berkas `BELUM`**.
   - **(ii) Anti-Lazy-Bailout Gate pada `07` (Pernyataan #11):** jalankan `python3 /home/ubuntu/.hermes/profiles/adv/verify/tools/verify07.py audit/07-needs-next-step.md`. Setiap entri `07` tanpa `Disposition:` atau tanpa perintah `$ ...` dan log nyata di `PERCOBAAN:` -> **`LAZY_BAILOUT_DETECTED`** -> kembalikan ke Fase 3. **Target akhir `07` = 0 entri.**
   - **(iii) Anti-Paper-Refutation Gate pada `06` (Pernyataan #11e):** periksa entri `06` berlabel `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, dan `REJECTED_DUST`. Jika ada yang dibuang hanya dengan klaim teks **tanpa bukti eksekusi test/fuzz** -> **`PAPER_REFUTATION_DETECTED`** -> kembalikan ke Fase 3 untuk disimulasikan!

1. **WAJIB jalankan Hakim Akhir (`verify/VERDICT.md`) — Satu-Satunya Gerbang Deployment & Pemisahan `09` vs `08`:**
   Panggil `delegate_task` dengan instruksi:
   > "Wajib panggil `skill_view('sc-phase4-report')` dan baca `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md` serta `audit/STATE.md`.
   > (a) **Jalankan Langkah 0 (Rekonsiliasi Identitas Deployment) di sini:** periksa apakah kandidat di `09-confirmed-findings.md` terbukti pada kontrak produksi yang sudah *live* (`FORK_LIVE` + bytecode/source on-chain cocok) atau pada kode repositori HEAD yang belum di-deploy / berbeda versi (`FORK_DEPLOYED_HEAD` / `HEAD-only`).
   > (b) **Adili dengan 11 Pernyataan Wajib `VERDICT.md`:**
   >   - Kandidat yang PoC-nya PASS, berdampak bahaya finansial nyata (Critical/High/Medium), **DAN** terbukti cocok dengan deployment produksi aktif -> Disahkan tetap di `09-confirmed-findings.md` (`VALID_ELIGIBLE`).
   >   - Kandidat yang PoC eksploitasi dan bahaya finansialnya sudah terbukti 100% `PASS` lewat `FORK_DEPLOYED_HEAD` / `LOKAL`, tetapi kontrak/fiturnya masih berstatus HEAD-only / belum *live* di produksi / di luar daftar alamat bounty saat ini -> Pindahkan dari `09` ke `08-valid-not-eligible.md` dengan kelas `LOW_CLASS: PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` **sambil mempertahankan kode PoC utuh dan perhitungan dampaknya**! (JANGAN dibuang ke `07` agar `07` tetap bersih 0 entri).
   >   - Kandidat yang PoC-nya PASS secara mekanis tetapi dampaknya tergolong `LOW_NUISANCE` (#10b) atau `ADMIN_ONLY` (#8b) -> Pindahkan dari `09` ke `08-valid-not-eligible.md`.
   >   - Kandidat yang terbukti memakai cheatcode terlarang (#9a) atau melanggar Pernyataan Ketat Mutlak #1–#6 -> Cabut ke `06-refuted-invalid.md`.
   > (c) Pastikan setiap vonis memuat `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH`. Rapikan keenam file (`04` s/d `09`), jalankan `verify07.py`, dan kembalikan ringkasan maksimal 12 baris."

2. Baca hasil akhir di `09`, `08`, `07`, `06`, dan `04`, lalu sajikan laporan eksekutif kepada pengguna — wajib menyertakan baris `COVERAGE:`, `LAZY_BAILOUT:`, jumlah entri `07`, serta **pemisahan jelas antara temuan Live Production (`09`) dan temuan Proven on Repo HEAD / Pre-Live (`08`)**.

---

## Verification
Pastikan di akhir eksekusi keenam file laporan (`04` s/d `09`) berada dalam kondisi rapi dan konsisten, kode sumber asli tidak berubah, dan tidak ada file test rusak yang tertinggal di repositori proyek. Laporkan jumlah item per file beserta daftar kandidat yang dicabut oleh Hakim `VERDICT.md` — DILARANG menyembunyikan pencabutan.
