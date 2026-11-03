# PROTOKOL PENILAI & HAKIM AKHIR (VERDICT GATE)

Dokumen ini adalah **standar hukum tertinggi** pada dua jalur:

1. **Jalur Audit Mandiri** (Fase 4 — `sc-phase4-report`): mengadili setiap kandidat yang lolos PoC Fase 3 sebelum diizinkan bertahan di `audit/09-confirmed-findings.md`.
2. **Jalur Verifikasi Inbox** (`verify/ingest.py`): mengadili klaim dari `.verify/queue.json` yang sudah lolos saringan mekanis.

Penilai **tidak** menyisir kode untuk mencari bug baru — itu tugas hulu. Tugas Penilai murni **mengadili bukti**, memisahkan pelanggaran mutlak dari temuan berbatas toleransi, dan menempatkannya ke wadah yang tepat: `06`, `07`, `08`, atau `09`.

---


## CAKUPAN BERLAKU (keputusan 2026-10-31)

Protokol ini berlaku untuk **audit baru**. Audit yang sudah berjalan dengan skema lama **tidak dimigrasikan**.

| Audit | Skema | Catatan |
|---|---|---|
| **Baru** (mulai sekarang) | `00`–`09` (10 file murni): `04-code-guarded` · `05-raw-leads` · `06-refuted-invalid` · `07-needs-next-step` · `08-valid-not-eligible` · `09-confirmed-findings` | 11 Pernyataan + Gate Cakupan + Tangga Bukti + Langkah 0 wajib |
| **Legacy** (mis. Across, selesai) | `04-rejected-hypotheses` · `05-raw-leads` · `06-unproven-needs-review` · `07-confirmed-findings` | tetap apa adanya; **jangan** dipetakan ulang. Catatan: `04` legacy = hipotesis ditolak, berbeda arti dari `04-code-guarded` skema baru |

Artefak legacy tetap sah dibaca dengan penomoran lamanya. Jangan mencampur penomoran antar-audit dalam satu laporan.

---

## LANGKAH 0 — Rekonsiliasi Identitas Deployment (wajib, sebelum menilai apa pun)

Tujuan: memastikan **kode yang dikutip adalah kode yang berjalan**.

1. Kumpulkan seluruh alamat kontrak yang diklaim (`In-Scope`).
2. Untuk setiap alamat: ambil source terverifikasi dari explorer (`module=contract&action=getsourcecode`).
   - Proxy (UUPS/ERC1967): baca slot `0x360894a1…2bbc` untuk mendapat **implementation**, lalu ambil source implementation — bukan proxy-nya.
3. Bandingkan dengan kode repo yang dikutip:
   - `sha256` berkas kontrak utama **sama** → klaim boleh disebut berlaku di **produksi**.
   - **berbeda** → klaim wajib ditandai **`HEAD-only`**, dan verdict tidak boleh melebihi `07-needs-next-step.md`.
4. Jika explorer tidak dapat diakses atau kontrak tidak terverifikasi, catat **nama sumber yang gagal** (`Sourcify`, `Blockscout`, `Etherscan`, RPC mana). Kegagalan sumber **bukan** bukti bahwa kode sesuai maupun tidak sesuai.

> **Dilarang** menyatakan sebuah klaim "blocked / butuh repo privat" sebelum langkah ini dijalankan.

---

## LANGKAH 1 — Jalankan & Periksa Bukti PoC

- PoC gagal kompilasi, atau **revert terhadap state nyata** → `REJECTED_POC_FAILS` → `06-refuted-invalid.md`.
- Rantai target punya RPC publik, tetapi PoC hanya dijalankan lokal tanpa fork state produksi (atau terhalang RPC/tooling, atau masih butuh verifikasi mainnet lanjutan) → `NEEDS_NEXT_STEP` → `07-needs-next-step.md`.
- **Output test kosong bukan kegagalan.** Pastikan pola pencarian benar (`--match-contract` memakai **nama kontrak**, bukan nama berkas; jalankan `forge test --list` lebih dulu). Baru setelah itu boleh menyimpulkan gagal.

---

## LANGKAH 2 — Audit Kejujuran PoC (Anti-Cheatcode & Anti-Fantasy-Mock)

