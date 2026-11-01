---
name: sc-phase4-report
description: Phase 4 — Final Verdict Judging (via verify/VERDICT.md) and Pure 6-File Audit Reporting (04 to 09).
version: 5.0.0
---

# Phase 4: Final Verdict Judging & Pure 6-File Audit Reporting (04–09)

Tujuan Fase 4 adalah bertindak sebagai Hakim Akhir (Bounty Judge) menggunakan standar /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md (memisahkan Pernyataan Ketat Mutlak vs Dalam Batasan) terhadap seluruh hasil Fase 3, lalu menyusun keenam file hasil (audit/04 s/d audit/09) secara bersih tanpa mencampur domain.

---

## Langkah 1: Eksekusi Vonis Akhir dengan /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md
1. **Wajib Baca Standar Hakim:** Panggil `read_file` pada `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md`.
2. **Jalankan Langkah 0 VERDICT.md lebih dulu — Rekonsiliasi Identitas Deployment (wajib, sebelum menilai apa pun):**
   Cocokkan kode yang dikutip dengan sumber terverifikasi explorer / `sha256`. Klaim yang hanya berlaku di HEAD — bukan di deployment produksi — wajib ditandai `HEAD-only` dan **maksimal berada di `07`**, tidak boleh diadili sebagai temuan.
3. **Adili Setiap Kandidat** di `audit/09-confirmed-findings.md` dan `audit/05-raw-leads.md`:
   Uji setiap kandidat terhadap 10 Pernyataan Wajib di VERDICT.md:
   - **Lolos Seluruh 10 Pernyataan (`VALID_ELIGIBLE`):** Terbukti lewat simulasi PoC pada fork state produksi (`Mode Uji: FORK`), tanpa *Fantasy Mock*/Cheatcode, dan membuktikan bahaya finansial nyata (pencurian dana, insolvensi, pembekuan aset permanen, atau sabotase repay/liquidate) -> Disahkan tetap di `audit/09-confirmed-findings.md`.
   - **Berada Dalam Batasan Toleransi / Low (`VALID_NOT_ELIGIBLE` — Pernyataan #7b, #8b, #10b):** Simulasi PoC jalan secara mekanis tanpa curang, tetapi dampaknya tergolong *"Annoying but not financially dangerous"* (`LOW_NUISANCE`: *DoS with no fund loss*, *minor capped economic damage*, *nuisance griefing* — #10b), merupakan *admin-only bug* tanpa jalur eksploitasi eksternal (#8b), atau fitur belum *live* (#7b) -> **WAJIB CABUT dari 09** dan pindahkan ke `audit/08-valid-not-eligible.md`!
   - **Berada Dalam Batasan Eksplorasi / Kendala RPC (`NEEDS_NEXT_STEP` — Pernyataan #9b):** Logika kode kuat namun butuh metode eksplorasi lanjut (`NEXT_EXPLORE`), butuh cek state mainnet (`NEXT_MAINNET`), belum diuji di fork karena kendala RPC/tooling (`TOOL_BLOCKED`), atau klaim masih `HEAD-only` (gagal #2) -> **WAJIB CABUT dari 09** dan pindahkan ke `audit/07-needs-next-step.md`!
   - **Melanggar Pernyataan Ketat Mutlak (`REJECTED_*` — Pernyataan #1–#6 beserta sub-kasus ketat #7a, #8a, #9a, #10a):** Memakai *Fantasy Mock* (#1), klaim produksi tanpa bukti kesetiaan deployment (#2), mengasumsikan `totalSupply == 0` pada pool *live* (#3), tidak ada korban rasional (#4), *Negative-EV* (#5), perilaku by-design / baris kode meleset (#6), menyerang `initialize()` terkunci (#7a), *privileged fantasy* (#8a), cheatcode / PoC gagal di state nyata (#9a), atau debu tanpa amplifikasi (#10a) -> **WAJIB CABUT dari 09** dan buang ke `audit/06-refuted-invalid.md`!
4. **Setiap vonis wajib memakai Format Keluaran `VERDICT.md`** (`ID`, `VERDICT`, `TARGET_FILE`, `ALASAN`, `BUKTI`, `TANGGA_BUKTI`, `DEPLOYMENT_MATCH`, `BIAYA-BACA`). Verdict tanpa `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH` dianggap belum sah.

---

## Langkah 2: Standarisasi Format Keenam File Murni (04 s/d 09)

1. `audit/09-confirmed-findings.md` (Murni `VALID_ELIGIBLE` — Siap Kirim Bounty):
   Memuat: Judul & Keparahan (CRITICAL/HIGH/MEDIUM), `Verdict: VALID_ELIGIBLE`, `Mode Uji: FORK (chain, block, RPC)`, Lokasi Kode & Invarian, Validasi Realitas Produksi, Akar Masalah & Dampak Finansial Kuantitatif, Kode PoC Utuh, Log Output, dan Patch Perbaikan (diff).
2. `audit/08-valid-not-eligible.md` (Murni `VALID_NOT_ELIGIBLE` — Valid dalam Batasan / Low):
   Memuat: ID, Lokasi, Sub-Kategori (`LOW_NUISANCE` | `ADMIN_ONLY` | `PRE_LIVE_SCOPE`), Bukti Simulasi PoC, dan alasan teknis mengapa masuk batas toleransi 08 (bukan 09).
3. `audit/07-needs-next-step.md` (Murni `NEEDS_NEXT_STEP` — Belum Selesai Diuji):
   Memuat: ID, Lokasi, Label Disposisi (`NEXT_EXPLORE` | `NEXT_MAINNET` | `TOOL_BLOCKED`), ringkasan apa yang sudah diuji di Fase 3, dan langkah konkret selanjutnya.
4. `audit/06-refuted-invalid.md` (Murni `REJECTED_*` — Gugur Permanen di Fase 3/4):
   Memuat: ID, Asal Lead, Kelas Vonis (`REJECTED_FANTASY_MOCK`, `REJECTED_POC_FAILS`, dll.), nomor Pernyataan `VERDICT.md` yang dilanggar, dan bukti penolakannya.
5. `audit/05-raw-leads.md` (Rekonsiliasi Status Antrean):
   Pastikan setiap `LEAD-XXX` memiliki penanda hasil akhirnya: `[STATUS -> 09]`, `[STATUS -> 08]`, `[STATUS -> 07]`, atau `[STATUS -> 06]`.
6. `audit/04-code-guarded.md` (Arsip Guard Kode dari Fase 2):
   Daftar hipotesis Fase 2 yang dihentikan oleh `require` / `if (...) revert` beserta status apakah berhasil ditembus di Putaran 2 atau tetap tertahan guard.

---

## Langkah 3: Ringkasan Eksekutif ke Pengguna
Tampilkan tabel ringkasan akhir kepada pengguna yang merinci jumlah item di masing-masing file (04, 05, 06, 07, 08, dan 09), beserta daftar kandidat yang dipindahkan oleh Hakim `VERDICT.md` dari 09 ke 08, 07, atau 06.
