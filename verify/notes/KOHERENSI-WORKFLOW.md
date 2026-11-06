# CATATAN KOHERENSI WORKFLOW

Status: 2026-11-06 · commit `e863d21`+ · bukan aturan mengikat, hanya peta rujukan.

Dokumen ini mencatat **di mana setiap konsep didefinisikan** (single source) dan
**duplikasi mana yang sengaja dibiarkan** karena isinya konsisten. Tujuannya: kalau
nanti ada yang mengubah satu tempat, ia tahu tempat lain mana yang harus ikut dicek.

---

## 1. Single Source (definisi resmi hanya di sini)

| Konsep | Didefinisikan di | Yang merujuk (tidak boleh mendefinisikan ulang) |
|---|---|---|
Paket delegasi (1)–(7) | `workspace/AGENTS.md` Pasal 4 | `sc-phase2-hunt`, `sc-autopilot` |
Batas manifes (16 Fase 2 / 14 Fase 3) | `workspace/AGENTS.md` Pasal 4 | `sc-autopilot` |
Skema RADAR + Gerbang 3-Uji | `verify/templates/RADAR.md` | `AGENTS.md`, `sc-phase2-hunt`, `sc-autopilot` |
Blueprint FACTS + Hukum Pengikatan Scope | `verify/templates/FACTS.md` | `AGENTS.md`, `sc-phase2`, `sc-phase3` |
Gerbang scope sebelum severity | `verify/VERDICT.md` §0.2c | `sc-phase3` |
Metode `M-xxx` | `sc-phase2-hunt/references/ref-method-registry.md` | `sc-phase2-hunt` |
Atomic write / anti-truncate | `sc-phase2-hunt/references/ref-atomic-write.md` | `AGENTS.md` §1.3, `sc-phase2` |
Taksonomi kelas topologi | `ref-method-registry.md` Bagian 1 | semua skill fase |

**Aturan:** konsep baru **wajib** masuk tabel ini saat ditambahkan. Tanpa entri di sini,
konsep itu akan terduplikasi dalam 2–3 rilis dan mulai menyimpang.

---

## 2. Duplikasi yang SENGAJA dibiarkan (isinya konsisten)

### 2.1 Blok "6 file murni `04`–`09`"
Muncul di **dua** tempat:
- `workspace/AGENTS.md` Pasal 2 (daftar file audit, versi panjang per file)
- `sc-autopilot` → Pitfalls & Hukum Mutlak (versi ringkas per file)

**Status:** konsisten, tidak bertolak belakang. **Tidak dikonsolidasi** karena bloknya
panjang dan banyak rujukan silang; risiko salah sunting lebih besar dari manfaatnya.

**Risiko:** jika salah satu diubah tanpa yang lain, gejalanya = daftar delegasi ganda
(yang pernah terjadi pada butir RADAR/§5). **Pemicu pengecekan:** setiap kali salah satu
blok ini disentuh, `diff` kedua blok.

### 2.2 Penjelasan rationale staging
"Kenapa staging, bukan ringkasan" muncul di `AGENTS.md` §1.3.4, `sc-phase2` (dua tempat),
dan `sc-autopilot`. Isinya sama (entri 15–20 baris vs unit 120–160 baris).

**Status:** konsisten. Dibiarkan karena masing-masing konteks butuh alasan itu di tempat.

### 2.3 Angka `≈12 baris` untuk ukuran §5
Merujuk pada **ukuran blok model per domain**, bukan batas manifes. Jangan tertukar
dengan batas manifes (16/14). Bila mencari "12 baris", pastikan konteksnya.

---

## 3. Aturan pemeliharaan

1. **Duplikasi yang konsisten → catat, jangan konsolidasi.** Konsolidasi hanya jika
   isinya bertolak belakang, atau jika salah satunya sudah tertinggal.
2. **Duplikasi yang bertolak belakang → WAJIB diperbaiki segera**, bukan dicatat.
   Contoh nyata yang sudah diperbaiki: daftar delegasi 5 vs 7 butir; batas manifes
   12 vs 16/14.
3. **Setelah mengubah single source**, jalankan pemeriksaan rujukan:
   ```bash
   grep -rn "<istilah-yang-diubah>" workspace/AGENTS.md skills/security/ verify/
   ```
4. **Jangan menambah konsep tanpa entri di tabel §1.**

---

## 4. Riwayat koreksi koherensi

| Tanggal | Temuan | Tindakan |
|---|---|---|
2026-11-06 | `sc-phase2` & `sc-autopilot` masih memakai daftar delegasi 5 butir (tanpa RADAR/§5) | diganti rujukan ke `AGENTS.md` §4 |
2026-11-06 | Manifes 12 baris tidak muat setelah +2 `R-CAND` +2 `M-FACT` | naik ke 16 (Fase 2) / 14 (Fase 3) |
2026-11-06 | 5 kemunculan `12 baris` tersisa di konteks manifes | diselaraskan ke 16/14 |