1. **Cheatcode terlarang**: `vm.prank` sebagai admin/owner/pool/keeper, `vm.store`, `vm.etch` state protokol, `deal` ke kontrak protokol, `vm.warp` lintas waktu tak wajar, reentrancy lewat `.transfer()` (2300 gas) → `REJECTED_CHEATCODE` → `06-refuted-invalid.md`.
   - Pengecualian yang sah: `vm.deal` ke **dompet penyerang/pelaku uji**; `vm.prank` sebagai **EOA tanpa hak**; `vm.etch` **lingkungan predeploy** pada uji lokal (wajib dicatat sebagai deviasi).
2. **Fantasy mock**: mengarang sifat Token Kasta 1 (LP Token, Vault Share, Receipt Token, WETH, token internal) berupa Fee-on-Transfer/Rebase/Callback/gagal-bool, menganggap USDT mainnet memotong fee, atau menyuntikkan kontrak jahat ke parameter yang dikunci Factory/Whitelist → `REJECTED_FANTASY_MOCK`.
3. **Mock-driven verdict (baru)**: mock terhadap **komponen protokol/bridge pihak ketiga** (CCTP `MessageTransmitter`, LayerZero endpoint, precompile) hanya boleh menopang bukti **STRUKTURAL**. Bukti semacam itu **dilarang** menaikkan verdict ke `09` maupun dipakai untuk menyatakan sebuah jalur "aman".

---

## LANGKAH 3 — Verifikasi Kesesuaian Kode (`lines` & Guard)

Baca **hanya** rentang baris yang diklaim beserta fungsi penjaga di sekitarnya.

- Kode tidak mendukung klaim → `REJECTED_MISMATCH` → `06-refuted-invalid.md`.
- Perilaku terbukti terdokumentasi sebagai disengaja (NatSpec, `DESIGN.md`, README, blog resmi, Snapshot/DAO) → `REJECTED_BY_DESIGN`.
- **Aksi `onlyOwner`/admin**: sebelum menyebutnya defek, periksa apakah ada **mandat governance** yang terdokumentasi (proposal Snapshot, pengumuman resmi). Tindakan resmi ber-mandat **bukan** kerentanan; paling jauh `08-valid-not-eligible.md` kelas `ADMIN_ONLY`.

---

## LANGKAH 4a — Gate Cakupan (WAJIB SEBELUM LANGKAH 4)

**Kualitas PoC hanya bermakna untuk permukaan yang benar-benar diperiksa.** Satu PoC sempurna di atas cakupan 2% tetap merupakan audit yang **gagal**. Karena itu gerbang ini dijalankan **lebih dulu**: Hakim DILARANG memeriksa 11 Pernyataan sebelum cakupan dinyatakan sah.

### Dua gerbang berbeda

| Gerbang | Ambang | Diukur pada |
|---|---|---|
| **Gerbang Fase 2** | ≥ 80% berkas `[MUST-AUDIT]` per domain berstatus `LEAD_GENERATED` atau `ATTESTED_CLEAN` | `audit/03-attack-surface-queue.md` |
| **Gerbang Fase 4** | 0 berkas `BELUM` di seluruh domain | tabel cakupan di `03` |

**DILARANG memakai "jumlah lead per domain" sebagai metrik kelulusan.** Kuota lead memicu pembuatan lead sampah pada modul yang memang aman (hukum Goodhart). Kelulusan diukur dari **jejak per berkas**, bukan banyaknya hipotesis.

### Kondisi pembatalan — `AUDIT_INCOMPLETE_COVERAGE_BIAS`

> **Rujukan silang:** status vonis & akibatnya di tingkat laporan juga dicatat di **Pernyataan #11d**. Bila ada perbedaan redaksi antara bagian ini dan #11d, **bagian ini (LANGKAH 4a) yang menang**.

Vonis ini dijatuhkan bila **salah satu** terpenuhi:

1. Ada domain `D1..Dn` tanpa berkas `[MUST-AUDIT]` sama sekali di antrean (domain kosong / tidak terwakili).
2. Ada berkas `[MUST-AUDIT]` berstatus `BELUM`, atau berstatus `DICAKUP_U1/U10/S-xx` tanpa uji spesifik.
3. Ada domain dengan cakupan < 80% pada Gerbang Fase 2.
4. Audit memakai sampel, bukan populasi penuh yang terdaftar di `00b-file-inventory.md`.

