---
name: sc-phase3-verify-and-poc
description: Phase 3 — Dynamic Registry-Routed Harness Design (M-001..M-NNN & [POV-XX]), Dual-Mode Fork Simulation (FORK_LIVE & FORK_DEPLOYED_HEAD) with Victim Seeding, 2-Manual + 1-Fuzz Escalation, and Pure Mechanism Staging (06, 07, 09).
version: 6.4.1
---

# Phase 3: Simulation-First Sanity Check & Local Fork Exploit Lab

Tujuan Fase 3 adalah menguji setiap hipotesis di audit/05-raw-leads.md di dalam laboratorium simulasi eksekusi nyata (Dual-Mode Fork: `FORK_LIVE` untuk kontrak produksi aktif, atau `FORK_DEPLOYED_HEAD` untuk kode repositori di atas state rantai nyata), dilengkapi *Realistic Victim Lifecycle Seeding* dan *Fuzzing Escalation*, lalu mendistribusikan hasilnya (via `audit/notes/staging-<id>.md`) ke tiga wadah murni: audit/06-refuted-invalid.md, audit/07-needs-next-step.md, atau audit/09-confirmed-findings.md — **penulisan ke ketiga wadah itu dilakukan Parent, bukan Subagent**.

**HUKUM INTI FASE 3 (SIMULATION-FIRST & BLIND TO BOUNTY SCOPE):**

1. **DILARANG menyentuh `08-valid-not-eligible.md` di Fase 3.** Pemisahan administratif apakah kontrak masih *pre-live* (HEAD-only), *admin-only*, atau berdampak *Low* adalah wewenang eksklusif Hakim Fase 4 (`VERDICT.md`) **setelah** mekanisme berhasil dibuktikan.
2. **Hukum *No Code, No Reject*:** DILARANG KERAS menggugurkan lead logika, matematika, pembulatan, likuidasi, atau transisi state ke `06` hanya dengan hitungan kertas atau baca kode sekilas **tanpa menjalankan kode test** (`forge test` / `cargo test` / `sui move test`).

**GERBANG TULIS (WAJIB):** sebelum menulis satu byte pun ke `audit/*.md` atau `notes/staging-*`, baca **`workspace/AGENTS.md` Pasal 1.3 (Protokol Anti-Truncate & Metode Write)**. `open(path,"w")` dan `>` shell **DILARANG**; untuk `05`/`07` gunakan `append` lalu `patch` saat status berubah, untuk `06`/`08`/`09` cukup `append`.

---

## Langkah 0b: Anti-Rabbit-Hole & Anti-Premature-Death — Protokol 2-Manual + 1-Fuzz Escalation (WAJIB)

### 0b.0 — LARANGAN MELABELI SEVERITY DI FASE 3 (WAJIB)

Fase 3 adalah **hunter**, bukan **classifier**. Menilai severity di tengah pencarian memecah fokus dari membangun harness dan menjalankan PoC, dan menghasilkan label tidak konsisten antar-lead (lead ke-3 dinilai dengan konteks berbeda dari lead ke-12).

**DILARANG menulis label severity di Fase 3:** `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `dust`, `griefing`, `informational`, `admin-only` — baik di `notes/lead-<id>.md`, staging, maupun `05-raw-leads.md`.

**Sebagai gantinya, catat DUA BARIS FAKTA** (objektif, tidak butuh rubrik, sudah jadi bagian kerja Fase 3):

```
Impact-facts : <apa yang TERUKUR di log, angka bukan label>
               contoh: "tidak ada dana berpindah; gas 24.536 terbuang; loop tidak maju"
               contoh: "attacker +1.000.000e18; korban 0; saldo pool turun 100%"
Pemicu       : <siapa yang bisa memicu, fakta bukan Likelihood>
               contoh: "EOA mana pun, tanpa role, calldata publik"
               contoh: "hanya pemegang STATE_UPDATER_ROLE (EOA tunggal)"
