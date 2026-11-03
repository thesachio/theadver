# PROJECT INTELLIGENCE BRIEF (PHASE 0)

> **Skema tunggal untuk `audit/INTEL.md`.** Ditempatkan sejajar dengan `audit/STATE.md`
> agar tidak bentrok dengan `00b-file-inventory.md` dan `00-project-map.md`.
> **Target saat diisi: 35–40 baris.** Berkas ini adalah *fakta yang dapat ditunjuk*,
> bukan narasi — setiap isian wajib berupa URL langsung atau penanda ketiadaan.
>
> **Hukum kejujuran:** bila sesuatu tidak ditemukan, tulis `TIDAK_DITEMUKAN`.
> DILARANG mengarang URL, mengisi nama auditor dari ingatan, atau menebak commit.
> `TIDAK_DITEMUKAN` adalah hasil yang sah dan tidak menurunkan kualitas audit;
> URL palsu menghancurkan seluruh laporan.

---

```markdown
# PROJECT INTELLIGENCE BRIEF (PHASE 0)

- Target Repo Path : <path absolut proyek lokal>
- Last Updated    : <YYYY-MM-DD>
- Intel Status    : COMPLETE | PARTIAL (catat bagian yang belum ditemukan)
- Diverifikasi Oleh: <perintah yang dijalankan untuk membuktikan tiap URL hidup>

## 1. Project Identity & Brief Overview
- Project Name : <Nama Resmi Proyek & Organisasi>
- Brief Overview : <1–3 kalimat ringkas mengenai fungsi dan mekanisme inti protokol>

## 2. Core Reference Links (Direct URLs Only)
- Main UI (dApp) : <URL langsung ke aplikasi web/UI utama tempat pengguna berinteraksi, atau TIDAK_DITEMUKAN>
- Official Docs  : <URL langsung ke dokumentasi teknis resmi, atau TIDAK_DITEMUKAN>
- Specific GitHub Repo : <URL langsung ke repositori GitHub spesifik yang menjadi target audit>
- Audited Commit / Branch : <branch> @ <commit_hash>

## 3. Bug Bounty Rules (Direct Link)
- Platform : <Docs Resmi | Immunefi | Cantina | Sherlock | Code4rena | CodeHawks | Lainnya | TIDAK_DITEMUKAN>
- Direct Bounty URL : <URL langsung ke halaman aturan/scope bug bounty spesifik proyek ini>
- High-Level Scope Note : <1–2 baris catatan faktual bila halaman bounty menyebut repo/kontrak/
  chain spesifik atau aturan pengecualian utama>

## 4. Past Audit Reports (Direct File/Report Links)
- [<Nama Auditor 1 — Tanggal/Tahun>](<URL langsung ke file PDF / repo / halaman laporan audit>) — Fokus/Versi: <singkat>
- [<Nama Auditor 2 — Tanggal/Tahun>](<URL langsung ke file PDF / repo / halaman laporan audit>) — Fokus/Versi: <singkat>
- *(Jika belum ditemukan laporan publik, tulis: `TIDAK_DITEMUKAN` — jangan mengosongkan bagian ini.)*

## 5. Deployment & Live Surface (fakta terukur, bukan asumsi)
- Chain / Network Aktif : <daftar chainId yang benar-benar dipakai, atau TIDAK_DITEMUKAN>
- Kontrak Utama (alamat) : <alamat + chain, atau TIDAK_DITEMUKAN>
- Bukti Live : <perintah `cast call`/`cast code` + hasil ringkas yang membuktikan kode ter-deploy>

## 6. Catatan Ketiadaan (WAJIB diisi bila Intel Status = PARTIAL)
- Tidak ditemukan : <daftar butir yang gagal ditemukan — mis. "bounty page", "laporan audit publik">
- Sudah dicoba : <sumber yang benar-benar dicek: docs resmi, GitHub org, Immunefi search, dll>
- Dampak ke audit : <apa yang TIDAK bisa diklaim nanti karena butir ini kosong>
```

---

## Aturan pengisian (mengikat)

1. **URL harus langsung.** `https://docs.protokol.xyz/security` ✅ — bukan `https://docs.protokol.xyz` ✅❌
   bila halaman itu tidak memuat aturan buruannya. DILARANG menaruh URL mesin pencari.
2. **Setiap URL wajib dibuktikan hidup** pada sesi yang sama (`curl -sI` → status 200/30x, atau
   `web_extract`). Catat perintahnya di baris `Diverifikasi Oleh`. URL mati → `TIDAK_DITEMUKAN`.
3. **Commit wajib dipin.** `Audited Commit / Branch` harus berisi hash yang benar-benar di-`git rev-parse`,
   bukan "latest". Ini input langsung untuk Langkah 0 Rekonsiliasi Deployment di `VERDICT.md`.
4. **Dilarang mengarang nama auditor.** Bila repo/docs menyebut "audit oleh X" tanpa tautan laporan,
   tulis `TIDAK_DITEMUKAN` di bagian 4 dan sebutkan klaim tak-terverifikasi itu di bagian 6.
5. **Bagian 5 bersifat terukur.** Deployment dinyatakan ada hanya bila ada `eth_getCode` non-kosong
   atau tx deploy. "Seharusnya live" bukan bukti.
6. **Bagian 6 tidak boleh kosong** bila `Intel Status = PARTIAL`. Justru bagian inilah yang
   melindungi audit dari klaim berlebih di Fase 4.
