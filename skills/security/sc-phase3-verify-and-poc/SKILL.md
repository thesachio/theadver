---
name: sc-phase3-verify-and-poc
description: Phase 3 — Dynamic Registry-Routed Harness Design (M-001..M-NNN & [POV-XX]), Dual-Mode Fork Simulation (FORK_LIVE & FORK_DEPLOYED_HEAD) with Victim Seeding, 2-Manual + 1-Fuzz Escalation, and Pure Mechanism Staging (06, 07, 09).
version: 6.2.0
---

# Phase 3: Simulation-First Sanity Check & Local Fork Exploit Lab

Tujuan Fase 3 adalah menguji setiap hipotesis di audit/05-raw-leads.md di dalam laboratorium simulasi eksekusi nyata (Dual-Mode Fork: `FORK_LIVE` untuk kontrak produksi aktif, atau `FORK_DEPLOYED_HEAD` untuk kode repositori di atas state rantai nyata), dilengkapi *Realistic Victim Lifecycle Seeding* dan *Fuzzing Escalation*, lalu mendistribusikan hasilnya (via `audit/notes/staging-<id>.md`) ke tiga wadah murni: audit/06-refuted-invalid.md, audit/07-needs-next-step.md, atau audit/09-confirmed-findings.md — **penulisan ke ketiga wadah itu dilakukan Parent, bukan Subagent**.

**HUKUM INTI FASE 3 (SIMULATION-FIRST & BLIND TO BOUNTY SCOPE):**

1. **DILARANG menyentuh `08-valid-not-eligible.md` di Fase 3.** Pemisahan administratif apakah kontrak masih *pre-live* (HEAD-only), *admin-only*, atau berdampak *Low* adalah wewenang eksklusif Hakim Fase 4 (`VERDICT.md`) **setelah** mekanisme berhasil dibuktikan.
2. **Hukum *No Code, No Reject*:** DILARANG KERAS menggugurkan lead logika, matematika, pembulatan, likuidasi, atau transisi state ke `06` hanya dengan hitungan kertas atau baca kode sekilas **tanpa menjalankan kode test** (`forge test` / `cargo test` / `sui move test`).

**GERBANG TULIS (WAJIB):** sebelum menulis satu byte pun ke `audit/*.md` atau `notes/staging-*`, baca **`workspace/AGENTS.md` Pasal 1.3 (Protokol Anti-Truncate & Metode Write)**. `open(path,"w")` dan `>` shell **DILARANG**; untuk `05`/`07` gunakan `append` lalu `patch` saat status berubah, untuk `06`/`08`/`09` cukup `append`.

---

