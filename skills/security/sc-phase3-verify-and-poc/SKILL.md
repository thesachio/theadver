---
name: sc-phase3-verify-and-poc
description: Phase 3 — Method-Routed Pre-PoC Triage (Methods 1-10 & POV), 6-Tier Local Fork Exploit Simulation, and Pure Staging Distribution (06, 07, 09).
version: 6.0.0
---

# Phase 3: Pre-PoC Sanity Check & Local Fork Exploit Simulation

Tujuan Fase 3 adalah menguji setiap hipotesis di audit/05-raw-leads.md dengan triage batch berbasis metode, lalu simulasi transaksi eksploitasi nyata di sandbox lokal/fork tanpa kecurangan, dan mendistribusikannya secara terpisah ke audit/06-refuted-invalid.md, audit/07-needs-next-step.md, atau audit/09-confirmed-findings.md.

---

## Langkah 0b: Anti-Rabbit-Hole — 2-Strike Circuit Breaker (WAJIB, berlaku sepanjang Fase 3)

Aturan ini mengikat **setiap lead** di `audit/05-raw-leads.md` dan berlaku sebelum, selama, dan sesudah Langkah 1–3.

### 1. Hitungan Strike
Strike dihitung **per lead**, bukan per berkas dan bukan per sesi:
- **Strike 1** — percobaan PoC pertama gagal: `revert` karena guard yang sah, `assert` ekspektasi tidak terpenuhi, **atau** selisih profit negatif / nol.
- **Strike 2** — percobaan perbaikan pertama juga gagal dengan sebab yang sama.

> Perbaikan **infrastruktur** (compile error, import salah, checksum alamat, salah ABI, salah offset decode) **BUKAN strike** — itu kegagalan alat, bukan kegagalan hipotesis. Aturan ini menjaga kasus "revert karena salah pakai `makeAddr`" agar tidak membuang lead yang sebenarnya benar.

### 2. Aksi Wajib pada Strike Kedua
Setelah **2 strike berturut-turut pada lead yang sama** — **maksimal 2 percobaan gagal per hipotesis** — agen **WAJIB**:
1. Berhenti menyentuh lead tersebut.
2. Pindahkan ke `audit/06-refuted-invalid.md` dengan vonis `REJECTED_POC_FAILS` (bukan `07`), mencantumkan **kedua** percobaan beserta alasan teknis kegagalannya.
3. Menulis 1 baris di `audit/notes/fase3-strikes.md`: **"2-STRIKE BREAKER TRIPPED"**, nama lead, dan berkas:baris.
4. **Wajib pindah ke berkas/hipotesis lain** — bukan lanjut ke variasi lain dalam berkas yang sama.

### 3. Larangan Iterasi Ketiga
**DILARANG** melakukan iterasi ke-3 pada berkas/fungsi yang sama sebelum **seluruh lead lain di `05-raw-leads.md`** selesai melewati Langkah 1a (batch triage) **dan** pengujian awal (maksimal 1 strike masing-masing).

Lead boleh **dibuka kembali** hanya bila ada **bukti baru yang material**:
- state on-chain nyata yang belum dibaca sebelumnya (membantah asumsi strike sebelumnya),
- source terverifikasi explorer yang berbeda dari asumsi kode,
- kombinasi *chaining* dengan lead **lain** yang sudah lolos uji awalnya.

Ide baru, sudut pandang baru, atau "coba saja cara lain" **BUKAN** bukti material dan tidak membuka kunci.

### 4. Anggaran Waktu per Lead
Sebelum meninggalkan satu lead, catat di `audit/notes/fase3-strikes.md` berapa **jumlah percobaan** dan **berapa berkas lain yang masih `BELUM`** di `00b-file-inventory.md`. Bila percobaan > 3 sementara berkas `BELUM` masih > 0, itu pelanggaran aturan dan wajib dilaporkan sebagai kegagalan proses.

### 5. Format Pencatatan Strike
```
<LEAD-ID> | <berkas:baris> | Strike 1: <sebab> | Strike 2: <sebab> | STATUS: TRIPPED/BELUM
```
Lead tanpa entri strike berarti belum diuji sama sekali — bukan berarti bersih.

---

## Langkah 0c: Anti-Menyerah #1 — Tangga Self-Healing Tooling (Syarat Mutlak Sebelum `TOOL_BLOCKED`)

