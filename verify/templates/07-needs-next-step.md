# 07 — Needs Next Step

Mekanisme nyata & PoC jujur, tetapi **belum dapat diputuskan** karena: butuh fork produksi,
RPC/tooling terblokir, verifikasi mainnet lanjutan, atau klaim masih `HEAD-only`
(gagal Pernyataan #2/#9b). **Bukan** tempat untuk temuan ber-dampak Low (itu `08`).

> **Target akhir `07` = 0 entri.** Setiap sisa wajib dipertahankan dengan log komputasi, bukan kalimat.
> Entri tanpa `Disposition:` **atau** tanpa blok `PERCOBAAN:` → `LAZY_BAILOUT_DETECTED`
> (Pernyataan #11) → **laporan DITOLAK** dan lead dikembalikan ke Fase 3.

---

## Field wajib per entri

Salin kerangka ini apa adanya. Semua field wajib terisi — `Disposition:` dan `PERCOBAAN:` **tidak boleh dihilangkan**.

```
ID                : <LEAD/L-xx, mis. L3-03>
VERDICT           : NEEDS_NEXT_STEP
Disposition       : <NEXT_EXPLORE | NEXT_MAINNET | TOOL_BLOCKED>   <- WAJIB, pilih tepat satu
TARGET_FILE       : 07-needs-next-step.md
ALASAN            : <1-2 kalimat: mengapa belum tuntas, rujuk Pernyataan #9b>
BUKTI             : <apa yang sudah terbukti sejauh ini>
TANGGA_BUKTI      : <B | C>   (A tidak sah di sini — A sudah bisa ke 09)
DEPLOYMENT_MATCH  : <sha256 sama | source explorer cocok | BEDA -> HEAD-only | tidak terverifikasi (sebut sumber yang gagal)>
PERCOBAAN:
  $ <perintah terminal yang BENAR-BENAR dijalankan>
  <keluaran / error / log — potongan apa adanya, bukan parafrase>
LANGKAH BERIKUTNYA : <aksi konkret & spesifik, bukan "perlu investigasi lebih lanjut">
```

**`PERCOBAAN:` bukan rencana.** Isinya perintah yang sudah dijalankan **beserta keluarannya**.
Menulis `$ forge test ...` tanpa output = pelanggaran #11.

---

## Format Wajib per Entri 07 (varian heading — sah, setara dengan blok di atas)

Dua bentuk diperbolehkan: blok field `ID : ...` (di atas) **atau** heading `## [ID-LEAD]` (di bawah).
Keduanya wajib memuat himpunan field yang **sama persis**. Hakim menerima keduanya; mencampur
sebagian field dari satu bentuk dan sebagian dari bentuk lain tidak sah.

```markdown
## [<ID-LEAD>] Judul Singkat Hipotesis
- VERDICT: NEEDS_NEXT_STEP
- Disposition: NEXT_EXPLORE | NEXT_MAINNET | TOOL_BLOCKED
- File & Baris: <PathFile:Baris>
- TANGGA_BUKTI: B | C
- DEPLOYMENT_MATCH: MATCH | HEAD-only | UNVERIFIED (<sumber gagal>)
- Ringkasan Mekanisme & Alasan Belum Tuntas: <penjelasan singkat>
- PERCOBAAN:
  - Perintah yang dijalankan: <perintah lengkap forge / cargo / halmos / cast>
  - Hasil / Log keluaran: <ringkasan presisi log terminal: jumlah runs/timeout fuzzer,
    atau log 3 usaha self-healing, atau bukti ketiadaan RPC>
- Langkah Konkret Berikutnya: <apa yang diperlukan untuk menuntaskan ke 09 atau 06>
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
DEPLOYMENT_MATCH  : BEDA -> HEAD-only (sha256 repo != program on-chain)
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
