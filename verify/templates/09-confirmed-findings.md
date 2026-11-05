# 09 — Confirmed Findings (Bounty-Ready / Live Production Only)

Wadah murni untuk temuan berstatus `VALID_ELIGIBLE` yang lolos **kesebelas** Pernyataan di `verify/VERDICT.md`, terbukti lewat eksekusi simulasi PoC tanpa curang (`[PASS]`), membuktikan bahaya finansial nyata (Critical / High / Medium), **DAN** terbukti eksis pada bytecode/kontrak produksi aktif (`DEPLOYMENT_MATCH: LIVE_MATCH`).

> **GERBANG PEMISAHAN `09` (LIVE) VS `08` (HEAD-ONLY / PRE-LIVE) DI FASE 4:**
> - **Masuk ke `09` ini:** PoC `[PASS]` pada state produksi nyata (`Mode Uji: FORK_LIVE`, atau `FORK_DEPLOYED_HEAD` yang kodenya terverifikasi 100% identik dengan bytecode produksi aktif) dan kontrak masuk cakupan aktif (`LIVE_MATCH`). Istilah "100% identik" di sini **bukan** berarti hash bytecode sama persis — yang diuji adalah **keberadaan & perilaku entrypoint yang diserang PoC** (lihat `VERDICT.md` §0.2b).
> - **Pindahkan ke `08-valid-not-eligible.md`** (`LOW_CLASS: PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`): Apabila di Fase 3 PoC eksploitasi sudah terbukti `[PASS]` di atas kode repositori (`FORK_DEPLOYED_HEAD` / `LOKAL`), namun pada Rekonsiliasi Langkah 0 Fase 4 terbukti bahwa kontrak/fungsi tersebut belum di-deploy ke mainnet (`HEAD-only`) atau belum masuk daftar alamat bounty aktif (`[REPO_STAGED]`), Hakim Fase 4 **WAJIB** memindahkan temuan tersebut (lengkap dengan kode PoC utuhnya) ke `08-valid-not-eligible.md` — **BUKAN** dibiarkan di `09` dan **BUKAN** diparkir di `07`!

## Field wajib per entri

```markdown
## [LEAD-001] Judul Kerentanan & Lokasi
ID                  : LEAD-001
SEVERITY            : CRITICAL | HIGH | MEDIUM          <- DARI IMPACT, bukan dari siklus
VERDICT             : VALID_ELIGIBLE
TARGET_FILE         : 09-confirmed-findings.md
TANGGA_BUKTI        : A   (A-HEAD DILARANG di sini — A-HEAD = HEAD-only)
DEPLOYMENT_MATCH    : LIVE_MATCH
CYCLE               : P4_LIVE_FULL | P3_LIVE_PARTIAL     <- WAJIB; P1/P2 DILARANG di 09
ELIGIBILITY         : LIVE_MATCH                         <- WAJIB; nilai lain -> 08
LIVE_IDENTITY       : <identitas TERUKUR: accountId()/sha256 ProgramData/bytecode hash>
POC_STATUS          : PASS                               <- WAJIB literal PASS
Mode Uji            : FORK_LIVE (chain: <...>, block: <...>, RPC: <...>)
File:Baris          : <path/to/File.sol:Baris>
Metode / POV        : <M-00X / [POV-XX]>
Invarian Dilanggar  : <invarian inti dari 00-project-map.md>
DAMPAK KUANTITATIF  : <profit bersih penyerang / kerugian protokol dalam angka eksak>
```

> **`LIVE_IDENTITY` wajib TERUKUR, bukan disimpulkan.** Contoh sah: `accountId()` = `biconomy.nexus.1.3.3`; `sha256(ProgramData)` = `8190d3f7…` untuk Solana; hash bytecode impl EIP-1967. Nilai ini diambil dari artefak `deploy_parity` (`audit/notes/deploy-parity-<ID>.json`). **Tanpa `LIVE_IDENTITY` terukur, `LIVE_MATCH` ditolak** (Pernyataan #2 + `VERDICT.md` §0.2).
>
> **`TANGGA_BUKTI: A-HEAD` DILARANG di `09`.** A-HEAD berarti PoC dijalankan pada kode repo, bukan kontrak live — temuan semacam itu milik `08`. Kombinasi `A-HEAD` + `LIVE_MATCH` adalah kontradiksi yang ditolak otomatis oleh `verify/ingest.py`.
>
> **`CYCLE: P1_PRE_DEPLOY` / `P2_TESTNET_ONLY` DILARANG di `09`** — belum/tidak live di mainnet.

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
