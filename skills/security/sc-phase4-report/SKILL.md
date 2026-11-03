---
name: sc-phase4-report
description: Phase 4 — Final Verdict Judging (via verify/VERDICT.md) and Pure 6-File Audit Reporting (04 to 09).
version: 6.0.0
---

# Phase 4: Final Verdict Judging & Pure 6-File Audit Reporting (04–09)

Tujuan Fase 4 adalah bertindak sebagai Hakim Akhir (Bounty Judge) menggunakan standar `verify/VERDICT.md` terhadap seluruh hasil Fase 3, lalu menyusun keenam file hasil (audit/04 s/d audit/09) secara bersih tanpa mencampur domain.

**GERBANG TULIS (WAJIB):** sebelum memindahkan/mengedit entri di `audit/04`–`09`, baca **`workspace/AGENTS.md` Pasal 1.3 (Protokol Anti-Truncate & Metode Write)**. `open(path,"w")` dan `>` shell **DILARANG** untuk seluruh `audit/*.md` — memotong file ke 0 byte saat dibuka. Pemindahan entri antar wadah wajib memakai `append` (entri baru) + `patch` (ubah status), dan diverifikasi dengan `grep -c '^## \['` sebelum & sesudah.

---

## Langkah 0a: Rekonsiliasi Cakupan Inventaris (Gate Anti-Sampling-Bias — WAJIB SEBELUM LANGKAH 1)

Hakim **DILARANG** memeriksa 11 Pernyataan kualitas bukti sebelum gerbang cakupan ini dijalankan. Kualitas PoC hanya bermakna untuk permukaan yang benar-benar diperiksa; satu PoC sempurna di atas 2% cakupan tetap merupakan audit yang gagal.

### 1. Hitung Rasio Cakupan - DUA Gerbang Berbeda
Bandingkan `audit/00b-file-inventory.md` (populasi) dengan `audit/03-attack-surface-queue.md` (jejak). Wajib periksa **keduanya**, karena keduanya bisa gagal secara independen:

**(a) Gerbang Pemetaan (warisan Fase 1):** berkas `[MUST-AUDIT]` yang `TERPETAKAN_DI_UNIT` ÷ total `[MUST-AUDIT]` = **100%**. Bila kurang, berarti ada berkas yang tidak pernah masuk antrean - kegagalan paling fatal, dan tidak bisa ditambal di Fase 4.

**(b) Gerbang Jejak (Fase 2):** berkas `[MUST-AUDIT]` berstatus `LEAD_GENERATED` **atau** `ATTESTED_CLEAN` ÷ total `[MUST-AUDIT]` >= **80% per domain**. Keduanya sah setara - modul yang memang aman dipenuhi dengan *Negative Attestation* berisi (fungsi apa diperiksa, Metode dipakai, mengapa invariant tahan), **bukan** lead karangan.

- **Penyebut:** seluruh berkas `[MUST-AUDIT]` di inventaris.
- `00b` **dieksklusi** dari pemindaian jejak (pengukur tidak boleh menjadi bagian populasi yang diukur).

**DILARANG memakai "jumlah lead per domain" sebagai metrik kelulusan** (Goodhart: memicu lead sampah pada modul aman).

### 2. Periksa Domain Kosong
Untuk setiap domain `D1..Dn` yang memiliki berkas `[MUST-AUDIT]`, hitung cakupannya sendiri. Domain dengan **cakupan 0%** adalah otomatis pelanggaran, tanpa melihat rata-rata total. Tandai khusus berkas terbesar per domain yang memiliki **0 jejak** — baik lead maupun atestasi — karena inilah pola sampling-bias yang paling sering terjadi: berkas raksasa dilewati sementara berkas kecil dilemburi.

**Catatan anti-Goodhart:** klasifikasi `[MUST-AUDIT]` ditentukan **perilaku** (mengubah state / merutekan dana / eksekusi alur), **bukan** ambang jumlah baris. Router/adapter tipis <200 LOC yang memindahkan dana tetap wajib berjejak.

