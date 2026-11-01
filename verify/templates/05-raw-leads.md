# 05 — Raw Leads (Antrean Aktif → Input Fase 3)

Wadah murni untuk anomali mutasi state / *Patch-Scar* / ketidaksinkronan View-vs-Write yang **belum terhalang
guard kode**. Di sini Anda Pemburu, bukan Hakim: jangan buang anomali kecil, ia bisa dirangkai di Putaran 2
atau diuji amplifikasinya di Fase 3.

Setiap lead (format `LEAD-XXX` atau `L-XX-N`) wajib memuat:

- `ID` — mis. `L-V5-1`
- `Metode Pencarian` — `Metode 1` .. `Metode 5`, dan/atau `[POV-XX]` dari `references/ref-attacker-pov.md`.
  Tanpa kolom ini, Fase 3 tidak bisa memilih uji termurah (lihat Langkah 0 Fase 3).
- `File:Kontrak:Fungsi (Baris)` — presisi sampai baris
- `Delta State` — `Expected vs Actual` (kerangka Metode 2): state sebelum, aksi, delta yang seharusnya,
  delta yang benar-benar tertulis di kode
- `Urutan Eksploitasi` — langkah penyerang, sertakan jumlah dompet yang dipakai (`Metode 3` = 2 dompet, 1 tx)
- `Potensi Rantai Serangan (Chaining)` — fungsi/lead lain yang bisa disambung
- `Status` — `[OPEN]` selama belum diadili Fase 3; setelah Fase 3/4 ganti dengan
  `[STATUS -> 09]`, `[STATUS -> 08]`, `[STATUS -> 07]`, atau `[STATUS -> 06]`

Aturan: lead tanpa `Metode Pencarian` atau tanpa `Delta State` dikembalikan ke penulisnya, bukan diteruskan ke Fase 3.
