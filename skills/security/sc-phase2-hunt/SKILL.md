---
name: sc-phase2-hunt
description: Phase 2 — Counter-Auditor Adversarial Hunting (First-Principles Foundation + Generalized Attacker POV) with Strict Static-vs-Dynamic Guard Separation (04 Static Only vs 05 Dynamic/Raw Leads).
version: 6.4.0
---

# Phase 2: Counter-Auditor Two-Stage Adversarial Hunting

Tujuan Fase 2 adalah menemukan kerentanan yang luput dari mata auditor standar. Jangan membaca kode secara pasif dari baris atas ke bawah seperti auditor biasa; gunakan Fondasi First-Principles dan metode dari `references/ref-method-registry.md` (`M-001..M-NNN`) di bawah ini tanpa melakukan penghakiman kelayakan ekonomi secara prematur.

---

## Protokol Anti-Truncate: Penulisan File Audit Wajib Atomik

**Hukum:** `open(path, "w")` dan `>` pada shell **DILARANG** untuk seluruh `audit/*.md` (termasuk `00`, `00b`, `01`, `02`, `03`, `STATE.md`). Keduanya memotong file ke **0 byte saat dibuka**, sebelum satu byte pun ditulis. Bila penulisan lalu gagal, isi asli hilang permanen — backup yang dibuat sesudahnya ikut menyimpan kekosongan.

**Sumber otoritatif:** `workspace/AGENTS.md` **Pasal 1.3** (Protokol Anti-Truncate & Metode Write). Ringkasan di bawah adalah salinan kerja; bila berbeda, **AGENTS.md yang menang**.

**Wajib:** tulis ke file `.tmp` → `fsync` → `os.replace()` (atomik). Backup **sebelum** mutasi, bukan sesudah. Verifikasi pasca-tulis (ukuran ≠ 0, heading domain masih ada).

**Satu penulis aktif pada satu waktu (`max_concurrent_children: 1`):** Subagent **DILARANG** menggunakan `write_file` penuh, `open("w")`, atau shell `>` pada `audit/03`–`09`. Subagent **WAJIB** memakai native `append` (entri baru) atau `patch` (ubah status baris di `03`/`04`/`05`/`07`) — **kecuali** entri hasil unit hantaran Fase 2, yang tetap **WAJIB** lewat staging `audit/notes/staging-<unit>.md` lalu di-merge Parent. `audit/STATE.md` **HANYA** boleh ditulis/di-`patch` oleh Parent.

**Batas yang mengikat (jangan dibaca sebagai izin umum):** izin `append`/`patch` langsung bagi Subagent hanya berlaku untuk entri yang **bukan** hasil pendadahan unit `S-n` — mis. temuan susulan, koreksi bukti, atau entri hasil verifikasi Fase 3 yang sudah final. Untuk unit `S-n`, staging tetap wajib karena Parent perlu memverifikasi jumlah entri terhadap manifes sebelum entri masuk file audit.

**Mengapa staging, bukan ringkasan 12 baris.** Satu entri `04`/`05` berukuran 15–20 baris. Unit normal menghasilkan 3 lead + 5 guard ≈ 120–160 baris. Ringkasan `≤12 baris` **secara matematis tidak dapat** membawa muatan itu — memaksanya berarti Parent menulis entri yang tidak pernah dibaca utuh oleh siapa pun, atau Subagent memangkas temuan agar muat. Keduanya kegagalan audit.

**Pembagian peran yang benar:**

| Peran | Menulis | Bentuk |
|---|---|---|
| Subagent | `audit/notes/staging-<unit>.md` **saja** | Entri lengkap siap-tempel (format final `04`/`05`), memakai `write_file` atau `atomic_write` |
| Subagent → Parent | Ringkasan `≤12 baris` | **Hanya** manifes: `STAGING: <path> \| 04: <n> \| 05: <n>` + 1 baris verdict per entri |
| Parent | `audit/04`–`09` | Salin dari staging memakai metode di `references/ref-atomic-write.md` (append/patch), verifikasi `grep -c '^## \['`, lalu hapus staging |

**Larangan tetap berlaku pada Parent:** dilarang `open(path,"w")` / `>` untuk `04`–`09`. Gunakan `append`/`patch` sesuai tabel karakteristik file.

### Metode Write per Karakteristik File (hemat token)

DILARANG memakai "append selalu" sebagai resep tunggal — tiap file punya pola mutasi berbeda, dan append pada file yang **diubah berulang** justru gagal (status tidak ter-update) atau memaksa baca penuh.