## Langkah 0b: Anti-Rabbit-Hole & Anti-Premature-Death — Protokol 2-Manual + 1-Fuzz Escalation (WAJIB)

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
- `[POV-MATH-01]` (desinkronisasi indeks akrual): Cek baris kode fungsi pemindah (`transfer`/`delegate`/`migrate`). Hanya gugur tanpa test bila fungsi pemindah secara literal memanggil sinkronisasi indeks untuk **`from` DAN `to`** sebelum baris mutasi saldo **DAN** menolak `from == to`. Jika urutan pemanggilannya mencurigakan atau menggunakan variabel memori sementara → **WAJIB tulis PoC!**
- `[POV-CALL-01]` (state desync saat callback): Cek apakah ada fungsi/kontrak lain (termasuk view/oracle/pool pasangan) yang membaca state yang sedang timpang. Jika ada **minimal satu pembaca** → **WAJIB tulis PoC callback!**
- `[POV-MATH-02]` & `[M-007]` (exact-input vs exact-output rounding / split-vs-bulk): **DILARANG menghitung di kertas lalu memvonis `REJECTED_DUST`!** Wajib tulis `testFuzz_` yang membandingkan $N \times aksi(kecil)$ vs $1 \times aksi(besar)$ dengan *3-Way EV Amplification* (Flashloan + Single-Tx Loop + Chaining).
- `[POV-CALL-02]` (isolated subcall try/catch divergence): Hanya gugur tanpa test bila target subcall adalah alamat internal `immutable` yang mustahil revert karena input pengguna. Jika subcall **bisa** gagal (out-of-gas 63/64, revert penerima, slippage, atau batas saldo) → **WAJIB tulis PoC yang memaksa masuk ke cabang `catch`/`!success`!**
- `[POV-DEFI-02]` (valuation-source vs execution-venue asymmetry): Jika fungsi pemicu dapat dipanggil publik (langsung atau tidak langsung), **WAJIB tulis PoC** yang memanipulasi likuiditas spot venue eksekusi menggunakan flashloan dalam **1 transaksi**!
- `[POV-EVM-01]` (batch delegatecall / msg.value / transient storage reuse): Hanya gugur tanpa test bila fungsi batch **tidak `payable` DAN tidak memakai `TSTORE`/state sementara**. Jika `payable` atau memakai state sementara → **WAJIB tulis PoC batch call!**
- `[POV-SOL-01]` (Solana account aliasing / post-CPI stale data): Hanya gugur tanpa test bila constraint `key() !=` **DAN** `.reload()?` sudah tertulis eksplisit di baris tersebut. Jika salah satu absen → **WAJIB tulis test** dengan akun kembar `[A, A]` atau CPI.
- `[POV-MOVE-01]` (Move cross-object spoofing / bit-shift mask): Hanya gugur tanpa test bila `assert!(receipt.pool_id == object::id(pool))` sudah tertulis eksplisit. Untuk operasi `<<`, **WAJIB tulis `#[test]`** dengan angka batas bit tinggi!
- `[POV-TON-01]` (TON 224-bit bounce truncation / in-flight lock): Jika handler `bounced` membaca data **atau** ada pengiriman pesan multi-hop → **WAJIB uji di `@ton/sandbox`** dengan skenario pesan mental (*bounce*) atau interleave!
- `[M-003 / Metode 3]` (multi-identity sybil): Kode PoC **WAJIB** mendeklarasikan minimal dua identitas/akun/objek yang dikendalikan penyerang dalam satu jendela eksekusi (`Attacker_A` dan `Attacker_B`).
- `[M-004 / Metode 4]` (patch-scar / view-vs-write): Jika tidak ada pemanggil on-chain tetapi fungsi view dipakai untuk kuotasi harga/integrasi penting, **tetap uji selisih angkanya di PoC** (Hakim Fase 4 yang akan memutuskan `08` vs `09`).
- `[M-005 / Metode 5]` (guard-inversion): Hanya gugur tanpa test bila seluruh variabel pembentuk guard **100% hanya bisa ditulis oleh `onlyOwner`** dan **tidak bergantung** pada saldo token, rasio pool, waktu, atau input pengguna. Jika ada satu saja variabel dinamis → **WAJIB tulis PoC/Fuzz!**
- `[M-006 / Metode 6]` (stale snapshot write-back / duplicate reference `[A, A]`): Jika belum ada deduplikasi eksplisit, **WAJIB tulis PoC 1 transaksi** dengan argumen kembar `[A, A]`!
- `[M-008 / Metode 8]` (caller-callee seam / direct downstream bypass): Jika hilir **tidak** membatasi caller **ATAU** hulu meneruskan parameter pengguna tanpa validasi penuh → **WAJIB tulis PoC** panggilan langsung ke hilir / injeksi parameter hulu!
- `[M-009 / Metode 9]` (half-baked / suspended lifecycle): **WAJIB tulis PoC 3 langkah**: Langkah 1 (Buat State Menggantung/Pending) → Langkah 2 (Panggil Fungsi Sampingan: transfer/borrow/liquidate/cancel) → Langkah 3 (Finalize/Claim).
- `[M-010 / Metode 10]` (residual state / delegated authority / post-upgrade drift):
  - **Jangan menggugurkan** bug kode di kontrak Router/Migrator/Helper hanya karena saldo di blok mainnet detik ini sedang 0! Jika kodenya memang mengizinkan pencurian *allowance* pengguna atau *residual balance* → **WAJIB tulis PoC** dengan menyimulasikan korban (`vm.prank(victim)`) yang memberikan `approve` normal atau menyisakan debu transaksi, lalu buktikan `attacker` bisa menyedotnya!
  - Untuk *post-upgrade drift*: periksa state proxy live (bila sudah deploy) **ATAU** uji skrip migrasi/upgrade di repo secara langsung di simulator.