Label `TOOL_BLOCKED` **DILARANG** dipakai untuk masalah kompilasi dependency, remapping, versi compiler, atau kegagalan test runner repo target. Kondisi itu bukan batas ekplorasi — itu pekerjaan yang belum dikerjakan.

Jika build/test bawaan repo bermasalah, agen **WAJIB** menaiki tangga eskalasi mandiri berikut secara berurutan, dan mencatat hasil tiap anak tangga di `audit/notes/`:

### Usaha 1 — Perbaikan Konfigurasi Lokal Sementara
Sesuaikan flag eksekusi sebelum menyimpulkan apa pun:
- Compiler/optimizer: `--via-ir`, `--optimize`, `--optimize-runs`, `--evm-version`.
- Remappings: lewat command line atau `foundry.toml` **terisolasi di folder test**, jangan mengubah konfigurasi repo target.
- Dependency: instal paket yang kurang bila environment mengizinkan.
- Non-EVM: `cargo-build-sbf` (bukan `cargo build --release`), `anchor build`, `anchor test --skip-local-validator`.
- Versi toolchain: bila repo mengunci versi tertentu, pakai `rust-toolchain.toml` / `foundry.toml` terpisah, bukan menimpa milik repo.

### Usaha 2 — Standalone Minimal Harness / Interface-Only Test
Jika _seluruh_ repo gagal dikompilasi karena satu sub-modul rusak, **JANGAN menyerah**. Buat **1 file test mandiri** yang:
- hanya mendeklarasikan `interface` kontrak target (signature fungsi yang diserang saja), **atau**
- hanya mengimpor 1–2 berkas kontrak relevan tanpa seluruh pohon dependency,

lalu tembak langsung alamat kontraknya di Local Fork, atau deploy kontrak tunggal tersebut di sandbox terisolasi. Untuk non-EVM: harness program tunggal + akun uji, tanpa workspace penuh.

Pola ini sudah terbukti: kendala workspace bisa dilewati dengan interface-only + fork call, dan hasilnya tetap sah selama `Mode Uji: FORK` dan tanpa cheatcode.

### Usaha 3 — Fallback RPC & Off-Chain State Read
Jika satu URL RPC gagal / rate-limited / membatasi `eth_getLogs`:
- baca seluruh variabel di `./rpc-env.sh` dan `.env.rpc`, cek `RPC-STATUS.md`,
- gunakan endpoint publik alternatif yang sah untuk rantai tersebut,
- untuk rentang log besar, pakai chunking + binary search alih-alih menyerah,
- bila data memang off-chain, lakukan rekonstruksi dari event on-chain lebih dulu sebelum menyatakan butuh repo privat.

### Hukum Besi `TOOL_BLOCKED`
Sebuah lead **HANYA sah** masuk `07` dengan label `TOOL_BLOCKED` jika **ketiga** usaha di atas sudah dijalankan **dan log terminal kegagalannya dilampirkan di dalam entri `07`** (perintah yang dijalankan + pesan error apa adanya).

> Mengklaim "masalah kompilasi dependency" tanpa mencoba *Standalone Interface / Minimal Harness* adalah **pelanggaran konstitusi**. Entri `07` tanpa lampiran log ketiga usaha ditolak dan lead dikembalikan ke antrean.

**Bukan `TOOL_BLOCKED`** (jangan salah label): hipotesis yang sudah diuji dan ditolak alam → `06` `REJECTED_POC_FAILS`; alat yang belum terpasang tetapi bisa dipasang → tetap di antrean, bukan `07`.

---

## Langkah 0d: Anti-Menyerah #2 — Hukum "Kerjakan Sekarang" (Anti-Procrastination `NEXT_MAINNET` & `NEXT_EXPLORE`)

`NEXT_MAINNET` dan `NEXT_EXPLORE` adalah **tempat parkir untuk hal yang mustahil dilakukan sekarang** — bukan untuk hal yang belum dikerjakan. Keduanya DILARANG dipakai selama pekerjaan itu **bisa diselesaikan pada sesi ini juga**.