```

**Penerjemahan fakta ke severity dan wadah adalah wewenang EKSKLUSIF Fase 4** (`sc-phase4-report` Langkah 0.3b), memakai rubrik `verify/SEVERITY-RUBRIC.md` (satu folder dengan `VERDICT.md`). Diputuskan sekali untuk semua lead dengan rubrik yang sama, sehingga konsisten. Bila platform berubah, cukup ubah di Fase 4 — catatan Fase 3 tidak perlu ditulis ulang.

**Alasan aturan ini:** pada audit nyata, agen menulis "griefing maksimal, bukan temuan" dan "LOW/informational" langsung di catatan Fase 3, lalu label itu diwarisi Fase 4 tanpa ditinjau — sehingga 4 temuan Low yang sah tidak pernah masuk laporan, padahal platform menilai dengan OWASP yang membayar Low.

Aturan ini mengikat **setiap lead** di `audit/05-raw-leads.md`: mencegah agen terjebak di satu lead tanpa batas, sekaligus melarang agen mematikan lead terlalu cepat hanya karena salah menebak angka manual.

### 1. Hitungan Strike & Kewajiban Eskalasi Fuzz pada Strike 3

Strike dihitung **per lead**, bukan per berkas dan bukan per sesi:

- **Strike 1 (Manual Sequence & Victim Seeding)** — percobaan PoC deterministik pertama gagal (`revert` karena guard, `assert` tidak terpenuhi, atau selisih profit $\le 0$).
- **Strike 2 (Perbaikan Setup Siklus Korban / Urutan Aksi / 3-Way Amplification)** — percobaan manual kedua dengan penyesuaian state korban (`vm.prank(victim)`), *flashloan scaling*, atau urutan transaksi juga gagal.
- **Strike 3 WAJIB (Mandatory Parameter Fuzzing / Symbolic Counterexample)** — **DILARANG** membuang lead ke `06` setelah Strike 2 tanpa menjalankan minimal 1× tes Fuzz (`testFuzz_...` di Foundry / `proptest` di Rust / `halmos`)! Biarkan mesin fuzzer mengacak parameter input (`amount`, `shares`, `timeDelta`, `splitCount`) untuk memastikan kegagalan Strike 1 & 2 **bukan** akibat salah pilih angka manual.

> Perbaikan **infrastruktur** (compile error, import salah, checksum alamat, salah ABI, salah offset decode) **BUKAN strike** — itu kegagalan alat, bukan kegagalan hipotesis.

### 2. Aksi Wajib Setelah Strike Ketiga (Fuzz Gagal)

Hanya setelah **Strike 1 (Manual) + Strike 2 (Manual/Amplifikasi) + Strike 3 (Fuzzing)** seluruhnya gagal membuktikan pelanggaran invarian, agen **WAJIB**:

1. Berhenti menyentuh lead tersebut.
2. Tulis entri ke **staging** untuk `audit/06-refuted-invalid.md` dengan vonis `REJECTED_POC_FAILS` (atau `REJECTED_NEGATIVE_EV` / `REJECTED_DUST`), **wajib melampirkan perintah dan ringkasan log eksekusi ketiga percobaan** (termasuk jumlah *runs* pada Strike 3 Fuzz).
3. Menulis 1 baris di `audit/notes/fase3-strikes.md`: **`"3-STAGE BREAKER TRIPPED"`**, nama lead, dan `berkas:baris`.
4. **Wajib pindah** ke berkas/hipotesis lain.

### 3. Larangan Iterasi Keempat & Syarat Buka Kembali

**DILARANG** melakukan iterasi ke-4 pada hipotesis yang sama sebelum **seluruh lead lain** di `05-raw-leads.md` selesai diuji. Lead boleh dibuka kembali **hanya** bila ada **bukti baru yang material** (kombinasi *chaining* dengan lead lain yang sudah lolos uji, atau penemuan jalur mutasi variabel baru).

### 4. Format Pencatatan Strike

```
<LEAD-ID> | <berkas:baris> | Strike 1: <sebab> | Strike 2: <sebab> | Strike 3 Fuzz: <perintah> | runs: <n> | STATUS: TRIPPED/BELUM
```
Lead tanpa entri strike berarti **belum diuji sama sekali** — bukan berarti bersih. Strike 3 tanpa `runs: <n>` dianggap tidak dijalankan.

### 5. Anggaran Waktu per Lead

Sebelum meninggalkan satu lead, catat di `audit/notes/fase3-strikes.md` berapa **jumlah percobaan** dan **berapa berkas lain yang masih `BELUM`** di `00b-file-inventory.md`. Bila percobaan > 3 sementara berkas `BELUM` masih > 0, itu pelanggaran aturan dan wajib dilaporkan sebagai kegagalan proses.

---

## Langkah 0c: Anti-Menyerah #1 — Tangga Self-Healing Tooling (Syarat Mutlak Sebelum `TOOL_BLOCKED`)

Label `TOOL_BLOCKED` **DILARANG** dipakai untuk masalah kompilasi dependency, remapping, versi compiler, atau kegagalan test runner repo target. Kondisi itu bukan batas ekplorasi — itu pekerjaan yang belum dikerjakan.

Jika build/test bawaan repo bermasalah, agen **WAJIB** menaiki tangga eskalasi mandiri berikut secara berurutan, dan mencatat hasil tiap anak tangga di `audit/notes/`:

### Usaha 1 — Perbaikan Konfigurasi Lokal Sementara
Sesuaikan flag eksekusi sebelum menyimpulkan apa pun:
- Compiler/optimizer: `--via-ir`, `--optimize`, `--optimize-runs`, `--evm-version`.
- Remappings: lewat command line atau `foundry.toml` **terisolasi di folder test**, jangan mengubah konfigurasi repo target.
- Dependency: instal paket yang kurang bila environment mengizinkan.
- Non-EVM: `cargo-build-sbf` (bukan `cargo build --release`), `anchor build`, `anchor test --skip-local-validator`.
- Versi toolchain: bila repo mengunci versi tertentu, pakai `rust-toolchain.toml` / `foundry.toml` terpisah, bukan menimpa milik repo.

### Usaha 2 — Standalone Minimal Harness / Interface-Only Test
Jika _seluruh_ repo gagal dikompilasi karena satu sub-modul rusak, **JANGAN menyerah**. Buat **1 file test mandiri** yang:
- hanya mendeklarasikan `interface` kontrak target (signature fungsi yang diserang saja), **atau**
- hanya mengimpor 1–2 berkas kontrak relevan tanpa seluruh pohon dependency,

lalu tembak langsung alamat kontraknya di Local Fork, atau deploy kontrak tunggal tersebut di sandbox terisolasi. Untuk non-EVM: harness program tunggal + akun uji, tanpa workspace penuh.

Pola ini sudah terbukti: kendala workspace bisa dilewati dengan interface-only + fork call, dan hasilnya tetap sah selama `Mode Uji: FORK` dan tanpa cheatcode.

### Usaha 3 — Fallback RPC & Off-Chain State Read
Jika satu URL RPC gagal / rate-limited / membatasi `eth_getLogs`:
- baca seluruh variabel di `./rpc-env.sh` dan `.env.rpc`, cek `RPC-STATUS.md`,
- gunakan endpoint publik alternatif yang sah untuk rantai tersebut,
- untuk rentang log besar, pakai chunking + binary search alih-alih menyerah,
- bila data memang off-chain, lakukan rekonstruksi dari event on-chain lebih dulu sebelum menyatakan butuh repo privat.

### Hukum Besi `TOOL_BLOCKED`
Sebuah lead **HANYA sah** masuk `07` dengan label `TOOL_BLOCKED` jika **ketiga** usaha di atas sudah dijalankan **dan log terminal kegagalannya dilampirkan di dalam entri `07`** (perintah yang dijalankan + pesan error apa adanya).

> Mengklaim "masalah kompilasi dependency" tanpa mencoba *Standalone Interface / Minimal Harness* adalah **pelanggaran konstitusi**. Entri `07` tanpa lampiran log ketiga usaha ditolak dan lead dikembalikan ke antrean.

**Bukan `TOOL_BLOCKED`** (jangan salah label): hipotesis yang sudah diuji dan ditolak alam → `06` `REJECTED_POC_FAILS`; alat yang belum terpasang tetapi bisa dipasang → tetap di antrean, bukan `07`.

---

## Langkah 0d: Anti-Menyerah #2 — Hukum "Kerjakan Sekarang" (Anti-Procrastination `NEXT_MAINNET` & `NEXT_EXPLORE`)

`NEXT_MAINNET` dan `NEXT_EXPLORE` adalah **tempat parkir untuk hal yang mustahil dilakukan sekarang** — bukan untuk hal yang belum dikerjakan. Keduanya DILARANG dipakai selama pekerjaan itu **bisa diselesaikan pada sesi ini juga**.

### 1. Larangan `NEXT_MAINNET` Malas
**DILARANG** menulis `Disposition: NEXT_MAINNET` dengan alasan *"butuh cek parameter/storage/proxy di mainnet"* bila RPC rantai tersebut **tersedia**. RPC publik bukan hambatan — gunakan langsung:
```bash
cast call <addr> "<sig>" --rpc-url <RPC>
cast storage <addr> <slot> --rpc-url <RPC>
cast implementation <proxy> --rpc-url <RPC>      # EIP-1967
cast admin <proxy> --rpc-url <RPC>
curl -s <RPC> -d '{"jsonrpc":"2.0",...}'
```
Lalu **tuntaskan vonis pada sesi yang sama**: ke `09` bila terbukti dan eligible, atau `06` bila terbantah. Membaca state live adalah pekerjaan menit, bukan pekerjaan minggu.

**`NEXT_MAINNET` hanya sah bila:** kontrak belum di-deploy sama sekali, atau rantai target benar-benar tidak punya akses RPC/explorer publik (dan Usaha 3 Langkah 0c sudah gagal dengan log).

### 2. Larangan `NEXT_EXPLORE` Malas
**DILARANG** menulis `Disposition: NEXT_EXPLORE` dengan alasan *"butuh multi-step chaining"*, *"butuh Stateful Fuzzing"*, atau *"butuh Halmos"* bila yang sudah dicoba baru **satu skenario sederhana**. Agen **WAJIB langsung menulis dan menjalankan** pada sesi yang sama:
- **Multi-step chaining** — rangkai ≥2 aksi/lead dalam satu transaksi atau satu blok.
- **Differential Test (Tier 3)** — bandingkan jalur A vs jalur B yang seharusnya setara.
- **Handler Fuzzing (Tier 2)** — invariant handler + `foundry.fuzz.runs` yang wajar.
- **Symbolic proving (Tier 5)** bila invariant bersifat aritmetis (`halmos --function check_*`).

`NEXT_EXPLORE` **hanya sah** bila tes di atas sudah **dijalankan** (lampirkan perintah + keluarannya) dan mencapai **timeout komputasi tanpa konklusi** — bukan karena belum dicoba.

### 3. Hukum Besi untuk Kedua Label
Setiap entri `07` berlabel `NEXT_MAINNET` atau `NEXT_EXPLORE` **WAJIB** memuat **bukti percobaan** berupa blok:
```
PERCOBAAN:
  <perintah yang dijalankan>
  <keluaran / error / statistik fuzz / waktu timeout>