**Bila `AUDIT_INCOMPLETE_COVERAGE_BIAS` dijatuhkan:**

- **DILARANG** menulis Ringkasan Eksekutif seolah audit selesai.
- Hakim **wajib** mengembalikan eksekusi ke Fase 1/Fase 2 untuk menyapu domain yang terlewat.
- Temuan yang sudah ada **tetap disimpan** sebagai hasil sementara dan **DILARANG dihapus**.
- Status akhir laporan wajib ditulis: `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`, bukan `PASS`.

### Format tabel cakupan wajib di Ringkasan Eksekutif

| Domain | Total | LEAD | ATTESTED | BELUM | % | Gate |
|---|---|---|---|---|---|---|

Laporan tanpa tabel ini **dianggap belum lengkap**. Baris status akhir: `COVERAGE: PASS` atau `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`.

---

## LANGKAH 4 — Gate 11 Pernyataan Wajib

Sebuah temuan HANYA boleh mendapat vonis `VALID_ELIGIBLE` dan bertahan di `audit/09-confirmed-findings.md` bila memenuhi **kesebelas** pernyataan berikut. Pernyataan #11 berbeda sifatnya: ia tidak menilai satu temuan, melainkan **kejujuran keseluruhan laporan** — dan bila dilanggar, seluruh laporan ditolak.

### A. ENAM PERNYATAAN KETAT MUTLAK (Zero-Tolerance — melanggar = `06-refuted-invalid.md`)

**1. Keaslian Entitas & Aset (No Fantasy Mock)**
> *"Seluruh token, LP token, share/receipt token, dan kontrak yang berinteraksi di dalam PoC memakai kode asli repositori, atau tiruan yang perilakunya 100% identik dengan aset produksi (tidak mengarang Fee-on-Transfer/Rebase/USDT-quirk pada token standar, dan tidak menyuntikkan kontrak jahat ke parameter yang dikunci Factory/Whitelist)."*
→ `REJECTED_FANTASY_MOCK`

**2. Kesetiaan Deployment & Provenance Kode (Deployment Fidelity)** — *baru*
> *"Kode yang dikutip terbukti identik dengan yang berjalan di produksi (source terverifikasi explorer, atau sha256 yang sama), **atau** klaim secara eksplisit ditandai `HEAD-only` dan verdict-nya tidak melebihi `07-needs-next-step.md`."*
→ Pelanggaran: `REJECTED_UNPROVEN_DEPLOYMENT` → `06-refuted-invalid.md` (bila klaim dipaksakan sebagai produksi).

**3. Keadaan Likuiditas Nyata (No Empty-Pool Mirage)**
> *"Eksploitasi terbukti berhasil pada keadaan TVL dan likuiditas nyata di produksi, bukan mengandalkan `totalSupply == 0` / First Depositor Attack pada pool yang sudah live atau sudah mencetak dead shares saat deploy — kecuali PoC membuktikan penyerang mampu membuat pool resmi baru secara permissionless atau menguras TVL ke nol lebih dulu."*
→ `REJECTED_GENESIS_MIRAGE`

**4. Korban Rasional & Dampak Eksternal (Rational Victim)**
> *"Serangan merugikan dana protokol atau pengguna lain yang bertindak rasional (memakai parameter perlindungan normal), bukan mengharuskan korban mematikan pelindungnya sendiri (`minAmountOut = 0`, `deadline = max`, mengirim token via `ERC20.transfer` di luar jalur deposit), dan bukan hanya merusak pool terisolasi milik penyerang."*
→ `REJECTED_NO_VICTIM`

**5. Kelayakan Ekonomi Serangan (Positive-EV / Cost Asymmetry)**
> *"Serangan menghasilkan keuntungan finansial bersih (Profit > gas + modal hangus) **atau** sanggup membekukan dana protokol/korban bernilai besar secara permanen dengan biaya sangat murah."*
→ `REJECTED_NEGATIVE_EV`

**6. Presisi Bukti Kode & Bukan Desain Sengaja (Code & Design Match)**
> *"Rentang `File:Baris` yang dikutip adalah akar masalah sesungguhnya, dan perilakunya tidak didokumentasikan sebagai mekanisme yang disengaja protokol."*
→ `REJECTED_MISMATCH` (baris tidak cocok) / `REJECTED_BY_DESIGN` (disengaja)

