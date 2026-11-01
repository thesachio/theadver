---
name: sc-phase2-hunt
description: Phase 2 — Two-Stage Domain-Agnostic Hunting (First-Principles + Analogical & Attacker POV Reference) with Pure Code-Guard Separation.
version: 5.0.0
---

# Phase 2: Two-Stage Domain-Agnostic Adversarial Hunting

Tujuan Fase 2 adalah menemukan celah logika dan anomali mutasi state secara kreatif tanpa terjebak *Checklist Tunnel Vision* dan tanpa melakukan penghakiman kelayakan ekonomi secara prematur.

---

## Aturan Orkestrasi Subagent (delegate_task)
Jika dijalankan melalui delegasi, berikan paket tugas berisi:
1. Daftar 1 Kelompok Fungsi Siklus Hidup (2-4 fungsi) dari audit/03-attack-surface-queue.md beserta tag [LOAD: ...].
2. Instruksi wajib membaca audit/00-project-map.md, audit/01-threat-and-env.md (terutama 3 Kasta Realitas Aset & Siklus Hidup Produksi), dan audit/02-state-and-var-matrix.md.
3. Instruksi menjalankan Tahap A (Bedah First-Principles) terlebih dahulu, dilanjutkan Tahap B (Analogi Referensi & Katalog Attacker POV), lalu Tahap C (Pemisahan `04-code-guarded.md` vs `05-raw-leads.md`).

---

## TAHAP A: Bedah Murni First-Principles (WAJIB Sebelum Membaca Referensi!)

### A1. Pelacakan Mundur (*Backward Sink-to-Source Tracing*)
Mulailah dari Titik Kritis di Bawah (*The Sink*) (baris pengiriman aset/NFT, perubahan hak/owner, penghapusan utang/kewajiban, atau perubahan status), lalu lacak mundur ke atas (*backward*) setiap variabel penentunya: *"Bagaimana memaksimalkan hasil di Sink sambil meminimalkan pengorbanan di Source menggunakan input yang diizinkan pada Kasta Aset di 01-threat-and-env.md?"*

### A2. Simulasi Tabel 4 Kondisi Konkret
Masukkan 4 kondisi konkret ini ke dalam rumus/logika fungsi dan hitung di audit/notes/:
1. Kondisi Batas Likuiditas: Uji dengan jumlah kecil/besar yang realistis (jangan mengasumsikan totalSupply == 0 jika 00-project-map.md menyatakan pool sudah *live* / memiliki *dead shares*, kecuali ada mekanisme mengurasnya ke nol terlebih dahulu).
2. Kondisi Batas Bawah & Pembulatan (*Boundary / Rounding*): Input bernilai 0, 1 wei, atau batas_minimum - 1 (apakah biaya/utang/penalti terpotong jadi 0 karena pembulatan, atau memicu desinkronisasi akuntansi?).
3. Kondisi Waktu & Blok Sama ($\Delta t = 0$): Fungsi dipanggil berulang kali di blok yang sama atau tepat pada batas *deadline*.
4. Kondisi Entitas & Diri Sendiri: Bagaimana jika sender == recipient, target == address(this) (self-call dalam batch), atau tokenId / tipe aset dimanipulasi dalam batas *whitelist*?

### A3. Eksplorasi 3 Lapis Mutasi State (Bebas Domain)
1. Lapis 1 (Radius 0-2 & Pasangan Siklus Hidup): Bandingkan mutasi state di fungsi Masuk/Buat vs fungsi Keluar/Batal/Transfer/Sita dari audit/02-state-and-var-matrix.md. Cari field struct/mapping yang lupa di-reset atau urutan operasi yang terbalik.
2. Lapis 2 (Permutasi 3-Langkah & 5 Primitif Universal): Uji urutan Aksi_A -> Transfer/SelfCall -> Aksi_B atau Partial_Action -> Cancel -> Claim terhadap: (1) Kuantisasi Proporsi, (2) Transisi Paksa & Sabotase DoS, (3) Replay Otoritas/Signature, (4) Penyerahan Kontrol Eksekusi, dan (5) Lompatan Mesin Status.
3. Lapis 3 (Interogasi Guard-Bypass): Untuk setiap require/if (...) revert, cari apakah variabel di dalam penjaga tersebut dapat dimanipulasi oleh fungsi publik lain tanpa hak Admin.

---

## TAHAP B: Pengayaan Analogi Mekanis & Attacker POV dari references/
Panggil skill_view("sc-phase2-hunt", "<nama-file-ref>") sesuai tag [LOAD: ...]:
1. Terjemahkan istilah DeFi di dalam referensi sebagai Pola Mekanis Abstrak lintas domain.
2. Cocokkan kondisi fungsi target dengan Katalog Generalized Attacker POV (`[POV-XX]`) di bagian bawah file referensi tersebut untuk melihat bagaimana rangkaian peristiwa eksploitasi nyata bekerja pada kondisi state serupa.
   - **Fallback wajib:** bila file referensi **belum** memuat katalog `[POV-XX]`, JANGAN mengarang nomor POV. Turunkan ke analogi mekanis bebas (poin 1) dan catat di `audit/notes/` bahwa katalog POV untuk file tersebut belum tersedia. *(Katalog POV ditambahkan bertahap — ketiadaannya bukan cacat, jangan "diperbaiki" dengan entri karangan.)*

---

## TAHAP C: Pemisahan Murni (04-code-guarded.md vs 05-raw-leads.md)
Di Fase 2, Anda adalah Pemburu (Hunter), bukan Hakim Ekonomi. Jangan membuang anomali hanya karena terlihat kecil atau belum jelas keuntungannya (karena akan dirangkai menjadi *attack chain* di Putaran 2 atau diuji amplifikasinya di simulasi Fase 3):
1. Dua Larangan Fakta Dasar Kode: Jangan mengarang sifat palsu pada Token Kasta 1 (LP/Share token = ERC-20 standar, bukan *Fee-on-Transfer*/USDT) dan jangan mengasumsikan penyerang bisa memanggil fungsi onlyOwner secara langsung.
2. Jika Anomali Tidak Dihentikan oleh Guard Kode (atau Guard Bisa Ditembus):
   Tulis langsung ke `audit/05-raw-leads.md` lengkap dengan File:Kontrak:Fungsi (Baris), Prasyarat, Urutan Eksploitasi, dan Potensi Rantai Serangan (Chaining).
3. Jika Hipotesis Benar-Benar Dihentikan oleh Guard Kode (`require` / `if (...) revert` / `assert!`):
   Tulis langsung ke `audit/04-code-guarded.md` lengkap dengan lokasi File:Baris guard dan nama variabel pembentuk guard tersebut (sebagai umpan *Guard-Bypass* untuk Subagent Putaran 2).
4. Tandai kelompok fungsi di audit/03-attack-surface-queue.md menjadi [HUNTED].