HASIL: masih terbuka karena <sebab yang tidak bisa diselesaikan sekarang>
```
Entri tanpa blok `PERCOBAAN` **ditolak** dan lead dikembalikan ke antrean untuk dikerjakan.

> Beda tegas: **`NEXT_EXPLORE` bukan `07` versi sopan dari `06`.** Bila setelah fuzzing/chaining hasilnya tetap negatif, lead pindah ke `06` `REJECTED_POC_FAILS` — bukan dibiarkan menggantung di `07`.

---

## Langkah 0e: Re-Read Pass Bersyarat — Verifikasi Hipotesis Sebelum PoC (WAJIB)

Fase 2 sudah membaca kode untuk **membentuk** lead. Fase 3 membaca kode yang sama untuk **membuktikan** lead. Kode tidak berubah — **pertanyaannya yang berubah**: Fase 2 bertanya "apakah ada celah?", Fase 3 bertanya "apakah celah ini benar-benar dieksekusi?".

**Wajib Re-Read Pass bila SALAH SATU terpenuhi:**
1. Lead mengandung **klaim negatif** ("tidak ada guard", "X tidak dipanggil", "tidak ada validasi").
2. Lead akan **digugurkan** (`06`). Menggugurkan tanpa membaca utuh adalah cara termahal untuk salah.
3. Fungsi target **> 60 baris**.
4. Anda **tidak ingat** isi fungsi itu secara utuh.

**Tidak wajib** bila: lead positif sederhana, fungsi pendek, dan rentang baca Fase 2 tercatat lengkap — sebutkan rujukannya di notes.

**Prosedur:**
1. Buka fungsi target, baca **utuh** dari `function` sampai `}` penyeimbang (`read_file` ber-`offset`/`limit`, bukan `sed|tail`).
2. Catat `File:awal-akhir` + jumlah baris di `notes/fase3-bukti-simulasi.md`.
3. Bandingkan dengan klaim lead: **cocok**, **sebagian**, atau **bertentangan**.
4. Bila bertentangan → lead **DILARANG** di-PoC apa adanya; tulis ke `06` sebagai `REJECTED_MISMATCH` dan lanjut ke lead berikutnya.

**Insiden yang melahirkan aturan ini:** `_fallback` di `ModuleManager.sol` diklaim "tidak pernah memanggil `postCheck`" dan masuk `05` sebagai lead kuat. Re-Read Pass membuktikan `postCheck` dipanggil sebelum `return` dan men-revert `PolicyBlocked()` — dua lead (`L-31`, `L-30`) mati seketika, setelah satu siklus PoC terbuang.

---

## Langkah 1: Klasifikasi Skenario Simulasi & Saringan Kesalahan Baca Statis (HUKUM: NO CODE, NO REJECT!)

### Langkah 1a: Triage BATCH & Pemetaan Chaining Lintas-Kelas (Unified Cross-Class Triage)

**Unified Phase 3 Gate.** Fase 3 berjalan di atas **gabungan seluruh lead** dari `[CLASS-A]`, `[CLASS-B]`, dan `[CLASS-C]` setelah Gate Cakupan Fase 2 terpenuhi.

Prosedur:
1. Tabel-kan semua lead di `audit/notes/fase3-urutan-poc.md`: `ID | Kelas | Berkas:Baris | Metode/POV | Skenario Harness & Setup Korban | Potensi Chaining Lintas-Kelas | Prioritas EV`.
   - Periksa apakah lead dari `[CLASS-A]` dapat menjadi **pemicu/penggeser state** untuk menjebol guard di `04-code-guarded.md`, atau menyulut lead `[CLASS-B]`/`[CLASS-C]` menjadi rantai eksploitasi.
2. **HUKUM MUTLAK *NO CODE, NO REJECT*:**
   - **DILARANG KERAS** menggugurkan lead ke `06` di Langkah 1 berdasarkan hitungan kertas EV, asumsi pembulatan kecil, atau dugaan bahwa "guard terlihat kuat".
   - Sebuah lead **HANYA BOLEH** digugurkan di Langkah 1 tanpa menulis kode test apabila terbukti merupakan **Kesalahan Baca Statis Literal** (*Literal Static Misread*) atau melanggar **4 Kemustahilan Statis Sempit** di Langkah 1c.
   - Seluruh lead selain itu **WAJIB** masuk ke Langkah 2 untuk dibuatkan kode simulasi (`forge test` / `cargo test` / `sui move test`)!

### Langkah 1b: Spesifikasi Skenario Harness Berdasarkan Metode Pencarian (Dynamic Registry Lookup)

Baca kolom `Metode Pencarian` dan `Delta State` pada lead di `audit/05-raw-leads.md`, lalu rujuk `sc-phase2-hunt/references/ref-method-registry.md` dan `ref-pov-*.md`.

Gunakan aturan metode berikut **BUKAN untuk membuang lead di atas kertas**, melainkan untuk merancang arsitektur kode test PoC yang benar:

- `[POV-DEFI-01]` (self-liquidation / bad debt): **JANGAN hitung di kertas lalu dibuang!** Tulis test dengan 2 akun (`Attacker_Borrower` & `Attacker_Liquidator`) + `testFuzz_` pada ukuran pinjaman dan perubahan harga batas untuk menguji apakah `Bonus_Liquidator + Utang_Dihapus > Collateral_Tersita` terjadi pada kondisi sudut (*corner case*). Hanya gugur jika di kode literal **tidak ada mekanisme bonus/bad-debt sama sekali**.
- `[POV-MATH-01]` (desinkronisasi indeks akrual): Cek baris kode fungsi pemindah (`transfer`/`delegate`/`migrate`). Hanya gugur tanpa test bila fungsi pemindah secara literal memanggil sinkronisasi indeks untuk **`from` DAN `to`** sebelum baris mutasi saldo, **tanpa cabang kondisional `if`/`else` yang dapat dilewati**, **tanpa menyalin struct ke memori lokal sebelum sinkronisasi**, **DAN menolak `from == to`**. Jika salah satu tidak terpenuhi → **WAJIB tulis PoC!**
- `[POV-CALL-01]` (state desync saat callback): Cek apakah ada fungsi/kontrak lain (termasuk view/oracle/pool pasangan) yang membaca state yang sedang timpang. Jika ada **minimal satu pembaca** → **WAJIB tulis PoC callback!**
- `[POV-MATH-02]` & `[M-007]` (exact-input vs exact-output rounding / split-vs-bulk): **DILARANG menghitung di kertas lalu memvonis `REJECTED_DUST`!** Wajib tulis `testFuzz_` yang membandingkan $N \times aksi(kecil)$ vs $1 \times aksi(besar)$ dengan *3-Way EV Amplification* (Flashloan + Single-Tx Loop + Chaining).
- `[POV-CALL-02]` (isolated subcall try/catch divergence): **DILARANG menggugurkan tanpa test meskipun target subcall adalah kontrak internal `immutable`!** Kontrak internal immutable tetap dapat dipaksa gagal (*Out-of-Gas* revert) oleh penyerang menggunakan aturan EIP-150 (63/64 gas rule) atau kondisi batas state/slippage. Selama ada perbedaan mutasi state antara cabang try/success dan cabang catch/`!success` (atau penyalinan returndata ke memori tanpa batas assembly), **WAJIB tulis PoC** di simulator yang memaksa eksekusi masuk ke cabang gagal (termasuk uji manipulasi gas 63/64 atau *Returnbombing*)!
- `[POV-DEFI-02]` (valuation-source vs execution-venue asymmetry): **DILARANG menggugurkan di atas kertas meskipun `amountOutMin` diturunkan dari harga Oracle Sumber A atau fungsi hanya dipanggil oleh Keeper/Bot!** Tetap **WAJIB tulis PoC** simulasi di atas fork untuk menguji: (a) apakah penyerang dapat mem-frontrun/backrun transaksi Keeper di mempool publik untuk mengekstrak *slippage tolerance* atau memicu DoS revert pada eksekusi Keeper, dan (b) apakah rumus konversi desimal/skala dari Oracle Sumber A ke `amountOutMin` Sumber B memiliki kesalahan presisi!
- `[POV-EVM-01]` (batch delegatecall / msg.value / transient storage reuse): Hanya gugur tanpa test bila fungsi batch **tidak `payable` DAN tidak memakai `TSTORE`/state sementara**. Jika `payable` atau memakai state sementara → **WAJIB tulis PoC batch call!**
- `[POV-SOL-01]` (Solana account aliasing / post-CPI stale data): Hanya gugur tanpa test bila constraint `key() !=` **DAN** `.reload()?` sudah tertulis eksplisit di baris tersebut. Jika salah satu absen → **WAJIB tulis test** dengan akun kembar `[A, A]` atau CPI.
- `[POV-MOVE-01]` (Move cross-object spoofing / bit-shift mask): Hanya gugur tanpa test bila `assert!(receipt.pool_id == object::id(pool))` sudah tertulis eksplisit **tanpa syarat di SETIAP fungsi publik penerima objek** (termasuk jalur alternatif pelunasan/penghancur *Hot Potato*). Untuk operasi `<<`, **WAJIB tulis `#[test]`** dengan angka batas bit tinggi!
- `[POV-TON-01]` (TON 224-bit bounce truncation / in-flight lock): Jika handler `bounced` membaca data **atau** ada pengiriman pesan multi-hop → **WAJIB uji di `@ton/sandbox`** dengan skenario pesan mental (*bounce*) atau interleave!
- `[M-003 / Metode 3]` (multi-identity sybil): Kode PoC **WAJIB** mendeklarasikan minimal dua identitas/akun/objek yang dikendalikan penyerang dalam satu jendela eksekusi (`Attacker_A` dan `Attacker_B`).
- `[M-004 / Metode 4]` (patch-scar / view-vs-write): **DILARANG menggugurkan desinkronisasi `View vs Write` ke `06` hanya karena hasil grep menunjukkan fungsi `view`/`preview*`/`quote*` tidak dipanggil secara on-chain di dalam repo!** Di produksi, fungsi `view`/`preview*`/`quote*` dipakai oleh Router eksternal, Solver/Relayer off-chain, dan Aggregator. Anda **WAJIB menulis PoC** yang mendemonstrasikan selisih angka antara hasil fungsi `View` vs eksekusi `Write` (dan menyerahkannya ke Hakim Fase 4 untuk diputuskan antara `09` vs `08`).
- `[M-005 / Metode 5]` (guard-inversion & 5 jalur penembusan guard): **DILARANG menggugurkan tanpa test hanya karena variabel pembentuk guard ditulis oleh `onlyOwner` atau bersifat `immutable`!** Sebuah lead `M-005` hanya boleh gugur tanpa test bila ia murni menuntut Admin bertindak jahat/bunuh diri secara langsung (`REJECTED_PRIVILEGED_FANTASY`). Apabila lead bekerja melalui salah satu dari **5 Jalur Permissionless** — yaitu: (1) variabel pembentuk guard dinamis/bisa digeser, (2) pemicuan lewat kontrak/modul hulu publik (`M-008`), (3) *Unprivileged State Poisoning* pada state/antrean/saldo yang dibaca oleh fungsi rutin (Keeper/Operator/Relayer), (4) pembacaan state timpang lintas-kontrak pada `nonReentrant` atau pause asimetris pada `whenNotPaused`, atau (5) *Cross-Whitelist Confusion* / *Unchecked Callback Initiator* — maka Anda **WAJIB menulis dan menjalankan kode simulasi PoC/Fuzz di Fase 3!**
- `[M-006 / Metode 6]` (stale snapshot write-back / duplicate reference `[A, A]`): Jika belum ada deduplikasi eksplisit, **WAJIB tulis PoC 1 transaksi** dengan argumen kembar `[A, A]`!
- `[M-008 / Metode 8]` (caller-callee seam / direct downstream bypass): Jika hilir **tidak** membatasi caller **ATAU** hulu meneruskan parameter pengguna tanpa validasi penuh → **WAJIB tulis PoC** panggilan langsung ke hilir / injeksi parameter hulu!
- `[M-009 / Metode 9]` (half-baked / suspended lifecycle): **WAJIB tulis PoC 3 langkah**: Langkah 1 (Buat State Menggantung/Pending) → Langkah 2 (Panggil Fungsi Sampingan: transfer/borrow/liquidate/cancel) → Langkah 3 (Finalize/Claim).
- `[M-010 / Metode 10]` (residual state / delegated authority / post-upgrade drift):
  - **Jangan menggugurkan** bug kode di kontrak Router/Migrator/Helper hanya karena saldo di blok mainnet detik ini sedang 0! Jika kodenya memang mengizinkan pencurian *allowance* pengguna atau *residual balance* → **WAJIB tulis PoC** dengan menyimulasikan korban (`vm.prank(victim)`) yang memberikan `approve` normal atau menyisakan debu transaksi, lalu buktikan `attacker` bisa menyedotnya!
  - Untuk *post-upgrade drift*: periksa state proxy live (bila sudah deploy) **ATAU** uji skrip migrasi/upgrade di repo secara langsung di simulator.

