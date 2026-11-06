# RADAR — Sinyal Celah Lintas-Domain (Append-Only)

Wadah untuk **sinyal yang belum layak jadi lead**: sesuatu yang janggal, presisi lokasinya,
tetapi belum ada bukti eksploitasi — dan **bukan** milik unit yang sedang dibedah.

> **Mengapa file ini ada.** Fase 2 hanya punya dua keluaran: `LEAD_GENERATED` dan
> `ATTESTED_CLEAN`. Sinyal "ini mencurigakan tapi saya belum bisa membuktikan apa pun"
> tidak punya rumah, sehingga dibuang bersama konteks subagent. Padahal justru kelas
> sinyal inilah yang paling sering menjadi temuan bernilai setelah dirangkai lintas-domain.

## Hukum Mutlak

1. **APPEND-ONLY.** Tidak ada satu baris pun yang boleh diedit setelah ditulis. Status
   dinyatakan sebagai **baris kejadian baru**, bukan dengan mengubah baris lama.
   Alasan: `04-code-guarded.md` pernah terpotong 0 byte dan ~286 entri hilang permanen.
   RADAR menyimpan insight yang **tidak bisa diregenerasi** dari kode — kerugiannya lebih besar.
2. **DILARANG memarkir bukti di sini.** Begitu ada PoC `[PASS]`, sinyal **wajib** naik jadi
   lead di `05` saat itu juga. RADAR yang menampung bukti berubah jadi tempat pembuangan
   dan lead berharga akan mati tanpa pernah masuk antrean Fase 3.
3. **Satu penulis: Parent.** Subagent hanya **mengusulkan** lewat manifes (maks 2 kandidat
   per unit). Parent menilai dengan 3-Uji lalu menulis. Alasan: `Pemicu` harus dinilai
   dengan pandangan lintas-unit yang tidak dimiliki subagent.
4. **Indeks sebenarnya adalah `Lokasi`, bukan `Tujuan`.** Saat menulis, agent belum tahu
   seluruh permukaan proyek — daftar `Tujuan` adalah **hipotesis**, bukan himpunan lengkap.
   Karena itu penarikan sinyal wajib berbasis **path file**, bukan ID unit.

---

## Gerbang 3-Uji (wajib lolos ketiganya sebelum ditulis)

| Uji | Pertanyaan | Gagal → |
|---|---|---|
| **Presisi** | Ada `File:Baris` konkret? | buang |
| **Asimetri** | Bisa menyebut *yang seharusnya* vs *yang terjadi*? | buang |
| **Pemicu** | Kondisi terukur apa yang mengubahnya jadi lead? | buang |

"Feels wrong" bukan sinyal. "Modifier dipakai 3 tempat, 1 tempat bypass lewat jalur berbeda"
adalah sinyal.

---

## Lapis 1 — Observasi (ditulis SEKALI, tidak pernah disentuh)

```markdown
## [R-012] Seam tanpa penjaga antar-modul
Lokasi   : WormholeAdapter.sol:340 -> HubPool:918
Domain   : D3 chain-adapters
Tujuan   : S-14, S-22, S-31
Asimetri : payload divalidasi di HubPool, di adapter hanya didekode
Pemicu   : jika ada jalur memanggil HubPool:918 sebelum transfer masuk
Unit Asal: S-08
```

- `Lokasi` — **wajib** `File:Baris`. Ini kunci indeks; tanpa ini sinyal tidak bisa ditemukan kembali.
- `Domain` — domain tempat sinyal ditemukan (bukan domain tujuan).
- `Tujuan` — unit yang **diduga** perlu memeriksa. Boleh tidak lengkap; lihat `TARGET-ADDED`.
- `Asimetri` — wajib menyebut harapan vs kenyataan, bukan opini.
- `Pemicu` — **wajib**. Kondisi konkret, bukan "mungkin nanti berguna".
- `Unit Asal` — unit yang sedang dibedah saat sinyal ditemukan.

---

## Lapis 2 — Kejadian (append, satu baris per perubahan)

