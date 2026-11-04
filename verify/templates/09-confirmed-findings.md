# 09 — Confirmed Findings (Bounty-Ready / Live Production Only)

Wadah murni untuk temuan berstatus `VALID_ELIGIBLE` yang lolos **kesebelas** Pernyataan di `verify/VERDICT.md`, terbukti lewat eksekusi simulasi PoC tanpa curang (`[PASS]`), membuktikan bahaya finansial nyata (Critical / High / Medium), **DAN** terbukti eksis pada bytecode/kontrak produksi aktif (`DEPLOYMENT_MATCH: LIVE_MATCH`).

> **GERBANG PEMISAHAN `09` (LIVE) VS `08` (HEAD-ONLY / PRE-LIVE) DI FASE 4:**
> - **Masuk ke `09` ini:** PoC `[PASS]` pada state produksi nyata (`Mode Uji: FORK_LIVE`, atau `FORK_DEPLOYED_HEAD` yang kodenya terverifikasi 100% identik dengan bytecode produksi aktif) dan kontrak masuk cakupan aktif (`LIVE_MATCH`).
> - **Pindahkan ke `08-valid-not-eligible.md`** (`LOW_CLASS: PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`): Apabila di Fase 3 PoC eksploitasi sudah terbukti `[PASS]` di atas kode repositori (`FORK_DEPLOYED_HEAD` / `LOKAL`), namun pada Rekonsiliasi Langkah 0 Fase 4 terbukti bahwa kontrak/fungsi tersebut belum di-deploy ke mainnet (`HEAD-only`) atau belum masuk daftar alamat bounty aktif (`[REPO_STAGED]`), Hakim Fase 4 **WAJIB** memindahkan temuan tersebut (lengkap dengan kode PoC utuhnya) ke `08-valid-not-eligible.md` — **BUKAN** dibiarkan di `09` dan **BUKAN** diparkir di `07`!

## Field wajib per entri

```markdown
## [LEAD-001] Judul Kerentanan & Lokasi
ID                  : LEAD-001
SEVERITY            : CRITICAL | HIGH | MEDIUM
VERDICT             : VALID_ELIGIBLE
TARGET_FILE         : 09-confirmed-findings.md
TANGGA_BUKTI        : A (atau A-HEAD bila bytecode identik LIVE_MATCH, atau B khusus non-EVM native runtime tanpa fork RPC)
DEPLOYMENT_MATCH    : LIVE_MATCH (<alamat kontrak & bukti kecocokan bytecode/source>)
Mode Uji            : FORK_LIVE (chain: <...>, block: <...>, RPC: <...>)
File:Baris          : <path/to/File.sol:Baris>
Metode / POV        : <M-00X / [POV-XX]>
Invarian Dilanggar  : <invarian inti dari 00-project-map.md>
DAMPAK KUANTITATIF  : <profit bersih penyerang / kerugian protokol dalam angka eksak>
```

## Bagian Naratif & Bukti Teknis Wajib (di bawah blok metadata tiap entri)

1. **Validasi Realitas Produksi & Identitas Deployment:**
   Bukti alamat kontrak aktif di mainnet, nilai parameter/storage produksi saat diuji (`cast call` / `cast storage`), dan konfirmasi tidak ada asumsi *Fantasy Mock* maupun *Empty-Pool Mirage*.
2. **Akar Masalah (*Root Cause*) & Urutan Eksploitasi:**
   Penjelasan presisi baris kode yang cacat beserta langkah transaksi dari *Victim Lifecycle Seeding* hingga ekstraksi nilai.
3. **Kode PoC Utuh yang Dapat Direproduksi:**
   Kode test lengkap (`foundry` / `cargo test` / `sui move test` / `@ton/sandbox`) tanpa *cheatcode* terlarang (`vm.store`, `vm.etch` state protokol, `vm.prank(admin)`).
4. **Perintah Eksekusi & Log Terminal `[PASS]`:**
   Perintah eksak (`FOUNDRY_JOBS=1 forge test --match-test ... -vvv`) beserta kutipan log yang mencetak saldo sebelum/sesudah dan `[PASS]`.
5. **Rekomendasi Perbaikan (*Patch Diff*):**
   Blok diff minimal pada kontrak sumber yang menutup akar masalah tanpa merusak invarian lain.

_(kosong)_
