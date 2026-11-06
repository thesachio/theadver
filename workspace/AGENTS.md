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
- **Langkah C** — Buka **FILE AUDIT** relevan (`03-attack-surface-queue.md` bila di Fase 2, `05-raw-leads.md` bila di Fase 3) **hanya pada baris item aktif**. Gunakan `grep -n` atau baca sebagian (`offset`/`limit`). **DILARANG memuat satu FILE AUDIT penuh.**
- **Langkah D** — **DILARANG KERAS** membaca ulang kode kontrak dari unit yang tercatat di `Completed Units`, dan **DILARANG menguji ulang** lead yang sudah ada di `06-refuted-invalid.md` (Dead-End) atau `08-valid-not-eligible.md` (Verified-Not-Eligible). Larangan ini juga berlaku untuk lead berstatus `REJECTED_POC_FAILS` yang terkunci `3-Stage Escalation (2 Manual + 1 Fuzz)`.

> ⚠️ **BATAS OBJEK LANGKAH C & D — BACA INI, JANGAN DITAFSIRKAN SENDIRI.**
> Hemat-konteks **BERLAKU HANYA UNTUK `audit/*.md`**. **KODE SUMBER KONTRAK (`source/`, `contracts/`, `src/`, `programs/`) TIDAK TERMASUK.**
> - **Kode kontrak WAJIB dibaca UTUH** dari `function` sampai `}` penyeimbang sebelum menulis lead (`sc-phase2-hunt` §A0) atau menulis PoC (`sc-phase3-verify-and-poc` Langkah 0e). `read_file` ber-`offset`/`limit` bila fungsi > 60 baris.
> - **`grep`/`sed`/`head`/`tail` HANYA untuk menemukan lokasi**, **DILARANG** dipakai menyimpulkan isi fungsi atau membuktikan klaim negatif ("tidak ada guard", "X tidak dipanggil").
> - **Pengecualian Langkah D:** larangan baca-ulang **GUGUR** bila unit di `Completed Units` **tidak mencatat rentang baca** (`File:awal-akhir` + jumlah baris). Tanpa rentang tercatat, unit **dianggap belum selesai** dan pembacaan utuh **WAJIB** dilakukan.
>
> **Alasan aturan ini saling berlawanan arah:** hemat-token melindungi **file audit** yang tumbuh besar (65 KB); anti-hemat melindungi **pemahaman kode** yang bisa hancur oleh potongan. Menerapkan salah satunya ke objek yang salah menghasilkan biaya atau lead palsu.

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

## 1.3 PROTOKOL ANTI-TRUNCATE & METODE WRITE (WAJIB SEBELUM MENULIS `audit/*.md`)

Berlaku **global untuk seluruh fase (Fase 1 s.d. Fase 4)** dan **setiap Subagent**, bukan hanya Fase 2. Subagent Fase 1/3/4 hanya memanggil `skill_view` pada skill fasenya sendiri, sehingga aturan ini **tidak** akan sampai lewat `sc-phase2-hunt` — karena itu ia diangkat ke konstitusi ini.

### 1.3.1 Hukum Atomisitas — `open("w")` DILARANG

- **DILARANG KERAS** `open(path, "w")` (Python) dan `>` (shell redirect) untuk **seluruh** `audit/*.md`, termasuk `00`, `00b`, `01`, `02`, `03`, `04`–`09`, `STATE.md`, dan `notes/`.
- **Alasan:** `open(path, "w")` memotong file ke **0 byte saat dibuka**, sebelum satu byte pun ditulis. Bila penulisan gagal di tengah (PermissionError, disk penuh, proses mati), isi asli **hilang permanen**.
- **Insiden nyata:** `04-code-guarded.md` terpotong menjadi 0 byte; backup write-ahead yang dibuat *sesudahnya* ikut menyalin file kosong. ~247 entri Putaran 1 + 39 entri Putaran 2 hilang; restorasi verbatim mustahil.
- **Mutasi yang SAH:** native tool `write_file`, `patch`, `append` (append via tool, bukan `>>`), atau skrip **wajib** memakai pola `.tmp` → `fsync` → `os.replace()` (atomik).
- **Larangan `>>` shell:** redirect append pada file audit juga dilarang karena tidak atomik dan tidak dilindungi lock; gunakan native tool.

### 1.3.2 Backup Write-Ahead

Backup **SEBELUM** mutasi, bukan sesudah. Backup yang dibuat setelah kegagalan menyimpan kekosongan dan tidak berguna. Verifikasi pasca-tulis wajib: ukuran ≠ 0 **dan** heading domain masih ada.

