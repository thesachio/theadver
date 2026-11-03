# 05 — Raw Leads (Antrean Aktif → Input Fase 3)

Wadah murni untuk anomali mutasi state / *Patch-Scar* / ketidaksinkronan View-vs-Write yang **belum terhalang
guard kode**. Di sini Anda Pemburu, bukan Hakim: jangan buang anomali kecil, ia bisa dirangkai di Putaran 2
atau diuji amplifikasinya di Fase 3.

Setiap lead (format `LEAD-XXX` atau `L-XX-N`) wajib memuat:

- `ID` — mis. `L-V5-1`
- `Kelas Topologi` — `[CLASS-A]` (Single-Entity) | `[CLASS-B]` (Dual-Entity) | `[CLASS-C]` (Multi-Entity Long Flow)
- `Metode Pencarian` — `M-001` .. `M-NNN` (atau `Metode 1` .. `Metode N`) dari `references/ref-method-registry.md`,
  dan/atau `[POV-XX]` dari `references/ref-attacker-pov.md`. Tanpa kolom ini, Fase 3 tidak bisa memilih uji termurah
  (lihat Langkah 0 Fase 3).
- `File:Kontrak:Fungsi (Baris)` — presisi sampai baris
- `Delta State` — `Expected vs Actual` (kerangka Metode 2): state sebelum, aksi, delta yang seharusnya,
  delta yang benar-benar tertulis di kode
- `Urutan Eksploitasi` — langkah penyerang (chain-neutral, berlaku EVM/Solana/Move/TON), sertakan jumlah
  identitas/objek/input khusus yang dipakai:
  `M-003`/`Metode 3` = >=2 identitas/akun/objek/capability dalam jendela eksekusi yang sama;
  `M-006`/`Metode 6` = stale local-snapshot write-back atau duplicate reference `[A, A]`;
  `M-007`/`Metode 7` = N panggilan kecil vs 1 besar;
  `M-008`/`Metode 8` = bypass langsung ke hilir atau unvalidated caller-callee seam;
  `M-009`/`Metode 9` = tahan di state pending/in-flight lalu panggil jalur samping
- `Potensi Rantai Serangan (Chaining)` — fungsi/lead lain yang bisa disambung
- `Status` — `[OPEN]` selama belum diadili Fase 3; setelah Fase 3/4 ganti dengan
  `[STATUS -> 09]`, `[STATUS -> 08]`, `[STATUS -> 07]`, atau `[STATUS -> 06]`

Aturan: lead tanpa `Kelas Topologi`, tanpa `Metode Pencarian`, atau tanpa `Delta State` dikembalikan ke penulisnya, bukan diteruskan ke Fase 3.
