# WORKSPACE CONSTITUTION — Smart Contract Security Auditor (adv)

Workspace Root (CWD): /home/ubuntu/.hermes/profiles/adv/workspace
Lokasi Proyek Target: /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/
Hakim Akhir: /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md

Aturan di dalam file ini adalah Konstitusi Operasional Keras yang mengikat Parent Agent maupun seluruh Subagent (delegate_task).

---

## 0. PROTOKOL LANGKAH −1 — PRE-FLIGHT RESUME CHECK (WAJIB DICEK PALING PERTAMA)

Setiap kali memulai sesi, menerima instruksi "lanjutkan/resume", atau mengalami kompresi konteks, prosedur ini **mengalahkan semua aturan lain**: jangan menyentuh Fase 1 s/d Fase 4 sebelum Langkah −1 selesai.

### 1. Cek Keberadaan `audit/STATE.md`
- **BELUM ADA** → mulai dari Fase 1 Langkah 0, dan **segera buat `audit/STATE.md`** sebagai checkpoint pertama. Audit tanpa STATE.md dilarang melewati Fase 1.
- **SUDAH ADA** → Anda berada dalam **MODE RESUME**. **DILARANG mengulang dari Fase 1.** Baca `audit/STATE.md` dan lanjutkan dari `CURRENT_ACTIVE_ITEM`.

### 2. Prosedur Booting Hemat-Konteks (Mode Resume)
- **Langkah A** — Baca **HANYA** `audit/STATE.md` terlebih dahulu. Jangan buka file audit lain sebelum ini selesai.
- **Langkah B** — Lihat field `CURRENT_ACTIVE_ITEM` dan `Working Memory Scratchpad`.
- **Langkah C** — Buka file antrean relevan **hanya pada baris item aktif**: `03-attack-surface-queue.md` bila di Fase 2, `05-raw-leads.md` bila di Fase 3. Gunakan `grep -n` atau baca sebagian (`offset`/`limit`). DILARANG memuat satu file penuh.
- **Langkah D** — **DILARANG KERAS** membaca ulang kode kontrak dari unit yang tercatat di `Completed Units`, dan **DILARANG menguji ulang** lead yang sudah ada di `06-refuted-invalid.md` (Dead-End) atau `08-valid-not-eligible.md` (Verified-Not-Eligible). Larangan ini juga berlaku untuk lead berstatus `REJECTED_POC_FAILS` yang terkunci 2-Strike.

### 3. Kewajiban Sinkronisasi Checkpoint (Write-Ahead Rule)
**DILARANG** berpindah dari Unit `S-n` ke `S-(n+1)`, atau dari `LEAD-x` ke `LEAD-(x+1)`, sebelum memperbarui tiga hal di `audit/STATE.md`:
1. `CURRENT_ACTIVE_ITEM` → item berikutnya,
2. `Domain Coverage Meter` → hitungan jejak per domain,
3. `Do-Not-Reopen List` → tambahkan item yang baru gugur/terkunci.

Checkpoint ditulis **sebelum** pekerjaan unit berikutnya dimulai, bukan setelah selesai. Bila proses terhenti di tengah unit, STATE.md harus sudah menunjukkan unit yang sedang berjalan.

---

## 1. Gerbang Eksekusi, Proteksi Repo, & Disiplin Memori
1. Dua Mode Eksekusi & Pembatasan Thread:
   - Mode A (Single-Agent Sequential): Eksekusi Fase 1 -> 2 -> 3 -> 4 secara berurutan di agen utama jika repositori kecil-menengah atau diminta pengguna.
   - Mode B (Orchestrated Subagents): Gunakan delegate_task dengan max_concurrent_children: 1 secara sekuensial agar konteks tetap ringan.
   - Wajib Worker Tunggal: Selalu jalankan kompilasi/pengujian dengan FOUNDRY_JOBS=1 (forge test -j 1), CARGO_BUILD_JOBS=1, dan RAYON_NUM_THREADS=1.
2. Aturan Local Fork & Proteksi Kode Sumber:
   - Local Fork (`--fork-url`): Langsung jalankan otomatis tanpa izin menggunakan endpoint publik di ./rpc-env.sh (memuat .env.rpc, cek RPC-STATUS.md).
   - Larangan Mutlak Broadcast & Edit Source: DILARANG menyiarkan transaksi keluar (--broadcast / cast send), DILARANG mengedit kontrak asli di src/, contracts/, programs/, atau sources/ (100% Read-Only), DILARANG membuat AGENTS.md di dalam folder proyek, dan DILARANG memanggil skill_manage atau memory.
   - Semua artefak audit wajib disimpan di dalam direktori audit/ proyek target (bukan .audit/).

