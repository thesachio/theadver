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
| **Baru** (mulai sekarang) | `00`–`09` (10 file murni): `04-code-guarded` · `05-raw-leads` · `06-refuted-invalid` · `07-needs-next-step` · `08-valid-not-eligible` · `09-confirmed-findings` | 10 Pernyataan + Tangga Bukti + Langkah 0 wajib |
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

## LANGKAH 4 — Gate 10 Pernyataan Wajib

Sebuah temuan HANYA boleh mendapat vonis `VALID_ELIGIBLE` dan bertahan di `audit/09-confirmed-findings.md` bila memenuhi **kesepuluh** pernyataan berikut.

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
- Logika kode + PoC lokal jujur tetapi belum dapat diuji pada fork produksi (RPC/tooling/verifikasi mainnet lanjutan) → **`NEEDS_NEXT_STEP`** → `07-needs-next-step.md`
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
| `VALID_ELIGIBLE` | Lolos 10 pernyataan | Fork PASS + tanpa curang + bahaya finansial nyata (Critical/High/Medium) | `09-confirmed-findings.md` |
| `VALID_NOT_ELIGIBLE` | Dalam batasan (#7b, #8b, #10b) | Mekanisme nyata, dampak Low/annoying, admin-only, atau belum live | `08-valid-not-eligible.md` |
| `NEEDS_NEXT_STEP` | Dalam batasan eksplorasi (#9b) | Logika kuat, butuh fork/verifikasi mainnet/RPC; atau klaim `HEAD-only` | `07-needs-next-step.md` |
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

---

## FORMAT KELUARAN

```text
ID                : <id_lead_atau_kandidat>
VERDICT           : <kelas_verdict>
TARGET_FILE       : <09-confirmed-findings.md | 08-valid-not-eligible.md | 07-needs-next-step.md | 06-refuted-invalid.md>
ALASAN            : <1-2 kalimat tegas, merujuk nomor Pernyataan (1-10) dan File:Baris>
BUKTI             : <Mode Uji FORK/LOKAL + hasil eksekusi, atau sumber on-chain>
TANGGA_BUKTI      : <A | B | C | D>
DEPLOYMENT_MATCH  : <sha256 sama | source explorer cocok | BEDA -> HEAD-only | tidak terverifikasi (sebut sumber yang gagal)>
BIAYA-BACA        : <jumlah baris yang dibaca>
```

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