### Langkah 1c: 4 Kemustahilan Statis Sempit (Hanya Ini yang Boleh Gugur Tanpa PoC!)

**Jangan gunakan saringan ini untuk membunuh bug yang sah!** Sebuah lead hanya boleh langsung masuk ke staging `06` tanpa kode PoC jika memenuhi **secara ketat** salah satu dari 4 kemustahilan statis berikut:

1. **Halusinasi Sifat Token Internal (Langgar Kasta 1 Murni):** Mengasumsikan token internal buatan protokol sendiri (LP Token / Vault Share yang kodenya ERC-20 murni di repo) tiba-tiba berubah menjadi *Fee-on-Transfer* atau memiliki *callback* jahat, atau menyuntikkan kontrak palsu ke parameter yang di baris kodenya dikunci oleh `onlyOwner` whitelist. *(Catatan: menguji token eksternal berdesimal 6/8, USDT return-bool quirk, atau token whitelist nyata adalah **SAH dan WAJIB di-PoC!**)*
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

**Aturan mutlak penulisan simulasi:**
1. **Larangan Fantasy Mock:** Gunakan kontrak LP/Share/Sistem asli dari repositori. Jika menggunakan MockERC20 untuk aset eksternal pada simulasi lokal, perilakunya WAJIB 100% IDENTIK dengan aset nyata yang diizinkan protokol di produksi.
2. **Inisialisasi Setara Produksi:** Setup awal di dalam setUp() wajib mencerminkan keadaan produksi nyata (sudah terinisialisasi dengan parameter normal dan memiliki likuiditas awal yang wajar).
3. **Larangan Cheatcode Curang:** Hanya gunakan `vm.prank(attacker)` (pengguna eksternal tak berizin). DILARANG menggunakan `vm.prank(admin/owner)`, `vm.store`, `vm.etch`, atau `deal` pada kontrak protokol untuk memalsukan state internal.
4. **Upaya Amplifikasi Dampak:** Jika dampak satu kali transaksi terlihat kecil, simulasikan apakah serangan dapat diulang dalam satu transaksi (*looping / flashloan amplification*) atau dirangkai dengan fungsi lain hingga menghasilkan bahaya finansial nyata.

### Langkah 2b: Simulasi pada Local Fork Produksi (Syarat Mutlak Masuk 09)
`09-confirmed-findings.md` mengklaim bukti terhadap state PRODUKSI nyata. Karena itu:
1. **Simulasi Local Fork WAJIB** bila chain target memiliki RPC publik: Jalankan simulasi transaksi PoC dengan menyalin state blok produksi (`forge test -j 1 --fork-url <RPC> --fork-block-number <N>`, gunakan `./rpc-env.sh`, tanpa `--broadcast`).
2. Di dalam fork tersebut, attacker bebas mengeksekusi transaksi serangan penuh terhadap kontrak target, namun hanya boleh didanai lewat `deal` pada dompet attacker **SENDIRI** atau lewat flashloan nyata. DILARANG mengubah storage protokol dengan `vm.store` atau `vm.etch`.
3. Jika RPC chain target tidak tersedia atau kontrak belum dapat dijangkau fork, temuan DILARANG masuk `09` — simpan ke `audit/07-needs-next-step.md` dengan label `NEXT_MAINNET` atau `TOOL_BLOCKED` **setelah menaiki seluruh Tangga Self-Healing (Langkah 0c)** dan melampirkan log ketiga usaha.
4. Jika simulasi fork berjalan namun transaksi eksploitasi revert terhadap state nyata = gugur ke `audit/06-refuted-invalid.md`.
5. Setiap entri di `09` dan `07` WAJIB mencantumkan baris `Mode Uji: FORK (chain, block, RPC)` atau `Mode Uji: LOKAL (alasan fork belum dilakukan)`.
6. **Identitas deployment (rujuk `verify/VERDICT.md` Langkah 0):** sebelum entri masuk `09`, pastikan kode yang diserang = kode yang berjalan (source terverifikasi explorer / `sha256` sama). Jika berbeda, entri wajib ditandai `HEAD-only` dan hanya boleh berada di `07`.

