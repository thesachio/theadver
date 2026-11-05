# 05 — Raw Leads (Antrean Aktif → Input Fase 3)

Wadah murni untuk anomali mutasi state, *Patch-Scar*, ketidaksinkronan View-vs-Write, serta **Guard Dinamis/Matematis** (rasio, pembulatan, batas saldo, akumulator waktu/indeks, atau panjang array) yang **wajib diuji secara mekanis** dengan simulasi dan fuzzer di Fase 3. Di sini Anda Pemburu, bukan Hakim: jangan buang anomali kecil, ia bisa dirangkai di Putaran 2 atau diuji amplifikasinya di Fase 3.

Setiap lead (format `## [LEAD-XXX] Judul Singkat` atau `## [L-XX-N] Judul Singkat`) wajib memuat:

```markdown
## [L-V5-1] Judul Singkat Hipotesis & Lokasi
- ID — mis. L-V5-1
- Kelas Topologi — [CLASS-A] | [CLASS-B] | [CLASS-C]
- Metode Pencarian — M-001 .. M-010 (Metode 1 .. Metode 10), dan/atau [POV-XX] dari references/ref-attacker-pov.md. Tanpa kolom ini, Fase 3 tidak dapat merancang harness simulasi yang presisi sesuai Langkah 1b.
- File:Kontrak:Fungsi (Baris) — presisi sampai baris
- Delta State — Expected vs Actual (kerangka Metode 2): state sebelum, aksi, delta yang seharusnya, delta yang benar-benar tertulis di kode
- Urutan Eksploitasi — langkah penyerang, sertakan jumlah identitas/input khusus yang dipakai:
  Metode 3 = 2 identitas/akun/objek/capability dalam 1 jendela eksekusi; Metode 6 = snapshot lokal stale ditulis balik / referensi kembar [A, A]; Metode 7 = N panggilan kecil vs 1 besar; Metode 8 = bypass langsung ke hilir atau seam hulu-hilir tanpa validasi ulang; Metode 9 = tahan di state pending lalu panggil jalur samping; Metode 10 = residual authority/balance atau state drift pasca-upgrade
- Potensi Rantai Serangan (Chaining) — fungsi/lead lain yang bisa disambung
- Status — [OPEN] selama belum diadili Fase 3; setelah Fase 3/4 ganti dengan [STATUS -> 09], [STATUS -> 08], [STATUS -> 07], atau [STATUS -> 06]
- Deployment (Fase 3, WAJIB sebelum harness) — `CYCLE`: P1_PRE_DEPLOY | P2_TESTNET_ONLY | P3_LIVE_PARTIAL | P4_LIVE_FULL | P0_UNKNOWN; `ENTRYPOINT`: LIVE_MATCH | HEAD_ONLY_PROVEN | TESTNET_ONLY | ENTRYPOINT_RELOCATED | ENV_ERROR | IDENTITY_ONLY. Diisi dari artefak `audit/notes/deploy-parity-<ID>.json` (jalankan `verify/tools/deploy_parity.py`). **Bila kosong, `Mode Uji` di Fase 3 tidak sah** — lihat `sc-phase3` Langkah 2b.
```

**Aturan:** lead tanpa `Kelas Topologi`, tanpa `Metode Pencarian`, atau tanpa `Delta State` dikembalikan ke penulisnya, bukan diteruskan ke Fase 3.

**Aturan Deployment:** lead yang akan masuk Fase 3 **wajib** membawa `CYCLE` + `ENTRYPOINT`. Lead tanpa itu tetap boleh berada di `05`, tetapi **DILARANG** dinaikkan ke `09`/`08` — hasil akhirnya maksimum `07` dengan `Disposition: ENV_ERROR`.

> **Gerbang Guard Statis vs Dinamis (rujuk `verify/templates/04-code-guarded.md`):** guard yang ekspresinya melibatkan aritmetika, `mulDiv`, `balanceOf`, `totalAssets`/`totalSupply`, akumulator waktu/indeks, batas LTV/likuidasi, atau panjang array **DILARANG diparkir di `04`** — hipotesisnya **wajib** masuk wadah ini dengan tag `M-005`/`M-007` agar di-fuzz di Fase 3.
