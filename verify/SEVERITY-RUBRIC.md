# SEVERITY RUBRIC — Standar Penilaian Severity Lintas Platform

> **Berlaku untuk seluruh audit, semua project.**
> Lokasi: `verify/SEVERITY-RUBRIC.md` — **satu folder dengan `VERDICT.md`**, dirujuk oleh
> `VERDICT.md` Langkah 0.3b. Hakim Fase 4 memuat berkas ini, bukan menebak.
> Terakhir diverifikasi: 2026-11-05 dari dokumentasi resmi masing-masing platform.

---

## 0. PRINSIP DASAR (tidak bisa dinegosiasikan)

1. **Severity = dua sumbu: Impact x Likelihood.** Dilarang menilai dari satu sumbu saja.
2. **Severity DITENTUKAN oleh impact, bukan oleh siklus deployment.** Temuan Critical yang hanya
   terbukti di HEAD tetap **Critical**; yang berubah hanya wadah (`09` vs `08`).
3. **Setiap label severity WAJIB menyebut platform/rujukan yang dipakai.** Tanpa rujukan = tidak sah.
4. **DILARANG menaikkan severity tanpa rujukan tertulis.** Saat ragu, turunkan dan deklarasikan asumsi.
5. **Setiap temuan wajib punya `BUKTI_SIMULASI`** sebelum diberi label apa pun.
6. **Wadah ditentukan DUA hal terpisah:** eligibility (live/head-only/admin) dan severity.
7. **Default bila platform tidak mendeklarasikan: LOW** (Bagian 4). Low adalah irisan teraman lintas
   semua platform; menurunkan tidak pernah membuat laporan salah, menaikkan tanpa rujukan membuat
   laporan ditolak. Low tetap dibayar di hampir semua program.

---

## 1. ALUR PENENTUAN (wajib dijalankan berurutan)

```
STEP 1 — Cari rujukan eksplisit platform
  a. Halaman bounty/scope  -> cari: "severity", "OWASP", "CVSS", "Impact", "Likelihood", "Immunefi"
  b. README repo           -> cari: "Severity", "Known Issues", "Out of Scope"
  c. Laporan audit repo    -> kerangka yang dipakai auditor sebelumnya
  d. Program induk (UMA, dsb.) bila platform menyebut "T&C berlaku dari X"

STEP 2 — Jika DITEMUKAN
  -> pakai kriteria platform tersebut, KUTIP URL-nya di laporan.
  -> selesai.

STEP 3 — Jika TIDAK DITEMUKAN setelah a-c dicoba
  -> pakai MATRIKS UNIVERSAL (Bagian 4).
  -> WAJIB tulis di laporan:
       "Platform tidak mendeklarasikan kriteria severity; dipakai Matriks Universal
        workspace (Cantina-Competition anchor), lihat SEVERITY-RUBRIC.md Bagian 4."

STEP 4 — Hitung Impact x Likelihood, isi format Bagian 5.

STEP 5 — Tentukan WADAH terpisah dari severity (Bagian 6).
```

**Dilarang** berhenti di STEP 3 tanpa mencatat asumsi. **Dilarang** memilih kriteria yang
menguntungkan diri sendiri secara diam-diam.

---

## 2. KRITERIA PER PLATFORM (sumber primer, terverifikasi)

### 2.1 OWASP Risk Rating — *dipakai Across Protocol*

- **Sumber:** `https://docs.across.to/introduction/bug-bounty`
- **Kutipan:** *"Severity is calculated according to the OWASP risk rating model based on Impact and Likelihood."*
- **Struktur:** Risk = Impact x Likelihood, masing-masing berskala Low/Medium/High.
- **Reward (Across):** Low $250 · Medium $1.000 · High $10.000 · Critical s.d. $1.000.000
- **Catatan:** OWASP asli memakai sub-faktor teknis; untuk pemetaan ke tier reward, gunakan
  Matriks Universal (Bagian 4) yang konsisten dengan pendekatan dua sumbu OWASP.

### 2.2 Immunefi v2.3 — *program yang menyebut Immunefi*

- **Sumber:** `https://immunefi.com/immunefi-vulnerability-severity-classification-system-v2-3/`
- **Tabel Smart Contracts (verbatim):**

