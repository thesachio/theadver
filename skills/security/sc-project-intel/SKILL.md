---
name: sc-project-intel
description: Phase 0 — Project Intelligence Recon. Isi audit/INTEL.md (identitas proyek, URL dApp/docs/repo, aturan bug bounty, laporan audit lampau, deployment terukur) SEBELUM Fase 1, dengan hukum kejujuran TIDAK_DITEMUKAN. Use when starting any new audit target or when audit/INTEL.md is missing.
version: 1.0.0
metadata:
  hermes:
    tags: [security, web3, whitehat, recon, phase0, intel]
    category: security
---

# Fase 0 — Project Intelligence Recon (`sc-project-intel`)

Mengisi `audit/INTEL.md` memakai skema `verify/templates/INTEL.md` **sebelum** Fase 1 menyentuh kode.

## Mengapa Fase 0 ada

Fase 1 lama langsung menghitung `00b-file-inventory.md` dari repo lokal. Akibatnya audit bisa berjalan
dengan asumsi yang tidak pernah dibuktikan: repo mana yang sebenarnya target, commit apa yang dipin,
aturan bounty apa yang membatasi scope, dan laporan audit mana yang harus dibaca lebih dulu agar tidak
menemukan ulang hal yang sudah diketahui publik. `INTEL.md` menutup empat celah itu **sebelum** biaya
token besar dikeluarkan.

**Ini bukan riset bebas.** Fase 0 hanya mengisi slot yang sudah didefinisikan skema. Tidak ada bagian
"informasi tambahan" — bila tidak masuk slot, tidak ditulis.

---

## Hukum Kejujuran (mengikat, melanggar = INTEL dianggap gagal)

1. **`TIDAK_DITEMUKAN` adalah hasil sah.** Setiap slot yang tidak dapat dipenuhi **wajib** ditulis
   `TIDAK_DITEMUKAN`, bukan dikosongkan, bukan diisi tebakan.
2. **DILARANG mengarang URL.** Setiap URL harus berasal dari hasil pencarian/ekstraksi nyata pada sesi
   ini, dan wajib dibuktikan hidup (`curl -sI` atau `web_extract`).
3. **DILARANG mengarang nama auditor, tanggal, atau nomor commit.** Commit diambil dari
   `git rev-parse`, bukan dari ingatan.
4. **"Tidak ketemu" ≠ "tidak ada".** Bila pencarian gagal karena alat/akses (mis. situs memblokir,
   halaman butuh login), tulis `TIDAK_DITEMUKAN` **dan** jelaskan di Bagian 6 bahwa penyebabnya
   adalah batasan akses — bukan menyimpulkan bahwa laporan/aturan itu tidak eksis.
5. **Dilarang melanjutkan ke Fase 1** bila `Intel Status = PARTIAL` tanpa mengisi Bagian 6.
   Bagian 6 adalah yang mencegah klaim berlebih di Fase 4.

---

## Prosedur

### Langkah 0 — Resolusi Target (tanpa jaringan)

```bash
# 1. Path absolut + apakah ini repo git
cd <path-proyek> && pwd && git rev-parse --is-inside-work-tree

# 2. Commit yang dipin (WAJIB hash, bukan "latest")
git rev-parse HEAD && git rev-parse --abbrev-ref HEAD
git remote -v

# 3. Remote URL -> identitas repo (owner/nama)
```

Bila bukan repo git → `Specific GitHub Repo : TIDAK_DITEMUKAN` dan `Audited Commit : TIDAK_DITEMUKAN`
(lalu jelaskan di Bagian 6). Jangan menebak repo dari nama folder.

### Langkah 1 — Identitas Proyek

Sumber berurutan: `README.md` repo → file `package.json`/`foundry.toml`/`Anchor.toml` →
`git remote -v`. `Brief Overview` maksimal 3 kalimat, hanya mekanisme inti yang bisa dibuktikan dari
berkas yang dibaca (sebut sumbernya di `Diverifikasi Oleh`).

### Langkah 2 — URL Referensi (wajibkan pembuktian hidup)

```bash
# Untuk setiap kandidat URL:
curl -s -o /dev/null -w '%{http_code} %{url_effective}\n' -L "<url>"
```

Aturan penerimaan:

| Hasil | Tindakan |
|---|---|
| `200` / `30x` ke halaman relevan | terima |
| `404` / `410` | tolak → `TIDAK_DITEMUKAN` |
| `403` / `429` / timeout | `TIDAK_DITEMUKAN` + catat di Bagian 6 sebagai batasan akses |
| Redirect ke beranda generik | tolak — bukan URL langsung |

**DILARANG** menulis URL hasil pencarian (`google.com/search?...`, `duckduckgo.com/?q=...`).
**DILARANG** menulis domain akar bila halaman spesifiknya sudah diketahui.

### Langkah 3 — Aturan Bug Bounty

Cari di urutan: docs resmi proyek (halaman `security`/`auditors`/`bug-bounty`) → platform
(Immunefi/Cantina/Sherlock/Code4rena/CodeHawks) → repo (`SECURITY.md`, `.github/SECURITY.md`).

Yang wajib dicatat di `High-Level Scope Note` **hanya bila tertulis eksplisit di halaman itu**:
repo/commit yang di-scope, chain yang berlaku, kelas temuan yang dikecualikan (mis. known issues,
centralization risk, oracle failure). **Jangan menyimpulkan scope** dari praktik umum.

### Langkah 4 — Laporan Audit Lampau

Cari di: folder `/audits` repo, situs auditor, halaman docs "Security". Untuk tiap laporan:
nama auditor + tahun + **URL langsung ke berkas/halaman** + fokus/versi yang di-audit.

Bila repo hanya **menyebut** audit tanpa tautan → Bagian 4 = `TIDAK_DITEMUKAN`, dan klaim tak
terverifikasi itu dicatat di Bagian 6. Jangan menaikkan klaim menjadi laporan.

### Langkah 5 — Deployment Terukur (bukan asumsi)

```bash
# Bukti kode benar-benar ter-deploy pada chain target
cast code <alamat> --rpc-url <rpc>   | wc -c     # 0x / 2 karakter = tidak ada kode
cast call <alamat> "owner()(address)" --rpc-url <rpc>
```

Daftar alamat diambil dari sumber resmi (`broadcast/deployed-addresses.json`,
`deployments/*.json`, docs). DILARANG menulis alamat dari ingatan.

> **Catatan metode:** `cast call` pada endpoint publik dapat mengembalikan `revert data "0x"`
> untuk selector yang **ada** maupun **tidak ada**. Jangan pakai itu sebagai bukti ketiadaan —
> pakai scan dispatcher `eth_getCode` (`PUSH4..EQ`). Lihat `VERDICT.md` Langkah 0.

---

## Keluaran

Tulis **hanya** `audit/INTEL.md`, memakai template `verify/templates/INTEL.md` apa adanya.
Panjang target 35–40 baris saat terisi.

**DILARANG** menulis ke `00`, `00b`, `01`, `02`, `03`, `STATE.md`, atau `04`–`09` dari fase ini.
Fase 0 berhenti setelah `INTEL.md` terisi dan `Intel Status` ditetapkan.

Protokol penulisan: ikuti `workspace/AGENTS.md` Pasal 1.3 (`.tmp` → `fsync` → `os.replace()`;
dilarang `open("w")` / `>`).

## Gate keluar Fase 0

| Syarat | Gagal berarti |
|---|---|
| `Target Repo Path` absolut & ada | Fase 1 tidak boleh mulai |
| `Audited Commit` berupa hash hasil `git rev-parse` | Fase 1 tidak boleh mulai |
| Setiap URL lolos uji `curl` | URL tersebut diturunkan ke `TIDAK_DITEMUKAN` |
| `Intel Status = PARTIAL` ⇒ Bagian 6 terisi | INTEL ditolak |
| Tidak ada slot yang dikosongkan | INTEL ditolak |

## Pitfalls yang sudah terbukti

- **Menulis "latest" sebagai commit** — Fase 4 tidak bisa merekonsiliasi deployment tanpa hash pasti.
- **Mengisi laporan audit dari ingatan model.** Ini kesalahan paling berbahaya: nama auditor terdengar
  meyakinkan tapi tidak dapat ditunjuk. Selalu butuh URL.
- **Menyimpulkan scope bounty** dari deskripsi umum platform. Scope hanya sah bila tertulis.
- **Menghitung URL mati sebagai "ada".** Cek status HTTP, jangan asumsikan 200.
- **Menulis alamat kontrak tanpa `cast code`.** Alamat salah = seluruh Fase 3 menembak target kosong.
