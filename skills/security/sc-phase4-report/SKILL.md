---
name: sc-phase4-report
description: Phase 4 — Final Verdict Judging (via verify/VERDICT.md), Deployment Eligibility Gate (09 Live vs 08 Pre-Live/HEAD-Only), Anti-Paper-Refutation Check (#11e), and Pure 6-File Audit Reporting (04 to 09).
version: 6.4.0
---

# Phase 4: Final Verdict Judging & Pure 6-File Audit Reporting (04–09)

Tujuan Fase 4 adalah bertindak sebagai Hakim Akhir (Bounty Judge) menggunakan standar `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md` terhadap seluruh hasil simulasi Fase 3, menjalankan **Rekonsiliasi Identitas Deployment** (memisahkan temuan *Live Production* ke `09` vs *Proven on Repo HEAD / Pre-Live* ke `08`), memeriksa integritas cakupan dan bukti simulasi (#11d, #11, #11e), lalu menyusun keenam file hasil (`audit/04` s/d `audit/09`) secara bersih.

**GERBANG TULIS (WAJIB):** sebelum memindahkan/mengedit entri di `audit/04`–`09`, baca **`workspace/AGENTS.md` Pasal 1.3 (Protokol Anti-Truncate & Metode Write)**. `open(path,"w")` dan `>` shell **DILARANG** untuk seluruh `audit/*.md` — memotong file ke 0 byte saat dibuka. Pemindahan entri antar wadah wajib memakai `append` (entri baru) + `patch` (ubah status), dan diverifikasi dengan `grep -c '^## \['` sebelum & sesudah.

---

## Langkah 0: Rekonsiliasi Identitas Deployment — TEKNIK BUKTI YANG SAH

**Hukum teknik (dari insiden nyata):** `eth_call` pada endpoint publik **mengembalikan `revert` dengan data KOSONG (`0x`) untuk selector APA PUN** — termasuk selector yang jelas ada. Bukti:
```
# selector VALID + ABI lengkap -> revert nyata dengan guard
cast call <periphery> "0x609ea081<ABI-lengkap>"  -> InvalidQuoteTimestamp  data "0xf722177f"
# selector VALID tanpa argumen      -> revert data "0x"
# selector PALSU 0x11111111         -> revert data "0x"   (identik)
```

**DILARANG** menyimpulkan "fungsi tidak ada" dari `revert 0x`. **Urutan bukti yang sah:**
1. **Scan dispatcher** dari `eth_getCode` — cari pola `PUSH4 <sel> EQ`; daftar selector inilah yang otoritatif (mis. `0x97CCDBea…` → 26 selector).
2. **Sentinel decoded-call** — panggil selector dengan ABI **lengkap**; guard nyata (`InvalidQuoteTimestamp`, `MsgValueDoesNotMatchInputAmount`, dll.) membuktikan fungsi ada **dan** jalur kodenya dieksekusi.
3. **Kompilasi silang** — kompilasi source terverifikasi explorer lalu diff selector hasil kompilasi terhadap daftar live (menemukan `HEAD-only` per-fungsi, bukan per-kontrak).

**Catatan `HEAD-only` per-fungsi:** kontrak bisa **sebagian** live — sebagian selector ada, sebagian tidak. Jangan menandai seluruh kontrak `HEAD-only` hanya karena satu fungsi absen. Contoh nyata: `SpokePoolPeriphery` live mengekspos 26 selector (termasuk `depositWithAuthorization 0x711bc67b` dan `depositNative 0x609ea081`) tetapi **tidak** mengekspos `MAX_RELATIVE_TIME_SECONDS 0x8dc18f26`, `swapAndBridge*`, dan `depositWithPermit*`.

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

**(b) Gerbang Jejak (Fase 2):** berkas `[MUST-AUDIT]` berstatus `LEAD_GENERATED` atau `ATTESTED_CLEAN` (wajib bersitasi `File:Baris` per fungsi) ÷ total `[MUST-AUDIT]` = **100% per domain** (`0 berkas BELUM`, `0 berkas DIBACA gantung`, dan `0 berkas DEFERRED` di seluruh domain).

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
| Gerbang jejak: cakupan `[MUST-AUDIT]` **< 100%** (masih ada berkas `BELUM`, `DIBACA` gantung, atau `DEFERRED`) | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Ada **>=1 domain** wajib ber-cakupan **0%** | `AUDIT_INCOMPLETE_COVERAGE_BIAS` |
| Seluruh kondisi di atas terpenuhi | lanjut ke Langkah 3b & 3c |

Bila status `AUDIT_INCOMPLETE_COVERAGE_BIAS`: **tolak** penyelesaian laporan, tulis status di kepala `03` dan `09`, dan kembalikan eksekusi ke Fase 1/2 **tanpa menghapus** temuan yang sudah ada.

### 3b. Audit Kejujuran Usaha pada `07` — Gate Anti-Lazy-Bailout (Pernyataan #11)

**Pernyataan #11 — `LAZY_BAILOUT_DETECTED`.** `07` bukan tempat membuang lead yang belum dikerjakan. Hakim **WAJIB** memeriksa **setiap** entri di `audit/07-needs-next-step.md` sebelum menerima laporan.

Jalankan validator mekanis lebih dulu:
```bash
python3 /home/ubuntu/.hermes/profiles/adv/verify/tools/verify07.py audit/07-needs-next-step.md
```

| Label | Yang wajib diperiksa Hakim | Vonis bila gagal |
|---|---|---|
| `TOOL_BLOCKED` | Log terminal **ketiga** usaha Tangga Self-Healing (`sc-phase3` Langkah 0c): (1) flag/remapping, (2) **Standalone Interface-Only Harness**, (3) fallback RPC. | `LAZY_BAILOUT_DETECTED` |
| `NEXT_MAINNET` | Bukti bahwa rantai **benar-benar** tanpa RPC/explorer publik. Bila RPC tersedia, Hakim **wajib menjalankan sendiri** `cast call` / `cast storage` / `cast code` **pada sesi itu** dan menuntaskan vonis ke `09`, `08`, atau `06`. | `LAZY_BAILOUT_DETECTED` |
| `NEXT_EXPLORE` | Log eksekusi fuzzer/chaining/halmos yang **mentok timeout komputasi**, bukan sekadar alasan teks. | `LAZY_BAILOUT_DETECTED` |

**Target akhir `07` = 0 entri.** Bila `verify07.py` mengembalikan **exit code 1** atau ada entri tanpa bukti komputasi nyata -> jatuhkan **`LAZY_BAILOUT_DETECTED`** dan kembalikan ke Fase 3.

**Label basi tidak sah.** Judul entri sudah menyatakan `DIPINDAHKAN KE 06`/`09` tetapi label lama (`NEXT_EXPLORE`/`NEXT_MAINNET`) masih tertinggal -> dihitung sebagai pelanggaran #11.

### 3c. Audit Kejujuran Penolakan pada `06` — Gate Anti-Paper-Refutation (Pernyataan #11e — BARU)

`06-refuted-invalid.md` **BUKAN** tempat membuang lead secara malas hanya dengan karangan teks!

Hakim **WAJIB** memeriksa seluruh entri di `audit/06-refuted-invalid.md` yang menyandang vonis:
`REJECTED_POC_FAILS` · `REJECTED_NEGATIVE_EV` · `REJECTED_DUST`

**Syarat Sah:** ketiga jenis vonis di atas **WAJIB** memuat blok `BUKTI_SIMULASI:` berisi perintah test yang benar-benar dieksekusi (`forge test` / `cargo test` / `sui move test`) beserta keluaran log terminalnya, yang menunjukkan bahwa:
1. Sudah dilakukan **Victim Lifecycle Seeding** (bila menyerang state dinamis/antrean/allowance), **DAN**
2. Sudah ditempuh protokol **3-Stage Escalation (2 Manual + 1 Mandatory Fuzz `testFuzz_`/`proptest`/`halmos`)**.

**Vonis Hakim:** apabila ditemukan entri `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, atau `REJECTED_DUST` di `06` yang hanya berisi hitungan kertas / klaim teks **tanpa log eksekusi test dan fuzz**, Hakim **WAJIB** menjatuhkan **`PAPER_REFUTATION_DETECTED`**, menolak laporan final, dan mengembalikan lead tersebut ke **Fase 3** untuk diuji di simulator!

**Pengecualian sah (boleh tanpa kode test):** hanya 4 Kemustahilan Statis Sempit — `REJECTED_FANTASY_MOCK` (#1), `REJECTED_GENESIS_MIRAGE` pada pool tunggal terkunci (#3), `REJECTED_NON_LIVE_INIT` yang terkunci rapat + `_disableInitializers()` (#7a), `REJECTED_PRIVILEGED_FANTASY` di luar batas validasi (#8a), serta `REJECTED_MISMATCH` (#6) dan `REJECTED_BY_DESIGN` (#6).


### 4. Format Wajib di Ringkasan Eksekutif
Setiap Ringkasan Eksekutif Fase 4 wajib mencantumkan tabel cakupan per domain (`Total | LEAD | ATTESTED | BELUM | % | Gate`) beserta baris status akhir: `COVERAGE: PASS` atau `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`, plus baris `LAZY_BAILOUT: PASS|DETECTED` dan `PAPER_REFUTATION: PASS|DETECTED`. Laporan tanpa ketiganya dianggap belum lengkap.

**Alasan aturan ini:** tanpanya, Hakim hanya mengadili kualitas di dalam cakupan yang kebetulan terbuka, lalu menyebutnya "audit selesai".

---

## Langkah 1: Eksekusi Vonis Akhir & Pemisahan Deployment dengan `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md`

1. **Wajib Baca Standar Hakim:** Panggil `read_file` pada `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md`.

2. **Jalankan Langkah 0 VERDICT.md — Rekonsiliasi Siklus Deployment & Kesetaraan Entrypoint (Gerbang Pemisahan `09` vs `08`):**
   - **Alat wajib:** `python3 verify/tools/deploy_parity.py --paradigm … --addr … --entrypoints "…" --rpc … --repo … --out audit/notes/deploy-parity-<ID>.json`. Jangan menilai manual.
   - Urutan: **0.0 Gerbang Siklus** (`P1`/`P2`/`P3`/`P4`) → **0.1 empat pra-syarat** (proxy EIP-1967 → fallback-router `MissingFallbackHandler` → delegatecall/library → multi-kontrak) → **0.2 lima verdict entrypoint** (`LIVE_MATCH` / `HEAD_ONLY_PROVEN` / `TESTNET_ONLY` / `ENTRYPOINT_RELOCATED` / `REGRESSION_FIXED` / `ENV_ERROR`).
   - **DILARANG** memakai "bytecode identik" atau "`sha256` explorer sama" sebagai syarat `LIVE_MATCH` — setiap repo punya siklus rilis berbeda dan build Foundry jarang reproducible. Yang diuji adalah **keberadaan & perilaku entrypoint yang diserang PoC**.
   - **DILARANG** menyimpulkan "fungsi tidak ada" dari `ENV_ERROR` (RPC 403, timeout, rate-limit). `ENV_ERROR` → `07 TOOL_BLOCKED`, bukan `06`/`08`.
   - **Severity tetap ditentukan impact** (Langkah 0.3): menurunkan severity karena HEAD-only/testnet adalah pelanggaran.
   - **Ingat:** Jangan gunakan `revert 0x` pada `eth_call` sebagai bukti fungsi tidak ada. `revert 0x` bersifat **ambigu** (bisa "tidak ada" atau "ada tapi revert tanpa pesan") → wajib klasifikasi lewat `deploy_parity` (kontrol negatif `0xdeadbeef` + `PUSH4` dispatcher). Untuk paradigma `generic` (rantai belum dikenal), `ABSENT` **DILARANG MUTLAK** — gunakan `IDENTITY_ONLY`.

3. **Adili Setiap Kandidat dengan 11 Pernyataan Wajib `VERDICT.md`:**

   **a. Lolos Seluruh 11 Pernyataan + Terbukti Aktif di Produksi (`VALID_ELIGIBLE` -> `09-confirmed-findings.md`)**
   Simulasi PoC `[PASS]` (`FORK_LIVE`, atau `FORK_DEPLOYED_HEAD` yang kodenya cocok dengan bytecode live `LIVE_MATCH`), tanpa *Fantasy Mock*/Cheatcode, dan membuktikan bahaya finansial nyata (Critical/High/Medium) -> **Disahkan di `audit/09-confirmed-findings.md`**.

   **b. PoC Eksploitasi Terbukti `[PASS]` & Berbahaya Finansial, TETAPI Kode Masih HEAD-only / Belum Live (`VALID_NOT_ELIGIBLE [PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN]` -> `08-valid-not-eligible.md`)**
   Simulasi PoC pada kode repo berhasil membuktikan eksploitasi (`FORK_DEPLOYED_HEAD` atau `LOKAL` `[PASS]`, `TANGGA_BUKTI: A-HEAD` atau `B`), namun kontrak belum di-deploy di mainnet, berada di luar daftar alamat bounty saat ini, atau fungsi yang rentan hanya ada di commit HEAD terbaru -> **Pindahkan dari `09` ke `audit/08-valid-not-eligible.md`** dengan `LOW_CLASS: PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`!
   **Wajib pertahankan kode PoC utuh dan angka kuantitatif dampaknya di dalam `08`** (jangan dipangkas, dan **JANGAN** dimasukkan ke `07`!).

   **c. Berada Dalam Batasan Toleransi / Low Lainnya (`VALID_NOT_ELIGIBLE` — Pernyataan #8b, #10b -> `08-valid-not-eligible.md`)**
   Simulasi PoC jalan secara mekanis tanpa curang, tetapi dampaknya tergolong *"Annoying but not financially dangerous"* (`LOW_NUISANCE`), atau merupakan *admin-only bug* tanpa jalur eksploitasi eksternal (`ADMIN_ONLY`) -> **Pindahkan dari `09` ke `audit/08-valid-not-eligible.md`**.

   **d. Kendala Komputasi/RPC Ekstrem yang Sudah Dibuktikan dengan Log Usaha (`NEEDS_NEXT_STEP` — Pernyataan #9b -> `07-needs-next-step.md`)**
   **Hanya** untuk kandidat yang benar-benar belum bisa diselesaikan setelah melewati **3-Step Self-Healing** atau **mentok timeout fuzzer/SMT**, dan **lulus validasi `verify07.py`**.

   **e. Melanggar Pernyataan Ketat Mutlak atau Gagal setelah 3-Stage Escalation (`REJECTED_*` -> `06-refuted-invalid.md`)**
   Memakai *Fantasy Mock* (#1), mengasumsikan `totalSupply == 0` pada pool live yang permanen terisi (#3), tidak ada korban rasional (#4), *Negative-EV* yang sudah dibuktikan gagal lewat test+fuzz (#5), by-design / baris kode meleset (#6), menyerang `initialize()` terkunci (#7a), *privileged fantasy* (#8a), cheatcode / PoC tetap gagal setelah *Victim Seeding* + Strike 3 Fuzz (#9a), atau debu tanpa amplifikasi setelah di-fuzz (#10a) -> **Buang ke `audit/06-refuted-invalid.md`** (wajib disertai log simulasi untuk #5, #9a, #10a).

4. **Setiap vonis wajib memakai Format Keluaran `VERDICT.md`** (`ID`, `VERDICT`, `TARGET_FILE`, `ALASAN`, `BUKTI`, `TANGGA_BUKTI`, `DEPLOYMENT_MATCH`, `BIAYA-BACA`).

5. **Kunci 3-Stage Escalation (2 Manual + 1 Fuzz):** lead yang berstatus `REJECTED_POC_FAILS` di `06` (setelah lulus bukti 2 Manual + 1 Fuzz di Fase 3) **DILARANG** dipindahkan kembali ke `07`.

---

## Langkah 2: Standarisasi Format Keenam File Murni (04 s/d 09)

1. `audit/09-confirmed-findings.md` (**Murni `VALID_ELIGIBLE` — Live Production & Siap Kirim Bounty**):
   Memuat: Judul & Keparahan (CRITICAL/HIGH/MEDIUM), `Verdict: VALID_ELIGIBLE`, `Mode Uji: FORK_LIVE (...)`, `DEPLOYMENT_MATCH: LIVE_MATCH`, Lokasi Kode & Invarian, Validasi Realitas Produksi, Akar Masalah & Dampak Finansial Kuantitatif, Kode PoC Utuh, Log Output, dan Patch Perbaikan (diff).
2. `audit/08-valid-not-eligible.md` (**Murni `VALID_NOT_ELIGIBLE` — `PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN`, `ADMIN_ONLY`, `LOW_NUISANCE`**):
   Memuat: ID, Lokasi, `LOW_CLASS`, `TANGGA_BUKTI` (`A-HEAD` atau `B`), `DEPLOYMENT_MATCH`, Bukti Simulasi PoC (**wajib kode PoC utuh untuk `HEAD_ONLY_PROVEN`**), Dampak Kuantitatif, dan alasan teknis mengapa masuk `08`.
3. `audit/07-needs-next-step.md` (**Murni `NEEDS_NEXT_STEP` — Target Akhir: 0 Entri**):
   Memuat: ID, Lokasi, `Disposition:` (`NEXT_EXPLORE` | `NEXT_MAINNET` | `TOOL_BLOCKED`), blok `PERCOBAAN:` berisi perintah `$ ...` dan output nyata, serta `Langkah Konkret Berikutnya:`.
4. `audit/06-refuted-invalid.md` (**Murni `REJECTED_*` — Gugur Permanen + Wajib Log Simulasi untuk `POC_FAILS`/`NEGATIVE_EV`/`DUST`**):
   Memuat: ID, Asal Lead, Kelas Vonis, nomor Pernyataan `VERDICT.md` yang dilanggar, `TANGGA_BUKTI`, `DEPLOYMENT_MATCH`, dan blok `BUKTI_SIMULASI:` (log eksekusi test + Strike 3 Fuzz untuk klaim kegagalan PoC/EV/Dust).
5. `audit/05-raw-leads.md` (**Rekonsiliasi Status Antrean**):
   Pastikan setiap `LEAD-XXX` memiliki penanda hasil akhirnya: `[STATUS -> 09]`, `[STATUS -> 08]`, `[STATUS -> 07]`, atau `[STATUS -> 06]`.
6. `audit/04-code-guarded.md` (**Arsip Guard Statis dari Fase 2**):
   Daftar hipotesis Fase 2 yang dihentikan oleh guard statis beserta status Putaran 2.

---


## Langkah 3: Ringkasan Eksekutif ke Pengguna
Tampilkan tabel ringkasan akhir kepada pengguna yang merinci jumlah item di masing-masing file (04, 05, 06, 07, 08, dan 09), beserta daftar kandidat yang dipindahkan oleh Hakim `VERDICT.md` dari 09 ke 08, 07, atau 06.

**Wajib disertai:** (a) tabel cakupan per domain dari Langkah 0a, (b) baris `COVERAGE: PASS` atau `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`, (c) baris `07: <N> entri` + `LAZY_BAILOUT: PASS|DETECTED`, dan (d) baris `PAPER_REFUTATION_06: PASS|DETECTED`. Bila status pembatalan aktif (`COVERAGE`, `LAZY_BAILOUT`, atau `PAPER_REFUTATION_06`), ringkasan **DILARANG** disajikan sebagai laporan final — sajikan sebagai laporan sementara beserta daftar domain/lead yang wajib dikerjakan ulang. Sertakan **pemisahan eksplisit** antara temuan `09` (Live Production) dan `08` (`PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN`).