### 1. Larangan `NEXT_MAINNET` Malas
**DILARANG** menulis `Disposition: NEXT_MAINNET` dengan alasan *"butuh cek parameter/storage/proxy di mainnet"* bila RPC rantai tersebut **tersedia**. RPC publik bukan hambatan — gunakan langsung:
```bash
cast call <addr> "<sig>" --rpc-url <RPC>
cast storage <addr> <slot> --rpc-url <RPC>
cast implementation <proxy> --rpc-url <RPC>      # EIP-1967
cast admin <proxy> --rpc-url <RPC>
curl -s <RPC> -d '{"jsonrpc":"2.0",...}'
```
Lalu **tuntaskan vonis pada sesi yang sama**: ke `09` bila terbukti dan eligible, atau `06` bila terbantah. Membaca state live adalah pekerjaan menit, bukan pekerjaan minggu.

**`NEXT_MAINNET` hanya sah bila:** kontrak belum di-deploy sama sekali, atau rantai target benar-benar tidak punya akses RPC/explorer publik (dan Usaha 3 Langkah 0c sudah gagal dengan log).

### 2. Larangan `NEXT_EXPLORE` Malas
**DILARANG** menulis `Disposition: NEXT_EXPLORE` dengan alasan *"butuh multi-step chaining"*, *"butuh Stateful Fuzzing"*, atau *"butuh Halmos"* bila yang sudah dicoba baru **satu skenario sederhana**. Agen **WAJIB langsung menulis dan menjalankan** pada sesi yang sama:
- **Multi-step chaining** — rangkai ≥2 aksi/lead dalam satu transaksi atau satu blok.
- **Differential Test (Tier 3)** — bandingkan jalur A vs jalur B yang seharusnya setara.
- **Handler Fuzzing (Tier 2)** — invariant handler + `foundry.fuzz.runs` yang wajar.
- **Symbolic proving (Tier 5)** bila invariant bersifat aritmetis (`halmos --function check_*`).

`NEXT_EXPLORE` **hanya sah** bila tes di atas sudah **dijalankan** (lampirkan perintah + keluarannya) dan mencapai **timeout komputasi tanpa konklusi** — bukan karena belum dicoba.

### 3. Hukum Besi untuk Kedua Label
Setiap entri `07` berlabel `NEXT_MAINNET` atau `NEXT_EXPLORE` **WAJIB** memuat **bukti percobaan** berupa blok:
```
PERCOBAAN:
  <perintah yang dijalankan>
  <keluaran / error / statistik fuzz / waktu timeout>
HASIL: masih terbuka karena <sebab yang tidak bisa diselesaikan sekarang>
```
Entri tanpa blok `PERCOBAAN` **ditolak** dan lead dikembalikan ke antrean untuk dikerjakan.

> Beda tegas: **`NEXT_EXPLORE` bukan `07` versi sopan dari `06`.** Bila setelah fuzzing/chaining hasilnya tetap negatif, lead pindah ke `06` `REJECTED_POC_FAILS` — bukan dibiarkan menggantung di `07`.

---

## Langkah 0e: Anti-Salah-Alamat — Isolasi Lapisan Sebelum Menyalahkan Target

**Hukum Dasar:** sebelum menyatakan *tool rusak*, *target rentan*, atau *vendor tidak mendukung*, wajib membuktikan **lapisan mana** yang gagal. Kegagalan pada rantai `kode → dependency → kompiler → toolchain → emulasi → OS/disk` hampir selalu berada di lapisan **paling bawah** yang belum diperiksa.

**DILARANG** menulis "bug X", "tidak didukung", atau "tidak ada workaround" tanpa salah satu bukti:
- log `df`/`free`/`ldd`/`file` yang membuktikan lapisan bawah sehat,
- reproduksi terisolasi yang gagal **tanpa** melibatkan kode target,
- pembanding yang berhasil (eksperimen kontrol).

**Eksperimen kontrol wajib:** setiap kegagalan build harus disandingkan dengan target yang **seharusnya berhasil**. Kontrol gagal → masalah tool/lingkungan. Kontrol berhasil → masalah kode.

Tangga isolasi 7 lapisan (disk → arsitektur → library → kompiler anak → integritas artefak → memori → kode target), contoh kasus nyata, dan format pencatatan: `references/ref-layer-isolation.md`. Baca file itu sebelum menyalahkan alat mana pun.

---

## Langkah 1: Saringan Fakta Keras Pra-PoC (Hemat Token — WAJIB Sebelum Menulis Kode PoC!)