| Karakteristik | File | Metode wajib | DILARANG |
|---|---|---|---|
| Tulis sekali | `INTEL.md`, `00`, `01`, `02` | `write_file` saat awal; tambahan kecil → `append` | tulis ulang penuh untuk tambahan |
| **Generate massal** | `00b` | **script** (`phase0_inventory.py` dll); verifikasi via `grep -n` | menulis manual; membaca penuh (≈9k token) |
| **Append-murni** | `06`, `08`, `09` | `append` (`mode="a"`) | baca-lalu-tulis-ulang |
| **Append lalu ubah status** | `04`, `05`, `07` | entri baru → `append`; ubah status → `patch` pada blok itu | append untuk mengubah; tulis ulang penuh |
| **Edit tabel/baris** | `03`, `STATE` | `patch` baris (`grep -n` dulu bila perlu) | baca penuh lalu tulis ulang |

**Patokan biaya:** entri baru ≈ 300 token tulis. Baca penuh `03`/`04`/`05` ≈ 4–5 ribu token, dan naik terus seiring file membesar. Ubah 1 baris tabel = ~40 token vs 5.364 token bila baca penuh (**rasio ≈134×**).

> ⚠️ **BATAS OBJEK — WAJIB DIBACA SEBELUM MENERAPKAN LARANGAN DI ATAS.** Seluruh larangan "baca penuh" / "membaca penuh" pada tabel metode write ini berlaku **eksklusif untuk FILE AUDIT** (`00b`, `03`, `04`, `05`, `06`, `07`, `08`, `09`, `STATE.md`). **KODE SUMBER KONTRAK TIDAK TERMASUK.** Membaca kode kontrak secara hemat (potongan, `sed`, `grep`, `head`, `tail`) **DILARANG** sebagai dasar menyimpulkan isi fungsi — lihat **§A0 Pembacaan Wajib Penuh** di bawah. Dua aturan ini hemat-token untuk file audit, dan **anti-hemat** untuk kode kontrak; keduanya sengaja berlawanan arah pada objek yang berbeda.

**Aturan pemilihan:** pilih metode dengan **token terendah yang tetap tidak merusak data**. Append hanya sah bila entri memang tidak akan diubah; bila status entri harus diperbarui kemudian, gunakan `patch`.

Pola kode lengkap, protokol backup write-ahead, dan prosedur pemulihan (termasuk kewajiban menandai **REKONSTRUKSI** bila isi asli hilang): `references/ref-atomic-write.md`.

---

## Aturan Orkestrasi Subagent (delegate_task)

Jika dijalankan melalui delegasi, berikan paket tugas berisi:
1. **Tepat 1 Unit `S-n`** dari `audit/03-attack-surface-queue.md` (lihat *Fixed Quota* di bawah), beserta tag `[LOAD: ...]`.
2. Instruksi wajib membaca `audit/00-project-map.md`, `audit/01-threat-and-env.md` (3 Kasta Aset & Jejak *Patch-Scar*), `audit/02-state-and-var-matrix.md`, dan `audit/INTEL.md` bila ada.
3. Pembagian Putaran Eksplorasi:
   - Putaran 1 (Mikro Unit Antrean): Jalankan Fondasi Batas & 5 Primitif + metode sesuai kelas topologi unit (lihat `references/ref-method-registry.md`) -> Tahap B (Symptom Router & Lazy-Load POV) -> Tahap C (klasifikasi `04` vs `05`).
   - **Tahap C — Keluaran:** tulis entri lengkap ke `audit/notes/staging-<unit>.md` (**bukan** ke `04`/`05` langsung). Format entri wajib sudah final agar Parent hanya menyalin: untuk `04` sertakan File:Baris, Ekspresi Guard, Variabel Pembentuk; untuk `05` sertakan Metode Pencarian (`M-001..M-NNN` dan/atau `[POV-XX]`) dan Delta State. Ringkasan ke Parent cukup manifes: `STAGING: <path> | 04: <n> | 05: <n>` + 1 baris per entri.
   - **Putaran 2 (Sintesis Makro Lintas-Unit & Pembongkaran `04`):** Setelah seluruh metode `M-001..M-010` dijalankan **penuh di tingkat unit** pada Putaran 1, rangkai sintesis lintas-unit (`M-004`, `M-005`, `M-008`, `M-009`, `M-010`) menggunakan `02-state-and-var-matrix.md`, `05-raw-leads.md`, dan **bongkar setiap guard di `04-code-guarded.md` terhadap 5 Jalur Permissionless.**

### Pengunci Anti-Low-Rate Reasoning (WAJIB)

