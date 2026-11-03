---
name: sc-project-intel
description: Phase 0 — Project Intelligence & Direct Reference Link Gatherer (Overview, Main UI, Specific GitHub Repo, Direct Bug Bounty Rules Link, and Direct Past Audit Report Links) into audit/INTEL.md.
version: 6.1.0
metadata:
  hermes:
    tags: [security, web3, whitehat, recon, phase0, intel]
    category: security
---

# Fase 0 — Project Intelligence & Direct Reference Link Gatherer (`sc-project-intel`)

Mengumpulkan **6 informasi konteks eksternal & tautan langsung** ke dalam `audit/INTEL.md`
**sebelum** `sc-phase1-recon` bekerja.

---

## Peran & Batas Cakupan Ketat (Anti-Redundansi dengan Fase 1)

Fase 0 adalah **pengumpul tautan**, bukan penganalisis kode. Semua pekerjaan struktural milik Fase 1.

### 6 Data Wajib yang Dicari (maksimal — tidak lebih)

| # | Data | Bentuk yang diterima |
|---|---|---|
| 1 | **Project** | Nama proyek & organisasi resmi |
| 2 | **Overview Singkat** | 1–3 kalimat fungsi utama protokol |
| 3 | **Situs Utama (UI Interaksi / dApp)** | Link langsung tempat pengguna berinteraksi + link docs resmi |
| 4 | **Repository GitHub Spesifik** | Link langsung ke repo target + branch & commit HEAD lokal |
| 5 | **Bug Bounty Spesifik (Direct Link)** | Link langsung ke aturan/cakupan bug bounty proyek — halaman di dokumentasi resmi **atau** platform pihak ketiga (Immunefi, Cantina, Sherlock, Code4rena, CodeHawks, dll.) |
| 6 | **File Laporan Auditor Sebelumnya (Direct Links)** | Link langsung ke file PDF, folder `audits/` di repo, atau halaman laporan audit terdahulu |

Berhenti setelah keenamnya terisi (atau ditandai `TIDAK_DITEMUKAN`). **Dilarang menambah bagian ke-7.**

### Larangan Keras di Fase 0 (tetap menjadi tugas `sc-phase1-recon`)

- **DILARANG** melakukan enumerasi berkas kontrak, menghitung LOC, atau membuat `00b-file-inventory.md`.
- **DILARANG** memetakan 3 Kasta Aset, Core Invariants, atau State-Mutation Matrix (`00`, `01`, `02`, `03`).
- **DILARANG** menyalin seluruh isi tabel bug bounty atau isi laporan audit panjang lebar ke dalam
  `audit/INTEL.md`. Jaga `audit/INTEL.md` **≤ 40 baris** agar hemat token. Cukup: link + 1–2 baris kualifikasi.
- **DILARANG** mengarang URL (**No Hallucinated Links**). Setiap URL wajib berasal dari:
  - berkas repo lokal: `README*`, `package.json`, `foundry.toml`, `Cargo.toml`, `Move.toml`, `Anchor.toml`,
    folder `docs/`, folder `audits/`, `SECURITY.md`, atau `git remote -v`; **atau**
  - hasil pencarian eksternal yang **terverifikasi**.

  Bila sudah dicari maksimal namun tidak ada → tulis `TIDAK_DITEMUKAN`.

> **Hukum kejujuran:** `TIDAK_DITEMUKAN` adalah hasil yang sah dan tidak menurunkan kualitas audit.
> URL karangan menghancurkan seluruh laporan. "Tidak ketemu" ≠ "tidak ada" — bila gagal karena blokir
> situs/login, tulis `TIDAK_DITEMUKAN` **dan** sebutkan penyebabnya.

### Aturan Jujur per Butir INTEL (mengikat)

Setiap butir punya cara sah menyatakan ketiadaan. **Mengosongkan slot = INTEL ditolak.**
Bentuk penulisan lengkap per butir ada di tabel "Aturan Jujur per Bagian" pada
`verify/templates/INTEL.md`.