### Langkah 1c: 4 Kemustahilan Statis Sempit (Hanya Ini yang Boleh Gugur Tanpa PoC!)

**Jangan gunakan saringan ini untuk membunuh bug yang sah!** Sebuah lead hanya boleh langsung masuk ke staging `06` tanpa kode PoC jika memenuhi **secara ketat** salah satu dari 4 kemustahilan statis berikut:

1. **Halusinasi Sifat Token Internal (Langgar Kasta 1 Murni):** Mengasumsikan token internal buatan protokol sendiri (LP Token / Vault Share yang kodenya ERC-20 murni di repo) tiba-tiba berubah menjadi *Fee-on-Transfer* atau memiliki *callback* jahat, atau menyuntikkan kontrak palsu **dari luar** ke parameter yang di baris kodenya dikunci oleh `onlyOwner` whitelist. *(Catatan Penting Anti-False-Negative: Menguji quirk nyata token eksternal Kasta 2 seperti desimal 6/8, USDT non-zero `approve` revert / return-bool quirk, stETH 1-wei rounding, **Cross-Whitelist Confusion** — yaitu mengoper kontrak/pool/token yang **MEMANG TERDAFTAR SAH** di whitelist/Factory tetapi untuk pasangan aset/market yang salah karena ketiadaan cek ikatan aset — serta **Callback Initiator Spoofing** pada Pool/Endpoint resmi adalah **100% SAH dan WAJIB di-PoC!**)*
2. **Ilusi Kolam Kosong pada Pool Tunggal yang Sudah Permanen Terisi:** Menyerang `totalSupply == 0` pada kontrak tunggal yang di mainnet sudah memiliki TVL terkunci / *dead shares* permanen **DAN** tidak bisa dikosongkan kembali.
   - **PENGECUALIAN WAJIB DI-POC (DILARANG DIBUANG!):** Jika (a) protokol memiliki **Factory** untuk membuat pool/vault baru, (b) seluruh penabung bisa menarik dana hingga `totalSupply` kembali 0 (*empty-again vault*), atau (c) kontrak di repo **belum ter-deploy** di mainnet dan skrip deploy-nya tidak mencetak *dead shares* secara atomik → **WAJIB DITULISKAN POC-NYA!**
