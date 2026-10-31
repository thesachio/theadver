---
name: sc-phase3-verify-and-poc
description: Phase 3 — 8-Gate Bounty-Reality Triage, Anti-Fantasy-Mock Enforcement, and Concrete PoC Execution.
version: 4.4.0
---

# Phase 3: 8-Gate Bounty-Reality Triage & Concrete PoC Execution

Tujuan Fase 3 adalah menguji setiap hipotesis di audit/05-raw-leads.md secara ketat dan jujur, lalu memisahkannya ke audit/07-confirmed-findings.md, audit/06-unproven-needs-review.md, atau audit/04-rejected-hypotheses.md.

---

## Langkah 1: Uji 8 Gerbang Realitas Bounty — WAJIB SEBELUM MENULIS PoC!
Periksa setiap Lead di audit/05-raw-leads.md terhadap 8 Pertanyaan Kematian Bounty (rujuk audit/00-project-map.md dan audit/01-threat-and-env.md). Jika jawaban dari SALAH SATU pertanyaan di bawah ini adalah YA, DILARANG memasukkannya ke `audit/07-confirmed-findings.md` — langsung pindahkan ke `audit/04-rejected-hypotheses.md`:

1. Gerbang #1 (Halusinasi Token/Kontrak): Apakah Lead ini mengasumsikan Token Kasta 1 (LP Token, Share/Receipt Token, WETH, Token Internal) memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau gagal mengembalikan bool seperti USDT? Atau mengasumsikan sifat token yang tidak ada pada daftar *Whitelist* Kasta 2 (seperti menganggap USDT memotong biaya transfer > 0)? Atau menyuntikkan kontrak palsu ke parameter yang sebenarnya divalidasi oleh *Factory/Whitelist*?
2. Gerbang #2 (Ilusi Kolam Kosong / Genesis): Apakah Lead ini membutuhkan kondisi totalSupply == 0 (*First Depositor Attack*) pada Vault/Pool yang di produksi sudah *live* memiliki TVL atau sudah mencetak *dead shares* saat deploy, tanpa ada cara bagi penyerang untuk menguras pool tersebut ke nol terlebih dahulu?
3. Gerbang #3 (Kode Mati / Sudah Diinisialisasi): Apakah Lead ini menyerang fungsi initialize() yang di produksi sudah dieksekusi saat deployment, atau menyerang modul/fitur yang dimatikan (*paused/deprecated*) di produksi?
4. Gerbang #4 (Admin / Keeper / Oracle Bunuh Diri): Apakah Lead ini mengharuskan Owner/Admin/Multisig/Governance/Trusted Keeper bertindak jahat atau memasukkan parameter konfigurasi yang bunuh diri (*Admin Misconfiguration*), atau mengasumsikan *feed* Chainlink rusak sendiri tanpa manipulasi on-chain?
5. Gerbang #5 (Sabotase Diri Sendiri & Input Korban Bodoh): Apakah Lead ini mengharuskan korban secara sukarela mematikan pelindungnya sendiri (misal: mengisi minAmountOut = 0 atau deadline = max), mengirim token langsung via ERC20.transfer di luar fungsi deposit, atau hanya merusak pool kustom milik penyerang sendiri?
6. Gerbang #6 (Debu 1-Wei Tanpa Amplifikasi): Apakah dampak maksimal Lead ini hanyalah selisih pembulatan debu (1 wei s/d beberapa sen) yang TIDAK menyebabkan transaksi penting revert (DoS) dan TIDAK BISA dilipatgandakan secara menguntungkan?
7. Gerbang #7 (Ekonomi Rugi Bandar / Negative-EV): Apakah untuk melancarkan serangan ini penyerang harus membakar biaya/modal permanen yang jauh lebih besar daripada nilai yang berhasil dicuri/dibekukan?
8. Gerbang #8 (Fiksi Fisika Blockchain): Apakah Lead ini mengandalkan mekanika rantai yang mustahil (seperti reentrancy lewat .transfer() 2300 gas, atau *front-running* mempool publik untuk transaksi tanpa MEV di jaringan dengan *private sequencer*)?

