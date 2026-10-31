---
name: sc-phase4-report
description: Phase 4 — Final Bounty-Grade Audit Report Polish and Strict 4-File Verification.
version: 4.4.0
---

# Phase 4: Final Bounty-Grade Audit Report & Quality Gate

Tujuan Fase 4 adalah melakukan audit kualitas terakhir terhadap keempat file keluaran (audit/04 s/d audit/07) agar siap diserahkan ke platform Bug Bounty tanpa ada satu pun temuan "Kondisi Istimewa" yang bocor ke dalam laporan utama.

---

## Langkah 1: Audit Kualitas Terakhir pada audit/07-confirmed-findings.md
Periksa kembali setiap temuan di dalam audit/07-confirmed-findings.md. Jika ditemukan temuan yang:
- Menggunakan Mock dengan perilaku palsu (*Fee-on-Transfer* pada LP/token standar, return boolean palsu, dll.),
- Mengasumsikan totalSupply == 0 pada pool yang sudah berjalan di produksi,
- Mengasumsikan Admin/Owner mengubah parameter menjadi nilai ekstrem,
- Hanya menghasilkan debu 1 wei tanpa DoS atau tanpa profit bersih (*Negative EV*), atau
- Menggunakan cheatcode curang (vm.store, vm.prank(owner)),
- Tidak memiliki bukti `Mode Uji: FORK (chain, block, RPC)` padahal chain target punya RPC publik yang dapat dipakai (atau memakai fork namun hasilnya tidak dicatat),
maka Anda WAJIB MENCABUT temuan tersebut dari audit/07-confirmed-findings.md dan memindahkannya ke audit/04-rejected-hypotheses.md!

---

## Langkah 2: Format Standar Setiap File Laporan (04 s/d 07 di audit/)

### 1. audit/07-confirmed-findings.md (Laporan Utama Siap Kirim Bounty)
Untuk setiap temuan yang 100% sah, tulis dengan struktur lengkap:
- Judul & Tingkat Keparahan: [CRITICAL / HIGH / MEDIUM] Judul Teknis Spesifik
- Lokasi Kode: File:Kontrak:Fungsi (Baris X-Y)
- Validasi Realitas Produksi: Jelaskan secara singkat mengapa skenario ini valid di produksi (aset apa yang dipakai, kondisi pool nyata, dan mengapa tidak memerlukan hak Admin).
- Akar Masalah (Root Cause) & Dampak Ekonomi Nyata: Jelaskan celah mutasi state/logika dan hitung dampak finansial bersihnya.
- Urutan Eksploitasi & Bukti PoC yang Dapat Direproduksi: Sertakan blok kode tes lengkap dan perintah eksekusinya.
- Rekomendasi Perbaikan (Diff/Patch): Berikan perbaikan kode minimal yang menutup celah tanpa merusak invarian lain.
### 2. audit/06-unproven-needs-review.md (Membutuhkan Tinjauan Manual)
Berisi hipotesis yang lolos 8 Gerbang Realitas dan secara kode terlihat rentan, namun eksekusi PoC lokalnya terhalang oleh kendala lingkungan/eksternal. Jelaskan apa yang sudah diuji dan apa yang perlu diverifikasi secara manual.

### 3. audit/05-raw-leads.md (Arsip Hipotesis Awal)
Pastikan setiap Lead di dalam file ini memiliki penanda status akhirnya ([CONFIRMED -> 07], [NEEDS-REVIEW -> 06], atau [REJECTED -> 04]).

### 4. audit/04-rejected-hypotheses.md (Catatan Hipotesis Gugur & Kondisi Istimewa)
Daftar ringkas seluruh hipotesis yang dibuang beserta alasan teknisnya (misal: *"Ditolak oleh Gerbang #1: LP Token adalah ERC-20 standar, tidak memiliki Fee-on-Transfer"* atau *"Ditolak oleh Guard pada baris X"*).

---

## Langkah 3: Ringkasan Eksekutif ke Pengguna
Setelah keempat file tersimpan rapi di audit/, tampilkan ringkasan eksekutif kepada pengguna yang memuat jumlah temuan di masing-masing file (07, 06, 05, 04) tanpa menyembunyikan apa pun.