3. **Menyerang `initialize()` Sekali-Pakai yang Sudah Terkunci Rapat:** Menyerang fungsi `initialize()` pada proxy yang sudah ter-deploy dan sudah terkunci initializer.
   - **PENGECUALIAN WAJIB DI-POC (DILARANG DIBUANG!):** Jika (a) kontrak *implementation* di balik proxy lupa memasang `_disableInitializers()` di constructor dan berpotensi diambil alih (mis. `delegatecall` / `selfdestruct`), (b) ada fungsi `reinitialize(n)` / `migrate()` yang terbuka, atau (c) skrip deployment di repo membiarkan jendela transaksi terpisah antara `deploy` dan `initialize()` → **WAJIB DITULISKAN POC-NYA!**
4. **Menuntut Aksi Admin Jahat di Luar Batas Validasi Kode:** Mengharuskan Admin/Owner memanggil fungsi dengan alamat kontrak palsu atau parameter bunuh diri yang tidak masuk akal.
   - **PENGECUALIAN WAJIB DI-POC (DILARANG DIBUANG!):** Jika Admin memasukkan nilai parameter yang berada **di dalam batas normal yang diizinkan** oleh `require(...)` kontrak (misal: mengubah fee, LTV, atau epoch di dalam rentang `MIN..MAX` yang sah), tetapi perubahan parameter sah tersebut menyebabkan perhitungan kontrak rusak, posisi pengguna gagal dilikuidasi, atau dana membeku (*Valid-Range Config Brick*) → **WAJIB DITULISKAN POC-NYA!**

## Langkah 2: Simulasi Eksploitasi di Sandbox Lokal & Pemilihan Mesin 6-Tier (Deterministic vs Nondeterministic)

### Urutan Eksekusi PoC — Prioritas EV, BUKAN FIFO
Setelah Langkah 1a lolos, **DILARANG** mengerjakan PoC berdasarkan urutan nomor `LEAD-01, 02, 03`. Urutkan berdasarkan:
1. **Dampak finansial tertinggi (Critical/High EV)** lebih dulu — perkirakan kerugian dalam satuan aset nyata, bukan "seberapa menarik kodenya".
2. **Keterwakilan domain** — pastikan lead dari domain berbeda ikut dieksekusi; jangan habiskan kuota pada satu domain.
3. **Biaya bukti paling murah** pada EV setara — lead yang butuh satu `cast call` didahulukan daripada yang butuh harness baru.

> **Mengapa urutan ini MENGIKAT, bukan preferensi estetika — Kelelahan Ketajaman Kognitif.** Kemampuan analisis penalaran (manusia maupun model bahasa) **menurun** seiring panjang sesi: perhatian pada detail melemah, premis sendiri mulai diterima tanpa uji, dan kesalahan mekanis meningkat. Konsekuensinya konkret: **lead yang dikerjakan di ekor sesi dinilai dengan ketajaman paling rendah.** Karena itu aturan ini melarang:
> - (a) Menaruh lead **EV tertinggi** di akhir antrean — lead terbaik WAJIB dinilai saat ketajaman masih penuh. "Nanti saja karena EV-nya besar" adalah pelanggaran.
> - (b) Mengerjakan lead **berat** (butuh harness baru) setelah sesi panjang menghabiskan kapasitas pada pekerjaan non-penemuan.
> - (c) Melanjutkan lead baru setelah **≥2 kegagalan mekanis berturut-turut** (patch/`old_string` gagal, salah baca statis yang langsung terbantah, kontradiksi diri sendiri). Itu **sinyal ketajaman turun**, bukan kebetulan: hentikan sesi, tulis checkpoint `audit/STATE.md`, dan lanjutkan lead berikutnya di sesi baru.
>
> **Aktivitas non-penemuan DILARANG memakan kuota lead.** Setup build, perbaikan remapping, debug tooling, dan penyiapan RPC dihitung sebagai **biaya infrastruktur** terpisah — bukan alasan menunda lead ber-EV tinggi ke ekor antrean.

**Batalkan PoC kapan saja** begitu `3-Stage Breaker` (Langkah 0b) terpicu — yaitu setelah Strike 1 (Manual) + Strike 2 (Manual/Amplifikasi) + Strike 3 (Fuzz) seluruhnya gagal.

**Pengunci Anti-Low-Rate #1 — Kuota Beban Identik & Position-Blind Dispatch (*No Tail-End Compression*).**
Jika dijalankan lewat delegasi Subagent: **1 Subagent menangani maksimal 1 s/d 3 Lead** untuk di-PoC — sama batasnya untuk lead urutan teratas maupun lead urutan paling buntut. **DILARANG KERAS** merapel 5–10 lead sisa di ekor antrean ke dalam satu "Subagent pembersih" di akhir. Prompt Subagent DILARANG memuat label posisi ("sisa", "prioritas rendah", "EV kecil").

**Pengunci Anti-Low-Rate #2 — Protokol *Mandatory 3-Way EV Amplification* sebelum vonis `REJECTED_DUST` / `REJECTED_NEGATIVE_EV`.**
Lead yang pada **1 transaksi sederhana** tampak menghasilkan selisih kecil **DILARANG** langsung dibuang ke `06`. Wajib diuji terhadap **3 Pengali Dampak** berikut dan hasilnya dicatat di `audit/notes/`:

| # | Pengali | Cara Uji |
|---|---|---|
| (a) | **Flashloan / Capital Scaling** | Uji dengan modal pinjaman kilat **maksimum yang realistis** pada pool/rantai target — bukan saldo attacker sendiri. |
| (b) | **Single-Tx Looping / Batching** | Uji pemanggilan berulang ($N$ iterasi) dalam **1 transaksi** (multicall, PTB, atau kontrak penyerang kustom) sampai batas gas/komputasi 1 blok. |
| (c) | **Cross-Lead / Cross-Class Chaining** | Uji apakah anomali kecil ini (misal dari unit `[CLASS-A]`) dapat menjadi **langkah pembuka** untuk menggeser variabel pembentuk guard di `04-code-guarded.md`, atau digabung dengan lead lain di `05-raw-leads.md` (`[CLASS-B]` / `[CLASS-C]`). |

> Vonis `REJECTED_DUST` / `REJECTED_NEGATIVE_EV` hanya sah bila **ketiga** pengali sudah dicoba dan dirinci angkanya. Menvonis tanpa mencatat ketiga hasil = pelanggaran Pernyataan #11 (`LAZY_BAILOUT_DETECTED`).