| Level | Impact |
|---|---|
| 4 Critical | Direct theft of any user funds (at-rest/in-motion, selain unclaimed yield); permanent freezing of funds; protocol insolvency; manipulation of governance voting result |
| 3 High | Theft/freezing of unclaimed yield atau royalties; **temporary freezing of funds** |
| 2 Medium | **Griefing** (no profit motive, damage to users/protocol); **theft of gas**; **unbounded gas consumption**; block stuffing; smart contract unable to operate due to lack of token funds |
| 1 Low | **Contract fails to deliver promised returns, but doesn't lose value** |

- **Implikasi penting:** griefing, gas theft, dan unbounded gas consumption = **Medium**, BUKAN Low.
- Di bawah Low tidak ada tier; Insight hanya untuk Blockchain/DLT.

### 2.3 Sherlock — *paling ketat*

- **Sumber:** `https://docs.sherlock.xyz/audits/judging/guidelines`
- **Kutipan:** *"Sherlock is exclusively focused on high and medium-severity findings."*
- **Tidak ada tier Low.** Selain High/Medium masuk "Recommendations" (informational).
- **Threshold loss:** >1% **dan** >$10 (principal / yield / fees) untuk dianggap signifikan.
- **DoS/griefing → Medium hanya bila:** (a) dana terkunci >1 minggu, ATAU (b) fungsi time-sensitive
  terdampak. Bila keduanya → High.
- **Admin trust:** *"Admin functions are generally assumed to be used correctly."*
  Role internal dianggap trusted kecuali README menyatakan sebaliknya.
- **Design decisions** = informational, bukan temuan.

### 2.4 Cantina — BUG BOUNTY

- **Sumber:** `https://docs.cantina.security/standards/severity/bug-bounty`
- **Matriks:**

| Likelihood \ Impact | Critical | High | Medium | Low |
|---|---|---|---|---|
| **High** | Critical | High | Medium | **Low** |
| **Medium** | High | High | Medium | **Low** |
| **Low** | Medium | Medium | **Low** | Informational |

- Medium: *"Theft of gas or griefing attacks with no direct profit motive"*,
  *"unintended smart contract behavior without direct financial risk"*.
- Low: *"Non-critical contract behavior or minor functionality issues"*.
- **Out of scope:** centralization risks umum, admin errors, malicious admin, weird ERC20,
  theoretical vulnerabilities tanpa PoC, DoS tanpa demonstrated impact.

### 2.5 Cantina — COMPETITION *(anchor Matriks Universal)*

- **Sumber:** `https://docs.cantina.security/standards/severity/competition`
- **Matriks (3 kolom):**

| Likelihood \ Impact | High | Medium | Low |
|---|---|---|---|
| **High** | High | High | **Medium** |
| **Medium** | High | Medium | **Low** |
| **Low** | Medium | Low | Informational |

- **Admin:** *"Issues that require admin access (or equivalent) to perform should be at most low severity."*
- **Weird ERC20** = *at most low*. **Dust/rounding** = *at most low*.

### 2.6 Code4rena — *Low disatukan ke QA*

- **Sumber:** `https://docs.code4rena.com/competitions/severity-categorization`
- **Skala:** High / Medium / **QA**.
- High: assets dapat dicuri/hilang langsung (atau via attack path valid tanpa hipotesis).
- Medium: assets tidak berisiko langsung, tetapi fungsi/availability terdampak, atau leak value
  dengan asumsi yang dinyatakan.
- **QA** = Low risk (state handling, function incorrect as to spec, komentar) **+**
  Governance/Centralization risk (**termasuk admin privileges**).
- Loss of **dust** = QA/Low. Loss of **unmatured yield** = maksimal Medium.
- **User mistake** (careless input) = QA at best.
- **Admin:** role dianggap trustworthy; *"Mistakes in code only unblocked through admin mistakes
  should be submitted within a QA Report."*

### 2.7 Relay — *S1–S4 x L1–L3 + modifier bobot*

- **Sumber:** `https://docs.relay.link/security/bounties`
  (URL `relay.link/security/bug-bounty` memblokir bot; dokumen resminya sama)
- **Struktur berbeda dari platform lain:** Severity (S1–S4) **dan** Likelihood (L1–L3) dinilai
  terpisah, lalu payout dibaca dari matriks, lalu dikenai **modifier multiplikatif** (x0.5 – x1.5).

**Severity (S) — besaran kerusakan bila dieksploitasi:**