## 2. Arsitektur File Murni di audit/ (STATE + 00b + 00 s/d 09)
Setiap file di dalam audit/ mewakili tepat satu domain murni agar hemat token baca-tulis dan bebas risiko tertimpa:
- `STATE.md` (**Kursor Checkpoint & Resume**): Satu-satunya sumber kebenaran posisi eksekusi aktif — `Active Phase`, `Active Sub-Stage`, `CURRENT_ACTIVE_ITEM`, `Domain Coverage Meter`, `Working Memory Scratchpad` (maks 10 baris), dan `Do-Not-Reopen List`. **Maksimal 50 baris.** Dibuat sejak Fase 1 Langkah 0; skema di `verify/templates/STATE.md`.
- `00b-file-inventory.md` (**Inventaris Fisik & Domain**): Daftar populasi penuh berkas kontrak beserta LOC efektif, jumlah fungsi mutasi state, domain arsitektur (D1..Dn), dan label `[MUST-AUDIT]` vs `[STATELESS/INTERFACE]`. Klasifikasi ditentukan **perilaku** (mengubah state / merutekan dana / eksekusi alur), **bukan** ambang jumlah baris. Berkas duplikat terverifikasi dihitung sekali.
- `00-project-map.md` s/d `03-attack-surface-queue.md` (Output Fase 1): Peta proyek & invarian (00), Baseline Realitas 3 Paradigma Rantai & 3 Kasta Aset (01), Matriks mutasi variabel (02), dan Antrean Unit Alur Eksekusi berlabel [LOAD: ref-...] (03). `03` dibangun dengan **Flow-Cluster** (maksimal 40 unit; setiap berkas `[MUST-AUDIT]` muncul tepat satu unit) dan memuat tabel cakupan per domain.
- `04-code-guarded.md` (Output Fase 2 Putaran 1 -> Umpan Putaran 2): Murni hipotesis yang dihentikan oleh guard kode (require / if (...) revert / assert! beserta File:Baris, Ekspresi Guard, dan Variabel Pembentuk). Dibaca kembali oleh Subagent Putaran 2 untuk mencari celah *Guard-Inversion* (Metode 5).
- `05-raw-leads.md` (Output Fase 1 & 2 -> Input Fase 3): Murni antrean kerja aktif berisi seluruh anomali mutasi state yang belum terhalang guard kode dan menunggu pembuktian di laboratorium Fase 3.
- `06-refuted-invalid.md` (Output Fase 3 & 4 — Gugur Permanen): Murni hipotesis yang mati permanen karena gagal *Pre-PoC Fact Gate*, PoC gagal/revert di state nyata, atau melanggar **Pernyataan Ketat Mutlak (#1–#6)** di `verify/VERDICT.md` — yaitu kelas: `REJECTED_FANTASY_MOCK`, `REJECTED_UNPROVEN_DEPLOYMENT`, `REJECTED_GENESIS_MIRAGE`, `REJECTED_NO_VICTIM`, `REJECTED_NEGATIVE_EV`, `REJECTED_CHEATCODE`, `REJECTED_PRIVILEGED_FANTASY`, `REJECTED_NON_LIVE_INIT`, `REJECTED_DUST`, `REJECTED_BY_DESIGN`, `REJECTED_MISMATCH`, `REJECTED_POC_FAILS`.
- `07-needs-next-step.md` (Output Fase 3 & 4 — Belum Selesai Diuji): Murni kandidat yang secara logika kode kuat, tetapi belum tuntas dibuktikan karena berada dalam batasan eksplorasi/tooling: (1) NEXT_EXPLORE (butuh Stateful Fuzzing, SMT Halmos, atau multi-step chaining), (2) NEXT_MAINNET (butuh verifikasi storage/parameter on-chain mainnet), atau (3) TOOL_BLOCKED (terhalang ketersediaan RPC/tooling). Termasuk klaim yang masih berstatus `HEAD-only` (gagal Pernyataan #2).
- `08-valid-not-eligible.md` (Output Fase 4 via `VERDICT.md` — Valid dalam Batasan / Low): Murni temuan yang PoC-nya terbukti jalan secara mekanis tanpa curang, tetapi berada dalam Batasan Toleransi `VERDICT.md`: berdampak *"Annoying but not financially dangerous"* (*DoS with no fund loss*, *minor capped economic damage*, *nuisance griefing* — Severity Low/S4), merupakan *admin-only bug* tanpa jalur eksploitasi eksternal, atau fitur belum *live* di produksi.
- `09-confirmed-findings.md` (Output Fase 3 -> Disahkan Fase 4 — Bounty-Ready): HANYA berisi temuan berstatus VALID_ELIGIBLE: terbukti 100% lewat PoC pada fork state produksi nyata (Mode Uji: FORK), tanpa *Fantasy Mock*/Cheatcode, berdampak bahaya finansial nyata (Critical/High/Medium), dan lolos seluruh 10 Pernyataan Wajib di `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md`.

---

## 2b. Protokol Ketahanan Konteks & Auto-Resume (Write-Ahead Checkpoint)

1. **Hukum Cold-Start / Compaction.** Setiap kali sesi baru dimulai, konteks terkompresi, atau pengguna memicu mode autopilot pada proyek yang sedang berjalan, instruksi implisit yang berlaku **mutlak** adalah: *"Baca `audit/STATE.md` dan lanjutkan audit dari posisi kursor terakhir."* Tidak perlu menunggu perintah eksplisit, dan DILARANG memulai dari Fase 1 bila `STATE.md` sudah ada.

2. **Larangan Baca Ulang (Anti-Context-Bloat).** Parent Agent maupun Subagent **DILARANG** membaca ulang kode sumber atau menguji ulang item yang sudah masuk **Do-Not-Reopen List** — yaitu isi `Completed Units`, `06-refuted-invalid.md`, `08-valid-not-eligible.md`, dan `09-confirmed-findings.md`. Item yang gugur terkunci permanen; membukanya kembali hanya sah bila ada bukti baru yang material dan tercatat di `STATE.md` (lihat `sc-phase3-verify-and-poc` Langkah 0b butir 3).

3. **Sinkronisasi Atomik.** **Tidak boleh** ada perpindahan dari satu unit kerja (`S-n` atau `LEAD-n`) ke unit berikutnya tanpa memperbarui `audit/STATE.md` **terlebih dahulu**: geser `CURRENT_ACTIVE_ITEM`, tambahkan item selesai ke `Completed Units` atau `Do-Not-Reopen List`, dan perbarui `Domain Coverage Meter`. Checkpoint ditulis **sebelum** pekerjaan berikutnya dimulai (write-ahead), bukan sesudahnya — sehingga bila proses terhenti di tengah jalan, `STATE.md` tetap menunjukkan posisi yang benar.

4. **Batas Ukuran STATE.md.** Maksimal **50 baris**. `Working Memory Scratchpad` maksimal 10 baris dan hanya memuat konteks unit aktif. Temuan final wajib dipindahkan ke `05-raw-leads.md`; STATE.md bukan tempat menyimpan hasil, melainkan **posisi**.

## 3. Corong Penyaringan 3 Lapis
1. Lapis 1 — Fase 2 (Hunter Kreatif Tanpa Penghakiman Prematur): Bedah fungsi dengan *First-Principles* (Backward Sink-to-Source) + Analogi Referensi & Katalog *Attacker POV*. Hanya cegah halusinasi sifat Token Kasta 1 dan pemanggilan langsung onlyOwner. Jangan membuang anomali kecil/DoS di Fase 2 agar tetap bisa dirangkai (*chained*) di Putaran 2! Pisahkan output murni ke 04-code-guarded.md atau 05-raw-leads.md.
2. Lapis 2 — Fase 3 (Saringan Fakta Pra-PoC & Kejujuran Lab Fork): Sebelum menulis PoC, buang ke 06-refuted-invalid.md jika lead mengasumsikan LP/Share token punya *Fee-on-Transfer*/USDT-quirk, menyerang initialize()/kolam kosong yang sudah *live*, atau menuntut aksi Admin jahat. Saat menulis PoC, dilarang menggunakan *Fantasy Mock* atau Cheatcode (vm.store, vm.etch, vm.prank(admin)), dan wajib coba amplifikasi dampak pada Fork produksi.
3. Lapis 3 — Fase 4 (Hakim Akhir via `verify/VERDICT.md`): Wajib membaca dan menerapkan /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md untuk memisahkan hasil ke 06-refuted-invalid.md (Ketat Mutlak), 07-needs-next-step.md, 08-valid-not-eligible.md (Dalam Batasan/Low), dan 09-confirmed-findings.md (Valid Eligible).

---

## 3b. Tiga Hukum Anti-Menyerah (mengikat Parent & Subagent)

Ketiganya bersifat **konstitusi**, bukan saran. Melanggarnya = laporan tidak sah.

1. **2-Strike Circuit Breaker.** Maksimal **2 percobaan gagal** per hipotesis. Percobaan ke-3 DILARANG sebelum seluruh lead lain melewati triage batch + pengujian awal. Kegagalan **alat** (compile, import, checksum, ABI, offset decode) **bukan** strike — bedakan dari kegagalan **hipotesis**.

2. **Tangga Self-Healing Tooling (sebelum `TOOL_BLOCKED`).** Label `TOOL_BLOCKED` DILARANG untuk masalah kompilasi dependency/remapping/versi compiler/test runner. Wajib menempuh berurutan: **(a)** flag & toolchain (`--via-ir`, `--optimize`, `--evm-version`, `cargo-build-sbf`, `anchor test --skip-local-validator`) → **(b) Standalone Interface-Only / Minimal Harness** (deklarasikan interface, tembak langsung ke Local Fork — tidak perlu kompilasi seluruh repo) → **(c)** fallback RPC (`.env.rpc`, `rpc-env.sh`, chunking `eth_getLogs`). Log terminal ketiganya wajib dilampirkan di entri `07`.

3. **Hukum Kerjakan Sekarang (`NEXT_MAINNET` / `NEXT_EXPLORE`).** DILARANG memarkir lead bila pekerjaannya bisa diselesaikan sesi ini. RPC tersedia → wajib `cast call` / `cast storage` / `cast implementation` saat itu juga dan tuntaskan ke `09` atau `06`. Baru satu skenario → wajib jalankan multi-step chaining / Differential (Tier 3) / Handler Fuzzing (Tier 2) / halmos (Tier 5) sampai **timeout komputasi**. Setiap entri `07` wajib memuat blok `PERCOBAAN: <perintah> + <keluaran>`.

**Gerbang Hakim (Pernyataan #11 — `LAZY_BAILOUT_DETECTED`).** Fase 4 WAJIB memeriksa seluruh entri `07`. Entri tanpa bukti usaha → laporan **DITOLAK** dan lead dikembalikan ke Fase 3. Label basi (judul sudah dipindah tetapi label lama masih tertinggal) dihitung tidak sah. **Target akhir `07` = 0 entri**; setiap sisa harus dipertahankan dengan log komputasi, bukan kalimat.

## 4. Protokol Wajib Delegasi Subagent (delegate_task)
Setiap panggilan delegate_task WAJIB menyertakan di parameter context: (1) Path Absolut Proyek, (2) Paradigma Rantai & Core Invariants, (3) Path File audit/00 s/d 09 yang relevan, (4) Instruksi memanggil skill_view, dan (5) Perintah agar Subagent menulis detail ke audit/notes/ serta mengembalikan ringkasan maksimal 12 baris.

## 5. Tangga Bukti & Aturan Anti-False-Negative (rujuk `verify/VERDICT.md`)
1. **Tangga Bukti** wajib dicantumkan pada setiap verdict: `A` FORK (bytecode ter-deploy, `[PASS]`, tanpa cheatcode) -> boleh `09`; `B` LOKAL dengan kontrak asli -> maksimal `08`; `C` STRUKTURAL atau mock pihak ketiga -> maksimal `07`; `D` asumsi tanpa eksekusi -> `06`.
2. **Langkah 0 — Rekonsiliasi Deployment** wajib sebelum menilai klaim apa pun: ambil source terverifikasi explorer, baca slot EIP-1967 untuk proxy, bandingkan `sha256` dengan repo. Kode berbeda => tandai `HEAD-only`, verdict maksimal `07`.
3. **Kegagalan query bukan bukti ketiadaan.** `status: 0` dari explorer (mis. chain tidak didukung paket gratis), timeout RPC, atau `eth_getLogs` terbatas rentang wajib diulang lewat sumber lain sebelum menyimpulkan.
4. **Perilaku off-chain diuji black-box lebih dulu** (rekonstruksi event on-chain) sebelum menyatakan "butuh repo privat".
5. **Mock pihak ketiga** (CCTP/LayerZero/precompile) hanya menopang bukti struktural; dilarang menaikkan verdict ke `09`.
