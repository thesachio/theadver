---
name: sc-phase4-report
description: Phase 4 — Final Verdict Judging (via verify/VERDICT.md), Deployment Eligibility Gate (09 Live vs 08 Pre-Live/HEAD-Only), Anti-Paper-Refutation Check (#11e), and Pure 6-File Audit Reporting (04 to 09).
version: 6.2.0
---

# Phase 4: Final Verdict Judging & Pure 6-File Audit Reporting (04–09)

Tujuan Fase 4 adalah bertindak sebagai Hakim Akhir (Bounty Judge) menggunakan standar `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md` terhadap seluruh hasil simulasi Fase 3, menjalankan **Rekonsiliasi Identitas Deployment** (memisahkan temuan *Live Production* ke `09` vs *Proven on Repo HEAD / Pre-Live* ke `08`), memeriksa integritas cakupan dan bukti simulasi (#11d, #11, #11e), lalu menyusun keenam file hasil (`audit/04` s/d `audit/09`) secara bersih.

**GERBANG TULIS (WAJIB):** sebelum memindahkan/mengedit entri di `audit/04`–`09`, baca **`workspace/AGENTS.md` Pasal 1.3 (Protokol Anti-Truncate & Metode Write)**. `open(path,"w")` dan `>` shell **DILARANG** untuk seluruh `audit/*.md` — memotong file ke 0 byte saat dibuka. Pemindahan entri antar wadah wajib memakai `append` (entri baru) + `patch` (ubah status), dan diverifikasi dengan `grep -c '^## \['` sebelum & sesudah.

---

## Langkah 0a: Rekonsiliasi Cakupan Inventaris & Integritas Bukti (WAJIB SEBELUM LANGKAH 1)

Hakim **DILARANG** memeriksa 11 Pernyataan kualitas bukti sebelum gerbang cakupan dan kejujuran usaha ini dijalankan.

### 1. Hitung Rasio Cakupan — Populasi Fisik Repo (`00b`) Adalah Penyebut Tunggal
Bandingkan `audit/00b-file-inventory.md` (populasi fisik seluruh kontrak non-test/non-mock di repo) dengan `audit/03-attack-surface-queue.md` (jejak). Wajib periksa keduanya.

**Peran `audit/INTEL.md` (Penanda Eligibilitas Non-Destruktif, BUKAN Pemangkas Cakupan):**
- **Bagian 3 INTEL — Bug Bounty Scope:** Digunakan di Fase 4 untuk memberi label status deployment pada tiap kontrak/temuan: `[LIVE_BOUNTY]` (terdaftar di halaman bounty & ter-deploy aktif) vs `[REPO_STAGED / PRE_LIVE]` (ada di kode repositori `00b`, namun belum masuk daftar alamat bounty atau belum di-deploy).
- **PENTING:** Adanya kontrak di `00b` yang belum terdaftar di halaman Bug Bounty **BUKAN** merupakan `AUDIT_INCOMPLETE_COVERAGE_BIAS`! Sebaliknya, seluruh kontrak `[MUST-AUDIT]` di `00b` (baik `[LIVE_BOUNTY]` maupun `[REPO_STAGED]`) **WAJIB diaudit 100%**. Hanya jika ada kontrak *in-scope* dari repositori yang sama yang **sengaja dihilangkan** dari `00b`, barulah dijatuhkan `AUDIT_INCOMPLETE_COVERAGE_BIAS`.
- **Bagian 4 INTEL — Past Audit Reports:** Memastikan area yang pernah diaudit pihak lain tetap berjejak (`LEAD_GENERATED`/`ATTESTED_CLEAN`), bukan dilewati karena diasumsikan aman.
- Bila `INTEL.md` tidak ada atau berstatus `TIDAK_DITEMUKAN`, populasi tetap sah memakai `00b` dan **dicatat secara eksplisit** di Ringkasan Eksekutif.

**(a) Gerbang Pemetaan (warisan Fase 1):** berkas `[MUST-AUDIT]` yang `TERPETAKAN_DI_UNIT` ÷ total `[MUST-AUDIT]` di `00b` = **100%**.

**(b) Gerbang Jejak (Fase 2):** berkas `[MUST-AUDIT]` berstatus `LEAD_GENERATED` atau `ATTESTED_CLEAN` (wajib bersitasi `File:Baris` per fungsi) ÷ total `[MUST-AUDIT]` >= **80% per domain**, dan pada Gerbang Fase 4 harus mencapai **0 berkas `BELUM`** di seluruh domain.

- **Penyebut:** seluruh berkas `[MUST-AUDIT]` di inventaris.
- `00b` **dieksklusi** dari pemindaian jejak (pengukur tidak boleh menjadi bagian populasi yang diukur).

**DILARANG memakai "jumlah lead per domain" sebagai metrik kelulusan** (Goodhart: memicu lead sampah pada modul aman).

### 2. Periksa Domain Kosong & Atestasi Hampa (#11c)
Untuk setiap domain `D1..Dn` yang memiliki berkas `[MUST-AUDIT]`, hitung cakupannya sendiri. Domain dengan **cakupan 0%** adalah otomatis pelanggaran, tanpa melihat rata-rata total. Tandai khusus berkas terbesar per domain yang memiliki **0 jejak**.

`ATTESTED_CLEAN` yang tidak memuat `File:Baris` konkret per fungsi yang diperiksa — atau yang bersandar hanya pada volume (`forge build`/`cargo test` PASS, jumlah berkas, `N/N PASS`, nama unit `S-0n`) — **DIBATALKAN** dan dikembalikan ke `BELUM` **sebelum** persentase dihitung.

**Catatan anti-Goodhart:** klasifikasi `[MUST-AUDIT]` ditentukan **perilaku** (mengubah state / merutekan dana / eksekusi alur), **bukan** ambang jumlah baris.

### 3. Vonis Pembatalan Cakupan (#11d)

| Kondisi | Status |
|---|---|
| Gerbang pemetaan: berkas `TERPETAKAN_DI_UNIT` **< 100%** | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Gerbang jejak: cakupan `[MUST-AUDIT]` **< 80%** atau masih ada berkas `BELUM` | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Ada **>=1 domain** wajib ber-cakupan **0%** | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Seluruh kondisi di atas terpenuhi | lanjut ke Langkah 3b & 3c |

Bila status `AUDIT_INCOMPLETE_COVERAGE_BIAS`: **tolak** penyelesaian laporan, tulis status di kepala `03` dan `09`, dan kembalikan eksekusi ke Fase 1/2 **tanpa menghapus** temuan yang sudah ada.

### 3b. Audit Kejujuran Usaha pada `07` — Gate Anti-Lazy-Bailout (Pernyataan #11)

**Jalankan validator mekanis** (bukan periksa manual):
```bash
python3 /home/ubuntu/.hermes/profiles/adv/verify/tools/verify07.py audit/07-needs-next-step.md
```
Exit code ≠ 0 ATAU ada entri dilaporkan gagal -> **`LAZY_BAILOUT_DETECTED`**, laporan **DITOLAK**, entri dikembalikan ke Fase 3. **Target akhir `07` = 0 entri.**

| Label | Yang wajib ada di entri | Tanpa bukti |
|---|---|---|
| `TOOL_BLOCKED` | Log terminal **ketiga** anak tangga Self-Healing (`sc-phase3` Langkah 0c): (1) flag/remapping/toolchain, (2) Standalone Interface-Only Harness, (3) fallback RPC | `LAZY_BAILOUT_DETECTED` |
| `NEXT_MAINNET` | Bukti rantai **benar-benar** tanpa RPC/explorer publik. Bila RPC tersedia, Hakim menjalankan sendiri `cast call`/`cast storage`/`cast implementation` **pada sesi itu** | `LAZY_BAILOUT_DETECTED` |
| `NEXT_EXPLORE` | Log Tier 2/3/5 (handler fuzzing, differential, halmos) yang **mentok timeout** + statistik waktu | `LAZY_BAILOUT_DETECTED` |

**Label basi tidak sah.** Judul entri sudah menyatakan `DIPINDAHKAN KE 06`/`09` tetapi label lama (`NEXT_EXPLORE`/`NEXT_MAINNET`) masih tertinggal -> dihitung sebagai pelanggaran #11 dan wajib dibersihkan.

### 3c. Audit Bukti Simulasi pada `06` — Gate Anti-Paper-Refutation (Pernyataan #11e)

**`PAPER_REFUTATION_DETECTED`.** Hakim **WAJIB** memeriksa setiap entri `06` yang menyandang vonis `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, atau `REJECTED_DUST`:

| Yang wajib ada di entri `06` | Vonis bila gagal |
|---|---|
| Blok `BUKTI_SIMULASI:` berisi perintah test yang benar-benar dijalankan + log terminal | `PAPER_REFUTATION_DETECTED` |
| Bukti *Victim Seeding* (`vm.prank(victim)` / setup korban non-EVM) tercatat di log | `PAPER_REFUTATION_DETECTED` |
| Minimal **1× eksekusi Fuzzing** (`testFuzz_` / `proptest` / `halmos`) pada Strike 3 + jumlah runs | `PAPER_REFUTATION_DETECTED` |
| Bukti **3-Way EV Amplification** (flashloan, single-tx loop, cross-lead chaining) untuk `NEGATIVE_EV`/`DUST` | `PAPER_REFUTATION_DETECTED` |

**Pengecualian sah (boleh tanpa kode test):** hanya 4 Kemustahilan Statis Sempit — `REJECTED_FANTASY_MOCK`, `REJECTED_GENESIS_MIRAGE` (pool tunggal terkunci), `REJECTED_NON_LIVE_INIT` (terkunci rapat + `_disableInitializers()`), `REJECTED_PRIVILEGED_FANTASY`, serta `REJECTED_MISMATCH` / `REJECTED_BY_DESIGN`.

**Vonis:** `PAPER_REFUTATION_DETECTED` -> **laporan DITOLAK**, entri `06` bermasalah dikembalikan ke **Fase 3** untuk dibuatkan simulasi PoC/Fuzz. Temuan lain tetap disimpan sebagai hasil sementara dan **DILARANG dihapus**.

### 4. Format Wajib di Ringkasan Eksekutif
Setiap Ringkasan Eksekutif Fase 4 wajib mencantumkan tabel cakupan per domain (`Total | LEAD | ATTESTED | BELUM | % | Gate`) beserta baris status akhir: `COVERAGE: PASS` atau `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`, plus baris `LAZY_BAILOUT: PASS|DETECTED` dan `PAPER_REFUTATION: PASS|DETECTED`. Laporan tanpa ketiganya dianggap belum lengkap.

**Alasan aturan ini:** tanpanya, Hakim hanya mengadili kualitas di dalam cakupan yang kebetulan terbuka, lalu menyebutnya "audit selesai".

---

## Langkah 1: Eksekusi Vonis Akhir dengan /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md
1. **Wajib Baca Standar Hakim:** Panggil `read_file` pada `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md`.
2. **Jalankan Langkah 0 VERDICT.md lebih dulu — Rekonsiliasi Identitas Deployment (wajib, sebelum menilai apa pun):**
   Cocokkan kode yang dikutip dengan sumber terverifikasi explorer / `cast code` + scan `PUSH4 <selector>` (jangan pakai `revert 0x` sebagai bukti fungsi absen). Hasil rekonsiliasi memberi label per kandidat:
   - `DEPLOYMENT_MATCH: LIVE_MATCH` — kode yang diserang = bytecode produksi aktif.
   - `DEPLOYMENT_MATCH: HEAD-only (PROVEN_ON_REPO_HEAD)` — kode repo berbeda dari produksi / belum di-deploy. **Temuan seperti ini tetap diadili**, bukan dikembalikan ke `07`.
   **Rekonsiliasi cakupan identitas:** rujuk `audit/INTEL.md` (bila ada) Bagian 3 (alamat/repo in-scope) dan Bagian 4 (laporan audit lampau) bersama `00-project-map.md` + `00b-file-inventory.md`.
3. **Adili Setiap Kandidat** di `audit/09-confirmed-findings.md` dan `audit/05-raw-leads.md`:
   Uji setiap kandidat terhadap 11 Pernyataan Wajib di VERDICT.md (termasuk Langkah 4a Gate Cakupan):
   - **Lolos Seluruh 11 Pernyataan + `LIVE_MATCH` (`VALID_ELIGIBLE`):** Terbukti lewat simulasi PoC pada `FORK_LIVE` terhadap bytecode produksi, tanpa *Fantasy Mock*/Cheatcode, dan membuktikan bahaya finansial nyata (pencurian dana, insolvensi, pembekuan aset permanen, atau sabotase repay/liquidate) -> Disahkan tetap di `audit/09-confirmed-findings.md`.
   - **PoC `[PASS]` tapi `HEAD-only` / Pre-Live / di luar daftar alamat bounty (`VALID_NOT_ELIGIBLE` — #2, #7b):** PoC terbukti `[PASS]` di `FORK_DEPLOYED_HEAD` / `LOKAL` dengan dampak finansial nyata, **tetapi** kontrak belum di-deploy, berbeda dari bytecode produksi, paused, atau belum masuk daftar bounty -> **WAJIB PINDAHKAN `09` -> `audit/08-valid-not-eligible.md`** dengan kelas `LOW_CLASS: PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`, **mempertahankan kode PoC utuh + log `[PASS]` + perhitungan dampak**. **DILARANG** membuangnya ke `07` (agar `07` tetap bersih 0 entri). *(Yang benar-benar belum teruji tetap `07`; yang sudah terbukti tapi belum live adalah `08`.)*
   - **Berada Dalam Batasan Toleransi / Low (`VALID_NOT_ELIGIBLE` — Pernyataan #8b, #10b):** Simulasi PoC jalan secara mekanis tanpa curang, tetapi dampaknya tergolong *"Annoying but not financially dangerous"* (`LOW_NUISANCE`), atau merupakan *admin-only bug* tanpa jalur eksploitasi eksternal (#8b) -> **WAJIB CABUT dari 09** dan pindahkan ke `audit/08-valid-not-eligible.md`!
   - **Berada Dalam Batasan Eksplorasi / Kendala RPC (`NEEDS_NEXT_STEP` — Pernyataan #9b):** Logika kode kuat namun butuh metode eksplorasi lanjut (`NEXT_EXPLORE`), butuh cek state mainnet (`NEXT_MAINNET`), atau belum diuji karena kendala RPC/tooling (`TOOL_BLOCKED`) -> **WAJIB CABUT dari 09** dan pindahkan ke `audit/07-needs-next-step.md`!
     **Syarat sah masuk `07`:** setiap entri wajib memuat blok `PERCOBAAN:` (perintah + keluaran) untuk label `NEXT_EXPLORE`/`TOOL_BLOCKED`, dan bukti bahwa RPC benar-benar tidak tersedia untuk `NEXT_MAINNET`. Entri tanpa bukti percobaan **ditolak Hakim** dan lead dikembalikan ke Fase 3 untuk dikerjakan sekarang — bukan diloloskan sebagai `07`.
     **`07` BUKAN penampung HEAD-only.** Bila PoC sudah `[PASS]` tetapi kodenya belum live, wadahnya `08` (`PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN`), bukan `07`.
   - **Melanggar Pernyataan Ketat Mutlak (`REJECTED_*` — Pernyataan #1–#6 beserta sub-kasus ketat #7a, #8a, #9a, #10a):** Memakai *Fantasy Mock* (#1), klaim produksi tanpa bukti kesetiaan deployment (#2), mengasumsikan `totalSupply == 0` pada pool *live* (#3), tidak ada korban rasional (#4), *Negative-EV* (#5), perilaku by-design / baris kode meleset (#6), menyerang `initialize()` terkunci (#7a), *privileged fantasy* (#8a), cheatcode / PoC gagal di state nyata (#9a), atau debu tanpa amplifikasi (#10a) -> **WAJIB CABUT dari 09** dan buang ke `audit/06-refuted-invalid.md`!
4. **Setiap vonis wajib memakai Format Keluaran `VERDICT.md`** (`ID`, `VERDICT`, `TARGET_FILE`, `ALASAN`, `BUKTI`, `TANGGA_BUKTI`, `DEPLOYMENT_MATCH`, `BIAYA-BACA`). Verdict tanpa `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH` dianggap belum sah.
5. **3-Stage Breaker:** lead yang berstatus `REJECTED_POC_FAILS` di `06` (setelah Strike 1 Manual + Strike 2 Manual/Amplifikasi + **Strike 3 Fuzz** gagal di Fase 3) **DILARANG** dipindahkan kembali ke `07`. Kunci breaker bersifat final sampai seluruh lead lain selesai diuji.

---

## Langkah 2: Standarisasi Format Keenam File Murni (04 s/d 09)

1. `audit/09-confirmed-findings.md` (Murni `VALID_ELIGIBLE` — Siap Kirim Bounty):
   Memuat: Judul & Keparahan (CRITICAL/HIGH/MEDIUM), `Verdict: VALID_ELIGIBLE`, `Deployment: LIVE_MATCH`, `Mode Uji: FORK_LIVE (chain, block, RPC)`, Lokasi Kode & Invarian, Validasi Realitas Produksi, Akar Masalah & Dampak Finansial Kuantitatif, Kode PoC Utuh, Log Output, dan Patch Perbaikan (diff).
2. `audit/08-valid-not-eligible.md` (Murni `VALID_NOT_ELIGIBLE` — Valid dalam Batasan / Low / Pre-Live):
   Memuat: ID, Lokasi, Sub-Kategori (`LOW_NUISANCE` | `ADMIN_ONLY` | `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`), Bukti Simulasi PoC **utuh** (`[PASS]` + log), dan alasan teknis mengapa masuk batas toleransi 08 (bukan 09). Untuk `PRE_LIVE_SCOPE`, wajib mencantumkan `Deployment: HEAD-only (PROVEN_ON_REPO_HEAD)` + `Mode Uji: FORK_DEPLOYED_HEAD / LOKAL`.
3. `audit/07-needs-next-step.md` (Murni `NEEDS_NEXT_STEP` — Belum Selesai Diuji):
   Memuat: ID, Lokasi, Label Disposisi (`NEXT_EXPLORE` | `NEXT_MAINNET` | `TOOL_BLOCKED`), ringkasan apa yang sudah diuji di Fase 3, dan langkah konkret selanjutnya.
4. `audit/06-refuted-invalid.md` (Murni `REJECTED_*` — Gugur Permanen di Fase 3/4):
   Memuat: ID, Asal Lead, Kelas Vonis (`REJECTED_FANTASY_MOCK`, `REJECTED_POC_FAILS`, dll.), nomor Pernyataan `VERDICT.md` yang dilanggar, **blok `BUKTI_SIMULASI:`** (perintah + log + Strike 3 Fuzz), dan bukti penolakannya.
5. `audit/05-raw-leads.md` (Rekonsiliasi Status Antrean):
   Pastikan setiap `LEAD-XXX` memiliki penanda hasil akhirnya: `[STATUS -> 09]`, `[STATUS -> 08]`, `[STATUS -> 07]`, atau `[STATUS -> 06]`.
6. `audit/04-code-guarded.md` (Arsip Guard Kode dari Fase 2):
   Daftar hipotesis Fase 2 yang dihentikan oleh `require` / `if (...) revert` beserta status apakah berhasil ditembus di Putaran 2 atau tetap tertahan guard.

---

## Langkah 3: Ringkasan Eksekutif ke Pengguna
Tampilkan tabel ringkasan akhir kepada pengguna yang merinci jumlah item di masing-masing file (04, 05, 06, 07, 08, dan 09), beserta daftar kandidat yang dipindahkan oleh Hakim `VERDICT.md` dari 09 ke 08, 07, atau 06.

**Wajib disertai:** (a) tabel cakupan per domain dari Langkah 0a, (b) baris `COVERAGE: PASS` atau `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`, dan (c) baris `07: <n> entri` + `LAZY_BAILOUT: PASS|DETECTED`. Bila status pembatalan aktif (`COVERAGE` atau `LAZY_BAILOUT`), ringkasan **DILARANG** disajikan sebagai laporan final — sajikan sebagai laporan sementara beserta daftar domain/lead yang wajib dikerjakan ulang.