| Tier | Rule of thumb | Definisi |
|---|---|---|
| **S4 Critical** | *Can drain everything immediately* | Total fund theft / insolvency tanpa waktu bereaksi |
| **S3 High** | *Large or fast theft, or permanent freeze* | Pencurian besar / freeze permanen; butuh setup tapi cepat setelah dipicu |
| **S2 Medium** | *Partial or slow damage* | Drain terbatas (capped) atau drain lambat dengan jendela respons; freeze sementara |
| **S1 Low** | *Annoying but not financially dangerous* | **Griefing, minor economic damage, DoS tanpa fund loss, atau admin-only tanpa jalur eksternal** |

**Empat aturan klasifikasi Relay:**

1. **Theft outranks freeze** — mencuri > mengunci, bahkan bila nominal freeze lebih besar.
2. **Instant outranks slow** — drain lambat memberi waktu deteksi/pause; instan tidak.
3. **Jika damage capped**, severity dihitung dari **cap**, bukan TVL.
4. **Admin-only = S1 tanpa kecuali** — *"do not escalate above S1 regardless of the potential damage"*.

**Likelihood (L):**

| Tier | Rule of thumb | Kriteria |
|---|---|---|
| **L3 High** | *Anyone can do it anytime* | Tanpa prasyarat; EOA mana pun dengan calldata publik |
| **L2 Medium** | *Needs setup* | Butuh flash loan, kondisi chain tertentu, infra MEV, atau protokol lain dalam state tertentu |
| **L1 Low** | *Needs a privileged role or rare situation* | Peran istimewa (operator/solver/oracle), kondisi pasar langka, atau serangan multi-langkah |

> **Aturan tambahan:** likelihood **diturunkan satu tier** (floor L1) bila eksploit **membekukan**
> alih-alih mencuri — kecuali freeze itu langkah menuju pencurian.

**Matriks payout (base, sebelum modifier):**

| | L3 High | L2 Medium | L1 Low |
|---|---|---|---|
| **S4 Critical** | $100.000 | $50.000 | $20.000 |
| **S3 High** | $30.000 | $15.000 | $7.500 |
| **S2 Medium** | $10.000 | $5.000 | $2.000 |
| **S1 Low** | $2.000 | $1.000 | $500 |

Floor $500 · Cap $100.000 · dibulatkan ke $500 terdekat.

**Modifier (multiplikatif, dapat ditumpuk):**

| Modifier | Pemicu | Faktor |
|---|---|---|
| Permanently unrecoverable | Damage tak dapat dibalik (laundered/bridged sebelum respons, atau freeze tanpa pause/upgrade) | x1.5 |
| High remediation cost | Fix butuh redeploy penuh lintas banyak chain | x1.25 |
| Silent / undetectable | Tanpa event on-chain, bisa berjalan diam-diam berhari-hari | x1.25 |
| High attacker cost | Butuh modal berisiko besar / fee yang memotong net gain | x0.75 |
| Pausable + monitored | Dapat di-pause + monitoring respons <5 menit atas eksploit ini | x0.75 |
| Bounded damage pool | Damage dibatasi sub-pool (mis. fee buffer), bukan TVL penuh | x0.5 |

**Syarat eligibility (sangat penting):**

- Floor $500 **hanya berlaku bila ada external exploit path** — penyerang tanpa peran dapat mencapai bug.
- **TIDAK eligible** bila: (a) satu-satunya jalur butuh peran istimewa; (b) pelapor tidak
  mendemonstrasikan pihak unprivileged dapat mencapai peran itu; (c) bug tidak menyala pada operasi normal.
- Admin-only bug = **S1 tetapi tidak dibayar** (kecuali ada jalur eksternal). Boleh dilaporkan untuk bonus diskresioner.

**Out of scope Relay (verbatim ringkas):** sudah dieksploitasi pelapor; phishing/social engineering/kunci
pribadi bocor; temuan di protokol pihak ketiga (kecuali root cause di kode Relay);
**DoS tanpa fund loss dan tanpa jalur ke fund loss**; isu teoretis tanpa PoC; **Relay Vaults** (RelayPool,
RelayBridge, RelayPoolFactory, RelayBridgeFactory, RelayPoolNativeGateway + API/UI-nya).

**PoC wajib:** S4 & S3 wajib PoC yang dapat dijalankan; S2 sangat disarankan; S1 cukup deskripsi + langkah reproduksi.

