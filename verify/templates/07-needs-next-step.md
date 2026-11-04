# 07 — Needs Next Step

Mekanisme nyata & PoC jujur, tetapi **belum dapat diputuskan** karena: butuh fork produksi, RPC/tooling terblokir, verifikasi mainnet lanjutan, atau **kendala komputasi/RPC ekstrem setelah 3-Step Self-Healing**. *(Catatan: temuan `HEAD-only` yang PoC-nya sudah `[PASS]` wajib masuk `08` sebagai `PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN`, **bukan** `07`; dan temuan berdampak Low juga masuk `08`.)*

> **GARIS PEMISAH `07` vs `08` — WAJIB DIBACA SEBELUM MENGISI ENTRI:**
> - **HEAD-only yang BELUM DIUJI** (RPC mati, tooling gagal, fork belum sempat dinyalakan) **tetap boleh** dicatat sebagai pekerjaan tertunda di `07` — asalkan pengujiannya memang **belum selesai** dan blok `PERCOBAAN:` membuktikan usaha yang sudah ditempuh.
> - **HEAD-only yang PoC-nya sudah `[PASS]` WAJIB masuk `08`** sebagai `LOW_CLASS: PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)` — lengkap dengan kode PoC utuh dan dampak kuantitatifnya. Temuan yang sudah terbukti **tidak boleh** diparkir di `07`.
> - **`07` DILARANG** dipakai untuk menyembunyikan temuan yang sudah terbukti, atau untuk menghindari kewajiban menyimpan PoC di `08`.

