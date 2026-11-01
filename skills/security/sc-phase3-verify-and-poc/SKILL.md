---
name: sc-phase3-verify-and-poc
description: Phase 3 — Method-Routed Pre-PoC Triage (Methods 1-10 & POV), 6-Tier Local Fork Exploit Simulation, and Pure Staging Distribution (06, 07, 09).
version: 5.1.0
---

# Phase 3: Pre-PoC Sanity Check & Local Fork Exploit Simulation

Tujuan Fase 3 adalah menguji setiap hipotesis di audit/05-raw-leads.md dengan menjalankan saringan cepat berbasis metode (Langkah 0–1) lalu simulasi transaksi eksploitasi nyata di sandbox lokal/fork tanpa kecurangan, dan mendistribusikannya secara terpisah ke audit/06-refuted-invalid.md, audit/07-needs-next-step.md, atau audit/09-confirmed-findings.md.

---

## Langkah 1: Saringan Fakta Keras Pra-PoC (Hemat Token — WAJIB Sebelum Menulis Kode PoC!)

**Langkah 0 — Routing berdasarkan Metode Pencarian (wajib, sebelum 4 saringan).**
Baca kolom `Metode Pencarian` dan `Delta State` pada lead di `audit/05-raw-leads.md`. Kolom itu bukan hiasan: ia menentukan uji termurah yang harus dijalankan lebih dulu, sehingga Anda tidak menulis PoC penuh untuk lead yang bisa digugurkan dengan satu pemeriksaan cepat:
- `[POV-03]` (self-liquidation / bad debt): hitung dulu pertidaksamaan `total Collateral_Tersita >= Bonus_Liquidator + Utang_Dihapus` memakai angka parameter live. Jika ruas kiri menang di semua kondisi batas -> lead **Negative-EV**, langsung ke `06` tanpa menulis PoC.
- `[POV-01]` (desinkronisasi indeks akrual): cek apakah fungsi pemindah menyinkronkan indeks untuk **from DAN to** sebelum saldo berubah. Jika ya -> `06` (Batas Realitas katalog terpenuhi).
- `[POV-02]` (state desync saat callback): cek apakah benar ada kontrak/fungsi lain yang membaca rasio mid-tx. Jika tidak ada pembaca eksternal -> tidak ada korban -> `06`.
- `[Metode 3]` (irrational 2-wallet): PoC WAJIB memakai dua dompet milik penyerang dalam satu transaksi; PoC satu-dompet tidak membuktikan apa pun.
- `[Metode 4]` (patch-scar / view-vs-write): jika klaim adalah desinkronisasi view vs write, pastikan ada fungsi tulis/eksternal yang benar-benar memanggil fungsi view tersebut untuk mengambil keputusan finansial; jika hanya untuk tampilan UI murni tanpa dampak on-chain -> `06` / `08`.
- `[Metode 5]` (guard-inversion): guard sudah dianalisis di Putaran 2. Jika tidak ada fungsi publik yang bisa menggeser variabel pembentuk guard -> `06`.
- `[Metode 6]` (memory cache overwrite / duplicate-array `[A, A]`): (a) untuk cache overwrite, pastikan baris akhir fungsi benar-benar menulis balik struct memori ke storage setelah panggilan yang mengubah storage tersebut; (b) untuk duplicate-array, cek apakah sudah ada deduplikasi (`ids[i] < ids[i+1]` / bitmap). Jika sudah ada -> `06`; jika belum -> PoC cukup 1 transaksi dengan array `[id, id]`.
- `[Metode 7]` (metamorphic split-vs-bulk): hitung selisih maksimum `N x aksi(kecil)` vs `1 x aksi(besar)` dalam batas gas 1 blok. Jika total selisih yang bisa diekstrak lebih kecil dari biaya gas + fee protokol -> gugur sebagai `REJECTED_DUST` / `REJECTED_NEGATIVE_EV` ke `06`.
- `[Metode 8]` (caller-callee seam / direct pool bypass): cek modifier akses pada fungsi kontrak hilir (Pool/Vault/Strategy). Jika sudah dikunci `onlyRouter`/`onlyManager` yang tidak bisa ditembus -> `06`; jika terbuka -> PoC wajib memanggil kontrak hilir secara langsung.
- `[Metode 9]` (half-baked / suspended lifecycle): cek apakah Langkah 1 (`request`/`createOrder`/`initiate`) sudah langsung mengurangi/mengunci saldo yang bisa ditransfer/dipinjam. Jika sudah dikunci penuh -> `06`; jika belum -> PoC wajib mengeksekusi urutan Langkah 1 (Gantung) -> Aksi Sampingan (Transfer/Borrow) -> Langkah 2.
- `[Metode 10]` (live on-chain residue / allowance / upgrade drift): sebelum menulis kode tes Foundry, jalankan query `cast call` / cek storage pada RPC produksi (`./rpc-env.sh`). Jika di state mainnet nyata tidak ada saldo mengendap, tidak ada *allowance* aktif ke kontrak tersebut, atau slot storage proxy sudah terinisialisasi benar -> langsung buang ke `06` tanpa menulis PoC.
Jika kolom `Metode Pencarian` tidak ada pada sebuah lead, catat di `audit/notes/` dan minta Fase 2 melengkapinya — jangan menebak metode.

