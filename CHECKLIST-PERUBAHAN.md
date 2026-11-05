# CHECKLIST PERUBAHAN WORKFLOW — Versi Universal

> **Tujuan:** memastikan setiap perubahan aturan workflow dapat ditinjau, diuji, dan dipulihkan
> tanpa bergantung pada ingatan siapa pun, dan tanpa merujuk ke satu proyek tertentu.
>
> **Cara pakai:** satu perubahan = satu entri. Isi SEBELUM mengubah, verifikasi SESUDAH.

---

## BAGIAN 0 — ATURAN PENULISAN (lintas entri)

Agar checklist ini berlaku untuk proyek apa pun, semua contoh **DILARANG** menyebut:

- nama proyek / protokol / kontrak nyata (mis. nama kontrak spesifik, nama validator)
- nama file audit nyata (mis. `08-valid-not-eligible.md` boleh sebagai **nama generik wadah**)
- ID lead / temuan sebagai **rujukan utama** — boleh sebagai lampiran arsip saja
- angka gas, alamat, selector, atau nilai spesifik dari satu run

**Ganti dengan kelas masalah.** Rumusnya: sebut **apa yang bisa salah**, bukan **di mana ia terjadi**.

Contoh bentuk universal (tanpa nama apa pun):
- "fungsi diklaim tidak melakukan X, padahal X ada di tengah fungsi"
- "lead palsu lolos ke antrean dan menghabiskan satu siklus verifikasi"
- "identitas deployment berbeda antara artefak live dan repositori"

**Alasan:** aturan yang menyebut satu proyek akan diabaikan di proyek lain karena dianggap
"tidak relevan di sini", atau lebih buruk — ditafsirkan terlalu sempit.

> Contoh anti-pola (nama spesifik yang harus dihindari) sengaja **tidak** ditulis di sini.
> Lihat **LAMPIRAN A** bila perlu pembanding.

---

## BAGIAN 1 — TEMPLATE ENTRI PERUBAHAN

Salin blok ini untuk setiap perubahan baru.

```
### [U-xx] <Judul singkat, maks 60 karakter>

**Status:** USULAN | DISETUJUI | TERPASANG | TERVERIFIKASI
**Kelas masalah:** <satu kalimat — apa yang bisa salah tanpa aturan ini>

#### 1. KONDISI AWAL (sebelum perubahan)
- Lokasi: <file:baris>
- Bunyi aturan lama: "<kutipan persis>"
- Apa yang DIIZINKAN oleh aturan lama yang seharusnya tidak:
  - <perilaku keliru yang lolos>
- Apa yang DILARANG oleh aturan lama yang seharusnya diizinkan (jika ada):
  - <perilaku sah yang terhambat>

#### 2. PERUBAHAN (apa yang ditambahkan/diganti)
- Jenis: TAMBAH | GANTI | HAPUS
- Lokasi baru: <file:baris>
- Bunyi aturan baru: "<kutipan persis>"
- Panjang: <jumlah baris ditambahkan / dihapus>

#### 3. CEGAHAN BENTURAN (WAJIB — tidak boleh kosong)
Cari semua aturan lain yang menyentuh objek yang sama:
- [ ] Grep kata kunci: `<kata>` di <daftar file>
- [ ] Aturan yang berpotensi berlawanan: <daftar file:baris + bunyinya>
- [ ] Cara keraguan dihilangkan: <batas objek / pengecualian / rujukan silang>

**Aturan yang boleh berlawanan arah** (sengaja) — sebutkan mana:
- <aturan A: arah hemat> vs <aturan B: arah anti-hemat>
- Pemisah: <batas objek eksplisit>

#### 4. UJI KEBERLAKUAN (bukan uji kebenaran)
Tiga pertanyaan; semua harus terjawab YA:
- [ ] Apakah aturan ini bisa dipahami **tanpa membaca proyek asal**?
- [ ] Apakah aturan ini **tidak bisa ditafsirkan** sebagai larangan pada objek lain?
- [ ] Apakah ada **satu kalimat** yang menjelaskan alasannya (bukan hanya perintahnya)?

#### 5. CARA PEMULIHAN
- Backup: <path .bak_pre_*>
- Perintah balik: <satu baris>
- Dampak bila aturan dicabut: <apa yang kembali rentan>

#### 6. VERIFIKASI PASCA-PASANG
- [ ] `grep -n "<penanda unik>"` menemukan tepat 1 kemunculan per file
- [ ] Tidak ada heading duplikat: `grep -c "^## <judul>" == 1`
- [ ] Urutan heading benar (aturan muncul SEBELUM bagian yang diaturnya)
- [ ] Tidak ada file `.tmp` tersisa
- [ ] `version:` dinaikkan bila isi berubah

#### 7. BUKTI JALANKAN (arsip, bukan rujukan utama)
- Proyek asal: <nama> — untuk penelusuran saja, bukan dasar keberlakuan
- Entri arsip terkait: <W-xx / L-xx>
```