> **Target akhir `07` = 0 entri.** Setiap sisa wajib dipertahankan dengan log komputasi, bukan kalimat.
> Entri tanpa `Disposition:` **atau** tanpa blok `PERCOBAAN:` → `LAZY_BAILOUT_DETECTED`
> (Pernyataan #11) → **laporan DITOLAK** dan lead dikembalikan ke Fase 3.

---

## Field wajib per entri

Salin kerangka ini apa adanya. Semua field wajib terisi — `Disposition:` dan `PERCOBAAN:` **tidak boleh dihilangkan**.

```text
ID                 : <id>
VERDICT            : NEEDS_NEXT_STEP
Disposition        : NEXT_EXPLORE | NEXT_MAINNET | TOOL_BLOCKED   <- WAJIB, pilih tepat satu
TARGET_FILE        : 07-needs-next-step.md
ALASAN             : <1-2 kalimat: mengapa belum tuntas, rujuk Pernyataan #9b>
BUKTI              : <ringkasan mekanisme & titik terhenti>
TANGGA_BUKTI       : B | C   *(A / A-HEAD yang sudah PASS tidak sah di sini — wajib ke 09 atau 08)*
DEPLOYMENT_MATCH   : LIVE_MATCH | HEAD-only (PROVEN_ON_REPO_HEAD) | UNVERIFIED (<sebut sumber yang gagal>)
PERCOBAAN:
  $ <perintah nyata yang dijalankan beserta log keluarannya>
LANGKAH BERIKUTNYA : <aksi konkret untuk menuntaskan pengujian>
```

**`PERCOBAAN:` bukan rencana.** Isinya perintah yang sudah dijalankan **beserta keluarannya**.
Menulis `$ forge test ...` tanpa output = pelanggaran #11.

---

## Format Wajib per Entri 07 (varian heading — sah, setara dengan blok di atas)

Dua bentuk diperbolehkan: blok field `ID : ...` (di atas) **atau** heading `## [ID-LEAD]` (di bawah).
Keduanya wajib memuat himpunan field yang **sama persis**. Hakim menerima keduanya; mencampur
sebagian field dari satu bentuk dan sebagian dari bentuk lain tidak sah.

```markdown
## [ID-LEAD] Judul Singkat Hipotesis
- VERDICT: NEEDS_NEXT_STEP
- Disposition: NEXT_EXPLORE | NEXT_MAINNET | TOOL_BLOCKED
- File & Baris: <path:baris>
- TANGGA_BUKTI: B | C
- DEPLOYMENT_MATCH: LIVE_MATCH | HEAD-only (PROVEN_ON_REPO_HEAD) | UNVERIFIED (<sumber gagal>)
- Ringkasan Mekanisme & Alasan Belum Tuntas: <...>
- PERCOBAAN:
  - Perintah yang dijalankan: $ ...
  - Hasil / Log keluaran: <...>
- Langkah Konkret Berikutnya: <...>
```

**Validasi cepat (dijalankan Hakim / Parent sebelum menerima entri):**

Gunakan alat fence-aware — **jangan** pakai `grep -c '^## \['` mentah, karena heading contoh
di dalam blok kode ikut terhitung (false positive).

```bash
python3 /home/ubuntu/.hermes/profiles/adv/verify/tools/verify07.py <file.md>          # ringkasan
python3 /home/ubuntu/.hermes/profiles/adv/verify/tools/verify07.py <file.md> --json   # mesin
# exit 0 = semua entri sah · 1 = ada LAZY_BAILOUT_DETECTED · 2 = file tidak terbaca
```

Alat ini memeriksa tiga hal wajib per entri: tepat **satu** `Disposition:`, ada blok
`PERCOBAAN:` yang memuat **baris perintah** (`$ ...` / `Perintah yang dijalankan:`), dan
ada field langkah berikutnya. Ia toleran terhadap ragam penulisan bold/backtick yang
dipakai di audit nyata (`- **Disposition:** `NEXT_MAINNET``).

---

## Bukti wajib per `Disposition`

| `Disposition` | Blok `PERCOBAAN:` wajib memuat | Tanpa ini |
|---|---|---|
| `NEXT_EXPLORE` | Log **Tier 2** (handler stateful fuzzing) / **Tier 3** (differential split-vs-bulk) / **Tier 5** (halmos/symbolic) yang **berjalan sampai timeout komputasi** — sertakan waktu run & jumlah iterasi | `LAZY_BAILOUT_DETECTED` |
| `TOOL_BLOCKED` | Log terminal **ketiga** anak tangga: **(1)** flag/remapping/toolchain (`--via-ir`, `--optimize`, `--evm-version`, `cargo-build-sbf`, versi compiler) -> **(2)** standalone interface-only / minimal harness -> **(3)** fallback RPC (`.env.rpc`, `rpc-env.sh`, chunking `eth_getLogs`) | `LAZY_BAILOUT_DETECTED` |
| `NEXT_MAINNET` | Bukti rantai/explorer **benar-benar tidak tersedia** (endpoint mati, chain tanpa RPC publik, kontrak belum ter-deploy). **Bila RPC tersedia, `07` tidak sah** — jalankan `cast call`/`cast storage`/`cast implementation` saat itu juga dan tuntaskan ke `09`/`06`/`08` | `LAZY_BAILOUT_DETECTED` |

---

## Contoh entri SAH

```
ID                : L3-03
VERDICT           : NEEDS_NEXT_STEP
Disposition       : TOOL_BLOCKED
TARGET_FILE       : 07-needs-next-step.md
ALASAN            : Kode di HEAD memperlihatkan jalur, tetapi bytecode ter-deploy berbeda
                    (Pernyataan #2). Build SBF gagal di host aarch64 sehingga bytecode lokal
                    tidak dapat dibandingkan dengan program on-chain.
BUKTI             : Source HEAD memuat instruksi yang tidak ada di program ter-deploy;
                    tidak bisa disimpulkan sebagai bug produksi.
TANGGA_BUKTI      : C
DEPLOYMENT_MATCH  : HEAD-only (PROVEN_ON_REPO_HEAD) — sha256 repo != program on-chain
PERCOBAAN:
  $ FOUNDRY_JOBS=1 forge test --match-path test/U9_X.t.sol --via-ir -j 1
  Error: Compiler run failed: Error (8936): Identifier-start is not allowed at end of a number.
  $ cargo-build-sbf --manifest-path programs/spell/Cargo.toml
  error: no binari aarch64-unknown-linux-gnu; x86_64 via qemu -> EXIT 137 setelah 84 menit
  $ cast call $PROGRAM --rpc-url $FALLBACK "getProgramData()"
  Error: RPC timeout after 30s (3 endpoint dicoba)
LANGKAH BERIKUTNYA : Jalankan `cargo-build-sbf` di host x86_64 native (bukan qemu), lalu
                    bandingkan sha256 `target/deploy/*.so` dengan program on-chain.
```

---

## Contoh entri DITOLAK (pelanggaran #11)

```
ID                : L3-08
VERDICT           : NEEDS_NEXT_STEP
ALASAN            : Perlu multi-step chaining untuk memastikan dampak.
LANGKAH BERIKUTNYA: Perlu investigasi lebih lanjut.
```

Tidak ada `Disposition:`, tidak ada `PERCOBAAN:`, dan "langkah berikutnya" bukan aksi.
Hasil: `LAZY_BAILOUT_DETECTED` — entri ini **bukan** hasil audit yang sah.
