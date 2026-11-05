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

## LANGKAH 0 — Rekonsiliasi Siklus Deployment & Kesetaraan Entrypoint (Gerbang Eksklusif Fase 4)

Tujuan: memisahkan temuan yang sudah terbukti secara mekanis di Fase 3 menjadi tiga jalur akhir: **Produksi Aktif** (`09`), **Pre-Live / Testnet / Entrypoint Relocated** (`08`), atau **Sudah Dipatch** (`06`) — berdasarkan **pengukuran**, bukan asumsi.

> **Penting:** Pengecekan ini adalah **wewenang eksklusif Hakim Fase 4**. Fase 3 **dilarang** menghentikan penulisan PoC hanya karena kontrak belum *live* atau versi repo berbeda.

> **Alat wajib:** seluruh Langkah 0 dijalankan lewat `verify/tools/deploy_parity.py` (bukan penilaian manual). Jalankan dengan `--out` agar artefak JSON tersimpan di `audit/notes/`. Aturan "bytecode harus identik" **DILARANG** dipakai: setiap repo punya siklus rilis berbeda dan build Foundry jarang reproducible. Yang diuji adalah **keberadaan & perilaku entrypoint yang diserang PoC**, bukan hash file.

### 0.0 — Gerbang Siklus (satu perintah per kontrak)

```bash
python3 verify/tools/deploy_parity.py --paradigm <evm|solana|sui|aptos|ton|generic|<plugin>> \
  --chain <mainnet|testnet|local> --addr <ALAMAT> --rpc <RPC> \
  --entrypoints "<signature yang diserang PoC>" --repo <path repo> \
  --out audit/notes/deploy-parity-<ID>.json
```

| Siklus | Kondisi | Konsekuensi |
|---|---|---|
| `P1_PRE_DEPLOY` | `cast code` = `0x` / akun tidak ada | **DILARANG** menjalankan pemeriksaan entrypoint; PoC tetap wajib (`LOKAL`/`FORK_DEPLOYED_HEAD`) → **`08`** |
| `P2_TESTNET_ONLY` | kode ada, chainId = testnet | bukti `TANGGA_BUKTI: B` → **`08`** |
| `P3_LIVE_PARTIAL` | kode ada di mainnet, sebagian entrypoint tidak terbukti | lanjut 0.1 & 0.2 |
| `P4_LIVE_FULL` | semua entrypoint PoC terbukti ada | kandidat **`09`** |

### 0.1 — Empat Pra-Syarat Wajib (sebelum menyimpulkan apa pun)

1. **Proxy** — baca slot EIP-1967 impl (`0x360894a1…2bbc`), beacon (`0xa3f0ad74…3d50`), admin (`0xb5312768…6103`). Bila proxy: analisis **implementation**, bukan proxy. `deploy_parity` melakukannya otomatis.
2. **Fallback-router** — bila probe mengembalikan custom error `MissingFallbackHandler` (selector `0x08c63e27`), entrypoint hidup di **handler**, bukan di kontrak titik serang → verdict `RELAYED_VIA_HANDLER`.
3. **Library / delegatecall** — bila entrypoint hidup di callee, T2/T3 wajib dijalankan pada **callee**, dan fakta itu dicatat di artefak.
4. **Multi-kontrak (router → hub → allocator)** — untuk attack-chain, **setiap** kontrak yang menjadi entrypoint lingkup temuan wajib diperiksa T2/T3 **terpisah**; satu artefak JSON per kontrak.

### 0.2 — Lima Verdict Entrypoint (jangan disatukan)

| Verdict | Arti | Wadah |
|---|---|---|
| `LIVE_MATCH` | entrypoint PoC terbukti ada & berperilaku sama di objek live | **`09`** |
| `HEAD_ONLY_PROVEN` | siklus P1, atau live tak tersedia | **`08`** `PRE_LIVE_SCOPE` |
| `TESTNET_ONLY` | siklus P2 | **`08`** `TESTNET_ONLY` |
| `ENTRYPOINT_RELOCATED` | entrypoint ada di handler/callee, bukan kontrak titik serang | **`08`** + catatan rute |
| `REGRESSION_FIXED` | live lulus & PoC di HEAD gagal (**dua-arah**, dua log) | **`06`** `REJECTED_BY_DESIGN` |
| `ENV_ERROR` / `UNVERIFIABLE` | RPC gagal 2×, rate-limit, revert tak terklasifikasi | **`07`** `TOOL_BLOCKED` |
| `IDENTITY_ONLY` | rantai belum dikenal / entrypoint tak terbaca otomatis | **`07`** `NEXT_EXPLORE` |

### 0.2b — Aturan Penempatan: `08` HANYA untuk PoC yang Sudah `[PASS]`

`08-valid-not-eligible.md` berarti **"valid tetapi tidak eligible"** — jadi **validitasnya sudah dibuktikan** oleh PoC `[PASS]`. **DILARANG** menempatkan temuan di `08` bila PoC belum/tidak bisa dijalankan.

