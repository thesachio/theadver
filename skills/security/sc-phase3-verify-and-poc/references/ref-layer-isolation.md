# Anti-Salah-Alamat: Isolasi Lapisan Sebelum Menyalahkan Target

**Hukum Dasar:** sebelum menyatakan *tool rusak*, *target rentan*, atau *vendor tidak mendukung*, wajib membuktikan **lapisan mana** yang gagal. Kegagalan pada rantai `kode → dependency → kompiler → toolchain → emulasi → OS/disk` hampir selalu berada di lapisan **paling bawah** yang belum diperiksa, bukan di yang paling terlihat.

## 1. Tangga Isolasi Lapisan (wajib berurutan, dari bawah)

| # | Lapisan | Cara membuktikan |
|---|---|---|
| 1 | **Disk & ruang** | `df -h` pada path kerja. Path di `/tmp` sering **tmpfs (RAM)** — wajib cek `df -h /tmp` sebelum ekstraksi >500 MB |
| 2 | **Arsitektur** | `file` pada **setiap** binari. Aarch64 ≠ x86_64 ≠ SBF ≠ WASM. DILARANG membandingkan lintas arsitektur |
| 3 | **Library dinamis** | `ldd <bin>`; error `cannot open shared object file` = paket `:amd64`/`:arm64` belum ada, bukan tool rusak |
| 4 | **Kompiler anak** | `cc`/`ar`/`linker` mana yang dipanggil? `-m64` ditolak = gcc arsitektur salah; perlu shim, bukan menimpa PATH global |
| 5 | **Integritas artefak** | Bandingkan ukuran **header vs file** (arsip: `ar t`; JSON: `jq .`; .so: `readelf -S`). "File terpotong" sering menyamar sebagai "tool tidak kompatibel" |
| 6 | **Kapasitas memori** | `free -h` sebelum build besar. `via_ir`/LTO bisa butuh 2–4 GB per invokasi |
| 7 | **Kode target** | **BARU** setelah 1–6 terbukti sehat, boleh menuduh kode |

## 2. Larangan Menyalahkan Alat Sebelum Membuktikan Disiplinnya

DILARANG menulis "bug X", "tidak didukung Y", atau "tidak ada workaround" bila belum ada **satu** dari:
- log `df`/`free`/`ldd`/`file` yang membuktikan lapisan bawah sehat,
- reproduksi terisolasi (1 file, 1 perintah) yang gagal **tanpa** melibatkan kode target,
- pembanding yang berhasil (eksperimen kontrol).

**Contoh nyata pelanggaran:** menyimpulkan *"emulator salah membaca arsip"* padahal empat dari lima arsip lain utuh dan yang satu terpotong — bukti justru menunjuk ke **ruang disk**, bukan emulator.

## 3. Aturan Eksperimen Kontrol

Setiap kali ada kegagalan kompilasi/build:
1. **Eksperimen gagal**: reproduksi minimal (1 file terkecil yang gagal).
2. **Eksperimen kontrol**: file yang **seharusnya berhasil** dengan tool yang sama.
3. Bandingkan. Jika kontrol juga gagal → masalah **tool/lingkungan**. Jika kontrol berhasil → masalah **kode/dependency**.

"build repo penuh gagal" tanpa kontrol **tidak** membuktikan tool rusak — bisa jadi hanya OOM atau satu modul.

## 4. Larangan Generalisasi Satu Kegagalan

DILARANG menyimpulkan status lingkungan dari **satu** invokasi. Wajib:
- ulang setelah memperbaiki lapisan bawah,
- uji pada minimal **dua** target berbeda (satu kecil, satu sedang),
- catat perbedaan hasilnya.

## 5. Kewajiban Mencatat Kegagalan Lingkungan

Setiap kegagalan yang bukan kesalahan kode target **wajib** dicatat di `audit/notes/` dengan 5 kolom:

| Gejala | Hipotesis awal | **Bukti lapisan** | Penyebab nyata | Perbaikan |
|---|---|---|---|---|

Tanpa kolom **bukti lapisan**, catatan ditolak.

## 6. Empat Kasus Nyata (rujukan pola)

| Gejala | Diagnosis salah | Penyebab nyata | Lapisan |
|---|---|---|---|
| "emulator salah baca arsip" | tool tidak kompatibel | `/tmp` tmpfs 2,9 GB penuh → ekstraksi terpotong | 1 (disk) |
| CLI mati tanpa pesan jelas | binari rusak | `libudev.so.1` x86_64 belum ada | 3 (library) |
| `cc: unrecognized '-m64'` | toolchain rusak | gcc ARM terpanggil untuk target x86_64 | 4 (kompiler anak) |
| `forge build` EXIT=143 | kode gagal kompilasi | OOM: RAM 5,8 GB + `via_ir` + 450 file | 6 (memori) |
| "1,46× = kode berbeda" | ada modul tersembunyi | membandingkan aarch64 vs SBF | 2 (arsitektur) |
| "selektor hilang di produksi" | kode produksi beda | grep hex tanpa normalisasi padding | 5 (integritas) |

**Pola tunggal:** menyimpulkan dari satu lapisan tanpa memeriksa lapisan di bawahnya. Berujung vonis teknis yang salah alamat.