---

## Langkah 2: Eksekusi PoC Tanpa "Fantasy Mock" & Tanpa Cheatcode Curang
Untuk Lead yang lolos seluruh 8 Gerbang di Langkah 1, tulis dan jalankan tes eksploitasi nyata (FOUNDRY_JOBS=1, CARGO_BUILD_JOBS=1, RAYON_NUM_THREADS=1) dengan aturan mutlak:
1. Larangan Fantasy Mock: Gunakan kontrak LP/Share/Sistem asli dari repositori. Jika menggunakan MockERC20 untuk aset eksternal, perilakunya WAJIB 100% IDENTIK dengan aset nyata yang diizinkan protokol di produksi (DILARANG menyuntikkan logika potongan *Fee-on-Transfer*, *hook* jahat, atau kegagalan boolean palsu ke dalam Mock!).
2. Inisialisasi Setara Produksi: Setup awal di dalam setUp() PoC wajib mencerminkan keadaan produksi nyata (sudah terinisialisasi dengan parameter normal dan sudah memiliki likuiditas awal yang wajar).
3. Larangan Cheatcode Curang: Hanya gunakan vm.prank(attacker) (pengguna tak berizin). DILARANG menggunakan vm.prank(admin/owner), vm.store, vm.etch, atau deal pada kontrak protokol untuk memalsukan state internal.

### Langkah 2b: Mode Uji — Aturan Fork untuk 07
`07-confirmed-findings.md` mengklaim bukti terhadap PRODUKSI, bukan terhadap source yang dikompilasi ulang. Karena itu:
1. Fork WAJIB bila chain target memiliki RPC publik: jalankan PoC terhadap bytecode yang ter-deploy pada blok yang dicatat (`forge test --fork-url <RPC> --fork-block-number <N>`). Bila repo HEAD berbeda dari versi deploy (versi lama, proxy, upgrade), fork adalah satu-satunya bukti yang sah.
2. Attacker hanya boleh didanai lewat `deal` pada dompetnya SENDIRI atau pembelian nyata. DILARANG `vm.store`, `vm.etch`, atau menyentuh state protokol. `vm.prank(victim)` hanya untuk EOA pengguna biasa, bukan Admin/Keeper/Oracle (Gerbang #4 & #8).
3. Jika RPC chain target tidak tersedia atau kontrak tidak dapat dijangkau fork, temuan DILARANG masuk `07` — pindahkan ke `06-unproven-needs-review.md` dengan blocker yang dinamai jelas (endpoint mana yang gagal, chain apa).
4. Fork berjalan namun exploit gagal terhadap state nyata = gugur ke `04-rejected-hypotheses.md`.
5. Setiap entri 07/06 WAJIB mencantumkan satu baris `Mode Uji: FORK (chain, block, RPC)` atau `Mode Uji: LOKAL (alasan fork tidak mungkin)`. Entri tanpa baris ini dianggap belum terverifikasi.

---

## Langkah 3: Klasifikasi Hasil Akhir (04, 06, atau 07 di audit/)
- Lolos 8 Gerbang + PoC PASS pada fork state produksi (Langkah 2b): Masukkan ke `audit/07-confirmed-findings.md` lengkap dengan kode PoC utuh, perhitungan profit/dampak nyata, dan log terminal.
- Gagal di Salah Satu dari 8 Gerbang ATAU PoC Gagal karena Guard Kode: Pindahkan ke `audit/04-rejected-hypotheses.md` beserta alasan penolakannya.
- Lolos 8 Gerbang & Logika Terbukti Rentan namun Terhalang Kendala Tooling Lokal: Masukkan ke `audit/06-unproven-needs-review.md`.
