---
name: sc-phase3-verify
description: Fase 3 Whitehat Adversarial Verification & 6-Tier Advanced Testing Lab - Pembuktian hipotesis, Stateful Invariant Fuzzing + Ghost Variables, Differential Testing, Local Fork, Symbolic Execution, dan pemisahan 4 file laporan
version: 4.0.0
metadata:
  hermes:
    tags: [security, web3, whitehat, adversarial, testing, fuzzing, symbolic, multichain, phase3]
    category: security
    requires_toolsets: [terminal]
---

# Phase 3: 6-Tier Advanced Testing Lab & 4-File Report Classification

## When to Use
Gunakan skill ini dalam dua skenario utama:
1. Verifikasi Hipotesis (Hypothesis Proving): Menguji jejak serangan dari .audit/06-raw-leads.md menggunakan pengujian lokal atau local read-only fork.
2. Eksplorasi Invarian Aktif (Active Fuzzing & Proving): Ketika Fase 2 tidak menemukan bug kasatmata atau membutuhkan pembuktian matematis mendalam, jalankan Tier 2 (Stateful Invariant Fuzzing + Ghost Variables), Tier 3 (Round-Trip/Differential Testing), atau Tier 5 (Symbolic Execution) untuk mematahkan Core Invariants dari .audit/00-project-map.md.

## Pitfalls & Hukum Kejujuran Sandbox (Larangan Keras di Fase 3)
- MODE EKSEKUSI & WORKER TUNGGAL: Jalankan seluruh pengujian lokal dan *Local Read-Only Fork* (--fork-url jika RPC tersedia di .env/konfigurasi) secara otomatis tanpa perlu meminta izin. DILARANG menggunakan --broadcast. Wajib gunakan flag worker tunggal (forge test -j 1 atau cargo test -j 1).
- DILARANG CURANG DENGAN CHEATCODE (NO CHEATCODE CHEATING):
  * Dilarang vm.prank sebagai owner, admin, pool, router, atau messenger kecuali rangkaian transaksi di dalam test tersebut telah membuktikan pengambilalihan otoritas itu secara sah dari akun tanpa hak istimewa.
  * Dilarang memodifikasi slot penyimpanan kontrak inti secara paksa menggunakan vm.store atau menimpa kode kontrak inti dengan vm.etch.
  * Dilarang menggunakan vm.warp atau vm.roll dengan rentang waktu yang mustahil secara ekonomi (misal melompat 50 tahun).
  * Wajib membuktikan Keuntungan Bersih Nyata (Net Profit) atau kerusakan invarian nyata: Saldo_Akhir_Penyerang > Modal_Awal + Pinjaman_FlashLoan.
- PROTEKSI KODE SUMBER & KEBERSIHAN FOLDER `test/`:
  * Dilarang mengedit file kontrak asli di src/, contracts/, programs/, atau sources/.
  * Beri nama file test buatanmu dengan awalan AdvVerify_ (misal AdvVerify_VaultInflation.t.sol).
  * Jika file test buatanmu gagal kompilasi dan belum bisa diperbaiki, WAJIB hapus file test tersebut sebelum mengakhiri tugas agar tidak merusak kompilasi proyek!
- PEMISAHAN TEGAS 4 FILE LAPORAN DI `.audit/`:
  * Jangan pernah mencampur hasil yang valid, kandidat potensial, dan yang ditolak ke dalam satu file!
- DILARANG MEMANGGIL `skill_manage` ATAU `memory`.

---

## Procedure (5 Langkah Pengujian & Klasifikasi)

Pastikan kamu bekerja pada /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/.

### Langkah 1: Pemuatan Referensi 6-Tier Pengujian Sesuai Rantai
Baca .audit/00-project-map.md untuk melihat rantai dan toolchain proyek, lalu WAJIB panggil skill_view pada modul referensi pengujian yang sesuai:
- Untuk EVM & Tron TVM (Foundry / Hardhat / Halmos):
  -> Panggil skill_view("sc-phase3-verify", "references/ref-test-evm-advanced.md").
- Untuk Solana (Rust/Anchor), Sui/Aptos (Move), atau TON (Func/Tact/Sandbox):
  -> Panggil skill_view("sc-phase3-verify", "references/ref-test-multichain-advanced.md").

### Langkah 2: Pemilihan Strategi dari 6 Tingkatan Pengujian (Tier 1 s/d Tier 6)
Pilih satu atau kombinasi Tier pengujian berikut sesuai target yang sedang diuji:
1. TIER 1 — Deterministic Multi-Actor Sequence & Boundary Test:
   - Gunakan untuk menguji skenario langkah demi langkah dari .audit/06-raw-leads.md (misal: Aktor A -> Aktor B -> Callback -> Likuidasi) atau menguji input ekstrem (0, 1 wei, alamat kembar from == to).
2. TIER 2 — Handler-Based Stateful Invariant Fuzzing + Ghost Variables:
   - Gunakan untuk mencari urutan transaksi multi-langkah acak yang memecahkan invarian akuntansi (sum(userShares) == totalShares atau totalAssets >= ghost_netDeposits).
3. TIER 3 — Differential & Round-Trip Symmetry Testing:
   - Gunakan untuk membongkar kebocoran pembulatan (redeem(deposit(x)) <= x dan withdraw(mint(s)) >= s) atau membandingkan fungsi matematika bitwise/assembly dengan rumus referensi presisi tinggi.
