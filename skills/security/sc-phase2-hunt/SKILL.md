---
name: sc-phase2-hunt
description: Phase 2 — Two-Stage Domain-Agnostic Adversarial Hunting (Unbiased First-Principles + Analogical Reference Enrichment).
version: 4.1.0
---

# Phase 2: Two-Stage Domain-Agnostic Adversarial Hunting

Tujuan Fase 2 adalah menemukan kerentanan logika nyata pada domain APA PUN (baik DeFi standar maupun Smart Wallet, NFT, Governance, Game, atau mekanisme baru yang belum pernah ada) tanpa terjebak oleh *Checklist Tunnel Vision*.

---

## Aturan Orkestrasi Subagent (delegate_task)
Jika dijalankan melalui delegasi, berikan paket tugas berisi:
1. Daftar 1 Kelompok Fungsi Siklus Hidup (2-4 fungsi) dari audit/03-attack-surface-queue.md beserta tag [LOAD: ...].
2. Instruksi untuk membaca audit/00-project-map.md, audit/01-threat-and-env.md, dan audit/02-state-and-var-matrix.md.
3. Instruksi wajib menjalankan Tahap A (Bedah Murni First-Principles Tanpa Bias Referensi) terlebih dahulu, baru dilanjutkan Tahap B (Pengayaan Analogi dari `references/`).

---

## TAHAP A: Bedah Murni First-Principles (WAJIB Dilakukan SEBELUM Membaca Checklist!)

Agar Anda tidak terjebak oleh istilah domain di referensi, bedah fungsi target secara murni dari mekanika kodenya melalui 4 Langkah First-Principles:

### A1. Pelacakan Mundur (*Backward Sink-to-Source Tracing*)
Jangan membaca fungsi dari atas ke bawah! Mulailah dari Titik Kritis di Bawah (*The Sink*):
1. Temukan baris paling berbahaya di dalam fungsi: tempat aset/NFT dikirim keluar, tempat hak/kepemilikan (owner/operator) diubah, tempat utang/kewajiban dihapus, atau tempat status penting diperbarui.
2. Lacak mundur ke atas (*backward*) setiap variabel yang menentukan eksekusi atau besaran nilai di baris tersebut hingga ke parameter input: *"Bagaimana caranya memaksimalkan apa yang saya dapat di Sink ini sambil meminimalkan apa yang harus saya bayar/korbankan di Source?"*
### A2. Simulasi Tabel 4 Angka & Kondisi Ekstrem Konkret
DILARANG menganggap rumus atau cabang logika aman hanya dengan membacanya secara abstrak! Masukkan 4 kondisi konkret ini ke dalam rumus/logika fungsi dan hitung hasilnya di audit/notes/:
1. Kondisi Kosong / Injeksi Langsung: Total awal 0 atau 1 wei sementara saldo fisik dimanipulasi dari luar.
2. Kondisi Debu (*Dust / Off-by-One*): Input bernilai 0, 1 wei, atau tepat batas_minimum - 1 (apakah biaya/penalti terpotong jadi 0 karena pembulatan ke bawah?).
3. Kondisi Waktu & Blok Sama ($\Delta t = 0$): Fungsi dipanggil berulang kali di transaksi/blok yang sama, atau tepat pada detik batas waktu (*deadline*).
4. Kondisi Entitas Asing / Diri Sendiri: Bagaimana jika sender == recipient, target == address(this) (self-call dalam batch), atau tokenId / tipe token yang dimasukkan berbeda dari ekspektasi?

### A3. Eksplorasi 3 Lapis Mutasi State (Bebas Domain)
1. Lapis 1 (Radius 0-2 & Pasangan Siklus Hidup):
   - Radius 0: Urutan operasi di dalam fungsi (apakah ada akrual/validasi yang terlambat atau panggilan eksternal sebelum state dikunci?).
   - Radius 1: Bandingkan mutasi state di fungsi Masuk/Buat vs fungsi Keluar/Batal/Transfer/Klaim dari audit/02-state-and-var-matrix.md. Apakah ada field di struct/mapping yang lupa di-reset atau dikurangi?
   - Radius 2: Apakah fungsi eksternal/pembaca di kontrak lain membaca state kontrak ini saat nilainya sedang berada di tengah perubahan?
2. Lapis 2 (Permutasi 3-Langkah & Invarian Universal):
   - Uji urutan tak wajar: Aksi_A -> Transfer/Modifikasi/SelfCall -> Aksi_B atau Partial_Action -> Cancel -> Claim.
   - Uji terhadap 5 Primitif Universal: (1) Kuantisasi Proporsi, (2) Transisi Paksa & Sabotase DoS, (3) Replay/Konteks Otoritas & Signature, (4) Penyerahan Kontrol Eksekusi, dan (5) Lompatan Mesin Status.
3. Lapis 3 (Interogasi Guard-Bypass):
   - Untuk setiap require / if (... ) revert yang menghalangi ide serangan, jangan menyerah! Tanyakan: *"Dari mana variabel di dalam penjaga ini berasal, dan fungsi mana yang bisa saya panggil sebelumnya untuk memanipulasi nilainya agar penjaga ini lolos?"*

---

## TAHAP B: Pengayaan Analogi Mekanis dari references/

Setelah menyelesaikan Tahap A, panggil skill_view("sc-phase2-hunt", "<nama-file-ref>") sesuai tag [LOAD: ...].
ATURAN TRANSLASI ANALOGI (ANTI-TUNNEL VISION):
Saat membaca file ref-math-and-vaults.md, ref-calls-tokens-reentrancy.md, atau ref-defi-oracles-liquidation.md, JANGAN membatasi maknanya pada istilah DeFi! Terjemahkan setiap poin di dalamnya sebagai Pola Mekanis Abstrak ke domain kontrak yang sedang Anda bedah:
- Istilah *"Vault / Shares / First Depositor"* wajib Anda terjemahkan menjadi sistem pembagian proporsi/bobot/poin/kuota apa pun di kontrak target.
- Istilah *"Liquidation / Borrower / Repay"* wajib Anda terjemahkan menjadi mekanisme penyitaan, kedaluwarsa paksa, lelang, pelunasan NFT, atau penalti/slashing apa pun di kontrak target (misal: bisakah pihak yang terkena sanksi/lelang memblokir eksekusi dengan menolak pembayaran balik?).
- Istilah *"External Call / Reentrancy / Permit"* wajib Anda terjemahkan mencakup callback NFT (`onERC721Received`/`onERC1155Received`), eksekusi batch Smart Wallet (`target == address(this)`), replay tanda tangan EIP-1271 lintas dompet, dan validasi cakupan Session Key.

---

## Langkah Terakhir: Devil's Advocate & Pencatatan
Evaluasi setiap temuan dari Tahap A dan Tahap B:
1. Jika Lolos (Tidak ada guard yang menggagalkan, atau guard terbukti bisa ditembus):
   Catat ke `audit/05-raw-leads.md` lengkap dengan File:Kontrak:Fungsi (Baris), Prasyarat, Urutan Eksploitasi Konkret, dan Invarian/Dampak yang Dilanggar.
2. Jika Gugur (Ada guard yang benar-benar menghentikan serangan):
   Catat secara singkat ke `audit/04-rejected-hypotheses.md` beserta alasan gugurnya (File:Baris guard yang menghentikan).
3. Tandai kelompok fungsi di audit/03-attack-surface-queue.md menjadi [HUNTED].