**A. Interleaved Domain Wave.** Dalam setiap rotasi domain (`D1 -> D2 -> ... -> Dn`), unit `[CLASS-A]`, `[CLASS-B]`, dan `[CLASS-C]` dibedah **proporsional sesuai aliran nilai** di domain tersebut. **DILARANG** menaruh seluruh `[CLASS-A]` di buntut sesi — kontrak tunggal `[CLASS-A]` dapat memegang **100% TVL**, sehingga menundanya = menunda aset terbesar.

**B. Position-Blind Subagent Dispatch & Fixed Quota (`1 Subagent = Tepat 1 Unit S-n`).**
- Setiap `delegate_task` di Fase 2 hanya mengerjakan **tepat 1 Unit Alur `S-n`**, dari unit pertama hingga unit terakhir. **DILARANG** merapel beberapa unit di ekor antrean (*No Tail-End Compression*).
- Prompt Subagent harus **Position-Blind**: DILARANG melabeli unit sebagai "prioritas rendah", "urutan bawah", atau "EV kecil". Subagent hanya menerima identitas unit, bukan posisinya dalam antrean.

**C. Eksekusi Berbasis Kelas Entitas (`[CLASS-A]` vs `[CLASS-B]` vs `[CLASS-C]`).**
- **`[CLASS-A]` (Single-Entity):** jalankan **1 Pass Tajam Tuntas (*Single-Pass Deep Kill*)** — seluruh variabel pembentuk guard berada di dalam 1 entitas, jadi Subagent **wajib langsung menguji Guard-Inversion (`M-005`) inline saat itu juga**, termasuk pola self-call `msg.sender == address(this)` / *internal batch routing* (`M-008`). Hanya lempar ke `04-code-guarded.md` bila guard terbukti tahan **di dalam** entitas namun berpotensi dipengaruhi faktor eksternal pada sintesis lintas-kelas.
- **`[CLASS-B]` (Dual-Entity) & `[CLASS-C]` (Multi-Entity Long Flow):** jalankan paket metode sesuai matriks kelas di `references/ref-method-registry.md`, lalu lanjutkan dengan **Putaran Sintesis Lintas-Jalur & Pembongkaran `04-code-guarded.md`** sebelum menutup Fase 2.


## Aturan Anti-Tunnel-Vision: Rotasi Domain & Clean-Unit Attestation

Kuota "minimal N lead per domain" **DILARANG** dipakai: memaksa jumlah lead mendorong agen mengarang hipotesis lemah hanya untuk memenuhi angka (hukum Goodhart). Yang dipaksa adalah **Penyapuan Merata (Breadth-First Sweep)** plus **bukti bahwa unit benar-benar diperiksa**.

### 1. Rotasi Domain Wajib
Pada Putaran 1 dan Putaran 2, eksekusi Unit Alur Eksekusi secara **bergilir lintas domain** (`D1 -> D2 -> D3 -> … -> D1`), **BUKAN** menghabiskan satu folder lalu berhenti. Satu putaran penuh = setiap domain ber-`[MUST-AUDIT]` mendapat giliran sebelum domain mana pun mendapat giliran kedua. Pelanggaran rotasi = putaran dibatalkan dan diulang.

### 2. Kewajiban Jejak Audit (Lead ATAU Negative Attestation)
Setiap berkas `[MUST-AUDIT]` dan setiap Unit Alur `S-n` **tidak boleh dilewati tanpa jejak**. Pilih tepat satu hasil:
- **`LEAD_GENERATED`** — ditemukan celah potensial: tulis entri lengkap ke `audit/notes/staging-<unit>.md` (template penuh).
- **`ATTESTED_CLEAN`** — setelah diuji dengan metode dari `ref-method-registry.md` (`M-001..M-NNN`) dan/atau `[POV-XX]` tidak ditemukan celah: tulis **1 baris Negative Attestation** di tabel cakupan `audit/03-attack-surface-queue.md`.

**Format Negative Attestation (wajib 4 unsur — tanpa keempatnya, atestasi ditolak):**
```
<Berkas>: <jumlah> fungsi mutasi dicek dengan Metode <X, Y, Z> —
  mengapa invariant bertahan: <alasan teknis konkret>
  jalur eksternal yang diuji: <daftar jalur/callback/CPI yang benar-benar disentuh>
  jalur yang TIDAK diuji: <daftar, atau "tidak ada">
```

**Larangan atestasi kosong.** Kalimat berikut **DILARANG** dan otomatis ditolak: *"sudah diperiksa, aman"*, *"kode standar"*, *"tidak ada masalah ditemukan"*, *"mengikuti OpenZeppelin/Anchor"*. Atestasi wajib menyebut **nama fungsi yang diperiksa**, **nomor Metode**, dan **mekanisme konkret** yang membuat invariant bertahan.