### 3. Vonis Pembatalan

| Kondisi | Status |
|---|---|
| Gerbang pemetaan: berkas `TERPETAKAN_DI_UNIT` **< 100%** | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Gerbang jejak: cakupan `[MUST-AUDIT]` **< 80%** | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Ada **>=1 domain** wajib ber-cakupan **0%** | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Berkas terbesar per domain masih `BELUM` | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Seluruh kondisi di atas terpenuhi | lanjut ke Langkah 1 |

Bila status `AUDIT_INCOMPLETE_COVERAGE_BIAS`:
1. **TOLAK penyelesaian laporan.** DILARANG menulis Ringkasan Eksekutif seolah audit selesai.
2. Tulis vonis pembatalan di kepala `audit/03-attack-surface-queue.md` dan `audit/09-confirmed-findings.md`: *"STATUS: AUDIT_INCOMPLETE_COVERAGE_BIAS — laporan ini tidak sah sebagai audit menyeluruh."*
3. **Kembalikan eksekusi ke Fase 1/Fase 2** untuk menyapu domain yang terlewat, memakai rotasi domain (`sc-phase2-hunt`).
4. Temuan yang sudah ada tetap disimpan sebagai **hasil sementara**, bukan laporan final. DILARANG menghapusnya.

### 3b. Audit Kejujuran Usaha pada `07` — Gate Anti-Lazy-Bailout (Pernyataan #11)

**Pernyataan #11 — `LAZY_BAILOUT_DETECTED`.** `07` bukan tempat membuang lead yang belum dikerjakan. Hakim **WAJIB** memeriksa **setiap** entri di `audit/07-needs-next-step.md` sebelum menerima laporan:

| Label | Yang wajib diperiksa Hakim | Vonis bila gagal |
|---|---|---|
| `TOOL_BLOCKED` | Bukti **3-Step Self-Healing** (`sc-phase3` Langkah 0c) dilampirkan: (1) flag/remapping/toolchain, (2) **Standalone Minimal / Interface-Only Harness**, (3) fallback RPC. Log terminal ketiganya harus ada di entri. | `LAZY_BAILOUT_DETECTED` |
| `NEXT_MAINNET` | Bukti bahwa rantai **benar-benar** tanpa RPC/explorer publik. Bila RPC tersedia, Hakim menjalankan sendiri `cast call` / `cast storage` / `cast implementation` **pada sesi itu** dan menuntaskan vonis. | `LAZY_BAILOUT_DETECTED` |
| `NEXT_EXPLORE` | Log eksekusi fuzzer/chaining/halmos yang **mentok timeout**, bukan sekadar alasan teks. Wajib ada perintah + keluaran + statistik waktu. | `LAZY_BAILOUT_DETECTED` |

**Vonis Hakim:** bila ada entri `07` yang belum memenuhi bukti usaha di atas, Hakim **WAJIB**:
1. Menandai status audit sebagai `LAZY_BAILOUT_DETECTED`.
2. **Menolak laporan** — DILARANG menulis Ringkasan Eksekutif seolah audit selesai.
3. Mengembalikan entri tersebut ke **Fase 3** untuk dieksekusi sampai tuntas — hasilnya wajib tegas: terbukti (`09`), valid-tapi-tidak-eligible (`08`), atau gugur (`06`).

**Target ideal `07` = 0 entri** pada akhir audit. Setiap entri yang tersisa harus bisa dipertahankan dengan **log komputasi**, bukan dengan kalimat.

> Catatan: entri `07` yang judulnya sudah menyatakan `DIPINDAHKAN KE 06`/`09` tetapi masih memuat label lama (`NEXT_EXPLORE`/`NEXT_MAINNET`) adalah **label basi** — wajib dibersihkan. Label basi dihitung sebagai entri tidak sah.

---

### 4. Format Wajib di Ringkasan Eksekutif
Setiap Ringkasan Eksekutif Fase 4 wajib mencantumkan tabel cakupan per domain (`Total | LEAD | ATTESTED | BELUM | % | Gate`) beserta baris status akhir: `COVERAGE: PASS` atau `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`. Laporan tanpa tabel ini dianggap belum lengkap.

