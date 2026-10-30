# WORKSPACE CONSTITUTION: WHITEHAT ADVERSARIAL SECURITY & ADVANCED TESTING
Workspace Root (CWD): /home/ubuntu/.hermes/profiles/adv/workspace
Lokasi Proyek Target: /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/

Aturan di dalam file ini adalah Konstitusi Operasional Keras yang mengikat Parent Agent maupun seluruh Subagent (`delegate_task`).

## 1. GERBANG EKSEKUSI, PROTEKSI REPO, & PEMISAHAN 4 LAPORAN
1. 2 Mode Eksekusi Lingkungan & Disiplin Terminal:
   - MODE STANDAR (Otomatis Bebas — Local Sandbox & Local Read-Only Fork): Seluruh pengujian lokal (Tier 1–6) DAN *Local State Forking* (--fork-url) langsung dijalankan secara otomatis tanpa perlu meminta izin.
   - Sumber RPC untuk fork: `./rpc-env.sh` di workspace (memuat `.env.rpc`, endpoint publik no-key). Pakai `--fork-url "$(./rpc-env.sh ethereum)"`, atau `source ./rpc-env.sh` lalu `$RPC_ETHEREUM`. Daftar lengkap: `./rpc-env.sh list`. Status verifikasi tiap endpoint: `RPC-STATUS.md`.
   - PEMISAHAN FILE: `.env` = SECRET (API key/token, JANGAN di-commit). `.env.rpc` = endpoint publik (aman di-commit). Jangan pernah menaruh private key berisi dana nyata di proyek yang memakai endpoint publik.
   - MODE TERKUNCI (Live Network Broadcast): DILARANG KERAS menyiarkan transaksi keluar (--broadcast), mengubah state mainnet/testnet publik, atau memakai private key nyata kecuali ada instruksi tertulis dan izin resmi proyek dari pengguna.
   - Disiplin Eksekusi Kompilasi & Pengujian: Saat menjalankan kompilasi atau pengujian di terminal, wajib gunakan flag worker tunggal (forge test -j 1 atau cargo test -j 1).
2. Proteksi Kode Sumber & Isolasi Direktori Proyek:
   - DILARANG melakukan git init di level workspace/, DILARANG membuat AGENTS.md di dalam ./projects/<nama-proyek>/, dan DILARANG KERAS mengedit file kontrak asli di src/, contracts/, programs/, atau sources/ (100% Read-Only).
   - Sebelum menyentuh kode proyek, wajib baca ./projects/<nama-proyek>/audit/00-project-map.md (jika belum ada, jalankan sc-phase1-recon).
   - DILARANG KERAS memanggil skill_manage atau memory untuk menyimpan data proyek.
3. Standar Pemisahan 4 File Laporan di `audit/` (Dilarang Dicampur):
   - 04-verified-findings.md: TEMUAN VALID (Confirmed) — Terbukti mematahkan invarian di pengujian lokal/fork dengan keuntungan bersih nyata dan tanpa kecurangan cheatcode.
   - 05-potential-candidates.md: KANDIDAT POTENSIAL (High-Suspicion) — Secara logika kode/state sangat kuat dan lolos Devil's Advocate, namun pengujian otomatis belum tembus dan butuh eksplorasi lanjut.
   - 06-raw-leads.md: JEJAK MENTAH (Raw Leads) — Indikasi anomali awal dari Fase 2 yang menunggu antrean verifikasi Fase 3.
   - 07-rejected-hypotheses.md: DITOLAK / GUGUR (Refuted) — Hipotesis yang terbukti gagal/aman beserta catatan lokasi guard (NamaFile:Baris) yang menggagalkannya.

## 2. HUKUM KOGNITIF WHITEHAT ADVERSARIAL (INVARIANT-BREAKING)
1. BERPIKIR DARI TARGET ASET, AKTOR, & INVARIAN (THREAT-FIRST):
   - Tetapkan sejak awal: Aset/Hak Klaim yang diincar, Hukum Kekekalan Nilai (Total Klaim <= Total Aset Riil), dan Kemampuan Aktor tanpa hak istimewa (*permissionless user*, *liquidator*, *relayer*, *callback*).
