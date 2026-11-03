# Protokol Anti-Truncate: Penulisan File Atomik & Backup Write-Ahead

**Insiden pemicu:** `04-code-guarded.md` terpotong jadi **0 byte**. Skrip Python membuka file dengan `mode="w"` (truncate seketika), lalu penulisan gagal `PermissionError`. Backup yang dibuat worker menyalin file yang **sudah kosong** — sehingga tidak ada salinan pulih. Hilang ~247 entri Putaran 1 + 39 entri Putaran 2; restorasi verbatim mustahil.

---

## 0. Metode Write per Karakteristik File (pilih yang paling murah, tapi tidak merusak)

DILARANG memakai "append selalu". Tiap file punya pola mutasi berbeda.

| Karakteristik | File | Metode | Alasan |
|---|---|---|---|
| Tulis sekali | `00`, `01`, `02` | `write_file` awal; tambahan → `append` | Isi hampir tidak berubah |
| Generate massal | `00b` | **script** (`phase0_inventory.py`); verifikasi `grep -n` | 260 baris; baca penuh ≈9k token tidak perlu |
| Append-murni | `06`, `08`, `09` | `append` | Entri tidak diubah setelah ditulis |
| Append lalu ubah status | `04`, `05`, `07` | entri baru → `append`; status → `patch` | Append saja membuat status basi |
| Edit tabel/baris | `03`, `STATE` | `patch` baris | 40 token/baris vs 5.364 baca penuh (134×) |

**Aturan pemilihan:** token terendah **yang tetap benar**. Append hanya sah bila entri tidak akan diubah; bila statusnya harus diperbarui nanti, pakai `patch`.

---

## 1. Hukum Atomisitas: `open("w")` DILARANG untuk file audit

`open(path, "w")` memotong file ke **0 byte saat dibuka**, sebelum satu byte pun ditulis. Jika penulisan gagal di tengah, isi asli sudah hilang permanen.

**WAJIB pakai pola tulis-lalu-rename:**

```python
import os, tempfile, pathlib

def atomic_write(path, data: str) -> None:
    path = pathlib.Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())        # paksa ke disk sebelum rename
    os.replace(tmp, path)           # atomik di POSIX
```

File lama **tidak tersentuh** sampai isi baru lengkap dan ter-flush. Gagal di tengah = file lama tetap utuh, hanya tersisa `.tmp`.

**Larangan setara** untuk shell:
- `>` DILARANG untuk file audit (sama-sama truncate). Pakai `>>` hanya untuk append, atau tulis ke file sementara lalu `mv`.
- `sed -i` / `python -c` yang menulis langsung ke file audit **DILARANG** — keduanya truncate.
- `write_file`/`patch` tool aman (bukan `open("w")` polos).

## 2. Backup Write-AHEAD (sebelum mutasi, bukan sesudah)

DILARANG membuat backup dari file setelah file itu disentuh. Urutan wajib:

1. **Sebelum** mutasi: salin file ke `audit/notes/backups/<nama>.<timestamp>.bak`
2. **Verifikasi** backup: ukuran > 0 dan `sha256` sama dengan sumber
3. **Baru** tulis perubahan (pakai `atomic_write`)
4. **Verifikasi** hasil: ukuran wajar & parses/terbaca

Backup yang dibuat **setelah** file rusak adalah jebakan: ia memberi rasa aman tanpa isi.

## 3. Guard Ukuran & Konten Pasca-Tulis

Setiap penulisan ke file audit wajib diikuti pemeriksaan:

| Cek | Aturan |
|---|---|
| Ukuran | File audit **tidak boleh** 0 byte. Jika sebelumnya >0 dan hasil =0 → **BATAL & pulihkan dari backup** |
| Penyusutan | Jika ukuran baru < 50% ukuran lama **tanpa alasan eksplisit** (mis. pemangkasan yang disengaja) → tandai & minta konfirmasi |
| Struktur | File `0X-*.md` wajib masih punya heading domainnya (mis. `## [G-` atau `## [L2-`). Hilang heading = rusak |
| Hash | Catat `sha256` lama vs baru di notes bila perubahan besar |

## 4. Larangan Penulisan Paralel & Disiplin Tool Subagent

**Hanya SATU penulis aktif pada satu waktu** (`max_concurrent_children: 1`). Bila memakai `delegate_task`:
- **DILARANG** menjalankan lebih dari 1 Subagent secara paralel.
- Subagent **HANYA** boleh menyentuh `audit/03`–`09` melalui native tool `append` (untuk menambah entri baru) atau `patch` (untuk memperbarui baris status), atau `atomic_write` via `.tmp` -> `os.replace`. Subagent **DILARANG KERAS** memakai `open("w")`, `>`, `sed -i`, atau `write_file` penuh pada file audit yang sudah ada.
- **Pengecualian wajib — entri unit `S-n`:** hasil pendadahan unit antrean Fase 2 tetap ditulis ke `audit/notes/staging-<unit>.md` (bukan langsung ke `04`/`05`), lalu Parent me-merge. Alasannya: hanya Parent yang dapat mencocokkan `grep -c '^## \['` terhadap manifes, dan hanya Parent yang memutuskan klasifikasi akhir `04` vs `05`.
- Khusus `audit/STATE.md`, Subagent **DILARANG** menulisnya sendiri — Subagent melaporkan perubahan kursor di ringkasan 12 baris, dan Parent yang melakukan `patch` pada `audit/STATE.md`.

> Rujukan: `workspace/AGENTS.md` Pasal 1.3 & 4.

## 5. Protokol Pemulihan Bila Terlanjur Terpotong

1. **Cek backup write-ahead** — bila ada & terverifikasi, pulihkan.
2. **Cek sumber sekunder** — `03-attack-surface-queue.md` (jejak unit), `05-raw-leads.md`, `notes/` (draf worker), riwayat chat.
3. **Rekonstruksi dari kode sumber** — bukti utama tetap `File:Baris` + ekspresi guard di source.
4. **Tandai jelas sebagai REKONSTRUKSI**, bukan file asli:
   ```
   REKONSTRUKSI 2026-MM-DD — isi asli hilang akibat truncate.
   Diturunkan dari: <source:baris>, <notes/...>, <03 unit>.
   Status Round-2 dipulihkan dari checkpoint terverifikasi: <daftar>.
   Unit lain: BELUM.
   ```
5. **DILARANG mengklaim file rekonstruksi sebagai file asli.** Kejujuran asal-usul adalah bagian dari bukti.

## 6. Checklist Sebelum Menyentuh File Audit Existing

- [ ] `df -h` — ruang cukup
- [ ] File sudah dibackup write-ahead + hash cocok
- [ ] Menulis lewat `atomic_write` (bukan `open("w")`)
- [ ] Satu penulis saja (tidak ada worker paralel)
- [ ] Verifikasi pasca-tulis: ukuran, heading, hash
- [ ] Bila gagal: pulihkan dari backup, jangan lanjut menulis