### Langkah 1a: Triage BATCH Seluruh Lead (Anti-FIFO, sebelum PoC apa pun)
**DILARANG** menulis kode PoC sebelum **seluruh** lead di `audit/05-raw-leads.md` melewati Langkah 0 (routing metode + 4 Kemustahilan Fakta) secara **batch**.

Prosedur:
1. Tabel-kan semua lead: `ID | Berkas:Baris | Metode/POV | Hasil Langkah 0 | Keputusan`.
2. Jalankan pemeriksaan termurah untuk **setiap** lead — tanpa menulis satu baris Solidity pun.
3. Lead yang gugur langsung ke `06-refuted-invalid.md` (`REJECTED_MISMATCH` / `REJECTED_BY_DESIGN` / `REJECTED_NO_VICTIM` / dst.) beserta buktinya.
4. Baru setelah tabel tuntas, lead yang tersisa masuk antrean PoC.

**Alasan:** lead paling menarik perhatian bukan berarti lead paling berharga. Triage batch memastikan keputusan "mana yang layak di-PoC" diambil dengan pandangan penuh, bukan karena kebetulan dibaca lebih dulu.

### Langkah 1b: Routing berdasarkan Metode Pencarian (wajib, sebelum 4 saringan)
Baca kolom `Metode Pencarian` dan `Delta State` pada lead di `audit/05-raw-leads.md`. Kolom itu bukan hiasan: ia menentukan uji termurah yang harus dijalankan lebih dulu, sehingga Anda tidak menulis PoC penuh untuk lead yang bisa digugurkan dengan satu pemeriksaan cepat:
- `[POV-DEFI-01]` (self-liquidation / bad debt): hitung dulu pertidaksamaan `total Collateral_Tersita >= Bonus_Liquidator + Utang_Dihapus` memakai angka parameter live. Jika ruas kiri menang di semua kondisi batas -> lead **Negative-EV**, langsung ke `06` tanpa menulis PoC.
- `[POV-MATH-01]` (desinkronisasi indeks akrual): cek apakah fungsi pemindah menyinkronkan indeks untuk **from DAN to** sebelum saldo berubah. Jika ya -> `06`.
- `[POV-CALL-01]` (state desync saat callback): cek apakah benar ada kontrak/fungsi lain yang membaca rasio mid-tx. Jika tidak ada pembaca eksternal -> tidak ada korban -> `06`.
- `[POV-MATH-02]` (exact-input vs exact-output rounding): sandingkan fungsi konversi *Exact-Input* vs *Exact-Output*; hitung $f(a)+f(b)$ vs $f(a+b)$ pada angka batas; bila selisih menguntungkan < 1 wei setelah biaya gas/loop -> `06` (`REJECTED_DUST`).
- `[POV-CALL-02]` (isolated subcall try/catch divergence): cek pengendali alamat target pada panggilan eksternal. Jika target kontrak internal/tetap *immutable* dan tidak meneruskan callback ke alamat pengguna -> langsung ke `06`.
- `[POV-DEFI-02]` (valuation-source vs execution-venue asymmetry): cek modifier akses fungsi pemicu dan rumus batas output minimum (*slippage*). Jika fungsi hanya bisa dipanggil operator tepercaya ATAU batas output dikunci ke harga Oracle dengan toleransi $< 2\times$ biaya swap -> langsung ke `06`.
- `[POV-EVM-01]` (batch delegatecall / msg.value / transient storage reuse): cek apakah fungsi batch benar-benar `payable` dan memakai `delegatecall` (atau tidak me-reset slot transient). Jika multicall tidak `payable` atau target tidak membaca `msg.value` -> `06`.
- `[POV-SOL-01]` (Solana account aliasing / post-CPI stale data): cek apakah ada constraint `key() !=` antar-akun `mut` atau `.reload()?` pasca-CPI. Jika sudah ada -> `06`.
- `[POV-MOVE-01]` (Move cross-object spoofing / bit-shift mask): cek apakah sudah memeriksa `assert!(receipt.pool_id == object::id(pool))` atau batas mask `<<` menolak bit tertinggi. Jika sudah ada -> `06`.
- `[POV-TON-01]` (TON 224-bit bounce truncation / in-flight lock): hitung total bit field sebelum data pemulihan (apakah $\le 224$ bit tanpa `ref`?) atau apakah state dikunci berdasarkan `query_id`. Jika terkunci -> `06`.
- `[Metode 3]` (multi-identity sybil): PoC WAJIB memakai dua identitas/akun/objek yang dikendalikan penyerang dalam satu jendela eksekusi — EVM: dua EOA dalam 1 tx; non-EVM: dua signer, dua capability, atau dua jalur message. PoC satu-identitas tidak membuktikan apa pun.
- `[Metode 4]` (patch-scar / view-vs-write): jika klaim desinkronisasi view vs write, pastikan ada fungsi tulis/eksternal yang benar-benar memanggil fungsi view tersebut untuk keputusan finansial; jika hanya tampilan UI -> `06` / `08`.
- `[Metode 5]` (guard-inversion): guard sudah dianalisis di Putaran 2. Jika tidak ada fungsi publik yang bisa menggeser variabel pembentuk guard -> `06`.
- `[Metode 6]` (stale snapshot write-back / duplicate reference `[A, A]`): (a) pastikan urutan baca-lokal -> mutasi-persisten -> tulis-balik benar-benar terjadi; jika tidak ada tulis-balik setelah interaksi eksternal -> `06`. (b) untuk referensi kembar, cek deduplikasi; jika sudah ada -> `06`; jika belum -> PoC cukup 1 transaksi dengan input kembar `[id, id]`.
- `[Metode 7]` (metamorphic split-vs-bulk): hitung selisih maksimum `N x aksi(kecil)` vs `1 x aksi(besar)` dalam batas gas 1 blok. Jika total selisih lebih kecil dari biaya gas + fee protokol -> `REJECTED_DUST` / `REJECTED_NEGATIVE_EV` ke `06`.
- `[Metode 8]` (caller-callee seam / direct downstream bypass): cek pembatasan caller di komponen hilir **dan** apakah validasi kritis diulang di sana. Jika pembatasan caller sah DAN validasi diulang -> `06`; jika salah satu tidak ada -> PoC wajib memanggil hilir secara langsung.
- `[Metode 9]` (half-baked / suspended lifecycle): cek apakah Langkah 1 (`request`/`createOrder`/`initiate`) langsung mengurangi/mengunci saldo. Jika sudah dikunci penuh -> `06`; jika belum -> PoC wajib mengeksekusi Langkah 1 (Gantung) -> Aksi Sampingan -> Langkah 2.
- `[Metode 10]` (live residual state / delegated authority / post-upgrade drift): sebelum menulis PoC, baca state live lebih dulu. Jika di state produksi tidak ada saldo tertinggal, tidak ada otorisasi tertunda aktif, dan field pasca-upgrade sudah terisi -> langsung buang ke `06` tanpa menulis PoC.