**Atestasi tidak boleh lebih murah daripada lead.** Bila alasan yang bisa ditulis hanyalah "tidak ada yang mencurigakan", itu tanda unit **BELUM** benar-benar diperiksa — kembalikan ke `BELUM` dan jalankan Metode yang belum dipakai.

### 2b. Gate Atestasi Bersitasi (anti-atestasi-hampa) — WAJIB SEBELUM Gate Keluar

**Insiden yang melahirkan gate ini:** pada audit nyata, 9 unit ditandai `ATTESTED_CLEAN` dengan kalimat berbasis *volume* ("SBF build EXIT=0, 34 berkas", "U18 4/4 PASS"). Coverage Gate **lulus 100%**, padahal `HyperliquidDepositHandler` (190 LOC, 10 fungsi mutasi, live di HyperEVM `0xbFB53E9C…27D5`) dan `DonationBox` (live `0xbb0B…d851`, layout **OZ-Ownable**, bukan `AccessControl`) belum pernah dibedah. Cacat itu baru tertangkap di putaran manual berikutnya, bukan oleh workflow.

**Akar masalah:** aturan "atestasi 4 unsur" ada, tetapi **penegakannya** memakai metrik volume. Compile sukses / jumlah berkas / jumlah test PASS **bukan** bukti bahwa fungsi diperiksa.

**Hukum baru — Atestasi DITOLAK bila tidak memuat keempatnya:**
1. **Nama fungsi yang diperiksa** — daftar eksplisit `namaFungsi()` untuk **setiap** berkas `[MUST-AUDIT]` di unit itu (bukan "10 state-fn").
2. **`File:Baris`** untuk minimal satu baris kode konkret per fungsi (mis. `handlers/HyperliquidDepositHandler.sol:299-302`).
3. **Metode** (M-001..M-NNN / `[POV-XX]`) yang benar-benar dipakai.
4. **Jalur eksternal yang disentuh** + **jalur yang TIDAK diuji** (eksplisit, boleh "tidak ada").

**DILARANG sebagai bukti tunggal** (otomatis tolak): `forge build`/`cargo test` PASS, jumlah berkas, jumlah fungsi mutasi, "unit X/ X PASS", nama unit (`S-0n`), atau rujukan ke `notes/s03/` tanpa kutipan `File:Baris`.

**Uji dry-run wajib:** sebelum menulis `ATTESTED_CLEAN` untuk sebuah unit, jalankan `skenario-kontra`: sebutkan **satu** hipotesis serangan konkret untuk berkas dengan LOC/fungsi-mutasi terbesar di unit itu, lalu jelaskan dalam 1 kalimat mengapa hipotesis itu gugur. Bila penjelasannya butuh membaca ulang kode → unit **BELUM** selesai; kembalikan ke `BELUM`.

**Rekonsiliasi wajib ke `00-project-map.md`:** atestasi tidak sah bila menyebut kontrak yang **tidak ada** di `00b-file-inventory.md` atau sebaliknya menyatakan kelas unit lain (mis. menyebut `ForwarderBase` untuk unit yang isinya `DonationBox`).

**Putaran Audit Ulang (opsional, wajib bila ada indikasi):** bila ditemukan unit ber-atestasi tanpa `File:Baris`, jalankan sub-putaran **P3** yang menyisir hanya unit tersebut memakai `PUSH4..EQ` dispatcher scan + `cast call` state live + baca kode per-fungsi. Hasil masuk `06` sebagai entri `P3-xx`, **tanpa mengubah verdict lama**.

### 3. Gate Keluar Fase 2
Agen **DILARANG** pindah ke Fase 3 sebelum **100% berkas `[MUST-AUDIT]` di SETIAP domain** berstatus `LEAD_GENERATED` **atau** `ATTESTED_CLEAN` yang lolos Gate Atestasi Bersitasi (§2b) (**0** berkas berstatus `BELUM` atau `DIBACA`).

| Metrik | Ambang |
|---|---|
| Berkas `[MUST-AUDIT]` berjejak (`LEAD_GENERATED` / `ATTESTED_CLEAN`) per domain | **= 100%** (setiap domain, tanpa kecuali) |
| Berkas `[MUST-AUDIT]` berstatus `BELUM` atau `DIBACA` gantung di domain mana pun | **0** |

