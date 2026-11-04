---
name: sc-autopilot
description: Master Orchestrator Whitehat Adversarial Lintas-Rantai (v6.2.0 Simulation-First) - Jalankan siklus penuh (Fase 0 Intel -> Fase 1 100% Repo Recon -> Fase 2 Class-Routed Hunt & Static-vs-Dynamic Guard Split -> Fase 3 Dual-Mode Fork & 3-Stage Fuzz Lab -> Fase 4 Verdict Judge & 09-vs-08 Deployment Split) secara otonom via delegate_task
version: 6.2.0
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
- Active Strike Count (Fase 3): <0/3 (2 Manual + 1 Mandatory Fuzz) atau "-" bila masih Fase 2>

## 2. Domain Coverage Meter (Syarat Gate = 100% `[MUST-AUDIT]`)
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
- **JAGA KONTEKS PARENT TETAP RINGAN:** Gunakan `delegate_task` (`max_concurrent_children: 1` secara sekuensial) agar setiap Subagent bekerja dengan konteks 0 token yang bersih.
- **PATUHI KONSTITUSI `workspace/AGENTS.md` PADA SETIAP `delegate_task`:** Sertakan Path Absolut Proyek, Paradigma Rantai, Core Invariants, Path File `audit/00` s/d `09`, instruksi `skill_view`, serta perintah agar Subagent menulis entri lengkap ke `audit/notes/staging-<unit>.md` dan mengembalikan **manifes** maksimal 12 baris (bukan muatan entri) — lihat **3b. Protokol Staging**.
- **JAGA PEMISAHAN 6 FILE HASIL (`04` s/d `09` — 1 File = 1 Domain Murni):**
  * `04-code-guarded.md` -> Murni hipotesis Fase 2 yang dihentikan oleh **Guard Statis / Struktural** (`onlyOwner`, `onlyRole`, `msg.sender == router`, `nonReentrant`, `whenNotPaused`, cek alamat `!= 0`). **DILARANG** menaruh guard matematis/dinamis di sini!
  * `05-raw-leads.md` -> Murni antrean aktif Fase 1 & 2 menuju Fase 3, mencakup seluruh anomali mutasi state, *Patch-Scar*, View-vs-Write, serta **Guard Dinamis / Matematis / State-Dependent** (rasio, pembulatan, saldo, waktu, panjang array) yang wajib diuji dengan fuzzer di Fase 3.
  * `06-refuted-invalid.md` -> Murni hipotesis gugur permanen karena salah baca statis literal, gagal setelah *Victim Seeding* + **3-Stage Escalation (2 Manual + 1 Mandatory Fuzz)**, atau melanggar Pernyataan Ketat Mutlak #1–#6 (#7a/#8a/#9a/#10a) di `VERDICT.md`. Wajib memuat blok **`BUKTI_SIMULASI:`** (log test + fuzz) untuk `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, dan `REJECTED_DUST` (Pernyataan #11e `PAPER_REFUTATION_DETECTED`).
  * `07-needs-next-step.md` -> Murni kandidat yang terhalang kendala komputasi/RPC ekstrem (`NEXT_EXPLORE` / `NEXT_MAINNET` / `TOOL_BLOCKED`) dan wajib lulus `verify07.py` (`Disposition:` + blok `PERCOBAAN:`). **Target akhir `07` = 0 entri** (temuan HEAD-only yang PoC-nya PASS **DILARANG** masuk `07`, melainkan ke `08`).
  * `08-valid-not-eligible.md` -> **Hanya boleh diisi oleh Hakim Fase 4 (`VERDICT.md`)!** Murni temuan yang PoC eksploitasinya terbukti `[PASS]` tanpa curang, namun berada dalam batasan eligibilitas: `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` (#2 & #7b — terbukti berbahaya di kode repo HEAD / `[REPO_STAGED]`, namun belum live di produksi), `ADMIN_ONLY` (#8b), atau `LOW_NUISANCE` (#10b).
  * `09-confirmed-findings.md` -> Murni `VALID_ELIGIBLE` (Simulasi `FORK_LIVE` `[PASS]` + `DEPLOYMENT_MATCH: LIVE_MATCH` + Bahaya Finansial Nyata + Lolos 11 Pernyataan `verify/VERDICT.md`).
- **WAJIB JALANKAN TAHAP 4 (`VERDICT.md` GATE):** Orchestrator **DILARANG** melaporkan temuan sebagai Confirmed sebelum Tahap 4 mengadilinya dengan `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md`.
- **DILARANG MEMANGGIL `skill_manage` ATAU `memory`.**

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

### Tahap Orkestrasi 1: Threat-First Recon & 100% Repo Inventory (sc-phase1-recon)
0. **Pre-flight:** bila `audit/STATE.md` belum ada, buat lebih dulu (lihat Langkah −1), lalu set `PHASE: 1`.
1. Periksa apakah `audit/00b-file-inventory.md` **DAN** `audit/00-project-map.md` s/d `audit/03-attack-surface-queue.md` sudah ada.
   - **Semua ada** -> lanjutkan ke butir 2 (jangan menimpa hasil yang sudah valid).
   - **Ada yang hilang** -> jalankan butir 2. Bila yang hilang hanya sebagian (mis. `00b` tidak ada tetapi `00`–`03` ada), **tetap jalankan dari Langkah 0**: inventaris adalah fondasi seluruh gerbang cakupan.

   **Proyek lama dengan `audit/` sebelumnya (rebuild bersih).** Untuk proyek yang sudah pernah diaudit dengan antrean lama, **DILARANG melanjutkan di atas folder lama**:
   ```bash
   mv audit audit_old_$(date +%Y%m%d)   # arsipkan, JANGAN rm -rf
   ```
2. Panggil `delegate_task` untuk Subagent Recon dengan instruksi wajib:
   - **Baca `audit/INTEL.md` lebih dulu** (bila ada) sebagai **penanda metadata non-destruktif**: beri tag setiap berkas di `00b-file-inventory.md` dengan **`[LIVE_BOUNTY]`** (terdaftar di halaman bounty & aktif di produksi) atau **`[REPO_STAGED]`** (ada di repositori fisik namun belum terdaftar di halaman bounty / masih HEAD-only). **DILARANG KERAS mengecualikan atau menghapus kontrak `[REPO_STAGED]` dari `00b`** — 100% kontrak non-test/non-mock di repo wajib masuk populasi! Gunakan juga Bagian 4 `INTEL.md` (riwayat audit) untuk memandu pelacakan *Patch-Scar*.
   - **Petakan rencana Dual-Mode Fork di `00-project-map.md`:** kontrak mana yang siap ditembak dengan `FORK_LIVE` dan kontrak `[REPO_STAGED]`/HEAD-only mana yang harus diuji dengan `FORK_DEPLOYED_HEAD` di Fase 3.
   - Menerapkan **3-Level Chain Detection** (`sc-phase2-hunt/references/ref-attacker-pov.md` Bagian 3) dan menuliskannya ke `00-project-map.md`; tulis `CHAIN: AMBIGUOUS (<runtime>)` bila `.rs` bukan program Solana.
   - Menetapkan **Kelas Topologi Entitas** pada **setiap** unit `S-n` di `03-attack-surface-queue.md`: `[CLASS-A]` (Single-Entity), `[CLASS-B]` (Dual-Entity), `[CLASS-C]` (Multi-Entity Long Flow).
   - Wajib `skill_view('sc-phase1-recon')`, DILARANG mengubah kode sumber, laporkan data untuk `STATE.md`, kembalikan ringkasan maksimal 12 baris.
3. Setelah selesai, **perbarui `audit/STATE.md`** (PHASE, Domain Coverage Meter, antrean), lalu baca `00-project-map.md` dan `03-attack-surface-queue.md`.

---

### Tahap Orkestrasi 2: Two-Stage Counter-Auditor Hunting & Static-vs-Dynamic Guard Split (sc-phase2-hunt)
0. **Pre-flight:** set `PHASE: 2`.

   **Interleaved Domain Wave & Position-Blind Fixed Quota:**
   - Rotasi berjalan lintas domain `D1 -> D2 -> ... -> Dn -> D1`. Di dalam setiap domain, unit `[CLASS-A]`, `[CLASS-B]`, dan `[CLASS-C]` (baik yang berlabel `[LIVE_BOUNTY]` maupun `[REPO_STAGED]`) dibedah **tanpa mendiskriminasi urutan bawah** — kontrak `[CLASS-A]` tunggal bisa memegang 100% TVL.
   - **1 panggilan `delegate_task` = tepat 1 Unit `S-n`.** DILARANG merapel beberapa unit di ekor antrean (*No Tail-End Compression*).
   - Prompt Subagent **DILARANG** memuat label "prioritas rendah / urutan bawah / EV kecil / belum masuk bounty" (*Position-Blind*).
   - Gate keluar: **= 100%** berkas `[MUST-AUDIT]` berjejak di **SETIAP** domain (**0** berkas `BELUM`). DILARANG memakai kuota "minimal N lead per domain".

1. **Putaran 1 (Mikro — metode sesuai kelas topologi unit + Gerbang Guard Statis vs Dinamis):**
   - Ambil **satu** unit dari `audit/03-attack-surface-queue.md`, panggil `delegate_task` satu per satu.
     * **Goal:** "Bedah unit `S-n` menggunakan prosedur Putaran 1 di `sc-phase2-hunt`."
     * **Context Wajib:**
       - Path Absolut Proyek, Paradigma Rantai, Core Invariants dari `00-project-map.md`, path `01-threat-and-env.md` & `02-state-and-var-matrix.md`, dan `audit/INTEL.md` bila ada.
       - Wajib `skill_view('sc-phase2-hunt')`, lalu baca **`references/ref-method-registry.md`** dan **`references/ref-attacker-pov.md`**.
       - **Jalankan paket metode `M-001..M-NNN` sesuai kelas topologi unit**:
         `[CLASS-A]` → *Single-Pass Deep Kill* (`M-001`, `M-002`, `M-003` internal 2-akun, `M-004`, `M-005` inline saat itu juga, `M-006` Prinsip B, `M-007`, `M-008` self-call/internal batch seam, `M-009`, `M-010` post-upgrade/residual lokal);
         `[CLASS-B]` → *Dual-Entity* (CLASS-A + `M-003`, `M-006` Prinsip A+B, `M-008`, `M-010`);
         `[CLASS-C]` → *Multi-Entity Long Flow* (paket penuh, penekanan rantai komposisi panjang).
       - **Lazy-load `references/ref-pov-*.md`** HANYA bila gejala pemicu di tabel router `ref-attacker-pov.md` terpenuhi.
       - **GERBANG PEMISAHAN GUARD STATIS VS DINAMIS (WAJIB):** Hanya guard otorisasi/struktural statis yang benar-benar **`TERSANGKAL`** (tidak tembus oleh **5 Jalur Permissionless** di `verify/templates/04-code-guarded.md`: mutasi variabel, pemicuan kontrak hulu, *state poisoning* pada eksekutor rutin, `nonReentrant` lintas-kontrak / `whenNotPaused` asimetris, serta *Cross-Whitelist Confusion* / *Callback Initiator*) yang boleh bertahan di `04-code-guarded.md`. Semua guard dinamis/matematis **dan semua guard statis yang memenuhi salah satu dari 5 jalur tersebut** **WAJIB ditulis sebagai entri `05-raw-leads.md`!**
       - **KELUARAN:** tulis entri LENGKAP siap-tempel ke `audit/notes/staging-<unit>.md` (staging WAJIB); `03` boleh di-`patch` pada baris status; **`STATE.md` DILARANG disentuh**. Kembalikan manifes ≤ 12 baris: `STAGING: <path> | 04: <n> | 05: <m>` + 1 baris verdict per entri.
       - Entri `05` wajib memuat `Kelas Topologi`, kolom Metode Pencarian (`M-00X`/`[POV-XX]`), dan Delta State; entri `04` wajib memuat File:Baris, Ekspresi Guard, Variabel Pembentuk, dan Penulis Variabel.

2. **Putaran 2 / Sintesis Lintas-Jalur:**
   - Bongkar **seluruh guard statis** di `04-code-guarded.md` lintas-entitas (`M-005` cross-contract, `M-008` seam, `M-009` suspended lifecycle, `M-010` residual/drift).
   - **Unified Phase 3 Gate:** DILARANG masuk Tahap Orkestrasi 3 sebelum **seluruh kelas (A, B, C)** lulus Gate Cakupan **= 100%** per domain (**0** berkas `BELUM`, atestasi bersitasi `File:Baris` lolos §2b) dan Putaran 2 ditutup.

---

### Tahap Orkestrasi 3: Simulation-First Lab, Dual-Mode Fork, & 3-Stage Fuzz Escalation (sc-phase3-verify-and-poc)
0. **Pre-flight:** set `PHASE: 3`.
   - **Langkah 1a wajib:** susun tabel triage **BATCH** atas **SELURUH** lead di `05-raw-leads.md` untuk memetakan **Mode Fork** (`FORK_LIVE` vs `FORK_DEPLOYED_HEAD`) dan **Skenario Victim Seeding**.
   - **HUKUM NO CODE, NO REJECT:** DILARANG KERAS menggugurkan lead matematika, logika, atau ekonomi ke `06` di Langkah 1 tanpa menulis dan menjalankan kode test! Hanya **4 Kemustahilan Fakta Statis Sempit** (Langkah 1c `sc-phase3-verify-and-poc`) yang boleh ditolak secara statis.
   - **3-Stage Escalation Breaker (2 Manual + 1 Mandatory Fuzz):** Sebuah hipotesis DILARANG dinyatakan `REJECTED_POC_FAILS` / `REJECTED_NEGATIVE_EV` / `REJECTED_DUST` sebelum melewati **Strike 1** (PoC Manual + *Victim Lifecycle Seeding*), **Strike 2** (Perbaikan Urutan + *3-Way EV Amplification*), dan **Strike 3** (1× tes Fuzz `testFuzz_` / `proptest` / `halmos`). Setelah ketiganya gagal, barulah dikunci di `06` beserta log eksekusinya (`BUKTI_SIMULASI:`) dan masuk **Do-Not-Reopen List**.
   - **Langkah 0c (Tangga Self-Healing) & Langkah 0d (Do-It-Now):** tetap mengikat mutlak sebelum klaim `TOOL_BLOCKED` / `NEXT_MAINNET` / `NEXT_EXPLORE`.

1. **Simulasi & Pembuktian Seluruh Raw Leads (`05-raw-leads.md`) — Blind to Bounty Scope:**
   - **Kuota delegasi PoC: maksimal 1 s/d 2 Lead per Subagent**, dari urutan **pertama sampai urutan paling akhir**. DILARANG KERAS merapel 5–10 lead sisa ke satu Subagent pembersih (*No Tail-End Compression*).
   - Untuk setiap lead aktif di `audit/05-raw-leads.md`, panggil `delegate_task` untuk menugaskan Subagent Verifier:
     * **Goal:** "Buktikan Lead `[ID_Lead]` (maks 1–2 lead) melalui simulasi kode nyata di Fase 3 sesuai `sc-phase3-verify-and-poc`."
     * **Context Wajib:** Path Absolut Proyek, detail lead dari `05-raw-leads.md`, path `audit/STATE.md`, dan instruksi:
       > "Wajib panggil `skill_view('sc-phase3-verify-and-poc')` dan baca `audit/STATE.md` lebih dulu.
       > **NO PAPER REFUTATION:** Dilarang menolak lead dengan hitungan kertas! Kecuali melanggar 4 Kemustahilan Statis Sempit, Anda WAJIB menulis dan menjalankan kode test.
       > **DUAL-MODE FORK:** Gunakan `FORK_LIVE` bila kontrak aktif di mainnet, atau `FORK_DEPLOYED_HEAD` (deploy kontrak repo HEAD di atas fork mainnet nyata) bila kontrak berstatus `[REPO_STAGED]` / HEAD-only / belum deploy. Jangan gunakan `revert 0x` pada `eth_call` sebagai alasan berhenti — cek selector via `cast code` atau jalankan `FORK_DEPLOYED_HEAD`!
       > **MANDATORY VICTIM SEEDING:** Sebelum kode penyerang berjalan di `setUp()`, wajib simulasikan transaksi pengguna/korban normal (`vm.prank(victim)`) agar pool, antrean, atau allowance terisi secara realistis.
       > **3-STAGE ESCALATION (2 MANUAL + 1 FUZZ) & 3-WAY EV AMPLIFICATION:** Jika Strike 1 & Strike 2 (Flashloan + Looping + Chaining) masih revert atau merugi, Anda WAJIB menulis dan menjalankan Strike 3 berupa fungsi `testFuzz_` untuk mengacak parameter input sebelum boleh memvonis `REJECTED_POC_FAILS` / `REJECTED_NEGATIVE_EV` / `REJECTED_DUST` ke `06` (dan wajib lampirkan log terminal test + fuzz di blok `BUKTI_SIMULASI:`).
       > **LARANGAN MENYENTUH `08` DI FASE 3:** Subagent Fase 3 **DILARANG** membuang lead ke `08-valid-not-eligible.md` dan DILARANG menurunkan temuan karena alasan HEAD-only/pre-live. Semua PoC yang `[PASS]` membuktikan eksploitasi wajib ditulis ke staging sebagai **kandidat `09`** (lengkap dengan tag `Mode Uji: FORK_LIVE` atau `FORK_DEPLOYED_HEAD`) untuk diadili oleh Hakim Fase 4!
       > **KELUARAN:** tulis entri LENGKAP siap-tempel ke `audit/notes/staging-<lead>.md` (staging WAJIB; jangan menulis ke `06`/`07`/`09` langsung). Kembalikan maksimal 12 baris berupa MANIFES: `STAGING: <path> | 06: <n> | 07: <n> | 09: <n>` + 1 baris verdict per entri."

2. **Fuzzing Invarian Stateful & Simetri Lintas-Alur:**
   - Untuk kandidat yang membutuhkan eksplorasi urutan mendalam, tugaskan Subagent Fase 3 menjalankan Handler Stateful Invariant Fuzzing (Tier 2), Differential/Split-vs-Bulk Fuzzing (Tier 3), atau Symbolic Proving Halmos (Tier 5) **pada sesi berjalan**.

---

### Tahap Orkestrasi 4: Final Verdict Judging, Deployment Split (09 vs 08), & Laporan 6 File (sc-phase4-report)
0. **Pre-flight — TIGA GERBANG INTEGRITAS:** set `PHASE: 4`.
   - **(i) Coverage Gate (Langkah 0a.1–3 / Pernyataan #11c & #11d):** bandingkan `00b-file-inventory.md` (100% populasi fisik repo) dengan tabel cakupan `03-attack-surface-queue.md`. Kontrak `[REPO_STAGED]` adalah **bagian sah** dari `00b` (bukan `COVERAGE_BIAS`). Bila cakupan `[MUST-AUDIT]` **< 100%** (masih ada berkas `BELUM`, `DIBACA` gantung, atau `DEFERRED`), ada **domain 0%**, atau ada `ATTESTED_CLEAN` hampa tanpa `File:Baris` -> **`AUDIT_INCOMPLETE_COVERAGE_BIAS`**: TOLAK laporan, kembalikan ke Fase 1/2.
   - **(ii) LAZY_BAILOUT Gate pada `07` (Langkah 0a.3b / Pernyataan #11):** jalankan `python3 /home/ubuntu/.hermes/profiles/adv/verify/tools/verify07.py audit/07-needs-next-step.md`. Entri `07` tanpa bukti komputasi nyata -> **`LAZY_BAILOUT_DETECTED`**: TOLAK laporan, kembalikan ke Fase 3. **Target akhir `07` = 0 entri.**
   - **(iii) ANTI-PAPER-REFUTATION Gate pada `06` (Langkah 0a.3c / Pernyataan #11e):** periksa seluruh entri `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, dan `REJECTED_DUST` di `06-refuted-invalid.md`. Bila ada yang tidak memuat log eksekusi test + Strike 3 Fuzz (`BUKTI_SIMULASI:`) -> **`PAPER_REFUTATION_DETECTED`**: TOLAK laporan, kembalikan lead tersebut ke Fase 3 untuk disimulasikan!

1. **WAJIB jalankan Hakim Akhir (`verify/VERDICT.md`) & Pemisahan Deployment (`09` vs `08`):**
   Panggil `delegate_task` dengan instruksi:
   > "Wajib panggil `skill_view('sc-phase4-report')` dan baca `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md` serta `audit/STATE.md`.
   >
   > **(1) Jalankan Langkah 0a** (Ketiga Gerbang Integritas: #11d Coverage, #11 `verify07.py`, dan #11e Anti-Paper-Refutation pada `06`).
   > **(2) Jalankan Langkah 0 VERDICT.md (Rekonsiliasi Identitas Deployment):** cocokkan setiap kandidat di `09-confirmed-findings.md` dengan bytecode/source produksi aktif (`cast code` / `cast implementation` / explorer) dan cakupan `INTEL.md`:
   >   - Kandidat yang PoC-nya `[PASS]`, lolos 11 Pernyataan, dan kodenya terbukti aktif di produksi (`DEPLOYMENT_MATCH: LIVE_MATCH`) -> tetap disahkan di `09-confirmed-findings.md` (`VALID_ELIGIBLE`).
   >   - Kandidat yang PoC-nya terbukti `[PASS]` dan berbahaya secara finansial pada kode repositori (`FORK_DEPLOYED_HEAD` / `LOKAL`), **TETAPI** kontrak/fiturnya masih HEAD-only, belum di-deploy di mainnet, atau berlabel `[REPO_STAGED]` -> **CABUT dari `09` dan pindahkan secara utuh** (lengkap dengan kode PoC & dampak kuantitatifnya) ke `08-valid-not-eligible.md` dengan `LOW_CLASS: PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` dan `TANGGA_BUKTI: A-HEAD / B`! (**DILARANG memasukkannya ke `07`!**).
   > **(3)** Cabut kandidat yang berdampak kelas Low (`LOW_NUISANCE` #10b) atau `ADMIN_ONLY` (#8b) dari `09` ke `08-valid-not-eligible.md`.
   > **(4)** Cabut kandidat yang melanggar Pernyataan Ketat Mutlak (#1–#6, #7a, #8a, #9a, #10a) ke `06-refuted-invalid.md`.
   > **(5)** Pastikan setiap entri di `06`, `07`, `08`, dan `09` memuat `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH`. Rapikan keenam file (`04` s/d `09`), pastikan status akhir semua lead di `05-raw-leads.md` sinkron, dan kembalikan ringkasan maksimal 12 baris."

2. Baca hasil akhir di `09`, `08`, `07`, `06`, `05`, dan `04`, lalu sajikan **Ringkasan Eksekutif** kepada pengguna — wajib menyertakan tabel cakupan per domain, baris `COVERAGE: PASS|AUDIT_INCOMPLETE_COVERAGE_BIAS`, baris `07: <n> entri | LAZY_BAILOUT: PASS|DETECTED`, baris `PAPER_REFUTATION_06: PASS|DETECTED`, serta **pemisahan tegas** antara temuan Live Production (`09`) dan Proven on Repo HEAD / Pre-Live (`08 - HEAD_ONLY_PROVEN`).

---


## Verification
Pastikan di akhir eksekusi keenam file laporan (`04` s/d `09`) berada dalam kondisi rapi dan konsisten, kode sumber asli tidak berubah, dan tidak ada file test rusak yang tertinggal di repositori proyek. Laporkan jumlah item per file beserta daftar kandidat yang dicabut oleh Hakim `VERDICT.md` — DILARANG menyembunyikan pencabutan.