> **Kontradiksi internal yang harus disadari:** DoS tanpa fund loss masuk definisi S1, tetapi juga
> dinyatakan out of scope. Kesimpulan operasional: **S1-DoS yang berdiri sendiri tidak dibayar**;
> S1 baru dibayar bila ada jalur menuju kerugian dana.

### 2.8 Self-Hosted / Tidak Ada Rujukan

- Bila halaman bounty hanya berisi alamat email + "kami berterima kasih atas laporan"
  → **tidak ada kriteria**. Gunakan **Matriks Universal (Bagian 4)**.
- Periksa tetap: T&C program induk bila disebut ("T&C dari X berlaku").
- **Selalu deklarasikan asumsi** di laporan.

---

## 3. TABEL PERBANDINGAN — di mana "griefing" diletakkan

| Kasus | OWASP | Relay | Immunefi | Cantina BB | Cantina Comp | C4 | Sherlock |
|---|---|---|---|---|---|---|---|
| Griefing tanpa profit | Low | **S1** ($1k–$2k) | **Medium** | **Medium** | Medium (jika Impact High) | Medium/QA | tidak diterima |
| Gas theft / unbounded gas | Low | S1 (DoS, out of scope bila tanpa jalur dana) | **Medium** | **Medium** | Medium | QA | tidak diterima |
| DoS sementara (<1 minggu) | Low | **S1** — tapi out of scope | **High** (jika freeze) | Medium | Medium | Medium | **tidak diterima** |
| DoS >1 minggu / time-sensitive | Low-Med | S2/S3 | High | Medium-High | High | Medium | **Medium/High** |
| Admin-only bug | Low | **S1, tidak dibayar** | Medium | **Low** (at most) | **Low** (at most) | QA | tidak diterima |
| Minor functionality | Low | **S1** | **Low** | Low | Low | QA | Recommendation |
| Dust / rounding | Low | S1 (capped) | Low | Low | Low | QA | Recommendation |

**Kesimpulan:** penyebaran terlebar ada pada **griefing/DoS** dan **admin-only**. Karena itu setiap
temuan kategori ini **WAJIB** menyebut platform; satu label tanpa rujukan tidak sah.

---

## 3b. PETA PLATFORM — project ini rujuk ke mana

| Project / Program | Rujukan | Bagian rubrik |
|---|---|---|
| **Across Protocol** | OWASP Risk Rating (dinyatakan di docs bug-bounty) | 2.1 + 4 |
| **Relay** | Relay S1–S4 x L1–L3 + modifier | 2.7 |
| Immunefi-hosted program | Immunefi v2.3 | 2.2 |
| Sherlock contest/audit | Sherlock (High/Medium saja) | 2.3 |
| Cantina bug bounty | Cantina BB matrix | 2.4 |
| Cantina competition | Cantina Comp matrix | 2.5 |
| Code4rena | High/Medium/QA | 2.6 |
| Self-hosted tanpa rujukan | **Kriteria Universal Bagian 4** | 4 |

**Cara mengisi:** setiap `INTEL.md` **wajib** menyebut baris ini, mis.
`Severity Basis : OWASP — https://docs.across.to/introduction/bug-bounty (rubrik 2.1)`.

---

## 4. KRITERIA UNIVERSAL — definisi LOW yang diadopsi

Berlaku bila platform **tidak mendeklarasikan** kriteria (self-hosted, halaman bounty tanpa severity
matrix, atau rujukan tidak dapat ditemukan setelah STEP 1).

### 4.0 Mengapa Low dipakai sebagai LANDASAN, bukan Medium

Tiga alasan berbasis data, bukan selera:

1. **Low adalah satu-satunya tier yang diakui semua platform.** Sherlock tidak punya Low (tapi juga
   tidak punya Medium-bayaran untuk kelas ini), Code4rena menyatukannya ke QA, Immunefi/Cantina
   menaikkan griefing ke Medium, OWASP/Relay menaruhnya di Low/S1. Low adalah **irisan teraman**.
2. **Menurunkan severity tidak pernah membuat laporan salah**; menaikkan tanpa rujukan membuat laporan
   ditolak atau dipotong. Asimetri ini menentukan arah default.
3. **Low tetap dibayar di hampir semua program** (Across $250 · Relay $500–$2.000 · Immunefi ada tier
   Low · Cantina ada Low). Jadi konservatif ≠ kehilangan reward sepenuhnya.