**Alasan aturan ini:** tanpanya, Hakim hanya mengadili kualitas di dalam cakupan yang kebetulan terbuka, lalu menyebutnya "audit selesai". Sampling yang tidak diakui akan selalu lolos sebagai laporan penuh.

---

## Langkah 1: Eksekusi Vonis Akhir dengan `verify/VERDICT.md`
1. **Wajib Baca Standar Hakim:** Panggil `read_file` pada `verify/VERDICT.md`.
2. **Jalankan Langkah 0 VERDICT.md lebih dulu — Rekonsiliasi Identitas Deployment (wajib, sebelum menilai apa pun):**
   Cocokkan kode yang dikutip dengan sumber terverifikasi explorer / `sha256`. Klaim yang hanya berlaku di HEAD — bukan di deployment produksi — wajib ditandai `HEAD-only` dan **maksimal berada di `07`**, tidak boleh diadili sebagai temuan.
3. **Adili Setiap Kandidat** di `audit/09-confirmed-findings.md` dan `audit/05-raw-leads.md`:
   Uji setiap kandidat terhadap 11 Pernyataan Wajib di VERDICT.md (termasuk Langkah 4a Gate Cakupan):
   - **Lolos Seluruh 11 Pernyataan (`VALID_ELIGIBLE`):** Terbukti lewat simulasi PoC pada fork state produksi (`Mode Uji: FORK`), tanpa *Fantasy Mock*/Cheatcode, dan membuktikan bahaya finansial nyata (pencurian dana, insolvensi, pembekuan aset permanen, atau sabotase repay/liquidate) -> Disahkan tetap di `audit/09-confirmed-findings.md`.
   - **Berada Dalam Batasan Toleransi / Low (`VALID_NOT_ELIGIBLE` — Pernyataan #7b, #8b, #10b):** Simulasi PoC jalan secara mekanis tanpa curang, tetapi dampaknya tergolong *"Annoying but not financially dangerous"* (`LOW_NUISANCE`), merupakan *admin-only bug* tanpa jalur eksploitasi eksternal (#8b), atau fitur belum *live* (#7b) -> **WAJIB CABUT dari 09** dan pindahkan ke `audit/08-valid-not-eligible.md`!
   - **Berada Dalam Batasan Eksplorasi / Kendala RPC (`NEEDS_NEXT_STEP` — Pernyataan #9b):** Logika kode kuat namun butuh metode eksplorasi lanjut (`NEXT_EXPLORE`), butuh cek state mainnet (`NEXT_MAINNET`), belum diuji di fork karena kendala RPC/tooling (`TOOL_BLOCKED`), atau klaim masih `HEAD-only` (gagal #2) -> **WAJIB CABUT dari 09** dan pindahkan ke `audit/07-needs-next-step.md`!
     **Syarat sah masuk `07`:** setiap entri wajib memuat blok `PERCOBAAN:` (perintah + keluaran) untuk label `NEXT_EXPLORE`/`TOOL_BLOCKED`, dan bukti bahwa RPC benar-benar tidak tersedia untuk `NEXT_MAINNET`. Entri tanpa bukti percobaan **ditolak Hakim** dan lead dikembalikan ke Fase 3 untuk dikerjakan sekarang — bukan diloloskan sebagai `07`.
   - **Melanggar Pernyataan Ketat Mutlak (`REJECTED_*` — Pernyataan #1–#6 beserta sub-kasus ketat #7a, #8a, #9a, #10a):** Memakai *Fantasy Mock* (#1), klaim produksi tanpa bukti kesetiaan deployment (#2), mengasumsikan `totalSupply == 0` pada pool *live* (#3), tidak ada korban rasional (#4), *Negative-EV* (#5), perilaku by-design / baris kode meleset (#6), menyerang `initialize()` terkunci (#7a), *privileged fantasy* (#8a), cheatcode / PoC gagal di state nyata (#9a), atau debu tanpa amplifikasi (#10a) -> **WAJIB CABUT dari 09** dan buang ke `audit/06-refuted-invalid.md`!
4. **Setiap vonis wajib memakai Format Keluaran `VERDICT.md`** (`ID`, `VERDICT`, `TARGET_FILE`, `ALASAN`, `BUKTI`, `TANGGA_BUKTI`, `DEPLOYMENT_MATCH`, `BIAYA-BACA`). Verdict tanpa `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH` dianggap belum sah.
5. **2-Strike:** lead yang berstatus `REJECTED_POC_FAILS` di `06` (karena 2 percobaan gagal di Fase 3) **DILARANG** dipindahkan kembali ke `07`. Kunci 2-Strike bersifat final sampai seluruh lead lain selesai diuji.

---

## Langkah 2: Standarisasi Format Keenam File Murni (04 s/d 09)

1. `audit/09-confirmed-findings.md` (Murni `VALID_ELIGIBLE` — Siap Kirim Bounty):
   Memuat: Judul & Keparahan (CRITICAL/HIGH/MEDIUM), `Verdict: VALID_ELIGIBLE`, `Mode Uji: FORK (chain, block, RPC)`, Lokasi Kode & Invarian, Validasi Realitas Produksi, Akar Masalah & Dampak Finansial Kuantitatif, Kode PoC Utuh, Log Output, dan Patch Perbaikan (diff).
2. `audit/08-valid-not-eligible.md` (Murni `VALID_NOT_ELIGIBLE` — Valid dalam Batasan / Low):
   Memuat: ID, Lokasi, Sub-Kategori (`LOW_NUISANCE` | `ADMIN_ONLY` | `PRE_LIVE_SCOPE`), Bukti Simulasi PoC, dan alasan teknis mengapa masuk batas toleransi 08 (bukan 09).
3. `audit/07-needs-next-step.md` (Murni `NEEDS_NEXT_STEP` — Belum Selesai Diuji):
   Memuat: ID, Lokasi, Label Disposisi (`NEXT_EXPLORE` | `NEXT_MAINNET` | `TOOL_BLOCKED`), ringkasan apa yang sudah diuji di Fase 3, dan langkah konkret selanjutnya.
4. `audit/06-refuted-invalid.md` (Murni `REJECTED_*` — Gugur Permanen di Fase 3/4):
   Memuat: ID, Asal Lead, Kelas Vonis (`REJECTED_FANTASY_MOCK`, `REJECTED_POC_FAILS`, dll.), nomor Pernyataan `VERDICT.md` yang dilanggar, dan bukti penolakannya.
5. `audit/05-raw-leads.md` (Rekonsiliasi Status Antrean):
   Pastikan setiap `LEAD-XXX` memiliki penanda hasil akhirnya: `[STATUS -> 09]`, `[STATUS -> 08]`, `[STATUS -> 07]`, atau `[STATUS -> 06]`.
6. `audit/04-code-guarded.md` (Arsip Guard Kode dari Fase 2):
   Daftar hipotesis Fase 2 yang dihentikan oleh `require` / `if (...) revert` beserta status apakah berhasil ditembus di Putaran 2 atau tetap tertahan guard.

---

## Langkah 3: Ringkasan Eksekutif ke Pengguna
Tampilkan tabel ringkasan akhir kepada pengguna yang merinci jumlah item di masing-masing file (04, 05, 06, 07, 08, dan 09), beserta daftar kandidat yang dipindahkan oleh Hakim `VERDICT.md` dari 09 ke 08, 07, atau 06.

**Wajib disertai:** (a) tabel cakupan per domain dari Langkah 0a, (b) baris `COVERAGE: PASS` atau `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`, dan (c) baris `07: <n> entri` + `LAZY_BAILOUT: PASS|DETECTED`. Bila status pembatalan aktif (`COVERAGE` atau `LAZY_BAILOUT`), ringkasan **DILARANG** disajikan sebagai laporan final — sajikan sebagai laporan sementara beserta daftar domain/lead yang wajib dikerjakan ulang.