**DILARANG memakai kuota "minimal N lead per domain" sebagai metrik kelulusan.** Kelulusan diukur dari **jejak per berkas**, bukan banyaknya hipotesis — agar modul yang memang aman tidak dipaksa melahirkan lead palsu; *Negative Attestation* yang jujur justru bukti cakupan yang sah.

Gagal satu sel tabel = Fase 2 **DITOLAK**, kembali ke rotasi domain.

**Pencatat status:** hasil atestasi ditulis ke `audit/03-attack-surface-queue.md` sebagai tabel cakupan per domain, direkonsiliasi dengan `audit/00b-file-inventory.md`. Status sah: `BELUM` / `DIBACA` / `LEAD_GENERATED` / `ATTESTED_CLEAN`.

---

## TAHAP A: Fondasi First-Principles & Resolusi Metode Dinamis (WAJIB Sebelum Membaca Referensi!)

### A0. PEMBACAAN WAJIB PENUH — Gerbang Sebelum Menulis Lead (WAJIB, SEBELUM TAHAP A)

**Hukum: klaim negatif DILARANG dibangun dari cara membaca yang cacat.**

Insiden nyata: `_fallback` dibaca dengan `sed -n '/function _fallback/,/^    }$/p' | tail -25`. `postCheck` berada di tengah fungsi dan **terpotong dari jendela baca**. Kesimpulan "tidak pernah memanggil postCheck" ditulis ke `05` dengan label *"asimetri terverifikasi, bukan dugaan"*. Fase 3 membuktikan sebaliknya — `postCheck` dipanggil dan me-revert `PolicyBlocked()`. Satu lead palsu lolos sebagai "lead kuat", menghabiskan satu siklus PoC penuh, dan nyaris masuk laporan.

**Kewajiban sebelum menulis entri apa pun ke `staging-<unit>.md`:**

1. **Baca fungsi UTUH** — dari baris `function` sampai kurung kurawal penutup yang menyeimbangkan. Bukan potongan, bukan "sekitar tempat yang menarik".
2. **`grep`/`sed` hanya untuk MENEMUKAN lokasi, bukan menyimpulkan isi.** DILARANG memakai `grep`, `sed`, `head`, `tail`, atau `grep -A/-B` sebagai dasar klaim negatif.
3. **Fungsi > 60 baris wajib** dibaca bertahap dengan `read_file` ber-`offset`/`limit` sampai tuntas, bukan dicicil dengan alat pencari.
4. **Setiap klaim negatif wajib menyertakan** `File:awal-akhir` + jumlah baris yang dibaca, dan bukti bahwa rentang itu mencakup **seluruh** fungsi.
5. **Label "terverifikasi" hanya sah** bila disertai kutipan kode; untuk klaim perilaku ("dipanggil", "tidak dipanggil", "revert sebelum X") wajib disertai **trace eksekusi**. Tanpa keduanya, label yang sah hanyalah **"indikasi"**.

**Klaim negatif meliputi:** "tidak ada guard", "X tidak dipanggil", "tidak ada cek", "tidak ada validasi", "selalu revert", dan segala bentuk "aman karena tidak ada ...".

**Kapan ini menggigit:** fungsi dengan pola `try/catch`, `_fallback`, router multi-cabang, loop kustom, atau pemanggilan eksternal di tengah — di situlah `sed|tail` paling sering memotong bagian penting.

---

### Fondasi Wajib: 4 Kondisi Batas Konkret & 5 Primitif Universal
Saat membedah setiap fungsi di unit antrean, selalu substitusikan 4 Kondisi Batas (1. Likuiditas realistis tanpa ilusi `totalSupply == 0` pada pool live; 2. Batas bawah 0, 1 wei, `min - 1`; 3. Blok/waktu sama $\Delta t = 0$; 4. Entitas kembar `sender == recipient` / `target == address(this)`) terhadap 5 Primitif Universal: (1) Kuantisasi Proporsi, (2) Transisi Paksa & Sabotase DoS, (3) Replay Otoritas/Signature, (4) Penyerahan Kontrol Eksekusi, dan (5) Lompatan Mesin Status.

---


### Resolusi Metode Dinamis via Single-Source Method Registry (`references/ref-method-registry.md`)

Seluruh definisi metode (`M-001` s/d `M-010`, plus slot ekspansi `M-011`..`M-NNN`) **tidak lagi ditulis di berkas ini**. Berkas ini hanya menyimpan prosedur pemanggilannya.