4. TIER 4 — Ephemeral Local Read-Only Fork & Market Stress Simulation:
   - Jika RPC tersedia, jalankan simulasi di atas state nyata untuk menguji interaksi Oracle Chainlink/Pyth, likuiditas DEX, token *fee-on-transfer* / *blacklist* (USDC/USDT), atau jatuhnya harga agunan (*bad debt*).
5. TIER 5 — Symbolic Execution & Formal Counterexample Proving:
   - Gunakan Halmos (check_*), Kani (#[kani::proof]), atau Move Prover (spec) untuk mencari secara matematis apakah ada 1 kombinasi angka yang mematahkan asersi.
6. TIER 6 — Multi-Chain Advanced Harnesses:
   - Sui Move: Simulasi *Programmable Transaction Blocks (PTB)* multi-langkah, *Cross-Pool Object ID Confusion*, dan *Hot Potato*.
   - TON: Simulasi rantai pesan @ton/sandbox, pemotongan payload bounced 256-bit, kekurangan *forward gas*, dan *async race condition*.
   - Solana: Manipulasi remaining_accounts dan pengujian pembacaan akun basi sebelum .reload() pasca-CPI.

### Langkah 3: Penulisan & Eksekusi Pengujian dengan Worker Tunggal (-j 1)
1. Baca 1 file test yang sudah ada di repositori (maksimal 100 baris) untuk menyamakan cara *import* dan *setup* resmi proyek.
2. Tulis file pengujian AdvVerify_<NamaTarget> dan jalankan dengan worker tunggal:
   - Foundry: forge test --match-contract AdvVerify_<NamaTarget> -vvvv -j 1 (tambahkan --fork-url <RPC> jika menggunakan Tier 4).
   - Rust/Solana: cargo test <nama_test> -j 1 -- --nocapture
   - Sui Move: sui move test <nama_test>
   - TON Sandbox: npx jest <nama_test> --runInBand atau npx blueprint test
3. Analisis jejak eksekusi (*trace*), perubahan state sebelum vs sesudah, dan bukti asersi.

### Langkah 4: Klasifikasi Tegas ke Dalam 4 File Laporan Terpisah
Berdasarkan hasil eksekusi pengujian di Langkah 3, perbarui file di .audit/ dengan pemisahan ketat berikut:

1. KATEGORI 1 — MASUK KE `.audit/04-verified-findings.md` (TEMUAN VALID / CONFIRMED):
   - Syarat Mutlak: Pengujian lokal/fork berhasil dijalankan dan membuktikan secara tak terbantahkan bahwa invarian protokol patah atau aktor tanpa hak istimewa memperoleh keuntungan bersih nyata tanpa kecurangan cheatcode.
   - Format Wajib di `04-verified-findings.md`:
     * Judul & Tingkat Keparahan (Critical / High / Medium)
     * Lokasi Kode Presisi (NamaFile:BarisAwal-BarisAkhir) & Invarian yang Patah
     * Akar Masalah Mekanis (*Root Cause*) & Urutan Eksploitasi (*Attack Sequence*)
     * Kode Pengujian Lengkap (AdvVerify_*) & Cuplikan Output Terminal (*Test Trace*)
     * Rekomendasi Patch Perbaikan Kode (diff minimal).
2. KATEGORI 2 — MASUK KE `.audit/05-potential-candidates.md` (KANDIDAT POTENSIAL / HIGH-SUSPICION):
   - Syarat Masuk: Secara analisis kode dan aliran state di Radius 0–2 celah ini sangat nyata dan lolos saringan *Devil's Advocate* (tidak ada guard yang menghadang), TETAPI pengujian otomatis di Fase 3 belum berhasil menembusnya (misal karena kendala kompilasi dependensi eksternal, membutuhkan setup integrasi multi-kontrak yang belum lengkap, atau fuzzer belum menjangkau cabang kondisi tersebut).
   - Format Wajib di `05-potential-candidates.md`:
     * Judul & Lokasi Kode (NamaFile:Baris)
     * Bukti Analisis Statis & Mengapa Guard Tidak Menahannya
     * Kendala Saat Pengujian Fase 3 & Langkah Eksplorasi Lanjutan yang Disarankan.

3. KATEGORI 3 — PEMBARUAN `.audit/06-raw-leads.md` (JEJAK MENTAH):
   - Tandai item di 06-raw-leads.md yang sudah selesai diuji menjadi [PROCESSED -> 04], [PROCESSED -> 05], atau [PROCESSED -> 07].

4. KATEGORI 4 — MASUK KE `.audit/07-rejected-hypotheses.md` (DITOLAK / GUGUR):
   - Syarat Masuk: Pengujian membuktikan bahwa transaksi gagal (revert/abort) karena pengaman protokol yang sah, atau perhitungan menunjukkan penyerang selalu merugi.
   - Format Wajib di `07-rejected-hypotheses.md`:
     * Judul Hipotesis Awal & Lokasi Target
     * Bukti Penolakan: Baris kode penjaga (NamaFile:Baris dari require/assert!/modifier) atau pesan revert terminal yang menggagalkan serangan.

### Langkah 5: Pembersihan & Laporan Ringkas (Maksimal 12 Baris)
Pastikan tidak ada file test yang rusak kompilasinya tertinggal di folder test/. Simpan detail panjang di .audit/notes/ dan file 04 s/d 07, lalu kembalikan ringkasan maksimal 12 baris ke Parent Agent.

---

## Verification
Pastikan setiap target yang diuji telah masuk ke salah satu file yang tepat (04-verified-findings.md, 05-potential-candidates.md, atau 07-rejected-hypotheses.md), kode sumber kontrak asli (src/) tidak tersentuh, dan tidak ada error kompilasi yang tertinggal.
