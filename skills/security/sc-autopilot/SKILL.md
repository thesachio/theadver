---
name: sc-autopilot
description: Master Orchestrator Whitehat Adversarial Lintas-Rantai - Jalankan siklus penuh (Fase 1 Threat Recon -> Fase 2 3-Layer Adversarial Hunt -> Fase 3 8-Gate Reality Triage & Concrete PoC -> Fase 4 Report) secara otonom via delegate_task
version: 4.4.0
metadata:
  hermes:
    tags: [security, web3, whitehat, adversarial, orchestrator, autopilot, delegation, multichain]
    category: security
    requires_toolsets: [terminal]
---

# Autonomous Whitehat Adversarial Audit Orchestrator (sc-autopilot)

## When to Use
Gunakan skill ini saat pengguna meminta eksekusi audit whitehat adversarial menyeluruh dari awal hingga akhir tanpa intervensi manual (*Full Autopilot*), atau saat mengorkestrasi pembedahan antrean audit/03-attack-surface-queue.md dan pengujian PoC 8-Gerbang secara otomatis.

## Pitfalls & Hukum Mutlak Orchestrator
- JAGA KONTEKS PARENT TETAP RINGAN: Jangan membedah seluruh kode atau menulis pengujian sendiri di proses utama. Gunakan delegate_task (max_concurrent_children: 1 secara sekuensial) agar setiap Subagent bekerja dengan konteks 0 token yang bersih.
- PATUHI KONSTITUSI `workspace/AGENTS.md` PADA SETIAP `delegate_task`: Karena Subagent melewati SOUL.md (skip_soul=True) dan mulai dari workspace/, setiap panggilan delegate_task WAJIB menyertakan: Path Absolut Proyek, Paradigma Rantai, Target Invarian, Path File audit/, instruksi skill_view, serta perintah agar Subagent mengembalikan ringkasan maksimal 12 baris saja.
- JANGAN BERHENTI DI LAPIS 1 JIKA BELUM ADA TEMUAN: Jika eksplorasi Lapis 1 (Radius 0–2) menghasilkan 0 lead, Orchestrator WAJIB memicu Subagent untuk menjalankan Eksplorasi Lapis 2 & 3 (Variable-Centric, 3-Step Sequence, Guard-Bypass, & Math Library) serta pengujian PoC/fuzzing invarian di Fase 3.
- JAGA PEMISAHAN 4 FILE LAPORAN: Pastikan hasil akhir terdistribusi secara akurat ke dalam 04-rejected-hypotheses.md, 05-raw-leads.md, 06-unproven-needs-review.md, dan 07-confirmed-findings.md.
- HUKUM 8 GERBANG REALITAS (berlaku untuk Orchestrator, bukan hanya Subagent): Tidak ada satu pun temuan yang boleh disebut ke pengguna sebagai "valid" tanpa lolos 8 Gerbang Realitas Bounty di workspace/AGENTS.md §3 DAN PoC nyata. Orchestrator DILARANG melompati Tahap 4 walau semua Subagent menyatakan PASS.
- DILARANG MEMANGGIL `skill_manage` ATAU `memory`.

---

## Procedure (Autonomous 4-Stage Adversarial Pipeline)

Saat pengguna memicu eksekusi otonom pada /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/, jalankan 4 tahapan orkestrasi berikut secara berurutan:
### Tahap Orkestrasi 1: Threat-First Recon (sc-phase1-recon)
1. Periksa apakah audit/00-project-map.md, audit/02-state-and-var-matrix.md, dan audit/03-attack-surface-queue.md sudah ada.
2. Jika BELUM ADA: Panggil delegate_task untuk menugaskan Subagent Recon:
   - Goal: "Jalankan prosedur lengkap sc-phase1-recon pada proyek <nama-proyek> untuk menghasilkan 00-project-map.md, 01-threat-and-env.md, 02-state-and-var-matrix.md, 03-attack-surface-queue.md, dan 05-raw-leads.md."
   - Context Wajib:
     * Path Absolut Proyek: /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>
     * Instruksi: "Wajib panggil skill_view('sc-phase1-recon'), periksa juga skrip deployment, jangan buat AGENTS.md di proyek, jangan ubah kode sumber, dan kembalikan ringkasan maksimal 12 baris."
3. Setelah selesai, baca audit/00-project-map.md dan audit/03-attack-surface-queue.md menggunakan read_file.