1. **Muat registry** — panggil `skill_view("sc-phase2-hunt", "references/ref-method-registry.md")` (atau `read_file`).
2. **Baca kelas topologi unit** yang sedang dibedah (`[CLASS-A]`, `[CLASS-B]`, atau `[CLASS-C]`) dari `audit/03-attack-surface-queue.md` (field `Topologi Entitas`).
3. **Jalankan seluruh metode yang dipetakan** untuk kelas tersebut pada Bagian 1 & Bagian 3 registry:
   - `[CLASS-A]` (Single-Entity): fokus utama `M-001` (*Backward Sink*), `M-002` (*State Delta*), `M-003` (*2-Identity Sybil di dalam 1 kontrak: self-transfer / self-liquidation*), `M-004` (*Patch-Scar & View-vs-Write*), `M-005` (*Inline Guard-Inversion*), `M-006` (*Prinsip B: Duplicate Reference `[A,A]`*), `M-007` (*Split-vs-Bulk*), `M-008` (*seam self-call `msg.sender == address(this)` & internal batch routing*), `M-009` (*Local Suspended State*), dan `M-010` (*Post-Upgrade Slot Drift & Residual Balance/Allowance lokal*) — plus `M-011..M-NNN` yang bertarget `[CLASS-A]`.
   - **`[CLASS-B]` (Dual-Entity):** seluruh metode relevan `[CLASS-A]` ditambah `M-003` (*Multi-Identity Sybil & Zero-Time Loop*), `M-006` (*Prinsip A: Stale Snapshot Write-Back* + Prinsip B), `M-008` (*Caller-Callee Seam & Direct Bypass*), `M-010` (*Residual Balance/Authority*) — plus `M-011..M-NNN` bertarget `[CLASS-B]`.
   - **`[CLASS-C]` (Multi-Entity Long Flow):** **Paket Penuh 100% metode** (`M-001`..`M-NNN`) dengan penekanan pada rantai komposisi panjang, `M-003`, `M-004`, `M-005` (*Cross-Contract*), `M-008`, `M-009` (*Suspended Multi-Step/Async Lifecycle*), dan `M-010` (*Post-Upgrade & Config Drift*).

> **Larangan angka mati:** DILARANG menyebut "Metode 1 s/d 10" sebagai himpunan tertutup. Metode yang sah = apa pun yang terdaftar di registry pada sesi itu. Menambah `M-011` cukup dengan menyunting registry, **tidak** berkas ini.

---

## TAHAP B: Pengayaan Analogi Mekanis & Katalog Attacker POV ([POV-XX])

Tahap B **modular dan lazy-load**. Jangan memuat seluruh katalog sekaligus.

1. **Muat Checklist Prinsip Dasar & Rantai (Tipis < 60 Baris).**
   Panggil `skill_view` pada checklist domain (`ref-math-and-vaults.md`, `ref-calls-tokens-reentrancy.md`, `ref-defi-oracles-liquidation.md`) dan **tepat 1** cartridge rantai (`ref-chain-*.md`) sesuai tag `[LOAD: ...]` pada unit `S-n`. Terjemahkan setiap butir sebagai **pola mekanis abstrak** lintas domain.
2. **Cek Gejala di Symptom Router (`references/ref-attacker-pov.md`).**
   Buka `references/ref-attacker-pov.md` dan periksa kolom **Gejala Pemicu di Kode (Trigger Symptom)** pada **Tabel Router Bagian 2**.
3. **Lazy-Load Katalog POV yang Cocok (`references/ref-pov-*.md`).**
   **HANYA JIKA** fungsi/unit yang sedang dibedah menunjukkan gejala pemicu tersebut, buka berkas `ref-pov-math.md`, `ref-pov-call.md`, `ref-pov-defi.md`, atau `ref-pov-chain.md` yang relevan, lalu cocokkan **Kondisi Prasyarat**, **Kacamata Attacker**, dan **Auditor Blindspot**-nya.

- **Fallback wajib:** bila tidak ada `[POV-XX]` yang cocok di katalog, **JANGAN mengarang nomor POV**. Gunakan metode dari `ref-method-registry.md` dan catat di `audit/notes/` bahwa katalog untuk pola tersebut belum tersedia.

---


## TAHAP C: Pemisahan Murni & Gerbang Guard Statis vs Dinamis (04-code-guarded.md vs 05-raw-leads.md)

Di Fase 2, Anda adalah **Pemburu (Hunter)**, bukan Hakim Ekonomi dan bukan Hakim Cakupan Bounty.
- **DILARANG** membuang anomali hanya karena terlihat kecil sendirian (karena akan dirangkai menjadi *attack chain* di Putaran 2 atau diuji amplifikasi 3-Jalurnya di simulator Fase 3).
- **DILARANG** melewati atau menurunkan prioritas berkas hanya karena berlabel `[REPO_STAGED]` / HEAD-only.

