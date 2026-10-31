---
name: sc-phase2-hunt
description: Phase 2 — Two-Stage Domain-Agnostic Hunting with Early 8-Gate Reality Filtering.
version: 4.4.0
---

# Phase 2: Two-Stage Domain-Agnostic Adversarial Hunting

Tujuan Fase 2 adalah menemukan kerentanan logika nyata pada domain APA PUN tanpa terjebak oleh *Checklist Tunnel Vision* maupun *Kondisi Istimewa* yang tidak realistis.

---
## Aturan Orkestrasi Subagent (delegate_task)
Jika dijalankan melalui delegasi, berikan paket tugas berisi:
1. Daftar 1 Kelompok Fungsi Siklus Hidup (2-4 fungsi) dari audit/03-attack-surface-queue.md beserta tag [LOAD: ...].
2. Instruksi wajib membaca audit/00-project-map.md, audit/01-threat-and-env.md (terutama Kasta Realitas Aset & Siklus Hidup Produksi), dan audit/02-state-and-var-matrix.md.
3. Instruksi menjalankan Tahap A (Bedah First-Principles) terlebih dahulu, dilanjutkan Tahap B (Analogi Referensi), lalu Tahap C (Saringan 8 Gerbang Realitas).

---

## TAHAP A: Bedah Murni First-Principles (WAJIB Sebelum Membaca Checklist!)

### A1. Pelacakan Mundur (*Backward Sink-to-Source Tracing*)
Mulailah dari Titik Kritis di Bawah (*The Sink*) (baris pengiriman aset/NFT, perubahan hak/owner, penghapusan utang/kewajiban, atau perubahan status), lalu lacak mundur ke atas (*backward*) setiap variabel penentunya: *"Bagaimana memaksimalkan hasil di Sink sambil meminimalkan pengorbanan di Source menggunakan input yang diizinkan di produksi?"*

### A2. Simulasi Tabel 4 Kondisi Konkret (Sesuai Realitas Produksi)
Masukkan 4 kondisi konkret ini ke dalam rumus/logika fungsi dan hitung di audit/notes/:
1. Kondisi Batas Likuiditas Realistis: Uji dengan jumlah kecil/besar yang realistis (JANGAN mengasumsikan totalSupply == 0 jika audit/00-project-map.md menyatakan pool sudah *live* / memiliki *dead shares*, kecuali ada cara mengurasnya ke nol terlebih dahulu).
2. Kondisi Debu yang Berdampak (*Amplifiable / DoS Dust*): Input bernilai 0, 1 wei, atau batas_minimum - 1 yang menyebabkan transaksi penting `revert` (DoS) atau biaya/utang terpotong jadi `0` secara berulang (abaikan selisih pembulatan 1 wei yang tidak bisa diamplifikasi).
3. Kondisi Waktu & Blok Sama ($\Delta t = 0$): Fungsi dipanggil berulang kali di blok yang sama atau tepat pada batas *deadline*.
4. Kondisi Entitas & Diri Sendiri: Bagaimana jika sender == recipient, target == address(this) (self-call dalam batch), atau tokenId / tipe standar aset yang dimasukkan dimanipulasi dalam batas *whitelist*?

### A3. Eksplorasi 3 Lapis Mutasi State (Bebas Domain)
1. Lapis 1 (Radius 0-2 & Pasangan Siklus Hidup): Bandingkan mutasi state di fungsi Masuk/Buat vs fungsi Keluar/Batal/Transfer/Sita dari audit/02-state-and-var-matrix.md. Cari field struct/mapping yang lupa di-reset atau urutan operasi yang terbalik.
2. Lapis 2 (Permutasi 3-Langkah & 5 Primitif Universal): Uji urutan Aksi_A -> Transfer/SelfCall -> Aksi_B atau Partial_Action -> Cancel -> Claim terhadap: (1) Kuantisasi Proporsi, (2) Transisi Paksa & Sabotase DoS, (3) Replay Otoritas/Signature, (4) Penyerahan Kontrol Eksekusi, dan (5) Lompatan Mesin Status.
3. Lapis 3 (Interogasi Guard-Bypass): Untuk setiap require/if (...) revert, cari apakah variabel di dalam penjaga tersebut dapat dimanipulasi oleh fungsi publik lain tanpa hak Admin.

---

## TAHAP B: Pengayaan Analogi Mekanis dari references/
Panggil skill_view("sc-phase2-hunt", "<nama-file-ref>") sesuai tag [LOAD: ...]. Terjemahkan istilah DeFi di dalam referensi sebagai Pola Mekanis Abstrak (misal: *"Vault/Shares"* = sistem proporsi/bobot/kuota apa pun; *"Liquidation"* = mekanisme penyitaan/lelang/kedaluwarsa/slashing apa pun; *"Reentrancy/Permit"* = termasuk callback NFT, batch address(this), dan signature EIP-1271/Session Key).

---
## TAHAP C: Saringan Devil's Advocate & 8 Gerbang Realitas Bounty
Sebelum mencatat temuan, uji dengan Larangan Kondisi Istimewa:
- Apakah hipotesis ini mengasumsikan LP/Share token punya *Fee-on-Transfer*/USDT quirk, menyerang initialize() yang sudah berjalan, membutuhkan Admin bodoh/jahat, membutuhkan korban mengisi slippage = 0, hanya menghasilkan debu 1 wei tanpa amplifikasi, atau merugikan penyerang sendiri (*Negative EV*)?
1. Jika Bebas dari Kondisi Istimewa & Tidak Ada Guard yang Menghentikan: Catat ke `audit/05-raw-leads.md`.
2. Jika Dihentikan Guard Valid ATAU Bergantung pada Kondisi Istimewa: Catat secara singkat ke `audit/04-rejected-hypotheses.md` beserta alasan gugurnya.
3. Tandai kelompok fungsi di audit/03-attack-surface-queue.md menjadi [HUNTED].