**Low yang diadopsi = Low yang paling defensible, bukan Low yang paling murah.**

### 4.1 DEFINISI LOW UNIVERSAL (kanonik)

> **LOW** = temuan yang **terbukti dengan PoC** dan berada di **salah satu** kategori berikut,
> **TANPA** menyebabkan hilangnya dana pengguna, pembekuan permanen, insolvensi, atau manipulasi
> governance:
>
> **(L1) Annoying but not financially dangerous** — gangguan yang tidak merugikan secara finansial:
> pengguna harus mengulang transaksi, gas terbuang, event tidak akurat, fungsi non-inti gagal.
>
> **(L2) Minor economic damage** — kerugian ekonomi kecil dan **terbatas (bounded)**, tidak dapat
> dikumulasikan menjadi pengurasan pool.
>
> **(L3) DoS with no fund loss** — fungsi terganggu/revert, tetapi **tidak ada dana hilang atau
> terkunci**, dan pengguna punya jalur alternatif tanpa kehilangan hak/pokok/yield.
>
> **(L4) Admin-only bug with no external exploit path** — bug mekanis nyata pada fungsi ber-peran
> (`onlyOwner`/role), di mana **tidak ada jalur bagi pihak tanpa izin** untuk mencapainya.
>
> **(L5) Contract fails to deliver promised returns, but doesn't lose value** — kontrak tidak
> memberikan hasil sesuai spesifikasi, tanpa kehilangan nilai (definisi verbatim Immunefi untuk Low).
>
> **(L6) Code-level defect / non-critical behavior** — state handling keliru, perilaku menyimpang dari
> spec, atau pelanggaran invarian internal yang **tidak berujung** pada kerugian finansial
> (definisi Code4rena QA + Cantina "non-critical contract behavior").

**Rumusan satu kalimat (untuk laporan):**
> *"Temuan ini nyata dan dapat direproduksi, tetapi tidak menimbulkan kerugian finansial bagi pengguna
> maupun protokol — dampaknya terbatas pada gangguan operasional, kerugian terbatas, atau memerlukan
> peran istimewa."*

### 4.2 Yang MENAIKKAN di atas Low (dilarang dilabeli Low)

Naik ke **Medium** bila **salah satu** terpenuhi:

- Dana berisiko **terbatas tetapi nyata** (bounded drain, bukan sekadar gas)
- Fungsi **inti** tidak dapat beroperasi, dan tidak ada jalur alternatif
- **Pembekuan sementara** dana
- Kerugian **yield** (bukan pokok)
- **Griefing dengan biaya murah yang dapat diulang** hingga pengguna terkunci efektif
- Pemicu **permissionless** pada dampak finansial apa pun yang dapat diakumulasi

Naik ke **High/Critical** bila: pencurian dana, pembekuan permanen, insolvensi, manipulasi governance.

### 4.3 Pemicu yang MENURUNKAN Likelihood (bukan severity)

- Butuh **peran istimewa** → Likelihood Low → cap **Low** (L4)
- Butuh **kunci privat / oracle meretas diri sendiri** → bukan temuan (gugur ke `06`)
- Butuh **user error** (input salah, tidak preview) → **Informational**, bukan Low

### 4.4 Matriks pendukung (bila perlu skor eksplisit)

| Likelihood \ Impact | High | Medium | Low |
|---|---|---|---|
| **High** | Critical | High | **Low** (L1/L2/L3) |
| **Medium** | High | Medium | **Low** (L1/L6) |
| **Low** | Medium | Low | **Informational** / Low (L4) |

Anchor: Cantina-Competition, dengan **satu penyesuaian**: sel `Low Impact x High Likelihood`
dipetakan ke **Low** (bukan Medium) mengikuti definisi L1/L3 di atas — karena dampak finansialnya nol,
dan menaikkannya menuntut klaim kerugian yang tidak ada buktinya.

### 4.5 Override yang mengikat (semua platform)

| Kondisi | Label maksimal |
|---|---|
| Butuh admin/role tanpa jalur eksternal | **Low** (L4) |
| Weird ERC20 / fee-on-transfer | **Low** |
| Dust / pembulatan tak dapat dilipatgandakan | **Low** → bila murni debu: gugur (`REJECTED_DUST`) |
| Design decision tanpa kerugian dana | **Informational** |
| Butuh user error | **Informational** |
| Butuh oracle meretas diri sendiri | **gugur** (`REJECTED_PRIVILEGED_FANTASY`) |