### 1. Dua Larangan Fakta Dasar Kode (Satu-satunya Filter di Fase 2 — Jangan Diperluas!)
Jangan mengarang sifat palsu pada Token Kasta 1 (LP/Share token internal = ERC-20 standar, bukan *Fee-on-Transfer*/USDT) dan jangan mengasumsikan penyerang tak berizin bisa memanggil fungsi `onlyOwner` secara langsung tanpa celah kontrol akses.
- **PERINGATAN ANTI-OVERFILTERING:** Larangan ini **TIDAK BERLAKU** untuk: **(a) Cross-Whitelist Confusion** (memasukkan kontrak/token/pool yang sah ada di whitelist tetapi untuk pasangan aset/konteks yang salah karena ketiadaan cek ikatan ID/aset), **(b) Callback Initiator Spoofing** (memicu Pool/Vault/Endpoint resmi secara *permissionless* agar memanggil fungsi callback kontrak target ketika parameter `initiator`/`sender` tidak divalidasi), dan **(c) Oracle Scaling/Staleness Flaw** (harga oracle 100% jujur, tetapi kontrak salah menghitung desimal/batas waktu). Ketiganya adalah kerentanan *permissionless* murni dan **WAJIB masuk `05-raw-leads.md`!**

### 2. GERBANG PEMISAHAN GUARD STATIS VS DINAMIS (WAJIB DIPATUHI!)

Kesalahan terbesar auditor adalah menganggap adanya `require(...)` atau `if (...) revert` sebagai bukti bahwa suatu fungsi sudah aman, lalu memarkirnya di `04-code-guarded.md` **tanpa pernah diuji secara mekanis**. Mulai v6.2.0, pisahkan dengan aturan keras berikut:

| Jenis Guard di Kode | Kriteria Eksplisit | Wadah Tujuan Wajib | Alasan |
|---|---|---|---|
| **A. Guard Statis / Struktural** | Pemeriksaan otorisasi tetap (`onlyOwner`, `onlyRole`, `msg.sender == router`), mutex reentrancy (`nonReentrant`), status pause boolean (`whenNotPaused`), atau cek alamat nol (`addr != address(0)`). | **`04-code-guarded.md`** (via `staging-<unit>.md`) — **HANYA bila `TERSANGKAL`**, yaitu variabel guard diubah admin sah **DAN** lolos kelima pemeriksaan **Jalur 1–5** di `verify/templates/04-code-guarded.md`. Bila salah satu dari 5 Jalur terpenuhi → **`TEMBUS`** dan wajib masuk `05-raw-leads.md`! | **DILARANG menandai `TERSANGKAL` hanya karena variabel `immutable` atau `onlyOwner`.** Wajib uji **5 Jalur Permissionless**: (1) Mutasi variabel guard (`M-005`), (2) Pemicuan lewat kontrak/modul hulu (`M-008`), (3) *Unprivileged State Poisoning* pada eksekusi rutin Keeper/Relayer/Solver (`M-005`/`M-009`), (4) Eskalasi lintas-kontrak pada `nonReentrant` / pause asimetris pada `whenNotPaused` (`[POV-CALL-01]`), dan (5) *Cross-Whitelist Confusion* / *Unchecked Callback Initiator* (`M-008`). |
| **B. Guard Dinamis / Matematis / State-Dependent** | Pemeriksaan yang melibatkan aritmetika, pembulatan (`mulDiv`, bagi-kali), rasio pool (`totalAssets`, `totalSupply`), saldo token (`balanceOf`), akumulator waktu/bunga (`block.timestamp`, `index`), batas kesehatan/LTV/likuidasi, slippage/fee dinamis, atau indeks/panjang array. | **`05-raw-leads.md`** (via `staging-<unit>.md`, beri tag `M-005` / `M-007`) | **DILARANG masuk `04`!** Guard dinamis sering kali tampak aman di atas kertas tetapi bocor pada kondisi batas, *rounding direction*, *dust splitting*, atau *flashloan skew* — wajib diuji dengan Fuzzer (`testFuzz_`/`proptest`/`halmos`) di Fase 3! |