Jika kolom `Metode Pencarian` tidak ada pada sebuah lead, catat di `audit/notes/` dan minta Fase 2 melengkapinya — jangan menebak metode. Jika metodenya ada tetapi **tidak punya rute khusus** (`Metode 1` backward tracing dan `Metode 2` delta analysis memang cara membaca, bukan gerbang), lanjutkan langsung ke 4 Kemustahilan Fakta tanpa mengarang uji tambahan.

### Langkah 1c: 4 Kemustahilan Fakta Dasar
Sebelum menghabiskan token menulis kode simulasi, periksa 4 Kemustahilan Fakta berikut (rujuk `00-project-map.md` dan `01-threat-and-env.md`). Jika jawaban dari SALAH SATU pertanyaan ini adalah YA, jangan tulis PoC — langsung buang ke `audit/06-refuted-invalid.md`:
1. Halusinasi Token/Kontrak (Langgar Kasta Aset): mengasumsikan Token Kasta 1 memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau gagal mengembalikan bool ala USDT? Atau menganggap USDT mainnet memotong pajak transfer? Atau menyuntikkan kontrak palsu ke parameter yang dikunci *Factory/Whitelist*?
2. Ilusi Kolam Kosong pada Pool Live: membutuhkan `totalSupply == 0` pada Vault/Pool yang di produksi sudah *live*, tanpa ada cara menguras pool ke nol terlebih dahulu?
3. Fungsi Sudah Terkunci / Non-Live: menyerang `initialize()` yang di produksi sudah dieksekusi saat deployment, atau menyerang modul yang dimatikan permanen?
4. Ketergantungan Aksi Admin / Korban Bunuh Diri: mengharuskan Owner/Admin/Keeper memasukkan konfigurasi bunuh diri, mengasumsikan *feed* Chainlink rusak sendiri, atau mengharuskan korban mematikan pelindungnya sendiri (`minAmountOut = 0` / kirim token langsung)?