---

## BAGIAN 2 — CONTOH TERISI (sudah selesai)

### [U-01] Baca utuh kode fungsi; larangan "baca penuh" dibatasi ke file audit

**Status:** TERVERIFIKASI
**Kelas masalah:** kesimpulan negatif tentang isi fungsi diambil dari cara membaca yang cacat, bukan dari kode.

#### 1. KONDISI AWAL
- Lokasi: `workspace/AGENTS.md:22-23`, `sc-autopilot:30-31`, `sc-phase2-hunt` (tabel metode write)
- Bunyi lama: *"DILARANG memuat satu file penuh."* / *"DILARANG memakai append selalu … memaksa baca penuh."*
- DIIZINKAN padahal salah: penggunaan `grep`/`sed`/`head`/`tail` sebagai dasar menyimpulkan isi fungsi, termasuk membuktikan klaim negatif ("X tidak ada", "Y tidak dipanggil").
- DILARANG padahal sah: **tidak ada** — tapi akibatnya, larangan hemat konteks terbaca sebagai larangan umum, sehingga kode pun dibaca sebagian.

#### 2. PERUBAHAN
- Jenis: **TAMBAH** (4 blok) + **GANTI** (2 kalimat larangan agar menyebut objeknya)
- Lokasi baru:
  - `AGENTS.md` — Langkah C diperjelas + blok ⚠️ BATAS OBJEK
  - `sc-autopilot` — Langkah C/D diperjelas
  - `sc-phase2-hunt` — ⚠️ BATAS OBJEK tabel + §A0 Pembacaan Wajib Penuh
  - `sc-phase3` — Langkah 0e Re-Read Pass Bersyarat
- Isi inti (universal): *kode sumber WAJIB dibaca utuh dari `function` sampai `}` penyeimbang; `grep`/`sed`/`head`/`tail` hanya untuk menemukan lokasi, dilarang menyimpulkan isi atau membuktikan klaim negatif.*

#### 3. CEGAHAN BENTURAN
- [x] Grep kata kunci: `baca penuh`, `DILARANG memuat`, `grep`, `sed`, `head`, `tail`, `offset`, `limit` di seluruh `skills/security/*/SKILL.md`, `workspace/AGENTS.md`, `verify/VERDICT.md`
- [x] Aturan berlawanan ditemukan: **5 kemunculan** larangan "baca penuh" di `sc-phase2-hunt` (tabel metode write) + 2 di `AGENTS.md`
- [x] Keraguan dihilangkan: setiap larangan kini menyebut objeknya (**FILE AUDIT**) + blok ⚠️ BATAS OBJEK

**Aturan yang sengaja berlawanan arah:**
- **Hemat-token** (file audit) vs **Anti-hemat** (kode kontrak)
- Pemisah: batas objek eksplisit di 3 file + kalimat alasan ("melindungi file audit yang tumbuh besar" vs "melindungi pemahaman kode yang bisa hancur oleh potongan")

#### 4. UJI KEBERLAKUAN
- [x] Bisa dipahami tanpa proyek asal — **ya**, tidak menyebut kontrak/protokol mana pun
- [x] Tidak bisa ditafsirkan ke objek lain — **ya**, batas objek menyebut path konkret (`source/`, `contracts/`, `src/`, `programs/`)
- [x] Ada satu kalimat alasan — **ya**, tertulis di blok alasan

#### 5. CARA PEMULIHAN
- Backup: `SKILL.md.bak_pre_*` (3 file) + `AGENTS.md.bak_pre_batas_objek`
- Perintah balik: `cp <file>.bak_pre_batas_objek <file>`
- Dampak bila dicabut: kesimpulan negatif dari potongan kode kembali sah → lead palsu dapat lahir lagi

#### 6. VERIFIKASI PASCA-PASANG
- [x] `grep -n "BATAS OBJEK"` = tepat 1 per file, di 3 file
- [x] Tidak ada heading duplikat
- [x] Urutan benar: §A0 sebelum Tahap A; Langkah 0e sebelum Langkah 1; Langkah 2c sebelum Langkah 3
- [x] Tidak ada `.tmp` tersisa
- [ ] `version:` dinaikkan — **BELUM** (`6.3.0`)