**Pencatatan wajib:** tulis urutan eksekusi beserta alasan EV di `audit/notes/fase3-urutan-poc.md` sebelum mulai. Urutan yang tidak tercatat dianggap FIFO dan melanggar aturan.

Panggil skill_view pada modul referensi pengujian sesuai rantai di 00-project-map.md (`references/ref-test-evm-advanced.md` untuk Tier 1–5, `references/ref-test-multichain-advanced.md` untuk Tier 6 non-EVM Solana/Sui/Aptos/TON), lalu jalankan simulasi (`FOUNDRY_JOBS=1`, `CARGO_BUILD_JOBS=1`, `RAYON_NUM_THREADS=1`):
- **Jalur Deterministic** (Tier 1 Sequence, Tier 4 Local Fork, Tier 5 Symbolic Halmos/Kani): Gunakan untuk membuktikan urutan langkah pasti dari 05-raw-leads.md atau mencari *counterexample* matematis eksak (`halmos --function check_*`).
- **Jalur Nondeterministic** (Tier 2 Handler Stateful Invariant Fuzzing, Tier 3 Round-Trip/Differential Fuzzing): Gunakan untuk mengeksplorasi kandidat `NEXT_EXPLORE` di 07-needs-next-step.md atau menguji Metode 7 (Split-vs-Bulk). Begitu fuzzer menemukan *counterexample*, WAJIB konversikan menjadi tes Deterministic Local Fork (Tier 4)!

**Aturan mutlak penulisan simulasi (Protokol *Realistic State & Victim Seeding*):**

1. **Larangan Fantasy Mock:** Gunakan kontrak asli dari repositori. Jika berinteraksi dengan token/pool eksternal (USDC, USDT, WETH, Chainlink, Uniswap, Aave), utamakan menjalankannya di atas Local Fork rantai target agar berinteraksi dengan kontrak eksternal asli.
2. **WAJIB *Realistic Victim Lifecycle Seeding* (Jangan Tembak Ruang Hampa!):**
   Banyak kerentanan nyata gagal (`revert`) saat diuji hanya karena di blok fork saat ini kebetulan belum ada posisi pengguna yang sedang berada pada tahap siklus hidup tersebut (misal: belum ada order gantung, belum ada permintaan `requestWithdraw`, belum ada pinjaman di dekat batas LTV, atau belum ada pengguna yang baru `approve` ke Router).
   - **Hukum Seeding Korban:** Sebelum menyimpulkan sebuah PoC gagal/`revert`, Anda **WAJIB** menyimulasikan 1–2 aktor pengguna normal (`address victim = makeAddr("victim")`, didanai secara wajar dengan `deal`) yang menjalankan aksi sah sesuai alur protokol (`deposit`, `borrow`, `stake`, `requestWithdraw`, `createOrder`, `approve`) menggunakan `vm.prank(victim)`.
   - Setelah posisi victim terbentuk secara sah (dan waktu/blok digeser secara wajar bila fitur memiliki *cooldown/epoch* normal), barulah eksekusi transaksi serangan menggunakan `vm.prank(attacker)`!
   - Menyimulasikan transaksi pengguna normal (`vm.prank(victim)`) **BUKAN cheatcode** — itu adalah standar pembuktian eksploitasi dunia nyata.
   - **Simulasi Eksekutor Rutin Pasca-Serangan Permissionless (BUKAN Cheatcode!):** Apabila sebuah fungsi dikunci oleh permission yang tidak bisa dimanipulasi (`onlyKeeper`, `onlyRelayer`, `onlyOperator`, `onlySettler`), dan hipotesis kerentanannya adalah penyerang tak berizin (`vm.prank(attacker)`) memanipulasi state protokol melalui fungsi publik, lalu menyebabkan fungsi rutin berizin tersebut mengalami *DoS revert* permanen (membekukan dana) atau salah mendistribusikan dana saat dieksekusi secara normal: Anda **WAJIB dan DIIZINKAN** memanggil `vm.prank(keeper/operator)` dengan parameter operasional normal **setelah** aksi attacker untuk membuktikan patahnya invarian tersebut! Yang dilarang keras hanyalah memakai `vm.prank(admin/keeper)` untuk menyuntikkan parameter jahat/bunuh diri yang tidak rasional.