### B. EMPAT PERNYATAAN HIBRIDA & BERBATAS (Bounded Threshold — memisahkan 06, 07, 08, 09)

**7. Status Live Produksi & Siklus Hidup Inisialisasi (Scope & Lifecycle)**
> *"Kontrak dan cabang fitur yang diserang termasuk cakupan resmi, aktif di produksi, dan tidak menyerang `initialize()` sekali-pakai yang sudah terkunci."*
- Menyerang `initialize()` yang sudah dieksekusi saat deploy → **[KETAT]** `REJECTED_NON_LIVE_INIT` → `06-refuted-invalid.md`
- Mekanisme nyata tetapi kontrak/fitur **pre-live**, **paused**, atau di luar scope utama → **`VALID_NOT_ELIGIBLE [PRE_LIVE_SCOPE]`** → `08-valid-not-eligible.md`

**8. Kemurnian Aktor Eksternal (Unprivileged External Path)**
> *"Seluruh langkah eksploitasi dapat dijalankan penyerang tak berizin dari awal hingga akhir, tanpa mengandalkan tindakan jahat/bodoh Admin/Owner/DAO/Keeper, dan bukan bug khusus fungsi admin tanpa jalur eksternal."*
- Mengasumsikan admin memasukkan konfigurasi bunuh diri, atau oracle rusak sendiri → **[KETAT]** `REJECTED_PRIVILEGED_FANTASY` → `06`
- Bug mekanis nyata pada fungsi **khusus admin** tanpa jalur eksploitasi eksternal (`admin-only bug with no external exploit path`) → **`VALID_NOT_ELIGIBLE [ADMIN_ONLY]`** → `08` *(bukan `06` — ini Low, bukan gugur)*