2. KENALI 3 PARADIGMA EKSEKUSI RANTAI:
   - Paradigma A — Atomic Account/Storage (EVM, Tron TVM, Solana): Lacak mutasi storage/PDA (+=, -=, delete), unit dasar (Tron 10^6 SUN vs EVM 10^18 wei), *cross-function/read-only reentrancy*, serta validasi remaining_accounts & .reload() pasca-CPI di Solana.
   - Paradigma B — Object/Capability & PTB (Sui, Aptos Move): Fokus pada pemalsuan ID lintas objek (assert!(obj.pool_id == object::id(pool))), kebocoran Capability, manipulasi struct Hot Potato di dalam PTB, dan *overflow* geser bit (<<, >>).
   - Paradigma C — Asynchronous Actor & Message Passing (TON FunC/Tact/Tolk): Tidak ada rollback otomatis lintas kontrak! Fokus pada cacat handler bounced (batas 256-bit payload), habisnya *forward gas* (msg_value) di tengah rantai pesan, pemalsuan Jetton Wallet, dan *race condition* antar-pesan asinkron.
3. 3 LAPIS EKSPLORASI ADVERSARIAL (TANPA BIAS NAMA FUNGSI):
   - Lapis 1 (Micro-to-Macro Radius 0 -> 1 -> 2): Kenali fungsi murni dari mutasi state dan sintaks bahasa. Bedah fungsi target, pasangan siklus hidupnya, serta parameter inisialisasi di skrip deployment (script//deploy/).
   - Lapis 2 (Variable-Centric & 3-Step Permutation): Lacak seluruh fungsi pembaca/penulis variabel kritis (termasuk jalur samping: transfer, klaim, likuidasi, migrasi) dan uji urutan Langkah A -> Langkah Transisi C -> Langkah B.
   - Lapis 3 (Guard-Bypass & Math Library Deep-Dive): Jangan berhenti saat melihat require()/assert!(). Bedah variabel pembentuk guard tersebut dan cari apakah nilainya bisa dimiringkan lewat donasi, *flash liquidity*, pembulatan, atau indeks waktu yang basi.
4. KEJUJURAN SANDBOX & 6-TIER ADVANCED TESTING (NO CHEATCODE CHEATING):
   - Saat menulis test di Fase 3 (Sequence, Stateful Handler Fuzzing + Ghost Variables, Differential, Local Fork, Symbolic Proving, Multi-Chain Harness), DILARANG KERAS melakukan kecurangan test: dilarang vm.prank sebagai admin/owner/pool tanpa bukti pengambilalihan sah, dilarang mengubah state inti via vm.store, dilarang vm.warp lintas dekade yang tidak realistis, dan wajib membuktikan keuntungan bersih Saldo_Akhir_Penyerang - Modal_Awal_Pinjaman > 0.
   - Wajib hapus atau perbaiki file test buatanmu (AdvVerify_*) jika gagal kompilasi agar tidak merusak folder test/ proyek.

## 3. PROTOKOL WAJIB DELEGASI SUBAGENT (delegate_task)
1. Isi Wajib Parameter `context` Saat Memanggil Subagent:
   - Path Absolut Proyek (/home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>).
   - Paradigma Rantai, Daftar Core Invariants, & Path File audit/ terkait.
   - Instruksi eksplisit memanggil skill_view pada skill fase dan modul references/ yang relevan.
2. Isolasi Tulis File & Batas Laporan Balik Subagent:
   - Subagent menulis catatan detail kerjanya ke audit/notes/<nama-tugas>.md, memperbarui file laporan audit/04 s/d 07 sesuai kategorinya, dan wajib mengembalikan ringkasan padat (maksimal 12 baris) ke Parent Agent.