| PoC sudah `[PASS]`? | Rantai/objek terdeteksi? | Wadah | Catatan severity |
|---|---|---|---|
| ✅ PASS | ❌ live tak terdeteksi, **tetapi** bisa dijalankan LOKAL/`FORK_DEPLOYED_HEAD` | **`08`** `PRE_LIVE_SCOPE` | **severity utuh (High tetap High)** |
| ✅ PASS | ✅ live | **`09`** | severity utuh |
| ❌ belum bisa dijalankan (RPC mati, endpoint tak dikenal, toolchain absen) | ❌ | **`07`** | **severity utuh — ditulis lengkap, hanya belum diuji** |
| ❌ dijalankan & gagal (3-Stage Breaker) | — | `06` | — |

**Konsekuensi penting:** rantai yang tidak terdeteksi **BUKAN** alasan menaruh temuan di `08`. Bila PoC tetap bisa dijalankan secara lokal atas kode repo (`LOKAL` / `FORK_DEPLOYED_HEAD`) dan `[PASS]` → `08` sah. Bila PoC **tidak dapat dijalankan sama sekali** (mis. `cargo-build-sbf` absen di ARM64) → **`07` `TOOL_BLOCKED`**, bukan `08`, bukan `06`.

**Severity tidak berubah di jalur mana pun.** Temuan High yang masuk `07` karena `TOOL_BLOCKED` **tetap ditulis High** — wadah `07` hanya menandai "belum tuntas diuji", bukan "kurang berbahaya".

**Aturan keras anti-false-negative:**

- `ENTRYPOINT_ABSENT` **HANYA** sah bila seluruh metode gagal **dan** ada bukti tambahan (`git log -S` tidak menemukan fungsi tersebut). Untuk paradigma `generic`, `ABSENT` **DILARANG MUTLAK** — gunakan `IDENTITY_ONLY`.
- `ENV_ERROR` **tidak pernah** menjadi bukti ketiadaan. Rate-limit TON, 403 RPC, atau timeout **bukan** "fungsi tidak ada".
- `HEAD_FIXED` / `REGRESSION_FIXED` wajib disertai **dua log eksekusi** (live PASS + HEAD FAIL). Tanpa itu → `ENV_ERROR`.
- Setiap artefak wajib memuat `live_identity` terukur (mis. `accountId()` = `biconomy.nexus.1.3.3`, atau `sha256(ProgramData)` untuk Solana). **Tanpa identitas terukur, `LIVE_MATCH` ditolak.**

### 0.3 — Severity DITENTUKAN oleh Impact, BUKAN oleh Siklus (DUA SUMBU ORTOGONAL)

`SEVERITY` dan `ELIGIBILITY` adalah dua sumbu terpisah dan **tidak boleh** dikalikan atau saling menurunkan.

| `SEVERITY` (dari impact saja) | Kriteria |
|---|---|
| Critical | Pencurian dana tanpa syarat / cetak dana tak terbatas |
| High | Pencurian bersyarat / pembekuan permanen / insolvensi |
| Medium | Kerugian terbatas / DoS yang mengunci dana / penalti paksa |
| Low | DoS sementara tanpa kerugian |
| Info | Tanpa dampak finansial |

**LARANGAN KERAS:** menurunkan `SEVERITY` karena alasan deployment (HEAD-only / testnet / belum deploy). Temuan Critical yang terbukti hanya di HEAD **tetap ditulis "Critical"** meski ditempatkan di `08`.

| Severity | Eligibility | Wadah | Label di entri |
|---|---|---|---|
| Critical / High | `LIVE_MATCH` | `09` | Critical / High |
| Critical / High | `HEAD_ONLY_PROVEN` | **`08`** | **Critical / High (tetap!)** |
| Critical / High | `ENV_ERROR` / `IDENTITY_ONLY` | **`07`** | **Critical / High (tetap!)** |
| Medium | `LIVE_MATCH` | `09` | Medium |
| Medium | `TESTNET_ONLY` | `08` | Medium |
| Low | `LIVE_MATCH` | `09` / `06` | Low |

**Dua wadah yang mengubah penempatan tanpa mengubah severity:** `08` (valid tapi belum live) dan `07` (belum tuntas diuji). Keduanya **mempertahankan label keparahan apa adanya**.

### 0.4 — Bila `DEPLOYMENT_MATCH` ≠ `LIVE_MATCH` padahal alamat live tersedia

**DILARANG** langsung menggeser ke `08`. Wajib:

1. Catat `RECHECK_REQUIRED` di artefak beserta `commit_ref` (HEAD) dan `nearest_tag`.
2. Kembalikan entri ke Fase 3 untuk **satu putaran PoC kedua** yang menembak **objek live** (lewat Factory resmi, atau `vm.etch` bytecode live yang dicatat sebagai deviasi).
3. Baru setelah putaran kedua itu, bila tetap tidak cocok, entri masuk `08` dengan `LOW_CLASS: PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`.

---

## LANGKAH 1 — Jalankan & Periksa Bukti Simulasi PoC (baik untuk `09`, `08`, maupun `06`)