Sebelum menghabiskan token menulis kode simulasi tes untuk sebuah Lead di audit/05-raw-leads.md, periksa 4 Kemustahilan Fakta Dasar berikut (rujuk audit/00-project-map.md dan audit/01-threat-and-env.md). Jika jawaban dari SALAH SATU pertanyaan ini adalah YA, jangan tulis PoC — langsung buang ke `audit/06-refuted-invalid.md`:

1. Halusinasi Token/Kontrak (Langgar Kasta Aset): Apakah Lead ini mengasumsikan Token Kasta 1 (LP Token, Share/Receipt Token, WETH, Token Internal) memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau gagal mengembalikan bool ala USDT? Atau menganggap USDT mainnet memotong pajak transfer (fee > 0)? Atau menyuntikkan kontrak palsu ke parameter yang dikunci oleh *Factory/Whitelist*?
2. Ilusi Kolam Kosong pada Pool Live: Apakah Lead ini membutuhkan totalSupply == 0 (*First Depositor Attack*) pada Vault/Pool yang di produksi sudah *live* memiliki TVL atau sudah mencetak *dead shares* saat deploy, tanpa ada cara menguras pool ke nol terlebih dahulu?
3. Fungsi Sudah Terkunci / Non-Live: Apakah Lead ini menyerang fungsi initialize() yang di produksi sudah dieksekusi saat deployment, atau menyerang modul yang dimatikan permanen di produksi?
4. Ketergantungan Aksi Admin / Korban Bunuh Diri: Apakah Lead ini mengharuskan Owner/Admin/Keeper memasukkan konfigurasi bunuh diri, mengasumsikan *feed* Chainlink rusak sendiri, atau mengharuskan korban mematikan pelindungnya sendiri (minAmountOut = 0 / kirim token langsung via ERC20.transfer)?

*(Catatan Penting: Untuk Lead yang berkaitan dengan pembulatan matematika, akrual indeks, atau DoS yang lolos Langkah 0 dan ke-4 saringan fakta di atas, JANGAN dibuang di Langkah 1 — wajib jalankan simulasi di Langkah 2 dan coba lipat gandakan dampaknya terlebih dahulu!)*

---

## Langkah 2: Simulasi Eksploitasi di Sandbox Lokal & Pemilihan Mesin 6-Tier (Deterministic vs Nondeterministic)
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
1. **Simulasi Local Fork WAJIB** bila chain target memiliki RPC publik: Jalankan simulasi transaksi PoC di komputer lokal dengan menyalin state blok produksi (`forge test -j 1 --fork-url <RPC> --fork-block-number <N>`, gunakan `./rpc-env.sh`, tanpa `--broadcast`).
2. Di dalam simulasi fork tersebut, attacker bebas mengeksekusi transaksi serangan penuh terhadap kontrak target, namun hanya boleh didanai lewat `deal` pada dompet attacker **SENDIRI** atau lewat flashloan nyata. DILARANG mengubah storage protokol dengan `vm.store` atau `vm.etch`.
3. Jika RPC chain target tidak tersedia atau kontrak belum dapat dijangkau fork, temuan DILARANG masuk `09` — simpan ke `audit/07-needs-next-step.md` dengan label `NEXT_MAINNET` atau `TOOL_BLOCKED`.
4. Jika simulasi fork berjalan namun transaksi eksploitasi revert terhadap state nyata = gugur ke `audit/06-refuted-invalid.md`.
5. Setiap entri di `09` dan `07` WAJIB mencantumkan baris `Mode Uji: FORK (chain, block, RPC)` atau `Mode Uji: LOKAL (alasan fork belum dilakukan)`.
6. **Identitas deployment (rujuk `verify/VERDICT.md` Langkah 0):** sebelum entri masuk `09`, pastikan kode yang diserang = kode yang berjalan (source terverifikasi explorer / `sha256` sama). Jika berbeda, entri wajib ditandai `HEAD-only` dan hanya boleh berada di `07`.

---

## Langkah 3: Distribusi Hasil Simulasi ke 3 Wadah Murni (06, 07, atau 09)
1. **Simulasi Fork PASS + Membuktikan Dampak Nyata:**
   Tulis ke `audit/09-confirmed-findings.md` lengkap dengan kode PoC utuh, baris `Mode Uji: FORK (...)`, perhitungan dampak/profit, dan log terminal (untuk selanjutnya diadili oleh Hakim `VERDICT.md` di Fase 4).
2. **Secara Logika Kode Kuat namun Belum Selesai Dibuktikan:**
   Tulis ke `audit/07-needs-next-step.md` dengan mencantumkan salah satu label disposisi berikut:
   - `Disposition: NEXT_EXPLORE` -> Simulasi PoC sederhana belum tembus, butuh metode eksplorasi lanjut (Stateful Invariant Fuzzing Tier 2, Symbolic Proving Halmos Tier 5, atau multi-step chaining).
   - `Disposition: NEXT_MAINNET` -> Simulasi lokal PASS, tetapi butuh verifikasi parameter/storage/proxy di mainnet atau penyesuaian blok fork.
   - `Disposition: TOOL_BLOCKED` -> Terhalang ketiadaan RPC publik, masalah kompilasi dependency eksternal, atau keterbatasan harness lokal.
3. **Gagal di Langkah 0/1 ATAU Simulasi PoC Gagal (`revert`) di State Nyata:**
   Tulis ke `audit/06-refuted-invalid.md` beserta alasan teknisnya (sertakan `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH` sesuai template `06`), dan hapus file test sementara yang gagal agar folder test/ tetap bersih.