3. **Larangan Cheatcode Curang pada State Internal:** DILARANG menggunakan `vm.prank(admin/owner)` untuk memasukkan konfigurasi jahat di luar rentang sah, dan DILARANG menggunakan `vm.store`, `vm.etch`, atau `deal` langsung ke alamat kontrak protokol yang merusak akuntansi internal tanpa melewati fungsi kontrak.
   - **Pengecualian sah — Eksekutor Rutin Pasca-Poisoning:** `vm.prank(keeper/relayer/operator/settler)` **SAH dan WAJIB** setelah state diracuni oleh aktor tak berizin tanpa cheatcode (`VERDICT.md` Pengecualian #9a-iii). Prank di sini mensimulasikan aktor rutin yang menjalankan tugas normalnya — bukan menyuntikkan state. Urutan wajib: (a) `vm.prank(attacker)` meracuni state via fungsi publik → (b) `vm.prank(keeper)` memicu fungsi rutin dengan parameter wajar → (c) ukur kebocoran nilai atau `revert` permanen. Prank untuk **mengarang** state (bukan memicu setelah poisoning) tetap `REJECTED_CHEATCODE`.
4. **Upaya Amplifikasi Dampak & Fuzzing:** Selalu uji dengan *3-Way EV Amplification* (Flashloan, Single-Tx Looping, Cross-Lead Chaining) dan jalankan `testFuzz_` (Strike 3) sebelum menyatakan sebuah anomali tidak menguntungkan.

### Langkah 2b: Protokol Dual-Mode Fork (FORK_LIVE & FORK_DEPLOYED_HEAD) — Tidak Ada Bailout Karena Stage Repo!

Repositori GitHub sering kali memuat campuran kontrak yang sudah *live* di mainnet dan kontrak baru/versi HEAD yang belum di-deploy atau berbeda dari on-chain. Ketidakpastian stage deployment di GitHub **DILARANG** dijadikan alasan untuk tidak menulis PoC Fork atau memarkir lead ke `07`/`08`!

Pilih **tepat satu** dari 3 mode eksekusi berikut (urut dari prioritas tertinggi):

1. **`Mode Uji: FORK_LIVE (chain, block, RPC)`** — Gunakan bila alamat kontrak target di mainnet sudah diketahui **dan** fungsi yang diserang sudah ada pada bytecode on-chain tersebut. Jalankan `forge test -j 1 --fork-url $RPC_URL --fork-block-number <N>` (gunakan `./rpc-env.sh`), lakukan *Victim Seeding* bila perlu, dan tembak langsung kontrak produksi.
2. **`Mode Uji: FORK_DEPLOYED_HEAD (chain, block, RPC)`** — Gunakan bila kontrak di repositori GitHub belum di-deploy ke mainnet, alamatnya belum diketahui, atau kode di HEAD lebih baru daripada bytecode on-chain.
   - **Prosedur:** Tetap nyalakan Local Fork rantai target (`vm.createSelectFork` / `--fork-url`) agar seluruh ekosistem pendukung (USDC, USDT, WETH, Oracle Chainlink, Pool Uniswap/Aave) menggunakan state mainnet asli, lalu **deploy kontrak dari kode repositori** (`src/`/`contracts/`) di atas fork tersebut dengan parameter inisialisasi standar proyek!
   - Selama PoC berhasil membuktikan eksploitasi (`[PASS]`) di atas `FORK_DEPLOYED_HEAD`, temuan tersebut **wajib didorong ke staging sebagai kandidat `09`** (nanti Hakim Fase 4 yang akan menilai status deployment-nya).
3. **`Mode Uji: LOKAL (alasan fork tidak tersedia)`** — Gunakan untuk rantai non-EVM (`cargo test` Solana, `sui move test` / `aptos move test`, TON `@ton/sandbox`) atau bila rantai target benar-benar tidak memiliki RPC publik setelah Usaha 3 Langkah 0c ditempuh. Deploy seluruh kontrak asli repositori, lakukan *Victim Seeding* realistis, dan buktikan patahnya invarian secara deterministik.

> **Wajib Jalankan Gerbang Siklus sebelum menulis PoC — tetapi DILARANG menghentikan PoC karenanya.** Subagent Fase 3 **wajib** menjalankan satu perintah sebelum menulis harness:
>
> ```bash
> python3 verify/tools/deploy_parity.py --paradigm <evm|solana|sui|aptos|ton|generic|<plugin>> \
>   --chain <mainnet|testnet|local> --addr <ALAMAT_LIVE> --rpc $RPC_URL \
>   --entrypoints "<signature yang diserang PoC>" --repo <path repo sumber> \
>   --out audit/notes/deploy-parity-<ID>.json
> ```
>
> Hasilnya **wajib dicatat** di staging sebagai `DEPLOYMENT_CLASS:` dan `Mode Uji:` — tetapi **TIDAK BOLEH** membuat Subagent berhenti menulis PoC. Aturan kerjanya:
>
> | Keluaran `deploy_parity` | Kewajiban Fase 3 |
> |---|---|
> | `LIVE_MATCH` | Tulis PoC; `Mode Uji: FORK_LIVE`; boleh berlabel `...Fork` |
> | `ENTRYPOINT_RELOCATED` / `HEAD_ONLY_PROVEN` | Tulis PoC; `Mode Uji: FORK_DEPLOYED_HEAD (live diverge)`; **DILARANG** menamai test `...Fork` — gunakan akhiran `...Head`; staging tetap kandidat `09` (Hakim Fase 4 yang memindahkan ke `08`) |
> | `ENV_ERROR` / `UNVERIFIABLE` | Tulis PoC apa adanya, catat `DEPLOYMENT_CLASS: ENV_ERROR`; **DILARANG** menyimpulkan "fungsi tidak ada" |
> | `P1_PRE_DEPLOY` | Tulis PoC `LOKAL`/`FORK_DEPLOYED_HEAD`; staging kandidat `08` |
>
> **DILARANG KERAS** memakai aturan "bytecode harus identik" atau "`sha256` explorer harus sama" sebagai alasan menggugurkan/menghentikan PoC: setiap repo punya siklus rilis berbeda dan build Foundry jarang reproducible. Yang diuji adalah **keberadaan & perilaku entrypoint**, bukan hash file. Tugas utama Fase 3 tetap: **membuktikan apakah kode tersebut dapat dijebol secara mekanis dan finansial di simulator!**

> **WAJIB: catat fakta lingkungan ber-scope ke `00-project-map.md §5`.** Setiap fakta otoritas/lifecycle yang ditemukan saat rekonsiliasi deployment (upgrade authority, apakah multisig, paused, sejak blok berapa, siapa pemilik proxy admin) **wajib** di-`patch` ke `§5 LINGKUNGAN` dengan tag `[chain:alamat]` + bukti perintah + blok. Fakta ini **DILARANG** disimpan tanpa tag scope (mis. "upgrade authority single EOA" tanpa `[ETH:0x...]`), karena akan terbawa ke chain/kontrak lain dan menghasilkan vonis palsu di Fase 4. Bila belum diverifikasi, tulis eksplisit `UNKNOWN` — bukan menghilangkannya.

---

### Langkah 2c: Kewajiban Kontrol Positif untuk Setiap Assertion Negatif (WAJIB)

**Hukum:** `assertFalse(ok)`, `assertEq(count, 0)`, `assertTrue(reverted)`, atau bentuk negatif apa pun **DILARANG berdiri sendiri**. Setiap harness wajib memuat minimal satu **kasus kontrol positif** yang membuktikan jalur yang sama bisa menghasilkan hasil positif.

**Alasan mekanis:** tanpa kontrol, **"tidak ada kegagalan" tak terbedakan dari "tidak ada eksekusi"**. `assertFalse(ok)` otomatis lulus ketika semua input me-revert karena alasan yang tidak ada hubungannya dengan hipotesis — mis. salah encoding, selector salah, modul tidak terpasang, atau input tidak valid.

**Pola wajib — 2 kasus minimum per harness:**

| Kasus | Tujuan | Harus menghasilkan |
|---|---|---|
| **Kontrol positif** | buktikan jalur bisa berjalan | eksekusi sukses / kondisi normal tercapai |
| **Kasus target** | buktikan hipotesis | delta state / revert yang dihipotesiskan |

**DILARANG menggugurkan lead bila kontrol positif tidak berhasil dibuat.** Harness yang tidak bisa membuktikan jalur normalnya berjalan **bukan bukti** bahwa protokol aman — itu bukti harness belum benar. Kembali ke Langkah 0c (Tangga Self-Healing), jangan tulis ke `06`.

**Insiden yang melahirkan aturan ini:** pada audit nyata, dua lead (`L-41`, `L-42`) dinyatakan gugur karena fuzzer menemukan "counterexample" (`typesLen=0`). Pemeriksaan ulang menunjukkan **seluruh input** me-revert `InvalidInput() 0xb4fa3fb3` — termasuk payload valid — sehingga assertion negatif lulus tanpa pernah mengeksekusi jalur target. Satu lead lain (`L-20`) juga gugur karena encoding mode salah sehingga "kontrol" ikut gagal, membuat uji returnbomb tidak bermakna. Ketiganya adalah **false positive yang menutupi kegagalan harness**, bukan temuan.

**Cek cepat sebelum menulis hasil harness:**
- [ ] Ada kasus kontrol positif? Apakah ia benar-benar `[PASS]`?
- [ ] Apakah kasus target masuk ke jalur yang dihipotesiskan, bukan revert lebih awal?
- [ ] Kode error kontrol berbeda dari kode error target? (kalau sama, tidak ada pembeda)

---

### Langkah 2d: Gate Penutupan Fase 3 — Artefak Wajib Berwujud (WAJIB SEBELUM LANJUT)

**Hukum: Fase 3 DILARANG dinyatakan "selesai" berdasarkan STATUS. Kelulusan diukur dari FILE yang benar-benar ada di disk.**

**Kejadian nyata:** seluruh lead diberi status keputusan di file antrean, lalu Fase 3 dinyatakan selesai. Ternyata file wadah penolakan **belum pernah dibuat**. Saat Fase 4 dijalankan, gate integritas penolakan (`#11e`) **tidak dapat dieksekusi** karena file yang diperiksa tidak ada — bukan karena isinya salah, tetapi karena **artefaknya belum berwujud**. Laporan otomatis tidak sah.

**Akar penyebab:** status keputusan ditulis ke **file antrean** (`05-raw-leads.md`) alih-alih **memindahkan** entri ke wadahnya (`06`/`07`/kandidat `09`). Akibat berantai: file antrean tumbuh tanpa batas (puluhan KB), memaksa pembacaan berulang, dan melanggar aturan "satu file satu domain".

**Pemeriksaan wajib sebelum menutup Fase 3 — semua harus terpenuhi:**

- [ ] `06-refuted-invalid.md` **ada sebagai file** (bila ada ≥1 lead gugur)
- [ ] `07-needs-next-step.md` **ada sebagai file** (bila ada ≥1 lead `NEXT_*`/`TOOL_BLOCKED`)
- [ ] Setiap entri `06` yang berstatus `REJECTED_POC_FAILS` / `REJECTED_NEGATIVE_EV` / `REJECTED_DUST` memuat blok `BUKTI_SIMULASI:`
- [ ] `grep -c 'Status Fase 3' 05-raw-leads.md` **== 0** — file antrean wajib bersih dari status keputusan
- [ ] Jumlah entri di `06` **==** jumlah lead yang benar-benar gugur
- [ ] Setiap lead yang diputuskan sudah **DIPINDAHKAN** (bukan sekadar ditandai) ke wadahnya

**Satu perintah verifikasi:**

```bash
test -f audit/06-refuted-invalid.md \
  && test -f audit/07-needs-next-step.md \
  && [ "$(grep -c 'Status Fase 3' audit/05-raw-leads.md)" -eq 0 ] \
  && echo "GATE PENUTUPAN: PASS" || echo "GATE PENUTUPAN: GAGAL — Fase 3 belum boleh ditutup"
```

**Bila gagal:** Fase 3 **belum selesai**, meski seluruh lead sudah punya keputusan. Kembali ke Langkah 3 dan wujudkan wadahnya.

---

### Langkah 2e: Penempatan Riwayat Uji — Kode, Log, dan Catatan (WAJIB)

**Hukum: `notes/` menyimpan CATATAN, bukan KODE. Kode tetap di folder kode.** Mencampur keduanya membuat `grep` tidak lagi bisa membedakan mana yang **dijalankan** dan mana yang **ditulis**, serta membuat tool build memindai folder yang salah.

**Lima jenis riwayat — lima tempat, jangan dicampur:**

| # | Jenis | Tempat | Boleh diringkas? |
|---|---|---|---|
| 1 | **Kode test/PoC hidup** (masih dipakai) | folder lab (`poc3/test/` dst.) | ❌ kode utuh |
| 2 | **Kode test/PoC gugur** (tidak dipakai lagi) | `audit/notes/testref/` | ❌ **dipindah**, jangan dihapus |
| 3 | **Log eksekusi mentah** (`forge test -vv`, `cast`, `cargo test`) | `audit/notes/lead-<id>.md` | ❌ log penuh |
| 4 | **Hipotesis + analisis + verdict** | `audit/notes/lead-<id>.md` | ⚠️ ringkas di `05`, utuh di sini |
| 5 | **Bukti final laporan** (`BUKTI_SIMULASI:` / `PERCOBAAN:`) | `06` / `07` / `08` / `09` | ❌ syarat sah — jangan disentuh |

**Bentuk wajib `audit/notes/lead-<id>.md`:**

```
# <ID> — <hipotesis satu baris>

## Test
<path kode test> — <nama fungsi test>

## Log
```$ <perintah persis>```
<keluaran nyata — ditempel, bukan ditulis ulang>

## Verdict
<status> → <wadah tujuan>
```

**Wajib `audit/notes/README.md` sebagai INDEKS** (dibuat saat lead pertama masuk `notes/`, diperbarui setiap lead baru):

| Lead | File | Verdict |
|---|---|---|
| `<ID>` | `lead-<ID>.md` | TERBUKTI / GUGUR / NEXT |

Indeks dibaca **sekali** saat resume, lalu langsung melompat ke file yang dituju — ini yang membuat pembacaan terarah, bukan menyeluruh.

**DILARANG:** menaruh berkas `.sol` / `.rs` / `.move` di dalam `notes/` selain di `notes/testref/`; menyalin kode test ke dalam `notes/lead-<id>.md` (cukup **path**-nya).

**Kenapa ini hemat, bukan boros:** satu file gabungan berisi log semua lead memaksa pembacaan **seluruh** file meski hanya butuh satu lead. Dengan `notes/lead-<id>.md` + indeks, pembacaan untuk 1 lead turun drastis — tanpa menambah total ukuran penyimpanan.

**DILARANG dihapus:** kode test yang menghasilkan bukti `[PASS]` atau yang mendasari penolakan ber-`BUKTI_SIMULASI`. Ia adalah jejak yang memungkinkan laporan diperiksa ulang. Bila test tidak lagi dipakai, **pindahkan** ke `audit/notes/testref/`, jangan hapus.

---

## Langkah 3: Distribusi Hasil Simulasi ke 3 Wadah Murni (06, 07, atau 09 — TANPA 08!)

Subagent Fase 3 **DILARANG** mendistribusikan atau menandai entri sebagai `08-valid-not-eligible.md`. Seluruh hasil Fase 3 ditulis lengkap ke `audit/notes/staging-<id>.md` menuju **tepat salah satu** dari 3 wadah berikut:

1. **Simulasi Eksploitasi `PASS`** (`FORK_LIVE`, `FORK_DEPLOYED_HEAD`, atau `LOKAL` Non-EVM) **& Invarian Terbukti Patah:**
   Tulis entri lengkap ke `audit/notes/staging-<id>.md` sebagai kandidat **`09-confirmed-findings.md`** lengkap dengan: kode PoC utuh, baris `Mode Uji: FORK_LIVE (...)` / `FORK_DEPLOYED_HEAD (...)` / `LOKAL (...)`, angka kuantitatif dampak/profit dari log terminal, dan patch perbaikan (diff). *(Hakim `VERDICT.md` di Fase 4 yang nantinya akan memisahkan mana yang bertahan di `09` dan mana yang bergeser ke `08` karena faktor pre-live/low/admin.)*
2. **Gagal Setelah *Victim Seeding* + *3-Way Amplification* + *3-Stage Escalation (2 Manual + 1 Fuzz)*:**
   Tulis entri lengkap ke `audit/notes/staging-<id>.md` sebagai kandidat **`06-refuted-invalid.md`** (`REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, `REJECTED_DUST`, dll.).
   - **SYARAT SAH MASUK `06` (Anti-Paper-Refutation):** Kecuali untuk kesalahan baca statis literal di Langkah 1c, setiap entri `06` **WAJIB** memuat blok `BUKTI_SIMULASI:` berisi perintah test yang dijalankan (termasuk Strike 3 `testFuzz_`) beserta output log terminal yang membuktikan invarian tetap bertahan. Entri `06` tanpa bukti eksekusi test akan ditolak di Fase 4 (**`PAPER_REFUTATION_DETECTED`**). Hapus file test sementara setelah log dicatat agar folder `test/` tetap bersih.
3. **Secara Logika Kode Kuat Namun Terhalang Batas Komputasi/Alat (`07-needs-next-step.md`):**
   Tulis entri lengkap ke `audit/notes/staging-<id>.md` dengan **tepat satu** Disposition (`NEXT_EXPLORE` | `NEXT_MAINNET` | `TOOL_BLOCKED`) dan blok wajib `PERCOBAAN:` berisi perintah `$ ...` + keluaran nyata sesuai Langkah 0c dan 0d.