---

## Langkah 3: Distribusi Hasil Simulasi ke 3 Wadah Murni (06, 07, atau 09)
1. **Simulasi Fork PASS + Membuktikan Dampak Nyata:**
   Tulis entri lengkap ke **`audit/notes/staging-<lead>.md`** (bukan ke `09` langsung) dengan kode PoC utuh, baris `Mode Uji: FORK (...)`, perhitungan dampak/profit, dan log terminal (untuk selanjutnya diadili oleh Hakim `VERDICT.md` di Fase 4).
2. **Secara Logika Kode Kuat namun Belum Selesai Dibuktikan:**
   Tulis entri lengkap ke **`audit/notes/staging-<lead>.md`** (bukan ke `07` langsung) dengan salah satu label disposisi berikut — **masing-masing tunduk pada Langkah 0c dan 0d**:
   - `Disposition: NEXT_EXPLORE` -> **hanya sah bila Tier 2/3/5 sudah dijalankan** (multi-step chaining, differential, handler fuzzing, halmos) dan mencapai timeout komputasi tanpa konklusi. Wajib lampirkan blok `PERCOBAAN: <perintah> + <keluaran>`. Alasan "butuh multi-step chaining" tanpa percobaan = pelanggaran.
   - `Disposition: NEXT_MAINNET` -> **hanya sah bila** kontrak belum di-deploy atau rantai benar-benar tanpa RPC/explorer publik (Usaha 3 Langkah 0c gagal dengan log). Bila RPC tersedia, DILARANG parkir di sini — jalankan `cast call`/`cast storage`/`cast implementation` saat itu juga dan tuntaskan ke `09` atau `06`.
   - `Disposition: TOOL_BLOCKED` -> **HANYA setelah Tangga Self-Healing Langkah 0c ditempuh penuh** (Usaha 1: flag/remapping/toolchain; Usaha 2: standalone interface-only / minimal harness; Usaha 3: fallback RPC & rekonstruksi off-chain) **dengan log terminal kegagalan ketiganya dilampirkan di entri `07`**. Tanpa lampiran, label ini tidak sah.
3. **Gagal di Langkah 0/1 ATAU Simulasi PoC Gagal (`revert`) di State Nyata:**
   Tulis entri lengkap ke **`audit/notes/staging-<lead>.md`** (bukan ke `06` langsung) beserta alasan teknisnya (sertakan `TANGGA_BUKTI` dan `DEPLOYMENT_MATCH` sesuai template `06`), dan hapus file test sementara yang gagal agar folder test/ tetap bersih.
4. **3-Stage Breaker (Langkah 0b):** lead hanya boleh masuk `06` `REJECTED_POC_FAILS` setelah **Strike 1 (Manual) + Strike 2 (Manual/Amplifikasi) + Strike 3 (Fuzz `testFuzz_`/`proptest`/`halmos`)** ketiganya gagal — dan ketiga log dilampirkan. `07` hanya sah untuk lead yang **belum** menuntaskan ketiga tahap itu, dan wajib memuat blok `PERCOBAAN:`.