#### 7. BUKTI JALANKAN
- Arsip: `WORKFLOW-KOREKSI.md` W-12, W-15 — rujukan penelusuran saja

---

## BAGIAN 2b — STATUS KEPUTUSAN PER BLOK

| Blok | Lokasi | Isi | Keputusan |
|---|---|---|---|
| 1 | `AGENTS.md:22` | GANTI "file penuh" → "FILE AUDIT penuh" | ✅ DISETUJUI |
| 2 | `AGENTS.md:25-32` | TAMBAH ⚠️ BATAS OBJEK Langkah C/D | ✅ DISETUJUI |
| 3 | `AGENTS.md:87-114` | TAMBAH Pasal 1.4 Integritas Bukti (`FABRICATED_EVIDENCE`) | ✅ DISETUJUI |
| 4 | `sc-autopilot:30-33` | GANTI+TAMBAH batas objek + pengecualian Langkah D | ✅ DISETUJUI |
| 5 | `sc-phase2-hunt:51-52` | TAMBAH ⚠️ BATAS OBJEK tabel metode write | ✅ DISETUJUI |
| 6 | `sc-phase2-hunt:143-162` | TAMBAH §A0 Pembacaan Wajib Penuh | ✅ DISETUJUI |
| 7 | `sc-phase3:139-160` | TAMBAH Langkah 0e Re-Read Pass Bersyarat | ✅ DISETUJUI |
| 8 | `sc-phase3:294-317` | TAMBAH Langkah 2c Kontrol Positif | ✅ DISETUJUI |
| 9 | `sc-phase4:15-33` | TAMBAH Langkah 0 Teknik Bukti Deployment | ⏸ MENUNGGU |

**Catatan asal-usul:** blok 1-8 berasal dari sesi yang sama (aturan baca utuh + integritas bukti +
kontrol positif). Blok 9 berasal dari patch tertunda tanggal lebih awal dan **belum** diputuskan.

---

## BAGIAN 3 — DAFTAR PERIKSA RINGKAS (untuk perubahan berikutnya)

Sebelum menyentuh file apa pun:

- [ ] Kelas masalah sudah ditulis **satu kalimat**, tanpa nama proyek
- [ ] Bunyi aturan lama dikutip **persis** (bukan dari ingatan)
- [ ] Grep kata kunci sudah dijalankan di **seluruh** file aturan, bukan hanya yang diingat
- [ ] Aturan berlawanan dicatat **beserta cara pemisahannya**
- [ ] Backup dibuat **sebelum** mutasi
- [ ] Tulis atomik (`.tmp` → `fsync` → `os.replace`)
- [ ] Verifikasi: `grep -n` posisi, heading tidak duplikat, urutan benar

Sesudah:

- [ ] Versi dinaikkan
- [ ] Sinkronisasi ke repo dilakukan **per perubahan**, bukan menumpuk
- [ ] Entri checklist diisi sampai bagian 6

---

## LAMPIRAN A — Uji anti-kontaminasi

Sebelum menyimpan perubahan workflow, jalankan tiga pemeriksaan ini:

```bash
# 1. Nama proyek / protokol / kontrak
grep -rniE "<nama-proyek>|<nama-kontrak>" skills/ workspace/

# 2. ID lead atau temuan dari run tertentu
grep -rnE "\b[A-Z]-[0-9]{2,}\b" skills/ workspace/

# 3. Path atau berkas milik satu proyek (nama lab, nama folder notes khusus)
grep -rnE "/(lab|poc|notes)/[a-z0-9_-]+" skills/ workspace/
```

**Ambang:** hasil **harus 0** untuk pemeriksaan 1 dan 3. Pemeriksaan 2 boleh
menghasilkan **placeholder** (`<ID>`, `L-xx`) tetapi **bukan** ID nyata.

**Bila ada yang lolos:** ganti dengan kelas masalah. Contoh rumus — sebut **apa yang bisa
salah**, bukan **di mana ia terjadi**:
- "fungsi diklaim tidak melakukan X, padahal X ada di tengah fungsi"
- "lead palsu lolos ke antrean dan menghabiskan satu siklus verifikasi"
- "identitas deployment berbeda antara artefak live dan repositori"
- "blok bukti memuat nama test yang tidak pernah dijalankan"

> **Mengapa tanpa contoh nama:** lampiran yang "hanya sebagai pembanding" tetap menanam nama
> proyek ke dalam repo workflow, dan pembaca berikutnya akan menyalinnya tanpa sadar bahwa itu
> contoh. Repo workflow harus bersih dari konteks proyek mana pun.