### 4.6 Uji cepat: "apakah ini benar-benar Low?"

Lima pertanyaan. Bila semua jawabannya **ya**, label Low sah:

1. Apakah PoC berjalan dan dapat direproduksi? *(tanpa ini: bukan temuan)*
2. Apakah **tidak ada** dana pengguna hilang atau terkunci permanen?
3. Apakah pengguna **masih punya jalur** untuk mencapai tujuannya (walau lebih mahal/lambat)?
4. Apakah dampaknya **tidak dapat diakumulasi** menjadi pengurasan?
5. Apakah jalur pemicunya **jelas** (permissionless → wadah `09`; ber-peran → wadah `08`)?

Bila ada satu "tidak" → naikkan severity dan buktikan dengan angka dari log PoC.

## 5. FORMAT WAJIB DI SETIAP TEMUAN

```yaml
Impact      : <High|Medium|Low> — <alasan konkret dari bukti PoC>
Likelihood  : <High|Medium|Low> — <siapa yang bisa memicu, butuh apa>
Severity    : <Critical|High|Medium|Low>
Rujukan     : <platform + URL>          # atau "Matriks Universal (SEVERITY-RUBRIC.md Bagian 4)"
Asumsi      : <jika platform lain dipakai, severity-nya akan berbeda: sebutkan>
TanggaBukti : <A|A-HEAD|B|C|D>
```

Bila severity **berbeda antar platform** (lazim pada griefing/DoS), tulis eksplisit:

```yaml
Severity    : Low (OWASP, sesuai docs.across.to)
Asumsi      : di Immunefi/Cantina-BB kategori ini setara Medium;
              di Sherlock kemungkinan tidak diterima. Diturunkan ke Low
              karena Across mengeksplisitkan OWASP.
```

Baris `Asumsi` **wajib** — ini yang mencegah tuduhan menurunkan/menaikkan severity diam-diam.

---

## 6. WADAH — TERPISAH DARI SEVERITY

| Kondisi | Wadah |
|---|---|
| `LIVE_MATCH` + severity >= Low + pemicu permissionless | `09` |
| `LIVE_MATCH` + severity Low + **butuh admin** | `08` `ADMIN_ONLY` |
| `HEAD_ONLY_PROVEN` (severity apa pun, tetap dilaporkan) | `08` `PRE_LIVE_SCOPE` |
| Belum tuntas diuji + RPC tersedia | **dilarang** `07` — selesaikan dulu |
| Refuted (salah baca / PoC gagal dengan log) | `06` |

**Catatan:** severity TIDAK berubah karena wadah. Temuan Critical di `08` tetap ditulis Critical.

---

## 7. LARANGAN

1. **Dilarang** memberi label severity tanpa menyebut platform/rujukan.
2. **Dilarang** menaikkan severity karena "di platform lain lebih tinggi".
3. **Dilarang** menurunkan severity karena alasan deployment (HEAD-only/testnet).
4. **Dilarang** memakai Griefing="Low" tanpa menyebut platform (Immunefi & Cantina menyebut Medium).
5. **Dilarang** melaporkan admin-only sebagai High tanpa jalur pemicu unprivileged (lihat catatan
   anti-false-negative: bila penyerang dapat meracuni state sehingga keeper/operator terpaksa
   mengeksekusi dengan hasil merugikan, itu **bukan** admin-only — naikkan Likelihood).
6. **Dilarang** menyembunyikan asumsi. Tulisan "asumsi" yang jujur selalu lebih baik daripada
   angka yang terlihat tegas tapi salah.

---

## 8. RUJUKAN URL (untuk dikutip saat dipertanyakan)

| Platform | URL |
|---|---|
| Across (OWASP) | https://docs.across.to/introduction/bug-bounty |
| Immunefi v2.3 | https://immunefi.com/immunefi-vulnerability-severity-classification-system-v2-3/ |
| Sherlock | https://docs.sherlock.xyz/audits/judging/guidelines |
| Cantina Bug Bounty | https://docs.cantina.security/standards/severity/bug-bounty |
| Cantina Competition | https://docs.cantina.security/standards/severity/competition |
| Relay | https://docs.relay.link/security/bounties |
| Code4rena | https://docs.code4rena.com/competitions/severity-categorization |