**9. Kejujuran Sandbox & Bukti Fork Produksi (Sandbox & Fork Integrity)**
> *"PoC dapat direproduksi dan menghasilkan `[PASS]` pada fork state produksi nyata (`Mode Uji: FORK`) tanpa memalsukan storage internal, dan mematuhi fisika gas/mempool rantai target."*
- `vm.store`, `vm.etch` state protokol, `vm.prank(admin/pool)`, `deal` ke protokol, atau revert di state nyata → **[KETAT]** `REJECTED_CHEATCODE` / `REJECTED_POC_FAILS` → `06`
- **Logika kode + PoC lokal jujur tetapi belum dapat diuji pada fork produksi → `NEEDS_NEXT_STEP` → `07-needs-next-step.md`, HANYA BILA memenuhi ketiga syarat berikut:**
  1. **Blok `PERCOBAAN:` wajib** — entri `07` harus memuat perintah yang benar-benar dijalankan **beserta keluarannya** (bukan rencana). `NEXT_EXPLORE` wajib melampirkan log Tier 2/3/5 (handler fuzzing, differential, multi-step chaining, halmos) yang **mentok timeout komputasi**; `TOOL_BLOCKED` wajib melampirkan log **ketiga** usaha Tangga Self-Healing (flag/toolchain → standalone interface-only → fallback RPC); `NEXT_MAINNET` wajib bukti rantai benar-benar tanpa RPC/explorer — bila RPC tersedia, DILARANG parkir di sini, jalankan `cast call`/`cast storage` saat itu juga.
  2. **RPC tersedia ⇒ DILARANG `07`.** Selama pekerjaan itu masih bisa diselesaikan pada sesi berjalan, `07` tidak sah.
  3. **Entri tanpa blok `PERCOBAAN:` = `LAZY_BAILOUT_DETECTED`** (lihat Pernyataan #11) → laporan DITOLAK dan lead dikembalikan ke Fase 3.
  4. **Field `Disposition:` wajib** — setiap entri `07` harus mendeklarasikan tepat satu label: `Disposition: NEXT_EXPLORE | NEXT_MAINNET | TOOL_BLOCKED`. Entri tanpa field ini tidak dapat diperiksa Hakim dan diperlakukan sebagai `LAZY_BAILOUT_DETECTED`.
- **Bukti berbasis mock pihak ketiga tidak dapat memenuhi pernyataan ini** (lihat Langkah 2.3).

**10. Kalibrasi Bahaya Finansial & Severity (Financial Danger Floor)**
> *"Dampak akhir PoC membuktikan bahaya finansial nyata — pencurian dana pokok/yield signifikan, insolvensi protokol, pembekuan aset permanen/jangka panjang, atau sabotase fungsi keselamatan berbatas waktu (repay/liquidate) yang memicu penyitaan paksa/kredit macet — bukan sekadar gangguan kelas Low ('Annoying but not financially dangerous'). Tingkat keparahan yang diklaim (CRITICAL/HIGH/MEDIUM) sesuai 100% dengan bukti kuantitatif pada log PoC."*
- Hanya pembulatan debu (1 wei–beberapa sen) yang tak dapat dilipatgandakan dan tidak mengunci dana → **[KETAT]** `REJECTED_DUST` → `06`
- Mekanisme nyata tetapi dampak jatuh ke kelas Low:
  1. **DoS with No Fund Loss** — transaksi hanya revert sementara; pengguna cukup mengirim ulang, mengubah parameter, atau memakai jalur darurat. Tidak ada dana hilang/beku.
  2. **Minor Capped Economic Damage** — kerugian kecil dan terbatas (*bounded*), tidak dapat menguras pool.
  3. **Nuisance Griefing** — memaksa gas ulang / mereset timer non-finansial, tanpa keuntungan penyerang dan tanpa pembekuan dana.
  → **`VALID_NOT_ELIGIBLE [LOW_NUISANCE]`** → `08-valid-not-eligible.md`
- Klaim HIGH/MEDIUM tetapi bukti hanya kelas Low atau admin-only → **turunkan ke LOW (S4)** dan pindahkan `09` → `08`.

### C. SATU PERNYATAAN INTEGRITAS LAPORAN (Report Integrity — melanggar = seluruh laporan DITOLAK)

**11. Kejujuran Usaha & Cakupan (Anti-Lazy-Bailout)** — *baru*

> *"Setiap entri di `07-needs-next-step.md` memuat blok `PERCOBAAN:` berisi perintah yang benar-benar dijalankan beserta keluarannya — bukan rencana, bukan kalimat alasan. Setiap klaim `TOOL_BLOCKED` melampirkan log ketiga usaha Tangga Self-Healing. Setiap klaim `NEXT_EXPLORE` melampirkan log Tier 2/3/5 yang mentok timeout komputasi. Setiap klaim `NEXT_MAINNET` melampirkan bukti bahwa RPC/explorer memang tidak tersedia."*

→ Pelanggaran: **`LAZY_BAILOUT_DETECTED`** → **laporan DITOLAK**, `07` dikembalikan ke Fase 3. Temuan yang sudah ada **tetap disimpan** sebagai hasil sementara dan DILARANG dihapus.

**Cara Hakim memeriksa (wajib, per entri `07`):**

| Label | Bukti yang wajib ada di entri | Tanpa bukti |
|---|---|---|
| `NEXT_EXPLORE` | Log Tier 2 (handler fuzzing) / Tier 3 (differential) / Tier 5 (halmos/symbolic) **yang berjalan sampai timeout komputasi** | `LAZY_BAILOUT_DETECTED` |
| `TOOL_BLOCKED` | Log terminal **ketiga** anak tangga: (1) flag/remapping/toolchain, (2) standalone interface-only harness, (3) fallback RPC | `LAZY_BAILOUT_DETECTED` |
| `NEXT_MAINNET` | Bukti chain tanpa RPC/explorer publik; bila RPC tersedia, **`07` tidak sah** — Hakim jalankan `cast call`/`cast storage` sendiri | `LAZY_BAILOUT_DETECTED` |

**Label basi tidak sah.** Judul entri sudah dipindah ke wadah lain tetapi label lama masih tertinggal → dihitung sebagai pelanggaran #11.

**11d. Gerbang Cakupan (`AUDIT_INCOMPLETE_COVERAGE_BIAS`) — laporan DITOLAK, dikembalikan ke Fase 1/2**

> **Prosedur, ambang, dan format tabel cakupan: lihat [LANGKAH 4a](#langkah-4a--gate-cakupan-wajib-sebelum-langkah-4) (sumber normatif).** Bagian ini hanya menetapkan **status vonis** dan akibatnya di tingkat laporan; bila ada perbedaan redaksi, **LANGKAH 4a yang menang**.

> *"Cakupan berkas `[MUST-AUDIT]` yang berstatus `LEAD_GENERATED` atau `ATTESTED_CLEAN` mencapai minimal 80% di setiap domain, dan tidak ada berkas terbesar di suatu domain yang masih berstatus `BELUM`."*

Hakim **WAJIB** menghitung sendiri dari `00b-file-inventory.md` × `03-attack-surface-queue.md`, bukan mempercayai tabel cakupan yang ditulis pelaksana.

**Syarat tolak (salah satu saja cukup):**
1. Cakupan `[MUST-AUDIT]` berstatus `LEAD_GENERATED` / `ATTESTED_CLEAN` **< 80%** pada domain mana pun.
2. Ada berkas `[MUST-AUDIT]` berstatus `BELUM`, atau berstatus `DICAKUP_U1/U10/S-xx` tanpa uji spesifik.
3. Ada domain `D1..Dn` tanpa berkas `[MUST-AUDIT]` sama sekali di antrean (domain kosong / tidak terwakili).
4. Audit memakai sampel, bukan populasi penuh yang terdaftar di `00b-file-inventory.md` (gate pemetaan < 100%).

**Atestasi hampa tidak dihitung sebagai jejak (#11c):** `ATTESTED_CLEAN` yang tidak memuat `File:Baris` konkret per fungsi yang diperiksa — atau yang bersandar hanya pada volume (`forge build`/`cargo test` PASS, jumlah berkas, `N/N PASS`, nama unit `S-0n`) — **DIBATALKAN**. Berkas tersebut dikembalikan ke `BELUM` **sebelum** persentase dihitung. Tanpa aturan ini, angka cakupan dapat mencapai 100% sementara berkas berisiko tinggi belum pernah dibedah.

→ Pelanggaran: **`AUDIT_INCOMPLETE_COVERAGE_BIAS`** → **laporan DITOLAK**. Akibat wajib (identik dengan LANGKAH 4a): (a) Ringkasan Eksekutif DILARANG ditulis seolah audit selesai; (b) eksekusi dikembalikan ke Fase 1/Fase 2; (c) temuan yang sudah ada tetap disimpan sebagai hasil sementara, DILARANG dihapus; (d) baris status wajib `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`, bukan `PASS`.

**Larangan pelarian wadah (#11b).** Memindahkan lead dari `07` ke `08` (`LOW_NUISANCE`/`ADMIN_ONLY`/`PRE_LIVE_SCOPE`) **hanya sah bila mekanismenya sudah terbukti secara mekanis** (PoC jalan tanpa curang + dampak kuantitatif terukur). Lead yang **belum teruji** lalu dilabeli Low = melanggar #11 dengan cara lain: `07` mensyaratkan bukti usaha, `08` mensyaratkan bukti mekanisme — **tidak ada wadah yang boleh menampung lead yang belum dikerjakan**. Bila ragu antara `07` dan `08`, lead itu masih `07` dan wajib `PERCOBAAN:`.

**Target akhir `07` = 0 entri.** Setiap sisa wajib dipertahankan dengan log komputasi, bukan kalimat.

**Hubungan dengan Aturan Anti-False-Negative:** #11 adalah cermin dari aturan tersebut. Anti-false-negative melarang menyimpulkan *"aman"* dari data kosong; #11 melarang menyimpulkan *"belum bisa diuji"* tanpa percobaan. Keduanya menolak kesimpulan yang lebih murah daripada pekerjaannya.

---

## ATURAN ANTI-FALSE-NEGATIVE (wajib dipatuhi)

Pelanggaran aturan ini pernah menghasilkan satu temuan High **palsu** yang nyaris dikirim.

1. **Kegagalan query ≠ ketiadaan data.** `status: 0` dari explorer (mis. *"Free API access is not supported for this chain"*), timeout RPC, atau `eth_getLogs` yang dibatasi rentang **bukan** bukti bahwa data tidak ada. Wajib diulang lewat sumber lain (RPC lain, endpoint arsip, explorer lain) sebelum menyimpulkan.
2. **Perilaku off-chain tidak otomatis "tidak dapat diuji".** Sebelum menulis "butuh repo privat", coba rekonstruksi dari event on-chain (mis. `RootBundleExecuted`, `RequestedSlowFill`, `FilledRelay`, `WithdrawRewards`, `RoleGranted`).
3. **Oracle eksistensi murah lebih dulu.** Untuk ID sekuensial (`depositId`, nonce, `rootBundleId`), `numberOfDeposits()`/hitung log memberi batas eksistensi tanpa perlu memindai seluruh history.
4. **Decode calldata produksi** untuk menguji batas kepercayaan (parameter committed vs submitter-supplied), sebelum menyimpulkan sebuah jalur terbuka atau tertutup.

---

## TANGGA BUKTI (wajib dicantumkan pada setiap verdict)

| Tingkat | Jenis bukti | Boleh menopang |
|---|---|---|
| **A** | `Mode Uji: FORK` terhadap bytecode ter-deploy, tanpa cheatcode, output `[PASS]` | hingga `09` |
| **B** | `Mode Uji: LOKAL` dengan kontrak asli (fork tidak mungkin, alasan dinamai) | hingga `08` |
| **C** | Bukti **struktural** (baca kode + `eth_call`), atau **mock pihak ketiga** | hingga `07` |
| **D** | Asumsi/analogi tanpa eksekusi | `06` (bukan temuan) |

---

## KELAS VERDICT & PEMETAAN WADAH

| Verdict | Ketegasan | Kriteria | Wadah |
|---|---|---|---|
| `VALID_ELIGIBLE` | Lolos 11 pernyataan | Fork PASS + tanpa curang + bahaya finansial nyata (Critical/High/Medium) | `09-confirmed-findings.md` |
| `VALID_NOT_ELIGIBLE` | Dalam batasan (#7b, #8b, #10b) | Mekanisme nyata, dampak Low/annoying, admin-only, atau belum live | `08-valid-not-eligible.md` |
| `NEEDS_NEXT_STEP` | Dalam batasan eksplorasi (#9b) | Logika kuat, butuh fork/verifikasi mainnet/RPC; atau klaim `HEAD-only` — **wajib `Disposition:` + blok `PERCOBAAN:`** | `07-needs-next-step.md` |
| `LAZY_BAILOUT_DETECTED` | **Penolakan laporan (#11)** | Entri `07` tanpa bukti usaha: `TOOL_BLOCKED` tanpa log 3-Step Self-Healing, `NEXT_MAINNET` padahal RPC tersedia, `NEXT_EXPLORE` tanpa log fuzzer/halmos mentok timeout, atau label basi | **DITOLAK** → kembali ke Fase 3 |
| `AUDIT_INCOMPLETE_COVERAGE_BIAS` | **Penolakan laporan (#11d)** | Cakupan `[MUST-AUDIT]` < 80% di domain mana pun, berkas terbesar per domain `BELUM`, domain 0%, gate pemetaan < 100%, atau `ATTESTED_CLEAN` tanpa `File:Baris` | **DITOLAK** → kembali ke Fase 1/2 |
| `REJECTED_POC_FAILS` | Gugur mutlak (#9a) | PoC gagal kompilasi / revert di state nyata | `06-refuted-invalid.md` |
| `REJECTED_FANTASY_MOCK` | Gugur mutlak (#1) | Sifat palsu pada token Kasta 1 / parameter ter-whitelist | `06-refuted-invalid.md` |
| `REJECTED_CHEATCODE` | Gugur mutlak (#9a) | `vm.store`/`vm.etch`/`vm.prank(admin)`/fisika rantai dilanggar | `06-refuted-invalid.md` |
| `REJECTED_GENESIS_MIRAGE` | Gugur mutlak (#3) | `totalSupply == 0` pada pool live / ber-dead-shares | `06-refuted-invalid.md` |
| `REJECTED_PRIVILEGED_FANTASY` | Gugur mutlak (#8a) | Mengandalkan admin/keeper bodoh-jahat atau oracle rusak sendiri | `06-refuted-invalid.md` |
| `REJECTED_NON_LIVE_INIT` | Gugur mutlak (#7a) | Menyerang `initialize()` yang sudah terkunci | `06-refuted-invalid.md` |
| `REJECTED_NO_VICTIM` | Gugur mutlak (#4) | Korban menyabotase diri sendiri; atau hanya pool penyerang | `06-refuted-invalid.md` |
| `REJECTED_DUST` | Gugur mutlak (#10a) | Debu 1 wei–beberapa sen tanpa amplifikasi & tanpa penguncian dana | `06-refuted-invalid.md` |
| `REJECTED_NEGATIVE_EV` | Gugur mutlak (#5) | Modal hangus > kerugian korban, tanpa keuntungan | `06-refuted-invalid.md` |
| `REJECTED_BY_DESIGN` | Gugur mutlak (#6) | Perilaku didokumentasikan sebagai disengaja | `06-refuted-invalid.md` |
| `REJECTED_MISMATCH` | Gugur mutlak (#6) | Baris kode tidak mendukung klaim | `06-refuted-invalid.md` |
| `REJECTED_UNPROVEN_DEPLOYMENT` | Gugur mutlak (#2) | Klaim produksi dipaksakan padahal kode ter-deploy tidak terbukti sama | `06-refuted-invalid.md` |
| **`AUDIT_INCOMPLETE_COVERAGE_BIAS`** | **Pembatalan laporan (#4a)** | Domain kosong, berkas `BELUM`, cakupan < 80%, atau audit memakai sampel | **Bukan wadah** — laporan DITOLAK, kembali ke Fase 1/2 |
| **`LAZY_BAILOUT_DETECTED`** | **Pembatalan laporan (#11)** | Entri `07` tanpa blok `PERCOBAAN:` / log Tangga Self-Healing / bukti RPC tidak tersedia | **Bukan wadah** — laporan DITOLAK, `07` dikembalikan ke Fase 3 |

---

## FORMAT KELUARAN

```text
ID                : <id_lead_atau_kandidat>
VERDICT           : <kelas_verdict>
TARGET_FILE       : <09-confirmed-findings.md | 08-valid-not-eligible.md | 07-needs-next-step.md | 06-refuted-invalid.md>
ALASAN            : <1-2 kalimat tegas, merujuk nomor Pernyataan (1-11) dan File:Baris>
BUKTI             : <Mode Uji FORK/LOKAL + hasil eksekusi, atau sumber on-chain>
TANGGA_BUKTI      : <A | B | C | D>
DEPLOYMENT_MATCH  : <sha256 sama | source explorer cocok | BEDA -> HEAD-only | tidak terverifikasi (sebut sumber yang gagal)>
BIAYA-BACA        : <jumlah baris yang dibaca>
```

Untuk verdict pembatalan laporan (`AUDIT_INCOMPLETE_COVERAGE_BIAS`, `LAZY_BAILOUT_DETECTED`), `TARGET_FILE` diisi `LAPORAN_DITOLAK` dan `ALASAN` wajib menyebut domain/entri `07` yang bermasalah, bukan nomor Pernyataan.

---

## LAMPIRAN — Peta Penomoran Lama → Baru

| Lama | Isi | Baru |
|---|---|---|
| #1 | Keaslian Entitas & Aset | **#1** |
| — | *(baru)* Kesetiaan Deployment | **#2** |
| #3 | Keadaan Likuiditas Nyata | **#3** |
| #6 | Korban Rasional | **#4** |
| #8 | Kelayakan Ekonomi | **#5** |
| #10 | Presisi Bukti & Bukan Desain | **#6** |
| #2 | Status Live & Inisialisasi | **#7** |
| #4 | Kemurnian Aktor Eksternal | **#8** |
| #5 | Kejujuran Sandbox & Fork | **#9** |
| #7 + #9 | Bahaya Finansial + Kalibrasi Severity | **#10** (digabung) |

## CATATAN MIGRASI WADAH

Protokol ini memakai penomoran wadah `06/07/08/09`. Audit yang masih memakai skema lama (`07-confirmed-findings.md`) wajib dipetakan:

- `07-confirmed-findings.md` (lama) → **`09-confirmed-findings.md`**
- `06-unproven-needs-review.md` (lama) → dipecah: bukti kuat-tapi-belum-fork → **`07-needs-next-step.md`**; mekanisme nyata-tapi-Low → **`08-valid-not-eligible.md`**; gugur → **`06-refuted-invalid.md`**