```markdown
[R-012/S-14] PROMOTED -> L-19
[R-012/S-14] RESOLVED-REFUTED L-19 -> guard _requireAdminSender ternyata menutup jalur
[R-012/S-22] PROMOTED -> L-31
[R-012/+S-40] TARGET-ADDED lokasi S-40 juga menyentuh HubPool.sol:918
[R-012/S-14] REOPENED -> L-27 pemicu-baru: jalur refund S-31 memanggil HubPool:918 lebih dulu
```

| Kejadian | Kapan |
|---|---|
| `PROMOTED -> L-nn` | sinyal naik jadi lead |
| `RESOLVED-CONFIRMED L-nn` | lead jadi temuan (`09`/`08`) |
| `RESOLVED-REFUTED L-nn -> <alasan 1 baris>` | lead gugur di `06` |
| `TARGET-ADDED` | ditemukan unit lain yang juga relevan |
| `REOPENED -> L-nn` | penolakan dibuka ulang dengan **pemicu berbeda** |
| `EXHAUSTED` | seluruh target sudah `RESOLVED` |

> **`RESOLVED-REFUTED` WAJIB memuat alasan 1 baris.** Ini satu-satunya cara sah menyimpan
> alasan penolakan, karena `AGENTS.md` melarang membaca ulang `06`/`08`. Tanpa alasan di sini,
> unit berikutnya akan mengulang jalan buntu yang sama — atau menunjuk verdict yang tak boleh dibuka.

### Aturan REOPENED
- Wajib **pemicu baru** yang berbeda dari aslinya.
- Wajib **lead ID baru** (`L-27`, bukan `L-19` lagi) — `L-19` sudah punya verdict di `06`.
- Maksimal **2×** per target. Lebih dari itu → tandai `CHURN` dan naikkan jadi unit tersendiri.

---

## Cara Membaca (dua grep, ±150 token)

**Saat MEMULAI unit** — tarik semua sinyal yang menyentuh berkas yang akan dibaca:
```bash
grep -n -B1 -A6 "<nama-berkas>.sol" audit/RADAR.md
```
Ini **jalur yang dijamin**: menemukan sinyal walau `Tujuan`-nya tidak menyebut unit ini.

**Jalur cepat** (bila `Tujuan` sudah benar):
```bash
grep -n -A6 "S-22" audit/RADAR.md
```

**Status terkini per target** — ambil kejadian terakhir:
```bash
grep "\[R-012/S-14\]" audit/RADAR.md | tail -1
```

**Saat MENUTUP unit** — cek pemicu yang mungkin terpenuhi:
```bash
grep -n "Pemicu" audit/RADAR.md
```

---

## Batas & Penutupan

- **Target 10–25 observasi per proyek.** Lebih dari itu = gerbang 3-Uji sedang dilonggarkan.
- Maksimal **2 kandidat per unit**; subagent wajib memilih yang terbaik, bukan menuang semua.
- Entri `EXHAUSTED` hilang dari grep penarikan, tetapi **tetap tersimpan** sebagai jejak audit.
- **Sweep wajib di akhir Putaran 2** (sintesis lintas-unit): saat seluruh `03` sudah diketahui,
  lengkapi `Tujuan` yang terlewat lewat `TARGET-ADDED`.

## Penjaga Integritas

- Entri yang `Lokasi`-nya tersentuh unit lain tetapi **tidak pernah** mendapat baris kejadian
  → itu **bukti sweep gagal**, bukan bukti tidak relevan. Wajib diperiksa satu per satu.
- Entri yang `Tujuan`-nya tidak pernah cocok dan `Lokasi`-nya juga tidak pernah tersentuh
  → aman, cukup `EXHAUSTED`.
- Kode di dalam repo yang ditandai `[STATELESS/INTERFACE]` di `00b` tetapi ternyata reachable
  → sinyal masuk RADAR dengan `Tujuan` unit yang memakainya; bila terbukti, **promosikan
  berkas itu jadi unit baru di `03`** dan catat koreksi inventaris.
