# Sisipan untuk `audit/00-project-map.md` — Seksion §5 (MODEL MEKANISME HIDUP)

> **Cara pakai:** tambahkan blok di bawah ini ke **akhir** `audit/00-project-map.md`
> pada Fase 1 (setelah §4 Invarian Inti). Seksion ini **hidup** — diperbarui selama
> Fase 2/3 dengan `patch` per baris, **bukan** ditulis ulang.

## Mengapa seksion ini ada

`§4 Invarian Inti` ditulis di Fase 1, **sebelum** ada yang benar-benar memahami proyek.
Pemahaman terdalam justru muncul saat membedah unit di Fase 2. Tanpa seksion ini, pemahaman
itu hilang bersama konteks — dan Fase 3 merancang harness dari peta yang sudah basi.

Model ini bukan daftar fakta. Ia harus membuat agent **sensitif** (tahu apa yang seharusnya ada),
**tajam** (bisa memprediksi di mana celah), dan **efisien** (memangkas jalan buntu).

---

## 5. Model Mekanisme Hidup (`patch` per baris; maks 12 baris/domain)

### D1: <nama-domain>
```
ALUR     : <aset bergerak: siapa -> siapa -> siapa>
BATAS    : <siapa boleh memanggil apa; mana yang diasumsikan jujur>
STATE    : <variabel kunci> penulis=<...> pembaca=<...>
INVARIAN : <"X harus selalu Y"> — ditegakkan di <File:Baris> (atau: TIDAK ditegakkan)
INVARIAN : <...>
ANEH     : <hal yang menyimpang dari pola umum / tidak lazim>
ASUMSI   : [A] <asumsi yang belum diverifikasi> — status: BELUM/TERVERIFIKASI/GUGUR
```

### D2: <nama-domain>
```
... (maks 12 baris)
```

---

## Aturan pengisian

1. **`patch` per baris, DILARANG tulis ulang penuh.** Kategori "Edit tabel/baris" di
   `AGENTS.md §1.3.3`. Menulis ulang = risiko terpotong 0 byte.
2. **Maks 12 baris per domain, maks 4 domain aktif.** Kalau lebih, kompres — model yang
   bengkak tidak terbaca, dan model yang tidak terbaca = nol.
3. **`INVARIAN` wajib menyebut lokasi penegaknya** (`File:Baris`) atau eksplisit
   `TIDAK ditegakkan`. Invarian tanpa penegak adalah **kandidat celah**, bukan sekadar catatan.
4. **`ANEH` adalah komponen paling berharga.** Pola yang menyimpang dari kebiasaan umum
   proyek adalah tempat celah paling sering bersembunyi.
5. **`ASUMSI` wajib punya status.** Asumsi `GUGUR` wajib memicu pemeriksaan ulang lead
   yang dibangun di atasnya.
6. **Diperbarui maksimal +3 baris per unit.** Tambahan lebih dari itu = model sedang
   dipaksa menampung hal yang seharusnya jadi lead atau `RADAR`.

---

## Kewajiban penyuntikan (ini yang membuat model berguna)

| Kapan | Perintah | Biaya |
|---|---|---|
Awal setiap unit | baca blok domain unit itu (≈12 baris) | ~250 token |
Setiap `delegate_task` | suntikkan blok domain itu ke `context` (butir 7) | ~250 token |
Setelah unit selesai | `patch` §5 bila model berubah | +≤3 baris |

**DILARANG** membiarkan §5 tanpa pembaruan sepanjang Fase 2 — itu tanda model tidak dipakai,
dan agent kembali menebak dari nol di setiap unit.

---

## Uji ketajaman (falsifiable, bukan retorika)

> **Sebelum** membaca kode unit, tulis prediksi: *"invarian apa yang saya harap ditegakkan di sini,
> dan di mana kemungkinan patah?"*
> **Setelah** selesai, bandingkan.

- Prediksi **tepat** → model sudah cukup tajam; jangan tambah baris.
- Prediksi **meleset** → model kurang; **itulah** yang wajib masuk §5 (biasanya `INVARIAN` atau `ANEH`).

Dengan ini setiap unit mengasah model, dan ketajaman menjadi terukur.