> **ATURAN EMAS UNTUK PERMISSION & GUARD STATIS YANG TIDAK BISA DIMANIPULASI (JANGAN JADIKAN GATE MATI DI `04`!):**
> Ketika sebuah fungsi dijaga oleh permission yang variabel alamat/perannya **tidak bisa diubah** oleh penyerang (`immutable`, konstanta, atau hanya bisa disetel `onlyOwner`), **DILARANG langsung menganggap fungsi itu aman/mati!** Sebelum dan saat membongkar `04-code-guarded.md`, Anda **WAJIB menguji rute *Permissionless*** yang tidak membutuhkan perubahan variabel permission:
> 1. **Rute Pemicuan Hulu (*Upstream Trigger* — `M-008`):** Jika permission mengizinkan kontrak/modul lain (mis. Router, PoolManager, Hub, Messenger), lacak apakah pengguna tak berizin (*unprivileged*) dapat memanggil kontrak hulu tersebut agar kontrak hulu mengeksekusi fungsi ini dengan parameter/state yang menguntungkan penyerang!
> 2. **Rute Peracunan State (*Unprivileged State Poisoning* — `M-002`/`M-005`):** Jika permission mengizinkan eksekutor operasional rutin (Keeper, Relayer, Bot, EpochSettler), periksa **seluruh** variabel state/saldo/antrean yang dibaca di dalam fungsi berizin tersebut! Apakah pengguna tak berizin dapat memanipulasi variabel state tersebut lewat fungsi publik biasa, sehingga saat eksekutor rutin menjalankan tugas normalnya, perhitungan di dalam fungsi berizin ini rusak atau selalu revert (DoS membekukan dana)? Jika ya, **masukkan langsung ke `05-raw-leads.md`!**
> 3. **Rute Lintas-Kontrak `nonReentrant` & Asimetri `whenNotPaused` (`[POV-CALL-01]` / `M-009`):** `nonReentrant` lokal **tidak menghentikan** pembacaan state timpang oleh kontrak pasangan/`view function` saat panggilan keluar terjadi; `whenNotPaused` yang memblokir `repay`/`addCollateral`/`cancel` tetapi membiarkan `liquidate`/penalti tetap berjalan adalah **celah penyitaan paksa yang valid!**
> 4. **Rute *Cross-Whitelist Confusion* & *Callback Initiator* (`M-008`):** Guard `isWhitelisted[x]` yang **tidak memeriksa kecocokan pasangan aset** (`pool.token() == asset`), atau callback (`onFlashLoan`, `swapCallback`, `onERC721Received`, `lzReceive`) yang **hanya memeriksa `msg.sender` tanpa memeriksa `initiator`/`srcSender`**, adalah **100% `TEMBUS`** dan wajib masuk `05-raw-leads.md`!

### 3. Prosedur Penulisan ke `audit/notes/staging-<unit>.md`

1. **Jika Ditemukan Anomali Tanpa Guard, Guard Bisa Ditembus (`M-005`), ATAU Dijaga oleh Guard Dinamis/Matematis (Kategori B di atas):**
   Tulis entri lengkap ke `audit/notes/staging-<unit>.md` dengan target **`05-raw-leads.md`** sesuai template `verify/templates/05-raw-leads.md`, lengkap dengan:
   - **Kelas Topologi** (`[CLASS-A]` | `[CLASS-B]` | `[CLASS-C]`),
   - **Metode Pencarian** (`M-001..M-NNN` dari `ref-method-registry.md` dan/atau `[POV-XX]`),
   - **File:Kontrak:Fungsi (Baris)** (presisi sampai baris),
   - **Delta State** (Expected vs Actual) — **serta ekspresi Guard Dinamis yang ingin ditembus lewat fuzzer/amplifikasi**,
   - **Urutan Eksploitasi** (chain-neutral), dan
   - **Potensi Rantai Serangan (Chaining)**.
   **DILARANG** menulis ke `05-raw-leads.md` langsung — `05` hanya ditulis Parent saat merge.
2. **Jika Hipotesis Benar-Benar Dihentikan oleh Guard Statis / Struktural Murni (Kategori A di atas):**
   Tulis entri lengkap ke `audit/notes/staging-<unit>.md` dengan target **`04-code-guarded.md`** sesuai template `verify/templates/04-code-guarded.md`, lengkap dengan: File:Baris, Ekspresi Guard, Variabel Pembentuk, Penulis Variabel (rujuk `02-state-and-var-matrix.md`), Hipotesis yang Dihentikan, dan **Status Putaran 2: `BELUM`**. **DILARANG** menulis ke `04-code-guarded.md` langsung.
3. Tandai kelompok fungsi di `audit/03-attack-surface-queue.md` menjadi `[HUNTED]`.
4. **Wajib tulis status jejak** pada tabel cakupan: `LEAD_GENERATED` atau `ATTESTED_CLEAN` (dengan 4 unsur atestasi lengkap + kutipan `File:Baris` konkret sesuai §2b). Kelompok tanpa keduanya tetap `BELUM` dan memblokir Gate Keluar Fase 2.