### 1.3.3 Tabel Metode Write per Karakteristik File

**DILARANG memakai "append selalu" sebagai resep tunggal.** Tiap file punya pola mutasi berbeda; append pada file yang **diubah berulang** membuat status basi.

| Karakteristik | File | Metode wajib | DILARANG |
|---|---|---|---|
| Tulis sekali | `INTEL.md`, `00`, `01`, `02` | `write_file` awal; tambahan → `append` | tulis ulang penuh |
| Generate massal | `00b` | **script** (`phase0_inventory.py`); verifikasi `grep -n` | baca penuh (≈9k token) |
| Append-murni | `06`, `08`, `09`, `RADAR` | `append` | edit entri setelah ditulis |
| Append lalu ubah status | `04`, `05`, `07` | entri baru → `append`; status → `patch` | append saja (status jadi basi) |
| Edit tabel/baris | `03`, `STATE` | `patch` baris | tulis ulang penuh (134× lebih mahal) |
| Staging Subagent | `notes/staging-<unit>.md` | `write_file` / `atomic_write` | menulis ke `04`–`09` |

**Aturan pemilihan:** metode dengan token terendah **yang tetap benar**.

### 1.3.4 Satu Penulis per File

Subagent **DILARANG** menulis ke `audit/04`–`09`. Mereka menulis entri lengkap ke `audit/notes/staging-<unit>.md`, lalu **Parent** yang menggabungkan (lihat Pasal 4 — Protokol Staging). Alasan: ringkasan `≤16 baris` tidak dapat membawa muatan 120–160 baris, dan `max_concurrent_children` adalah konfigurasi yang bisa berubah, bukan jaminan.

---

## 1.4 PROTOKOL INTEGRITAS BUKTI — DILARANG MENULIS BUKTI DARI INGATAN

**Hukum:** blok bukti di `06`/`08`/`09` (`BUKTI_SIMULASI:`, `PERCOBAAN:`, log `forge test`/`cast`) **WAJIB** ditempel dari keluaran yang benar-benar dijalankan, atau disalin dari `audit/notes/*-bukti-simulasi.md` yang sudah memuat log aslinya. Menyusunnya dari narasi atau ingatan = **`FABRICATED_EVIDENCE`** = laporan DITOLAK.

**Mengapa aturan ini terpisah dari `#11e`:** `#11e` mencegah *"gugur tanpa bukti"*. Aturan ini mencegah **"menyajikan bukti yang tidak ada"** — kegagalan yang **lolos semua gerbang otomatis**. `verify07.py` hanya memeriksa *ada-tidaknya* baris `$ ...`; `grep -c` hanya menghitung entri; `#11e` hanya memeriksa keberadaan kata `BUKTI_SIMULASI`. Semuanya **PASS** meski isinya palsu.

**Insiden nyata:** pada audit run-2, blok bukti di `08-valid-not-eligible.md` memuat tiga nama test yang **tidak pernah ada** (`test_L03_timelockStartByThirdParty`, `test_L03_ownerCannotCancel`, `test_L03_resetWindowExtends3x`). Berkas aslinya berisi nama berbeda. Nama-nama itu terasa masuk akal sehingga lolos tanpa dicurigai.

**Verifikasi wajib sebelum menutup Fase 4:**

```bash
# 1. Nama test di 06/08/09 harus ADA di lab atau arsip
forge test --list | grep -oE 'test[A-Za-z0-9_]+' | sort -u > /tmp/real.txt
cat audit-lab-archive/*.sol 2>/dev/null \
  | grep -hoE 'function (test[A-Za-z0-9_]+)' | sed 's/function //' >> /tmp/real.txt
sort -u /tmp/real.txt -o /tmp/real.txt
# ekstrak test_* dari 06/08/09, sisa yang tidak cocok = FABRICATED_EVIDENCE
```

```bash
# 2. Nomor File:Baris wajib dicek ulang, bukan dari ingatan
# 3. Setiap baris "Perintah yang dijalankan:" harus punya keluarannya, bukan hanya perintahnya
```

**Label yang sah:** hanya **"terverifikasi"** bila ada kutipan kode + log eksekusi. Tanpa keduanya, label yang jujur adalah **"indikasi"**.

---