| Butir | Bila tidak ditemukan | DILARANG |
|---|---|---|
| Project Name | `TIDAK_DITEMUKAN` + sumber dicek | Menebak dari nama folder |
| Overview | `TIDAK_DITEMUKAN — tidak ada README/docs` | Mengarang dari pengetahuan umum model |
| Main UI (dApp) | `TIDAK_DITEMUKAN` (mungkin kontrak/library tanpa UI) | Menulis domain akar belum diuji |
| Official Docs | `TIDAK_DITEMUKAN` | URL mesin pencari |
| GitHub Repo | `TIDAK_DITEMUKAN — bukan repo git` | Menebak `github.com/<org>/<nama>` |
| Audited Commit | `TIDAK_DITEMUKAN` | `latest` / `main` / hash karangan |
| Bug Bounty | `TIDAK_DITEMUKAN` | Mengisi `Immunefi` tanpa halaman nyata |
| Scope Note | `TIDAK_DITEMUKAN — tidak ada aturan tertulis` | **Menyimpulkan scope dari praktik umum** |
| Past Audits | `TIDAK_DITEMUKAN` | Menaikkan "disebut di README" jadi laporan |
| Deployment | `TIDAK_DITEMUKAN` per sub-baris | Alamat tanpa `cast code` non-kosong |

**Empat hukum penegakan:**

1. **Satu alasan per ketiadaan.** `TIDAK_DITEMUKAN` tanpa alasan + sumber di Bagian 6 = INTEL **tidak jujur**.
2. **"Gagal diakses" ≠ "tidak ada".** 403/429 hanya berarti bot-protection — coba `browser_exec`
   dulu; bila tetap gagal, tulis `TIDAK_DITEMUKAN (batas akses: <penyebab>)`.
   DILARANG menyimpulkan aturan/laporan itu tidak eksis.
3. **Bila ragu, turunkan.** Satu slot kosong yang jujur tidak merusak laporan; satu URL palsu membatalkan seluruhnya.
4. **Konsistensi status.** `COMPLETE` hanya sah bila keenam butir di Bagian 6 = `DITEMUKAN`.
   Satu saja `TIDAK_DITEMUKAN` ⇒ wajib `PARTIAL`.

---

## Prosedur Eksekusi 3 Langkah

### Langkah 1 — Ekstraksi Fakta Lokal Cepat

Periksa berkas berikut di dalam repo target (urutan ini, berhenti saat 6 data lengkap):

```bash
git remote -v                    # -> Repository GitHub Spesifik
git rev-parse HEAD               # -> commit pin (wajib hash, bukan "latest")
git rev-parse --abbrev-ref HEAD  # -> branch
ls README* SECURITY.md docs/ audits/ 2>/dev/null
```

| Berkas | Yang dicari |
|---|---|
| `git remote -v` | URL repo (owner/nama) |
| `git rev-parse HEAD` + `--abbrev-ref` | branch @ commit |
| `README*` | Nama proyek, overview, link UI/docs/bounty |
| `SECURITY.md`, `.github/SECURITY.md` | Halaman bounty / kontak keamanan |
| `package.json`, `foundry.toml`, `Cargo.toml`, `Move.toml`, `Anchor.toml` | Homepage, repository, URL docs |
| `docs/` | Halaman aturan bounty / arsitektur |
| `audits/` | PDF / laporan auditor terdahulu |

Tangkap URL resmi, link UI, link bounty, dan file PDF audit yang **sudah tersedia di repo**.
Bila bukan repo git → `Repository GitHub Spesifik : TIDAK_DITEMUKAN` dan commit `TIDAK_DITEMUKAN`
(jelaskan di Bagian 6). Jangan menebak repo dari nama folder.

### Langkah 2 — Pencarian Link Eksternal Spesifik

Hanya untuk slot yang **belum lengkap** dari Langkah 1. Lakukan pencarian **terarah**:

1. **Direct link ke halaman bug bounty proyek** — cek dokumentasi resmi (`/security`, `/auditors`,
   `/bug-bounty`) lalu platform (Immunefi / Cantina / Sherlock / Code4rena / CodeHawks).
2. **Direct link ke file/halaman laporan auditor terdahulu** — situs auditor, halaman docs "Security",
   atau repo terpisah `audits`.

**Saring sebelum menerima** (wajib):

| Hasil uji | Tindakan |
|---|---|
| `200` / `30x` ke halaman relevan | terima |
| `404` / `410` | tolak → `TIDAK_DITEMUKAN` |
| `403` / `429` | **ADA (terblokir bot-protection)** — coba `browser_exec`, jangan tandai hilang |
| Redirect ke beranda generik | tolak — bukan URL langsung |

```bash
curl -s -o /dev/null -w '%{http_code} %{url_effective}\n' -L "<url>"
```