### Tahap Orkestrasi 2: 3-Layer Adversarial Hunting (sc-phase2-hunt)
1. Putaran 1 (Lifecycle & Radius 0–2 Hunt):
   - Ambil unit antrean prioritas dari audit/03-attack-surface-queue.md (1 fungsi kompleks atau 1 pasang fungsi Masuk/Keluar yang menyentuh state yang sama).
   - Panggil delegate_task satu per satu untuk setiap unit antrean:
     * Goal: "Bedah unit antrean [NamaTarget] menggunakan prosedur 3-Lapis di sc-phase2-hunt."
     * Context Wajib: Sertakan Path Absolut Proyek, Paradigma Rantai, Core Invariants dari 00-project-map.md, path ke 02-state-and-var-matrix.md, dan instruksi eksplisit: "Wajib panggil skill_view('sc-phase2-hunt') dan panggil skill_view pada modul references/ sesuai tag [LOAD: ...]. Tulis lead yang lolos ke audit/05-raw-leads.md, tulis yang gugur ke audit/04-rejected-hypotheses.md, dan kembalikan ringkasan maksimal 12 baris."
2. Putaran 2 (Deep-Dive Variable-Centric, 3-Step Permutation, & Guard-Bypass):
   - Periksa isi audit/05-raw-leads.md dan audit/04-rejected-hypotheses.md.
   - Tugaskan Subagent khusus untuk melakukan eksplorasi mendalam pada: (a) 3 variabel akuntansi/indeks paling kritis di 02-state-and-var-matrix.md pada jalur sampingan (transfer, claim, liquidate, migrate) dan urutan 3-langkah (A -> C -> B), serta (b) membedah ulang variabel pembentuk guard (require/assert!) di 04-rejected-hypotheses.md dan pustaka libraries//math/.

### Tahap Orkestrasi 3: 8-Gate Reality Triage & Concrete PoC (sc-phase3-verify-and-poc)
1. Verifikasi Seluruh Raw Leads (`05-raw-leads.md`):
   - Untuk setiap lead aktif di audit/05-raw-leads.md, panggil delegate_task untuk menugaskan Subagent Verifier:
     * Goal: "Buktikan atau patahkan Lead [ID_Lead] dengan triage 8 Gerbang Realitas lalu PoC lokal/fork sesuai sc-phase3-verify-and-poc."
     * Context Wajib: Path Absolut Proyek, detail lead dari 05-raw-leads.md, dan instruksi: "Wajib panggil skill_view('sc-phase3-verify-and-poc'). Jalankan triage 8 Gerbang Realitas SEBELUM menulis PoC, gunakan kontrak asli (larangan fantasy mock), hanya vm.prank(attacker) tanpa vm.store/vm.etch, pakai worker tunggal (-j 1), dan klasifikasikan tegas ke 07-confirmed-findings.md (lolos 8 Gerbang + PoC PASS), 06-unproven-needs-review.md (lolos 8 Gerbang namun tooling terhalang), atau 04-rejected-hypotheses.md (gagal gerbang/guard). Kembalikan maksimal 12 baris."
2. Fuzzing Invarian Stateful & Simetri (hanya setelah lead lolos 8 Gerbang):
   - Tugaskan 1 Subagent khusus Fase 3 untuk menjalankan Handler Stateful Invariant Fuzzing (dengan Ghost Variables) atau Differential/Round-Trip Math Test terhadap Core Invariants utama dari 00-project-map.md. Jika fuzzer menemukan pelanggaran invarian baru, catat bukti lengkapnya ke audit/07-confirmed-findings.md.
### Tahap Orkestrasi 4: Quality Gate Final & Laporan Eksekutif (sc-phase4-report)
1. WAJIB jalankan quality gate sebelum melapor: panggil delegate_task dengan instruksi "Wajib panggil skill_view('sc-phase4-report'). Jalankan audit kualitas terakhir: CABUT setiap temuan di audit/07-confirmed-findings.md yang bergantung pada fantasy mock, totalSupply == 0 pada pool live, parameter admin ekstrem, debu 1 wei tanpa amplifikasi, atau cheatcode, lalu pindahkan ke audit/04-rejected-hypotheses.md. Rapikan format baku 04 s/d 07 dan kembalikan maksimal 12 baris."
2. Jika gate mencabut temuan: laporkan jumlah yang dicabut beserta alasannya. DILARANG menyembunyikan pencabutan.
3. Baca hasil akhir di audit/07-confirmed-findings.md, audit/06-unproven-needs-review.md, dan audit/04-rejected-hypotheses.md, lalu sajikan laporan akhir kepada pengguna yang membedakan secara jelas:
1. Temuan Terkonfirmasi — lolos 8 Gerbang + PoC PASS (`07-confirmed-findings.md`)
2. Belum Terbukti / Perlu Tinjauan Manual (`06-unproven-needs-review.md`)
3. Hipotesis Ditolak beserta Gerbang/Guard Penjaganya (`04-rejected-hypotheses.md`)

---

## Verification
Pastikan di akhir eksekusi keempat file laporan (04 s/d 07) berada dalam kondisi rapi dan konsisten, kode sumber asli tidak berubah, dan tidak ada file test rusak yang tertinggal di repositori proyek.