- Untuk kandidat **`09` & `08`**: PoC wajib dapat dikompilasi dan menghasilkan `[PASS]` (membuktikan invarian patah) pada `FORK_LIVE`, `FORK_DEPLOYED_HEAD`, atau `LOKAL` (khusus non-EVM / rantai tanpa RPC).
- Untuk entri penolakan di **`06`** (`REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, `REJECTED_DUST`):
  - PoC hanya sah dinyatakan gagal (`REJECTED_POC_FAILS`) atau merugi (`REJECTED_NEGATIVE_EV` / `REJECTED_DUST`) apabila di dalam entri `06` dilampirkan **bukti eksekusi simulasi nyata** (log terminal yang menjalankan *Victim Seeding* + *3-Way Amplification* + Strike 3 Fuzzing `testFuzz_`/`proptest`/`halmos`).
  - Menolak lead ke `06` hanya dengan hitungan/argumen teks di atas kertas tanpa log eksekusi test adalah pelanggaran **`PAPER_REFUTATION_DETECTED`** (Pernyataan #11e) → **laporan DITOLAK** dan lead dikembalikan ke Fase 3!
- **Output test kosong bukan bukti kegagalan maupun keamanan.** Pastikan pola pencarian benar (`--match-contract` memakai **nama kontrak**, bukan nama berkas; jalankan `forge test --list` lebih dulu).

---

## LANGKAH 2 — Audit Kejujuran PoC (Anti-Cheatcode & Anti-Fantasy-Mock)

1. **Cheatcode terlarang**: `vm.prank` sebagai admin/owner/pool/keeper, `vm.store`, `vm.etch` state protokol, `deal` ke kontrak protokol, `vm.warp` lintas waktu tak wajar, reentrancy lewat `.transfer()` (2300 gas) → `REJECTED_CHEATCODE` → `06-refuted-invalid.md`.
   - Pengecualian yang sah: `vm.deal` ke **dompet penyerang/pelaku uji**; `vm.prank` sebagai **EOA tanpa hak** (penyerang maupun korban `victim`); `vm.warp` / `vm.roll` **maju secara monoton (ke masa depan)** dalam rentang operasional wajar protokol (melewati durasi *cooldown*, *epoch*, *vesting*, *timelock*, lelang, atau akrual bunga normal — yang **dilarang** hanyalah memutar waktu **mundur** atau melompat puluhan/ratusan tahun secara absurd); `vm.prank(keeper/operator/relayer)` **HANYA** untuk mengeksekusi langkah operasional normal/rutin guna membuktikan bahwa aksi *permissionless* penyerang sebelumnya telah berhasil merusak akuntansi atau mem-brick (DoS) fungsi berizin tersebut; serta `vm.etch` **lingkungan predeploy** pada uji lokal (wajib dicatat sebagai deviasi).
   - *(Pengecualian #9a-iii — Permission yang Tidak Bisa Dimanipulasi: `vm.prank(keeper)` / `vm.prank(relayer)` / `vm.prank(solver)` / `vm.prank(operator)` **SAH dan WAJIB** dipakai untuk memicu fungsi rutin berizin secara normal, asalkan **seluruh state yang dibaca fungsi tersebut diracuni lebih dulu oleh aktor tak berizin tanpa cheatcode** (*Unprivileged State Poisoning* — Jalur 3). Penyerang sebenarnya adalah pemanggil permissionless yang meracuni state; prank hanya mensimulasikan aktor rutin yang menjalankan tugasnya secara wajar. PoC **WAJIB** mendokumentasikan rangkaian: (a) aksi tak berizin yang meracuni antrean/saldo/state, lalu (b) pemanggilan rutin sebagai Keeper/Relayer yang memicu kebocoran nilai atau DoS revert. Prank sebagai Keeper untuk **mengarang** state (bukan memicunya setelah poisoning) TETAP `REJECTED_CHEATCODE`.)*
2. **Fantasy mock**: mengarang sifat Token Kasta 1 (LP Token, Vault Share, Receipt Token, WETH, token internal) berupa Fee-on-Transfer/Rebase/Callback/gagal-bool, menganggap USDT mainnet memotong fee, atau menyuntikkan kontrak jahat ke parameter yang dikunci Factory/Whitelist → `REJECTED_FANTASY_MOCK`.
   - *(Catatan Penting Anti-False-Negative: Menguji quirk nyata dari token **Kasta 2** yang memang didukung protokol — seperti USDT non-zero `approve` revert, USDC/USDT blacklist DoS, stETH 1-wei transfer rounding, PAXG transfer fee, atau ekstensi SPL Token-2022 — adalah **FAKTA PRODUKSI** yang sah dan **DILARANG divonis sebagai `REJECTED_FANTASY_MOCK`!*)*
3. **Mock-driven verdict & Pengecualian Simulasi Lintas-Rantai (Bridge/Precompile)**:
   - Mock bebas terhadap **komponen protokol/bridge pihak ketiga** (CCTP `MessageTransmitter`, LayerZero endpoint, Wormhole, precompile) yang mengarang payload mustahil **tanpa membuktikan bahwa payload tersebut dapat dihasilkan dari transaksi pengguna tak berizin di rantai asal (Chain A)** hanya boleh menopang bukti **STRUKTURAL (Tingkat C)** dan **dilarang** menaikkan verdict ke `09`.
   - **PENGECUALIAN SAH (Berhak Tingkat A -> `09-confirmed-findings.md`):** Apabila PoC membuktikan bahwa penyerang tak berizin dapat:
     *(a)* Memanggil fungsi pengirim di rantai asal (Chain A) untuk menghasilkan *payload/message* yang sah secara aturan jembatan, lalu meneruskan *payload* persis tersebut melalui alamat Endpoint/Transmitter resmi di rantai tujuan (Chain B) menggunakan `vm.prank(officialEndpoint)` untuk membuktikan cacat pemrosesan di kontrak penerima (`lzReceive` / `receiveMessage` / `handle`); **ATAU**
     *(b)* Memanggil fungsi `retryPayload` / `clear` / `execute` publik pada Endpoint/jembatan **asli** yang sudah ter-deploy di fork; **ATAU**
     *(c)* Menguji respons kontrak terhadap output standar precompile sesuai spesifikasi teknis rantai target;
     maka simulasi tersebut **BUKAN Fantasy Mock**, melainkan pembuktian mekanis yang **SAH untuk `09-confirmed-findings.md`!**

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
| **Gerbang Fase 2** | **= 100%** berkas `[MUST-AUDIT]` per domain berstatus `LEAD_GENERATED` atau `ATTESTED_CLEAN` (**0** berkas `BELUM` / `DIBACA` / `DEFERRED`) | `audit/03-attack-surface-queue.md` |
| **Gerbang Fase 4** | **= 100%** berkas `[MUST-AUDIT]` per domain berjejak, **0** berkas `BELUM` / `DIBACA` / `DEFERRED` di seluruh domain | tabel cakupan di `03` |

**DILARANG memakai "jumlah lead per domain" sebagai metrik kelulusan.** Kuota lead memicu pembuatan lead sampah pada modul yang memang aman (hukum Goodhart). Kelulusan diukur dari **jejak per berkas**, bukan banyaknya hipotesis.

### Kondisi pembatalan — `AUDIT_INCOMPLETE_COVERAGE_BIAS`

> **Rujukan silang:** status vonis & akibatnya di tingkat laporan juga dicatat di **Pernyataan #11d**. Bila ada perbedaan redaksi antara bagian ini dan #11d, **bagian ini (LANGKAH 4a) yang menang**.

Vonis ini dijatuhkan bila **salah satu** terpenuhi:

1. Ada domain `D1..Dn` tanpa berkas `[MUST-AUDIT]` sama sekali di antrean (domain kosong / tidak terwakili).
2. Ada berkas `[MUST-AUDIT]` berstatus `BELUM`, atau berstatus `DICAKUP_U1/U10/S-xx` tanpa uji spesifik.
3. Ada domain dengan cakupan **< 100%** pada Gerbang Fase 2.
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
> *(Catatan Anti-False-Negative #1b — Cross-Whitelist Confusion & Callback Initiator: Menyuntikkan kontrak/pool/token yang **MEMANG TERDAFTAR SAH** di dalam Factory/Whitelist produksi tetapi dipakai pada pasangan aset/pasar yang **salah** karena ketiadaan validasi ikatan aset di kode (Cross-Whitelist Confusion), **ATAU** memicu Pool/Vault/Endpoint produksi **asli** agar memanggil callback kontrak target karena ketiadaan validasi `initiator == address(this)`, adalah **100% eksploitasi nyata** (`VALID_ELIGIBLE` -> `09`) dan **DILARANG KERAS divonis sebagai `REJECTED_FANTASY_MOCK`!*)*

**2. Kesetiaan Deployment & Pemisahan Live vs Repo-HEAD (Deployment Fidelity)**
> *"Untuk masuk ke `09-confirmed-findings.md`, kode yang diserang wajib terbukti eksis dan aktif pada deployment produksi (`LIVE_MATCH`). Apabila PoC eksploitasi berhasil (`[PASS]`) membuktikan kerentanan nyata pada kode repositori (`FORK_DEPLOYED_HEAD` / `LOKAL`), namun kontrak/fitur tersebut masih berstatus `HEAD-only` (belum di-deploy ke mainnet atau berbeda dari bytecode produksi aktif), temuan tersebut **WAJIB disimpan secara utuh** di `08-valid-not-eligible.md` dengan kelas `PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` — bukan dipaksakan ke `09` dan bukan diparkir di `07`."*
→ Pelanggaran (memaksakan kode HEAD-only sebagai `09` produksi aktif tanpa cek deployment): `REJECTED_UNPROVEN_DEPLOYMENT` — atau turunkan dari `09` ke `08` [`PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`] bila PoC-nya valid.

> *(Catatan Anti-False-Negative #2b — Deployment Fidelity Berbasis Entrypoint, BUKAN Bytecode Identik: `LIVE_MATCH` **TIDAK BOLEH** dituntut sebagai "bytecode identik". Setiap repo punya siklus rilis berbeda (live bisa v1.3.3 sementara repo HEAD v1.2.1) dan build Foundry jarang reproducible (metadata hash, optimizer, versi solc). Yang wajib diuji adalah **keberadaan dan perilaku entrypoint yang diserang PoC** pada objek live — lewat `verify/tools/deploy_parity.py` (Gerbang Siklus 0.0 → pra-syarat 0.1 → lima verdict 0.2). Menolak temuan karena "ukuran bytecode berbeda" atau "sha256 tidak sama" adalah `REJECTED_MISMATCH` yang SALAH dan dilarang.)*

> *(Catatan Anti-False-Negative #2c — `ENV_ERROR` Bukan Bukti Ketiadaan: rate-limit RPC, HTTP 403, timeout, atau `revert 0x` yang tidak terklasifikasi **DILARANG** dijadikan dasar menyimpulkan "fungsi tidak ada di produksi". Verdict yang sah adalah `ENV_ERROR` → `07 TOOL_BLOCKED` dengan `PERCOBAAN:` berisi minimal dua percobaan endpoint. Khusus paradigma `generic` (rantai belum dikenal), verdict `ABSENT` **DILARANG MUTLAK**; gunakan `IDENTITY_ONLY`.)*

**3. Keadaan Likuiditas Nyata (No Empty-Pool Mirage)**
> *"Eksploitasi terbukti berhasil pada keadaan TVL dan likuiditas nyata di produksi, bukan mengandalkan `totalSupply == 0` / First Depositor Attack pada pool yang sudah live atau sudah mencetak dead shares saat deploy — kecuali PoC membuktikan penyerang mampu membuat pool resmi baru secara permissionless atau menguras TVL ke nol lebih dulu."*
→ `REJECTED_GENESIS_MIRAGE`

**4. Korban Rasional & Dampak Eksternal (Rational Victim)**
> *"Serangan merugikan dana protokol atau pengguna lain yang bertindak rasional (memakai parameter perlindungan normal), bukan mengharuskan korban mematikan pelindungnya sendiri (`minAmountOut = 0`, `deadline = max`, mengirim token via `ERC20.transfer` di luar jalur deposit), dan bukan hanya merusak pool terisolasi milik penyerang."*
→ `REJECTED_NO_VICTIM`
> *(Catatan Anti-False-Negative #4b — Attacker Donation vs Victim Mistake: Larangan "mengirim token via `ERC20.transfer` di luar jalur deposit" **HANYA berlaku jika hipotesis mengharuskan KORBAN** berbuat bodoh membuang tokennya sendiri. Apabila **PENYERANG** (`attacker`) yang sengaja mengirim token via `ERC20.transfer` / donasi langsung ke kontrak untuk memanipulasi akuntansi `balanceOf(address(this))`, menggagalkan guard kesamaan saldo (*strict balance equality DoS*), atau menyela alur resmi *push-then-sync* / distribusi reward sebelum disinkronkan, itu adalah **100% serangan valid** (`VALID_ELIGIBLE` -> `09`) dan **DILARANG KERAS divonis sebagai `REJECTED_NO_VICTIM`!*)*

**5. Kelayakan Ekonomi Serangan (Positive-EV / Cost Asymmetry)**
> *"Serangan menghasilkan keuntungan finansial bersih (Profit > gas + modal hangus) **atau** sanggup membekukan dana protokol/korban bernilai besar secara permanen dengan biaya sangat murah."*
→ `REJECTED_NEGATIVE_EV`

**6. Presisi Bukti Kode & Bukan Desain Sengaja (Code & Design Match)**
> *"Rentang `File:Baris` yang dikutip adalah akar masalah sesungguhnya, dan perilakunya tidak didokumentasikan sebagai mekanisme yang disengaja protokol."*
→ `REJECTED_MISMATCH` (baris tidak cocok) / `REJECTED_BY_DESIGN` (disengaja)
- *(Peringatan Keras Anti-False-Negative pada `REJECTED_BY_DESIGN`: Komentar NatSpec/README yang **sekadar mendeskripsikan rumus atau alur fungsi BUKAN bukti** bahwa dampak eksploitasinya disengaja! **DILARANG KERAS** menjatuhkan vonis `REJECTED_BY_DESIGN` apabila penyerang tak berizin dapat menyalahgunakan mekanisme tersebut untuk mencuri dana (*Positive-EV theft*), menciptakan kredit macet/insolvensi, atau membekukan dana pengguna secara permanen — **kecuali** dokumentasi resmi secara eksplisit menulis bahwa risiko kehilangan dana/eksploitasi spesifik tersebut memang diketahui dan diterima sebagai *trade-off*!)*

### B. EMPAT PERNYATAAN HIBRIDA & BERBATAS (Bounded Threshold — memisahkan 06, 07, 08, 09)

**7. Status Live Produksi & Siklus Hidup Inisialisasi (Scope & Lifecycle)**
> *"Kontrak dan cabang fitur yang diserang termasuk cakupan aktif di produksi, dan tidak menyerang `initialize()` sekali-pakai yang sudah terkunci rapat tanpa jalur re-inisialisasi."*
- Menyerang `initialize()` yang sudah dieksekusi dan dikunci di produksi (dan kontrak implementation juga sudah dikunci `_disableInitializers()`) → **[KETAT]** `REJECTED_NON_LIVE_INIT` → `06-refuted-invalid.md`
- Mekanisme eksploitasi nyata dan PoC terbukti `[PASS]` (`FORK_DEPLOYED_HEAD` / `LOKAL`), tetapi kontrak/fitur masih pre-live (`HEAD-only`), paused, atau berada di repositori namun belum masuk daftar alamat halaman bounty → **`VALID_NOT_ELIGIBLE [PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN]`** → `08-valid-not-eligible.md` *(wajib menyertakan kode PoC utuh & log `[PASS]`)*.

**8. Kemurnian Aktor Eksternal (Unprivileged External Path)**
> *"Seluruh langkah eksploitasi dapat dijalankan penyerang tak berizin dari awal hingga akhir, tanpa mengandalkan tindakan jahat/bodoh Admin/Owner/DAO/Keeper, dan bukan bug khusus fungsi admin tanpa jalur eksternal."*
- Mengasumsikan admin memasukkan konfigurasi bunuh diri **di luar batas normal**, atau mengasumsikan penyedia Oracle eksternal (Chainlink/Pyth) **meretas dirinya sendiri** dan mengirim harga bohong → **[KETAT]** `REJECTED_PRIVILEGED_FANTASY` → `06`. *(Peringatan: Apabila Oracle eksternal mengembalikan data **normal/jujur**, namun kontrak protokol **salah mengonversi desimal** harga oracle, **salah membaca field `updatedAt`/staleness**, atau **salah menghitung rumus batas harga/LTV**, itu adalah **Bug Kode Kontrak yang VALID (`09`)**, BUKAN "oracle rusak sendiri"!)*
- Bug mekanis nyata pada fungsi **khusus admin** tanpa jalur eksploitasi eksternal (`admin-only bug with no external exploit path`) → **`VALID_NOT_ELIGIBLE [ADMIN_ONLY]`** → `08` *(bukan `06` — ini Low, bukan gugur)*
- *(Catatan Anti-False-Negative pada Fungsi Ber-Permission Statis: Apabila fungsi yang rusak/bocor dilindungi oleh permission yang tidak bisa dimanipulasi (`onlyRouter`, `onlyKeeper`, `onlyOperator`, `onlyHub`), namun pemicu akarnya **100% dilakukan oleh penyerang tak berizin** (`unprivileged external actor`) — baik melalui pemanggilan kontrak hulu yang sah maupun melalui manipulasi state/likuiditas/antrean publik yang membuat eksekusi rutin Keeper/Operator membekukan dana atau salah menghitung nilai — maka temuan tersebut **MEMENUHI Pernyataan #8 sepenuhnya** (`VALID_ELIGIBLE` -> `09`) dan **DILARANG divonis sebagai `REJECTED_PRIVILEGED_FANTASY` maupun `ADMIN_ONLY`!*)*

**9. Kejujuran Sandbox & Bukti Fork Produksi (Sandbox & Fork Integrity)**
> *"PoC dapat direproduksi dan menghasilkan `[PASS]` pada `FORK_LIVE`, `FORK_DEPLOYED_HEAD`, atau `LOKAL` (non-EVM / rantai tanpa RPC) tanpa memalsukan storage internal, dan mematuhi fisika gas/mempool rantai target."*
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
  1. **DoS with No Fund Loss** — transaksi hanya revert **sementara sekali waktu**; pengguna cukup mengirim ulang atau memakai jalur alternatif **tanpa kehilangan pokok/yield/hak** dan **tanpa bisa diblokir ulang terus-menerus secara murah** oleh penyerang. *(Peringatan: Apabila penyerang dapat mem-frontrun/me-reset kondisi secara berulang dengan biaya murah sehingga pengguna **terkunci secara efektif**, memblokir fungsi keselamatan berbatas waktu seperti `repay`/`liquidate`, **ATAU** memaksa pengguna keluar lewat `emergencyWithdraw` yang menghanguskan yield/mengenakan penalti/potongan pokok, maka itu adalah **Bahaya Finansial Nyata (HIGH/MEDIUM -> `09`)**, BUKAN `LOW_NUISANCE`!)*
  2. **Minor Capped Economic Damage** — kerugian kecil dan terbatas (*bounded*), tidak dapat menguras pool.
  3. **Nuisance Griefing** — memaksa gas ulang / mereset timer non-finansial, tanpa keuntungan penyerang dan tanpa pembekuan dana.
  → **`VALID_NOT_ELIGIBLE [LOW_NUISANCE]`** → `08-valid-not-eligible.md`
- Klaim HIGH/MEDIUM tetapi bukti hanya kelas Low atau admin-only → **turunkan ke LOW (S4)** dan pindahkan `09` → `08`.

> *(Catatan Anti-False-Negative #10b — Severity DITENTUKAN Impact, BUKAN Siklus Deployment: `SEVERITY` dan `ELIGIBILITY` adalah **dua sumbu ortogonal** dan DILARANG dikalikan. Menurunkan severity karena alasan "masih HEAD-only", "hanya testnet", atau "belum di-deploy" adalah pelanggaran berat. Temuan yang terbukti mencuri dana tanpa syarat **tetap `Critical`** meski harus ditempatkan di `08` dengan `PRE_LIVE_SCOPE`. Yang berubah karena siklus hanyalah **wadah** (`09` vs `08`), **bukan label keparahan**. Penurunan severity hanya sah bila bukti impact-nya sendiri lebih kecil (dana terbukti kecil, atau butuh korban bertindak bodoh).)*

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

> *"Cakupan berkas `[MUST-AUDIT]` yang berstatus `LEAD_GENERATED` atau `ATTESTED_CLEAN` mencapai **100% di setiap domain**, tanpa berkas yang masih berstatus `BELUM`, `DIBACA`, maupun `DEFERRED`."*

Hakim **WAJIB** menghitung sendiri dari `00b-file-inventory.md` × `03-attack-surface-queue.md`, bukan mempercayai tabel cakupan yang ditulis pelaksana.

**Syarat tolak (salah satu saja cukup):**
1. Cakupan `[MUST-AUDIT]` berstatus `LEAD_GENERATED` / `ATTESTED_CLEAN` **< 100%** pada domain mana pun (termasuk sisa berkas `DIBACA` atau `DEFERRED`).
2. Ada berkas `[MUST-AUDIT]` berstatus `BELUM`, atau berstatus `DICAKUP_U1/U10/S-xx` tanpa uji spesifik.
3. Ada domain `D1..Dn` tanpa berkas `[MUST-AUDIT]` sama sekali di antrean (domain kosong / tidak terwakili).
4. Audit memakai sampel, bukan populasi penuh yang terdaftar di `00b-file-inventory.md` (gate pemetaan < 100%).

**Atestasi hampa tidak dihitung sebagai jejak (#11c):** `ATTESTED_CLEAN` yang tidak memuat `File:Baris` konkret per fungsi yang diperiksa — atau yang bersandar hanya pada volume (`forge build`/`cargo test` PASS, jumlah berkas, `N/N PASS`, nama unit `S-0n`) — **DIBATALKAN**. Berkas tersebut dikembalikan ke `BELUM` **sebelum** persentase dihitung. Tanpa aturan ini, angka cakupan dapat mencapai 100% sementara berkas berisiko tinggi belum pernah dibedah.

→ Pelanggaran: **`AUDIT_INCOMPLETE_COVERAGE_BIAS`** → **laporan DITOLAK**. Akibat wajib (identik dengan LANGKAH 4a): (a) Ringkasan Eksekutif DILARANG ditulis seolah audit selesai; (b) eksekusi dikembalikan ke Fase 1/Fase 2; (c) temuan yang sudah ada tetap disimpan sebagai hasil sementara, DILARANG dihapus; (d) baris status wajib `COVERAGE: AUDIT_INCOMPLETE_COVERAGE_BIAS`, bukan `PASS`.

**Larangan pelarian wadah (#11b).** Memindahkan lead dari `07` ke `08` (`LOW_NUISANCE`/`ADMIN_ONLY`/`PRE_LIVE_SCOPE`) **hanya sah bila mekanismenya sudah terbukti secara mekanis** (PoC jalan tanpa curang + dampak kuantitatif terukur). Lead yang **belum teruji** lalu dilabeli Low = melanggar #11 dengan cara lain: `07` mensyaratkan bukti usaha, `08` mensyaratkan bukti mekanisme — **tidak ada wadah yang boleh menampung lead yang belum dikerjakan**. Bila ragu antara `07` dan `08`, lead itu masih `07` dan wajib `PERCOBAAN:`.

**Target akhir `07` = 0 entri.** Setiap sisa wajib dipertahankan dengan log komputasi, bukan kalimat.

**11e. Larangan Penolakan Kertas Tanpa Bukti Simulasi (`PAPER_REFUTATION_DETECTED`) — laporan DITOLAK, dikembalikan ke Fase 3**

> *"Setiap entri di `06-refuted-invalid.md` yang menyandang vonis `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, atau `REJECTED_DUST` **WAJIB** memuat blok `BUKTI_SIMULASI:` berisi perintah test yang benar-benar dijalankan beserta log terminalnya — termasuk bukti telah dilakukannya *Victim Seeding* dan minimal 1× eksekusi Fuzzing (`testFuzz_` / `proptest` / `halmos`) pada Strike 3. Penolakan tanpa kode test hanya diizinkan untuk 4 Kemustahilan Statis Sempit (`REJECTED_FANTASY_MOCK`, `REJECTED_GENESIS_MIRAGE` pada pool tunggal terkunci, `REJECTED_NON_LIVE_INIT` yang terkunci, `REJECTED_PRIVILEGED_FANTASY` di luar batas validasi, `REJECTED_MISMATCH`, dan `REJECTED_BY_DESIGN`)."*

→ Pelanggaran: **`PAPER_REFUTATION_DETECTED`** → **laporan DITOLAK**, entri `06` yang bermasalah dikembalikan ke Fase 3 untuk dibuatkan simulasi PoC/Fuzz-nya.

**Hubungan dengan Aturan Anti-False-Negative:** #11 adalah cermin dari aturan tersebut. Anti-false-negative melarang menyimpulkan *"aman"* dari data kosong; #11 melarang menyimpulkan *"belum bisa diuji"* tanpa percobaan; #11e melarang menyimpulkan *"gugur"* tanpa eksekusi. Ketiganya menolak kesimpulan yang lebih murah daripada pekerjaannya.

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
| **A** | `Mode Uji: FORK_LIVE` terhadap bytecode produksi ter-deploy, tanpa cheatcode, output `[PASS]` | hingga `09` |
| **A-HEAD** | `Mode Uji: FORK_DEPLOYED_HEAD` (kontrak repo di-deploy di atas fork mainnet nyata, `[PASS]`, tanpa cheatcode) | `09` (bila kode identik dgn live) atau `08` [`PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN`] (bila kode belum live) |
| **B** | `Mode Uji: LOKAL` dengan kontrak asli (khusus non-EVM `cargo test`/`sui move test`/`@ton/sandbox`, atau rantai tanpa RPC) | hingga `09` (non-EVM kode cocok live) atau `08` (EVM tanpa RPC / HEAD-only) |
| **C** | Bukti **struktural** (baca kode + `eth_call`), atau **mock pihak ketiga** | maksimal `07` (dengan `PERCOBAAN:`) atau `06` (untuk salah baca statis) |
| **D** | Asumsi/hitungan kertas **tanpa eksekusi test** | **TIDAK SAH** untuk `09`/`08`/`07` maupun untuk `06` (`POC_FAILS`/`NEGATIVE_EV`/`DUST`) → memicu `PAPER_REFUTATION_DETECTED` |

---

## KELAS VERDICT & PEMETAAN WADAH

| Verdict | Ketegasan | Kriteria | Wadah |
|---|---|---|---|
| `VALID_ELIGIBLE` | Lolos 11 pernyataan | Fork PASS + tanpa curang + bahaya finansial nyata (Critical/High/Medium) | `09-confirmed-findings.md` |
| `VALID_NOT_ELIGIBLE` | Dalam batasan (#7b, #8b, #10b) | Mekanisme nyata & PoC PASS, dampak Low/annoying, admin-only, atau `HEAD_ONLY_PROVEN` | `08-valid-not-eligible.md` |
| `NEEDS_NEXT_STEP` | Dalam batasan eksplorasi (#9b) | Logika kuat tetapi pengujian **belum tuntas** — **wajib `Disposition:` + blok `PERCOBAAN:`** | `07-needs-next-step.md` |
| `PAPER_REFUTATION_DETECTED` | **Penolakan laporan (#11e)** | Entri `06` (`REJECTED_POC_FAILS`/`REJECTED_NEGATIVE_EV`/`REJECTED_DUST`) tanpa log eksekusi test + Strike 3 Fuzz | **DITOLAK** → kembali ke Fase 3 |
| `LAZY_BAILOUT_DETECTED` | **Penolakan laporan (#11)** | Entri `07` tanpa bukti usaha: `TOOL_BLOCKED` tanpa log 3-Step Self-Healing, `NEXT_MAINNET` padahal RPC tersedia, `NEXT_EXPLORE` tanpa log fuzzer/halmos mentok timeout, atau label basi | **DITOLAK** → kembali ke Fase 3 |
| `AUDIT_INCOMPLETE_COVERAGE_BIAS` | **Penolakan laporan (#11d)** | Cakupan `[MUST-AUDIT]` **< 100%** di domain mana pun, sisa berkas `BELUM`/`DIBACA`/`DEFERRED`, domain 0%, gate pemetaan < 100%, atau `ATTESTED_CLEAN` tanpa `File:Baris` | **DITOLAK** → kembali ke Fase 1/2 |
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
ALASAN            : <1-2 kalimat tegas, merujuk nomor Pernyataan (1-11) dan File:Baris>
BUKTI             : <Mode Uji FORK_LIVE/FORK_DEPLOYED_HEAD/LOKAL + hasil eksekusi, atau sumber on-chain>
TANGGA_BUKTI      : <A | A-HEAD | B | C | D>
DEPLOYMENT_MATCH  : <LIVE_MATCH | HEAD-only (PROVEN_ON_REPO_HEAD) | UNVERIFIED (sebut sumber yang gagal)>
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