**DILARANG** menulis URL mesin pencari (`google.com/search?...`, `duckduckgo.com/?q=...`).
**DILARANG** menulis domain akar bila halaman spesifiknya sudah diketahui.
**DILARANG** menyimpulkan scope bounty dari praktik umum — scope hanya sah bila **tertulis** di halaman itu
(repo/commit yang di-scope, chain yang berlaku, kelas temuan yang dikecualikan).

### Langkah 3 — Penulisan Atomik `audit/INTEL.md`

1. Pastikan direktori `audit/` ada (`mkdir -p audit`).
2. Tulis mengikuti skema `verify/templates/INTEL.md` — **jangan mengubah strukturnya**.
3. Gunakan `write_file` untuk penulisan awal; gunakan `patch`/`append` bila hanya memperbarui field.
4. **DILARANG** memakai `open(path, "w")` atau shell `>` (lihat `workspace/AGENTS.md` Pasal 1.3).
   Bila menulis lewat skrip: `.tmp` → `f.flush()` → `os.fsync()` → `os.replace()`.
5. Verifikasi pasca-tulis: ukuran ≠ 0, keenam heading bagian masih ada, total **≤ 40 baris**.

---

## Cara Konsumsi oleh Hilir (`sc-phase1-recon` & `sc-autopilot`)

`audit/INTEL.md` **dibaca oleh `sc-phase1-recon` pada awal Fase 1** untuk dua hal:

1. **(a) Sinkronisasi scope** — memastikan daftar kontrak in-scope di `00b-file-inventory.md`
   selaras dengan apa yang disebut oleh **link Bug Bounty** (Bagian 3 `INTEL.md`). Kontrak yang
   tidak masuk cakupan bounty tidak boleh dihitung sebagai permukaan serang yang dapat dibayar.
2. **(b) Petunjuk Patch-Scar** — menggunakan **daftar laporan audit sebelumnya** (Bagian 4) sebagai
   petunjuk awal saat melacak *Patch-Scar* di `01-threat-and-env.md`. Temuan auditor terdahulu
   menandakan area yang pernah ditambal — di situlah jalur sampingan paling sering luput.

`sc-autopilot` membaca `audit/INTEL.md` pada Tahap Orkestrasi 0 untuk menentukan apakah Fase 1
boleh dimulai (lihat Gate di bawah).

---

## Gate Keluar Fase 0

| Syarat | Gagal berarti |
|---|---|
| `Target Repo Path` absolut & ada | Fase 1 **tidak boleh mulai** |
| `Audited Commit` berupa hash hasil `git rev-parse` | Fase 1 **tidak boleh mulai** |
| Setiap URL lolos uji `curl` atau `browser_exec` | URL tersebut diturunkan ke `TIDAK_DITEMUKAN` |
| `Intel Status = PARTIAL` ⇒ Bagian 6 terisi | INTEL **ditolak** |
| Tidak ada slot dikosongkan | INTEL **ditolak** |
| `audit/INTEL.md` ≤ 40 baris | INTEL **ditolak** (kelebihan muatan) |

**DILARANG** menulis ke `00`, `00b`, `01`, `02`, `03`, `STATE.md`, atau `04`–`09` dari fase ini.
Fase 0 berhenti setelah `INTEL.md` terisi dan `Intel Status` ditetapkan.

---

## Pitfalls yang sudah terbukti

- **Menulis "latest" sebagai commit** — Fase 4 tidak bisa merekonsiliasi deployment tanpa hash pasti.
- **Mengisi laporan audit dari ingatan model.** Nama auditor terdengar meyakinkan tapi tak dapat
  ditunjuk. Selalu butuh URL.
- **Menyimpulkan scope bounty** dari deskripsi umum platform. Scope hanya sah bila tertulis.
- **Menghitung URL mati sebagai "ada".** Cek status HTTP, jangan asumsikan 200.
- **Menyalin tabel bounty utuh** ke `INTEL.md` — melanggar batas 40 baris dan menduplikasi pekerjaan
  Fase 1.
- **Melanjutkan ke enumerasi kontrak** karena "sekalian" — itu tugas `sc-phase1-recon`, dan
  menggandakannya membuat dua sumber kebenaran yang saling bertentangan.
- **Menulis alamat kontrak tanpa `cast code`.** Alamat salah = seluruh Fase 3 menembak target kosong.
