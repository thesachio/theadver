---
name: sc-phase3-verify-and-poc
description: Phase 3 — Pre-PoC Fact Sanity Check, Local Fork Exploit Simulation, and Pure Staging Distribution (06, 07, 09).
version: 5.0.0
---

# Phase 3: Pre-PoC Sanity Check & Local Fork Exploit Simulation

Tujuan Fase 3 adalah menguji setiap hipotesis di audit/05-raw-leads.md dengan menjalankan simulasi transaksi eksploitasi nyata di sandbox lokal/fork tanpa kecurangan, lalu mendistribusikannya secara terpisah ke audit/06-refuted-invalid.md, audit/07-needs-next-step.md, atau audit/09-confirmed-findings.md.

---

## Langkah 1: Saringan Fakta Keras Pra-PoC (Hemat Token — WAJIB Sebelum Menulis Kode PoC!)
Sebelum menghabiskan token menulis kode simulasi tes untuk sebuah Lead di audit/05-raw-leads.md, periksa 4 Kemustahilan Fakta Dasar berikut (rujuk audit/00-project-map.md dan audit/01-threat-and-env.md). Jika jawaban dari SALAH SATU pertanyaan ini adalah YA, jangan tulis PoC — langsung buang ke `audit/06-refuted-invalid.md`:

1. Halusinasi Token/Kontrak (Langgar Kasta Aset): Apakah Lead ini mengasumsikan Token Kasta 1 (LP Token, Share/Receipt Token, WETH, Token Internal) memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau gagal mengembalikan bool ala USDT? Atau menganggap USDT mainnet memotong pajak transfer (fee > 0)? Atau menyuntikkan kontrak palsu ke parameter yang dikunci oleh *Factory/Whitelist*?
2. Ilusi Kolam Kosong pada Pool Live: Apakah Lead ini membutuhkan totalSupply == 0 (*First Depositor Attack*) pada Vault/Pool yang di produksi sudah *live* memiliki TVL atau sudah mencetak *dead shares* saat deploy, tanpa ada cara menguras pool ke nol terlebih dahulu?
3. Fungsi Sudah Terkunci / Non-Live: Apakah Lead ini menyerang fungsi initialize() yang di produksi sudah dieksekusi saat deployment, atau menyerang modul yang dimatikan permanen di produksi?
4. Ketergantungan Aksi Admin / Korban Bunuh Diri: Apakah Lead ini mengharuskan Owner/Admin/Keeper memasukkan konfigurasi bunuh diri, mengasumsikan *feed* Chainlink rusak sendiri, atau mengharuskan korban mematikan pelindungnya sendiri (minAmountOut = 0 / kirim token langsung via ERC20.transfer)?

*(Catatan Penting: Untuk Lead yang berkaitan dengan pembulatan matematika, akrual indeks, atau DoS yang lolos ke-4 saringan fakta di atas, JANGAN dibuang di Langkah 1 — wajib jalankan simulasi di Langkah 2 dan coba lipat gandakan dampaknya terlebih dahulu!)*

---

## Langkah 2: Simulasi Eksploitasi di Sandbox Lokal Tanpa "Fantasy Mock" & Tanpa Cheatcode
Untuk Lead yang lolos Langkah 1, tulis dan jalankan simulasi transaksi eksploitasi (`FOUNDRY_JOBS=1`, `CARGO_BUILD_JOBS=1`, `RAYON_NUM_THREADS=1`) dengan aturan mutlak:
1. **Larangan Fantasy Mock:** Gunakan kontrak LP/Share/Sistem asli dari repositori. Jika menggunakan MockERC20 untuk aset eksternal pada simulasi lokal, perilakunya WAJIB 100% IDENTIK dengan aset nyata yang diizinkan protokol di produksi.
2. **Inisialisasi Setara Produksi:** Setup awal di dalam setUp() wajib mencerminkan keadaan produksi nyata (sudah terinisialisasi dengan parameter normal dan memiliki likuiditas awal yang wajar).
3. **Larangan Cheatcode Curang:** Hanya gunakan vm.prank(attacker) (pengguna eksternal tak berizin). DILARANG menggunakan vm.prank(admin/owner), vm.store, vm.etch, atau deal pada kontrak protokol untuk memalsukan state internal.
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
   - `Disposition: NEXT_EXPLORE` -> Simulasi PoC sederhana belum tembus, butuh metode eksplorasi lanjut (Stateful Invariant Fuzzing Tier 2, Symbolic Proving Halmos, atau multi-step chaining).
   - `Disposition: NEXT_MAINNET` -> Simulasi lokal PASS, tetapi butuh verifikasi parameter/storage/proxy di mainnet atau penyesuaian blok fork.
   - `Disposition: TOOL_BLOCKED` -> Terhalang ketiadaan RPC publik, masalah kompilasi dependency eksternal, atau keterbatasan harness lokal.
3. **Gagal di Langkah 1 ATAU Simulasi PoC Gagal (`revert`) di State Nyata:**
   Tulis ke `audit/06-refuted-invalid.md` beserta alasan teknisnya, dan hapus file test sementara yang gagal agar folder test/ tetap bersih.