*(Catatan: untuk Lead pembulatan matematika, akrual indeks, atau DoS yang lolos Langkah 0 dan 4 saringan di atas, JANGAN dibuang di Langkah 1 — wajib jalankan simulasi di Langkah 2 dan coba lipat gandakan dampaknya terlebih dahulu!)*

---

## Langkah 2: Simulasi Eksploitasi di Sandbox Lokal & Pemilihan Mesin 6-Tier (Deterministic vs Nondeterministic)

### Urutan Eksekusi PoC — Prioritas EV, BUKAN FIFO
Setelah Langkah 1a lolos, **DILARANG** mengerjakan PoC berdasarkan urutan nomor `LEAD-01, 02, 03`. Urutkan berdasarkan:
1. **Dampak finansial tertinggi (Critical/High EV)** lebih dulu — perkirakan kerugian dalam satuan aset nyata, bukan "seberapa menarik kodenya".
2. **Keterwakilan domain** — pastikan lead dari domain berbeda ikut dieksekusi; jangan habiskan kuota pada satu domain.
3. **Biaya bukti paling murah** pada EV setara — lead yang butuh satu `cast call` didahulukan daripada yang butuh harness baru.

**Batalkan PoC kapan saja** begitu `2-Strike Circuit Breaker` (Langkah 0b) terpicu.

**Pencatatan wajib:** tulis urutan eksekusi beserta alasan EV di `audit/notes/fase3-urutan-poc.md` sebelum mulai. Urutan yang tidak tercatat dianggap FIFO dan melanggar aturan.

Panggil skill_view pada modul referensi pengujian sesuai rantai di 00-project-map.md (`references/ref-test-evm-advanced.md` untuk Tier 1–5, `references/ref-test-multichain-advanced.md` untuk Tier 6 non-EVM Solana/Sui/Aptos/TON), lalu jalankan simulasi (`FOUNDRY_JOBS=1`, `CARGO_BUILD_JOBS=1`, `RAYON_NUM_THREADS=1`):
- **Jalur Deterministic** (Tier 1 Sequence, Tier 4 Local Fork, Tier 5 Symbolic Halmos/Kani): Gunakan untuk membuktikan urutan langkah pasti dari 05-raw-leads.md atau mencari *counterexample* matematis eksak (`halmos --function check_*`).
- **Jalur Nondeterministic** (Tier 2 Handler Stateful Invariant Fuzzing, Tier 3 Round-Trip/Differential Fuzzing): Gunakan untuk mengeksplorasi kandidat `NEXT_EXPLORE` di 07-needs-next-step.md atau menguji Metode 7 (Split-vs-Bulk). Begitu fuzzer menemukan *counterexample*, WAJIB konversikan menjadi tes Deterministic Local Fork (Tier 4)!

**Aturan mutlak penulisan simulasi:**
1. **Larangan Fantasy Mock:** Gunakan kontrak LP/Share/Sistem asli dari repositori. Jika menggunakan MockERC20 untuk aset eksternal pada simulasi lokal, perilakunya WAJIB 100% IDENTIK dengan aset nyata yang diizinkan protokol di produksi.
2. **Inisialisasi Setara Produksi:** Setup awal di dalam setUp() wajib mencerminkan keadaan produksi nyata (sudah terinisialisasi dengan parameter normal dan memiliki likuiditas awal yang wajar).
3. **Larangan Cheatcode Curang:** Hanya gunakan `vm.prank(attacker)` (pengguna eksternal tak berizin). DILARANG menggunakan `vm.prank(admin/owner)`, `vm.store`, `vm.etch`, atau `deal` pada kontrak protokol untuk memalsukan state internal.
4. **Upaya Amplifikasi Dampak:** Jika dampak satu kali transaksi terlihat kecil, simulasikan apakah serangan dapat diulang dalam satu transaksi (*looping / flashloan amplification*) atau dirangkai dengan fungsi lain hingga menghasilkan bahaya finansial nyata.