## 2. Arsitektur File Murni di audit/ (STATE + INTEL + 00b + 00 s/d 09)
Setiap file di dalam audit/ mewakili tepat satu domain murni agar hemat token baca-tulis dan bebas risiko tertimpa:
- `STATE.md` (**Kursor Checkpoint & Resume**): Satu-satunya sumber kebenaran posisi eksekusi aktif — `Active Phase`, `Active Sub-Stage`, `CURRENT_ACTIVE_ITEM`, `Domain Coverage Meter`, `Working Memory Scratchpad` (maks 10 baris), dan `Do-Not-Reopen List`. **Maksimal 50 baris.** Dibuat sejak Fase 1 Langkah 0; skema di `verify/templates/STATE.md`.
- `INTEL.md` (**Konteks Awal & Tautan Referensi Langsung — Fase 0**): Berisi 6 informasi inti hasil `sc-project-intel` (Nama Proyek, Overview singkat 1–3 kalimat, Link UI/dApp, Link Repo GitHub Spesifik + commit HEAD, Direct Link aturan Bug Bounty, dan Direct Links laporan audit terdahulu). Maksimal 40 baris; skema di `verify/templates/INTEL.md`.
- `00b-file-inventory.md` (**Inventaris Fisik & Domain**): Daftar populasi penuh berkas kontrak beserta LOC efektif, jumlah fungsi mutasi state, domain arsitektur (D1..Dn), dan label `[MUST-AUDIT]` vs `[STATELESS/INTERFACE]`. Klasifikasi ditentukan **perilaku** (mengubah state / merutekan dana / eksekusi alur), **bukan** ambang jumlah baris. Berkas duplikat terverifikasi dihitung sekali.
- `00-project-map.md` s/d `03-attack-surface-queue.md` (Output Fase 1): Peta proyek & invarian (00), Baseline Realitas 3 Paradigma Rantai & 3 Kasta Aset (01), Matriks mutasi variabel (02), dan Antrean Unit Alur Eksekusi berlabel [LOAD: ref-...] (03). `03` dibangun dengan **Flow-Cluster** (maksimal 40 unit; setiap berkas `[MUST-AUDIT]` muncul tepat satu unit) dan memuat tabel cakupan per domain. Setiap unit `S-n` di `03` juga memuat tag **Kelas Topologi Entitas** (`[CLASS-A]` Single-Entity, `[CLASS-B]` Dual-Entity, `[CLASS-C]` Multi-Entity Long Flow) dan memanggil `ref-method-registry.md` + `ref-attacker-pov.md` pada baris `[LOAD: ...]`. Baseline Fase 1 bersifat **BEKU**; pemahaman hidup ada di `FACTS.md`.
- `04-code-guarded.md` (Output Fase 2 Putaran 1 -> Umpan Putaran 2): Murni hipotesis yang dihentikan oleh **Guard Statis / Struktural** (`onlyOwner`, `onlyRouter`, `msg.sender == x`, `nonReentrant`, `whenNotPaused`, cek alamat `!= 0`) yang berstatus **`TERSANGKAL`** (tidak tembus oleh **5 Jalur Permissionless** di `verify/templates/04-code-guarded.md`), beserta File:Baris, Ekspresi Guard, dan Variabel Pembentuk. **DILARANG** memasukkan guard dinamis/matematis (perhitungan rasio, pembulatan, saldo, waktu, panjang array) **maupun guard statis yang `TEMBUS` salah satu dari 5 Jalur Permissionless** ke `04` — semuanya wajib masuk ke `05-raw-leads.md` untuk diuji di Fase 3!
- `FACTS.md` (**Fakta Mekanisme Proyek — terverifikasi, hidup**): Berisi pemahaman bagaimana proyek bekerja yang membuat Fase 3 dapat merancang uji tajam. Tujuh komponen wajib per domain: `BERKAS` (kunci pencarian), `MEKANISME`, `CHAINING` (state yang bertahan lintas-hop), `DATA` (tipe/satuan/sentinel), `INVARIAN` (+penegak atau `TIDAK ditegakkan`), `LINGKUNGAN` (klasifikasi otoritas ber-tag `[chain:alamat]`), `ASUMSI`. **DILARANG memuat hipotesis** (itu `05`) **dan status deployment** (`CYCLE`/`ENTRYPOINT`/`Mode Uji` — itu `deploy-parity-*.json`). `patch` per baris, ≤12 baris/domain, +≤3 baris/unit, maks 2 `M-FACT` per unit. Disuntikkan ke `context` setiap `delegate_task` (butir 7) dan dicari Fase 3 lewat `grep` path berkas. Blueprint lengkap: `verify/templates/FACTS.md`.
- `RADAR.md` (Output Fase 2 — **Sinyal Lintas-Domain, Append-Only**): Murni observasi berpresisi `File:Baris` yang **belum layak jadi lead** — belum ada bukti eksploitasi, tetapi menunjukkan asimetri (harapan vs kenyataan) pada seam/urutan/state yang mungkin relevan bagi **unit lain di proyek yang sama**. Bukan `05` (belum teruji) dan bukan atestasi (jelas ada kejanggalan). **Dua lapis**: Observasi (ditulis sekali) + Kejadian (`PROMOTED`, `RESOLVED-*`, `TARGET-ADDED`, `REOPENED`, `EXHAUSTED`) — keduanya **append murni, dilarang edit**. Sinyal **DILARANG** diparkir di sini bila sudah ada PoC `[PASS]` (wajib naik ke `05`). Penarikan sinyal wajib berbasis **path berkas**, bukan ID unit, karena daftar `Tujuan` dianggap hipotesis. Skema & gerbang 3-Uji di `verify/templates/RADAR.md`.
- `05-raw-leads.md` (Output Fase 1 & 2 -> Input Fase 3): Murni antrean kerja aktif berisi seluruh anomali mutasi state, *Patch-Scar*, ketidaksinkronan View-vs-Write, serta **Guard Dinamis/Matematis** yang menunggu pembuktian simulasi dan fuzzing di laboratorium Fase 3. Sinyal yang **belum teruji dan bukan milik unit aktif** tidak masuk sini — tempatnya di `RADAR.md`.
- `06-refuted-invalid.md` (Output Fase 3 & 4 — Gugur Permanen): Murni hipotesis yang mati permanen karena merupakan **kesalahan baca statis literal**, PoC tetap gagal/`revert` setelah *Victim Seeding* + *3-Stage Escalation (2 Manual + 1 Fuzz)*, atau melanggar **Pernyataan Ketat Mutlak (#1–#6)** di `verify/VERDICT.md` — kelas: `REJECTED_FANTASY_MOCK`, `REJECTED_UNPROVEN_DEPLOYMENT`, `REJECTED_GENESIS_MIRAGE`, `REJECTED_NO_VICTIM`, `REJECTED_NEGATIVE_EV`, `REJECTED_CHEATCODE`, `REJECTED_PRIVILEGED_FANTASY`, `REJECTED_NON_LIVE_INIT`, `REJECTED_DUST`, `REJECTED_BY_DESIGN`, `REJECTED_MISMATCH`, `REJECTED_POC_FAILS`. **Hukum Anti-Paper-Refutation (#11e):** setiap entri `REJECTED_POC_FAILS`, `REJECTED_NEGATIVE_EV`, dan `REJECTED_DUST` di `06` **WAJIB** melampirkan log eksekusi test + fuzz (`BUKTI_SIMULASI:`); penolakan kertas tanpa kode test memicu **`PAPER_REFUTATION_DETECTED`** dan membatalkan laporan.
- `07-needs-next-step.md` (Output Fase 3 & 4 — Belum Selesai Diuji): Murni kandidat yang secara logika kode kuat, tetapi belum tuntas dibuktikan karena berada dalam **batasan komputasi/tooling ekstrem**: (1) `NEXT_EXPLORE` (mentok timeout saat Stateful Fuzzing/Halmos), (2) `NEXT_MAINNET` (rantai benar-benar tanpa RPC/explorer publik), atau (3) `TOOL_BLOCKED` (gagal setelah 3-Step Self-Healing). Setiap entri **WAJIB** memuat `Disposition:` dan blok `PERCOBAAN:` berisi perintah `$ ...` + keluaran nyata. **Target akhir `07` = 0 entri** (temuan `HEAD-only` yang PoC-nya sudah `PASS` **DILARANG** ditaruh di `07`, melainkan masuk ke `08`).
- `08-valid-not-eligible.md` (Output **Eksklusif Fase 4** via `VERDICT.md` — Valid Secara Mekanis, Dalam Batasan Eligibilitas): Murni temuan yang PoC eksploitasi dan mekanismenya terbukti `[PASS]` tanpa curang, tetapi dipisahkan oleh Hakim Fase 4 karena: (a) **`PRE_LIVE_SCOPE (HEAD_ONLY_PROVEN)`** — terbukti berbahaya pada kode repositori (`FORK_DEPLOYED_HEAD` / `LOKAL`), namun kontrak/fitur belum *live* di produksi atau berada di luar daftar alamat bounty saat ini; (b) **`ADMIN_ONLY`** (#8b); atau (c) **`LOW_NUISANCE`** (#10b — Severity Low/S4). **Subagent Fase 3 DILARANG mengirim entri langsung ke `08`.**
- `09-confirmed-findings.md` (Output Fase 3 -> Disahkan Fase 4 — Bounty-Ready **Live Production**): HANYA berisi temuan berstatus `VALID_ELIGIBLE`: terbukti 100% lewat PoC pada fork state produksi nyata (`Mode Uji: FORK_LIVE`, atau `FORK_DEPLOYED_HEAD` yang kodenya terverifikasi identik dengan bytecode produksi **`LIVE_MATCH`**), tanpa *Fantasy Mock*/Cheatcode, berdampak bahaya finansial nyata (Critical/High/Medium), dan lolos seluruh **11 Pernyataan Wajib** di `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md`.

---

## 2b. Protokol Ketahanan Konteks & Auto-Resume (Write-Ahead Checkpoint)

1. **Hukum Cold-Start / Compaction.** Setiap kali sesi baru dimulai, konteks terkompresi, atau pengguna memicu mode autopilot pada proyek yang sedang berjalan, instruksi implisit yang berlaku **mutlak** adalah: *"Baca `audit/STATE.md` dan lanjutkan audit dari posisi kursor terakhir."* Tidak perlu menunggu perintah eksplisit, dan DILARANG memulai dari Fase 1 bila `STATE.md` sudah ada.

2. **Larangan Baca Ulang (Anti-Context-Bloat).** Parent Agent maupun Subagent **DILARANG** membaca ulang kode sumber atau menguji ulang item yang sudah masuk **Do-Not-Reopen List** — yaitu isi `Completed Units`, `06-refuted-invalid.md`, `08-valid-not-eligible.md`, dan `09-confirmed-findings.md`. Item yang gugur terkunci permanen; membukanya kembali hanya sah bila ada bukti baru yang material dan tercatat di `STATE.md` (lihat `sc-phase3-verify-and-poc` Langkah 0b butir 3).

3. **Sinkronisasi Atomik.** **Tidak boleh** ada perpindahan dari satu unit kerja (`S-n` atau `LEAD-n`) ke unit berikutnya tanpa memperbarui `audit/STATE.md` **terlebih dahulu**: geser `CURRENT_ACTIVE_ITEM`, tambahkan item selesai ke `Completed Units` atau `Do-Not-Reopen List`, dan perbarui `Domain Coverage Meter`. Checkpoint ditulis **sebelum** pekerjaan berikutnya dimulai (write-ahead), bukan sesudahnya — sehingga bila proses terhenti di tengah jalan, `STATE.md` tetap menunjukkan posisi yang benar.

4. **Batas Ukuran STATE.md.** Maksimal **50 baris**. `Working Memory Scratchpad` maksimal 10 baris dan hanya memuat konteks unit aktif. Temuan final wajib dipindahkan ke `05-raw-leads.md`; STATE.md bukan tempat menyimpan hasil, melainkan **posisi**.

## 2c. Protokol Anti-Truncate & Metode Write per Karakteristik File (Mengikat Seluruh Fase)
1. **Larangan Mutlak Truncate (`open("w")` & `>`)**: Menggunakan `open(path, "w")`, shell `>`, atau `sed -i` pada file `audit/*.md` **DILARANG KERAS** karena langsung memotong file menjadi **0 byte** sebelum data ditulis. Jika menulis via skrip Python, wajib gunakan pola atomik: tulis ke `.tmp` -> `f.flush()` -> `os.fsync()` -> `os.replace(tmp, path)`. Backup wajib dibuat **sebelum** mutasi (*write-ahead backup*), bukan sesudahnya.
2. **Pemilihan Metode Write (Wajib Hemat Token & Tidak Merusak Status)**:
   - **Tulis sekali** (`INTEL.md`, `00`, `01`, `02`): gunakan `write_file` saat inisialisasi awal; tambahan kecil berikutnya gunakan `append`. **Dilarang tulis ulang penuh.**
   - **Generate massal** (`00b`): gunakan script (`phase0_inventory.py`) dan verifikasi via `grep -n`. Dilarang menulis manual atau membaca penuh.
   - **Append-murni** (`06`, `08`, `09`): gunakan `append` karena entri yang sudah masuk tidak diubah lagi statusnya.
   - **Append lalu ubah status** (`04`, `05`, `07`): saat menambah entri baru gunakan `append`; saat mengubah status entri (mis. `BELUM` -> `DITEMBUS`/`TETAP_AMAN` di `04`, atau update status di `05`/`07`) **wajib** gunakan `patch` pada blok entri tersebut.
   - **Edit tabel/kursor baris** (`03`, `STATE.md`): wajib gunakan `patch` baris spesifik (cari nomor baris via `grep -n` bila perlu; ~40 token vs ~5.300 token baca-tulis penuh). Khusus `STATE.md` **hanya boleh di-`patch` oleh Parent Orchestrator**.

---

## 3. Corong Penyaringan 3 Lapis (Simulation-First Architecture)
1. **Lapis 1 — Fase 2 (Hunter Kreatif & Pemisahan Guard Statis vs Dinamis):** Bedah fungsi dengan *First-Principles* (`M-001..M-010` dari `ref-method-registry.md`) + Katalog *Attacker POV* (`ref-pov-*.md`). Hanya cegah halusinasi sifat Token Kasta 1 dan pemanggilan langsung `onlyOwner`. Jangan membuang anomali kecil/DoS di Fase 2! Pisahkan output murni: **hanya guard izin/struktural statis yang terbukti `TERSANGKAL`** (lolos uji **5 Jalur Permissionless**) yang boleh ke `04-code-guarded.md`; **semua anomali mutasi state, guard statis yang `TEMBUS` salah satu dari 5 Jalur Permissionless, dan seluruh guard dinamis/matematis wajib masuk ke `05-raw-leads.md`**.
2. **Lapis 2 — Fase 3 (Simulation-First Lab, Blind to Bounty Scope, & No Code No Reject):**
   - **Hukum *No Code, No Reject*:** Dilarang menggugurkan lead logika, matematika, atau ekonomi ke `06` hanya dengan hitungan kertas di Langkah 1. Kecuali 4 kemustahilan statis sempit, seluruh lead **wajib dibuatkan kode simulasi test**!
   - **Dual-Mode Fork & Victim Seeding:** Gunakan `FORK_LIVE` bila kontrak sudah aktif di mainnet, atau `FORK_DEPLOYED_HEAD` (deploy kontrak repo di atas fork mainnet) bila kontrak belum deploy / kode HEAD lebih baru. Wajib simulasikan transaksi pengguna normal (`vm.prank(victim)`) sebelum menyatakan PoC gagal/`revert`.
   - **Buta Cakupan Administratif:** Subagent Fase 3 **dilarang menyentuh `08`** atau menggugurkan lead karena alasan HEAD-only/pre-live. Semua PoC yang `[PASS]` wajib diajukan sebagai **kandidat `09`** untuk diadili di Fase 4.
3. **Lapis 3 — Fase 4 (Hakim Akhir & Gerbang Deployment via `verify/VERDICT.md`):** Wajib menjalankan Langkah 0 Rekonsiliasi Deployment dan 11 Pernyataan Wajib untuk memisahkan kandidat secara presisi ke `09-confirmed-findings.md` (`LIVE_MATCH`), `08-valid-not-eligible.md` (`HEAD_ONLY_PROVEN` / `LOW_NUISANCE` / `ADMIN_ONLY`), `07-needs-next-step.md` (target 0 entri), dan `06-refuted-invalid.md` (wajib bukti log simulasi untuk #11e).

---

## 3b. Tiga Hukum Anti-Menyerah (mengikat Parent & Subagent)

Ketiganya bersifat **konstitusi**, bukan saran. Melanggarnya = laporan tidak sah.

1. **3-Stage Escalation Breaker (2 Manual + 1 Mandatory Fuzz).** Sebuah hipotesis di Fase 3 **DILARANG** dinyatakan gugur (`REJECTED_POC_FAILS` / `REJECTED_NEGATIVE_EV` / `REJECTED_DUST`) hanya dari 1–2 percobaan angka manual. Setelah **Strike 1** (Manual + *Victim Seeding*) dan **Strike 2** (Perbaikan Urutan + *3-Way Amplification*) gagal, agen **WAJIB** menjalankan **Strike 3** berupa 1× tes Fuzz (`testFuzz_` / `proptest` / `halmos`) untuk mengacak parameter input. Barulah jika Strike 3 Fuzz juga gagal, lead dikunci di `06` beserta log eksekusinya dan agen wajib pindah ke lead berikutnya. **Kegagalan alat** (compile, import, checksum, ABI) **bukan** strike.

2. **Tangga Self-Healing Tooling (sebelum `TOOL_BLOCKED`).** Label `TOOL_BLOCKED` **DILARANG** untuk masalah kompilasi dependency/remapping/versi compiler/test runner. Wajib menempuh berurutan: **(a)** flag & toolchain (`--via-ir`, `--optimize`, `--evm-version`, `cargo-build-sbf`, `anchor test --skip-local-validator`) → **(b)** **Standalone Interface-Only / Minimal Harness** (deklarasikan interface atau salin kontrak minimal, tembak langsung ke Local Fork) → **(c)** fallback RPC (`.env.rpc`, `rpc-env.sh`, chunking `eth_getLogs`). Log terminal ketiganya **wajib dilampirkan** di entri `07`.

3. **Hukum Kerjakan Sekarang (`NEXT_MAINNET` / `NEXT_EXPLORE`) & Larangan Paper Refutation (#11 & #11e).** **DILARANG** memarkir lead di `07` bila pekerjaannya bisa diselesaikan sesi ini, dan **DILARANG** membuang lead ke `06` tanpa log simulasi nyata.
   - **Gerbang Hakim (#11 & #11e):** Fase 4 **WAJIB** menjalankan `verify07.py` pada `07` dan memeriksa blok `BUKTI_SIMULASI:` pada `06`. Entri `07` tanpa bukti usaha (**`LAZY_BAILOUT_DETECTED`**) atau entri `06` tanpa log eksekusi test/fuzz (**`PAPER_REFUTATION_DETECTED`**) menyebabkan **laporan DITOLAK** dan dikembalikan ke Fase 3.

---

## 4. Protokol Wajib Delegasi Subagent (delegate_task)
Setiap panggilan delegate_task WAJIB menyertakan di parameter context: (1) Path Absolut Proyek, (2) Paradigma Rantai & Core Invariants, (3) Path File audit/00 s/d 09 yang relevan, (4) Instruksi memanggil skill_view, (5) **Protokol Staging** berikut, (6) **Sinyal RADAR** — hasil `grep -n -B1 -A6 "<berkas-yang-akan-dibaca>" audit/RADAR.md` untuk berkas yang menjadi lingkup unit tersebut (kosongkan bila tidak ada), dan (7) **Model Mekanisme** — kutip **utuh** blok domain unit tersebut dari `audit/FACTS.md` — temukan lewat `grep -n "<NamaBerkas>.sol" audit/FACTS.md` (≈12 baris). Tanpa butir 7, subagent menalar tanpa model proyek dan ketajaman kembali ke nol.

- Subagent menulis entri **lengkap siap-tempel** ke `audit/notes/staging-<unit>.md` (format final: kolom wajib, File:Baris, guard, Delta State, blok `PERCOBAAN:` bila relevan).
- Subagent **DILARANG** menulis ke `audit/04`–`09`. Wadah itu **hanya** ditulis Parent.
- Subagent mengembalikan **manifes** maksimal **16 baris**: 1 baris `STAGING: <path> | 04: <n> | 05: <n>` + 1 baris verdict per entri + maks 2 `R-CAND` + maks 2 `M-FACT`. Ringkasan **bukan** tempat muatan entri — satu entri 15–20 baris, unit normal 120–160 baris, jadi memuat isi di 12 baris mustahil tanpa memangkas temuan. (Batas dinaikkan dari 12 → 16 saat kanal `R-CAND`/`M-FACT` ditambahkan; tanpa itu unit dengan 8 entri + 4 kanal akan melampaui batas.)
- Subagent **WAJIB** mengembalikan maksimal **2 kandidat `R-xx`** (boleh 0) dengan format satu baris: `R-CAND: <Lokasi File:Baris> | <Asimetri> | <Pemicu> | Tujuan: <unit/domain>`. Kandidat ini **bukan** lead dan **tidak** dihitung sebagai temuan. **Parent** yang menilai dengan Gerbang 3-Uji (`verify/templates/RADAR.md`) lalu menulis `audit/RADAR.md` — subagent **DILARANG** menulisnya.
- Subagent **WAJIB** mengembalikan maksimal **2 `M-FACT`** (boleh 0) — fakta mekanisme yang **mengubah model proyek**, format satu baris: `M-FACT: <BERKAS|MEKANISME|CHAINING|DATA|INVARIAN|LINGKUNGAN|ASUMSI> <fakta> | <File:Baris> | dampak: <apa yang berubah>`. Fakta yang **mengubah cara Fase 3 merancang harness**, **membatalkan asumsi**, atau **menjelaskan keanehan** wajib dilaporkan; selebihnya tidak. **Parent** yang menilai dan `patch` `audit/FACTS.md` (+≤3 baris/unit) — subagent **DILARANG** menulisnya.
- Parent menggabungkan memakai `append`/`patch` sesuai tabel karakteristik file di `sc-phase2-hunt/references/ref-atomic-write.md` (**DILARANG** `open("w")` / `>`), lalu menghapus staging dan memverifikasi dengan `grep -c '^## \[' <file>` terhadap manifes.
- **WAJIB sebelum menghapus staging: catat ke `audit/notes/MERGE-LOG.tsv`** (append-only, TSV, tab) — inilah **manifes-dari-manifes** yang membuat puluhan staging bisa dicocokkan:
  `timestamp  phase  item  staging  sha256  n04  n05  n06  n07  n09  status`
  - `sha256` = hash staging **saat di-merge** (membuktikan isi yang di-merge = file yang tercatat; bila staging diubah sesudahnya, hash berbeda → terdeteksi).
  - `n04..n09` = jumlah entri yang **diklaim** masuk ke tiap wadah.
  - Menghapus staging **DILARANG** sebelum baris log ditulis. Tanpa log, penghapusan = kehilangan bukti permanen.
- **Pencocokan wajib dijalankan** sebelum Fase 2 ditutup dan sebelum Fase 4 dimulai:
  `python3 verify/tools/merge_audit.py --audit-dir audit`
  Mendeteksi lima kegagalan: `STAGING YATIM` (belum di-merge), `HASH BERUBAH` (diubah setelah merge), `ENTRI HILANG` (wadah < klaim), `ENTRI EKSTRA` (masuk tanpa log), `MERGE GANDA` (ID duplikat). Exit 1 = wajib diperbaiki sebelum lanjut.
- **Penamaan wajib agar bisa dicocokkan mesin:** staging `notes/staging-<FASE>-<ITEM>.md` (mis. `staging-P2-S-08.md`, `staging-P3-L-067.md`); backup `notes/backups/<YYYYMMDD-HHMMSS>-<nama-asli>` (**DILARANG** menaruh backup di `notes/` langsung — pola `05-backup-premarge2.md` yang tidak terparse membuat `notes/` menjadi tumpukan 50+ file tanpa urutan).

## 5. Tangga Bukti & Aturan Anti-False-Negative (rujuk `verify/VERDICT.md`)
1. **Tangga Bukti** wajib dicantumkan pada setiap verdict:
   - **`A`** (`Mode Uji: FORK_LIVE` terhadap bytecode produksi ter-deploy, `[PASS]`, tanpa cheatcode) -> berhak masuk `09`;
   - **`A-HEAD`** (`Mode Uji: FORK_DEPLOYED_HEAD` — kontrak repo di-deploy di atas fork mainnet nyata, `[PASS]`, tanpa cheatcode) -> masuk `09` bila kode cocok produksi (`LIVE_MATCH`), atau masuk `08` [`PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN`] bila kontrak/fitur belum live (`HEAD-only`);
   - **`B`** (`Mode Uji: LOKAL` dengan kontrak asli untuk non-EVM / rantai tanpa RPC) -> hingga `09` (non-EVM live) atau `08` (HEAD-only / EVM tanpa RPC);
   - **`C`** (bukti struktural atau mock pihak ketiga) -> maksimal `07` (dengan `PERCOBAAN:`) atau `06` (salah baca statis);
   - **`D`** (asumsi/hitungan kertas tanpa eksekusi test) -> **TIDAK SAH** (memicu `PAPER_REFUTATION_DETECTED` bila dipakai menggugurkan PoC/EV/Dust di `06`).
2. **Langkah 0 — Rekonsiliasi Deployment (Eksklusif di Fase 4):** ambil source/bytecode terverifikasi explorer atau cek selector via `cast code`, baca slot EIP-1967 untuk proxy, dan bandingkan dengan repo. Kode yang terbukti rentan lewat PoC namun masih HEAD-only ditempatkan di `08-valid-not-eligible.md` (`PRE_LIVE_SCOPE / HEAD_ONLY_PROVEN`), **bukan** di `07`.
3. **Kegagalan query bukan bukti ketiadaan.** `status: 0` dari explorer, `revert 0x` pada `eth_call`, timeout RPC, atau `eth_getLogs` terbatas rentang wajib diulang lewat sumber lain / inspeksi bytecode `cast code` sebelum menyimpulkan.
4. **Perilaku off-chain diuji black-box lebih dulu** (rekonstruksi event on-chain) sebelum menyatakan "butuh repo privat".
5. **Simulasi Jembatan Lintas-Rantai (Bridge/Precompile) vs Mock Pihak Ketiga:** Mock pihak ketiga yang **mengarang** payload mustahil hanya menopang bukti struktural (`C`). Namun, **merelay payload yang terbukti dapat dibentuk secara *permissionless* dari kontrak pengirim (Chain A)** melalui `vm.prank(officialEndpoint)` ke kontrak penerima (Chain B) di atas Local Fork adalah **bukti mekanis sah yang berhak masuk `09`**.