### Langkah 2b: Simulasi pada Local Fork Produksi (Syarat Mutlak Masuk 09)
`09-confirmed-findings.md` mengklaim bukti terhadap state PRODUKSI nyata. Karena itu:
1. **Simulasi Local Fork WAJIB** bila chain target memiliki RPC publik: Jalankan simulasi transaksi PoC dengan menyalin state blok produksi (`forge test -j 1 --fork-url <RPC> --fork-block-number <N>`, gunakan `./rpc-env.sh`, tanpa `--broadcast`).
2. Di dalam fork tersebut, attacker bebas mengeksekusi transaksi serangan penuh terhadap kontrak target, namun hanya boleh didanai lewat `deal` pada dompet attacker **SENDIRI** atau lewat flashloan nyata. DILARANG mengubah storage protokol dengan `vm.store` atau `vm.etch`.
3. Jika RPC chain target tidak tersedia atau kontrak belum dapat dijangkau fork, temuan DILARANG masuk `09` — simpan ke `audit/07-needs-next-step.md` dengan label `NEXT_MAINNET` atau `TOOL_BLOCKED` **setelah menaiki seluruh Tangga Self-Healing (Langkah 0c)** dan melampirkan log ketiga usaha.
4. Jika simulasi fork berjalan namun transaksi eksploitasi revert terhadap state nyata = gugur ke `audit/06-refuted-invalid.md`.
5. Setiap entri di `09` dan `07` WAJIB mencantumkan baris `Mode Uji: FORK (chain, block, RPC)` atau `Mode Uji: LOKAL (alasan fork belum dilakukan)`.
6. **Identitas deployment (rujuk `verify/VERDICT.md` Langkah 0):** sebelum entri masuk `09`, pastikan kode yang diserang = kode yang berjalan (source terverifikasi explorer / `sha256` sama). Jika berbeda, entri wajib ditandai `HEAD-only` dan hanya boleh berada di `07`.

---

## Langkah 3: Distribusi Hasil Simulasi ke 3 Wadah Murni (06, 07, atau 09)
1. **Simulasi Fork PASS + Membuktikan Dampak Nyata:**
   Tulis ke `audit/09-confirmed-findings.md` lengkap dengan kode PoC utuh, baris `Mode Uji: FORK (...)`, perhitungan dampak/profit, dan log terminal (untuk selanjutnya diadili oleh Hakim `VERDICT.md` di Fase 4).
2. **Secara Logika Kode Kuat namun Belum Selesai Dibuktikan:**
   Tulis ke `audit/07-needs-next-step.md` dengan salah satu label disposisi berikut — **masing-masing tunduk pada Langkah 0c dan 0d**:
   - `Disposition: NEXT_EXPLORE` -> **hanya sah bila Tier 2/3/5 sudah dijalankan** (multi-step chaining, differential, handler fuzzing, halmos) dan mencapai timeout komputasi tanpa konklusi. Wajib lampirkan blok `PERCOBAAN: <perintah> + <keluaran>`. Alasan "butuh multi-step chaining" tanpa percobaan = pelanggaran.
   - `Disposition: NEXT_MAINNET` -> **hanya sah bila** kontrak belum di-deploy atau rantai benar-benar tanpa RPC/explorer publik (Usaha 3 Langkah 0c gagal dengan log). Bila RPC tersedia, DILARANG parkir di sini — jalankan `cast call`/`cast storage`/`cast implementation` saat itu juga dan tuntaskan ke `09` atau `06`.
   - `Disposition: TOOL_BLOCKED` -> **HANYA setelah Tangga Self-Healing Langkah 0c ditempuh penuh** (Usaha 1: flag/remapping/toolchain; Usaha 2: standalone interface-only / minimal harness; Usaha 3: fallback RPC & rekonstruksi off-chain) **dengan log terminal kegagalan ketiganya dilampirkan di entri `07`**. Tanpa lampiran, label ini tidak sah.
3. **Gagal di Langkah 0/1 ATAU Simulasi PoC Gagal (`revert`) di State Nyata:**
   Tulis ke `audit/06-refuted-invalid.md` beserta alasan teknisnya (sertakan `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH` sesuai template `06`), dan hapus file test sementara yang gagal agar folder test/ tetap bersih.
4. **2-Strike Circuit Breaker:** bila percobaan PoC gagal 2 kali berturut-turut pada lead yang sama, butir 3 berlaku **otomatis** dengan label `REJECTED_POC_FAILS` — lead tidak boleh masuk `07` dan tidak boleh diiterasi ke-3. `07` hanya sah untuk lead yang **belum** mencapai 2 strike.
