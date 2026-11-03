# Single-Source Counter-Auditor Method Registry (`M-001` .. `M-NNN`)

Berkas ini adalah **pusat kendali tunggal (Plug-and-Play Registry)** untuk seluruh Metode Pencarian Kerentanan di Fase 2 dan Routing Uji Cepat Pra-PoC di Fase 3.
- **Aturan Penamaan Kompatibel:** Setiap metode memiliki ID stabil `M-00X` dan nama alias `Metode X` (keduanya sah ditulis di `audit/05-raw-leads.md` dan `audit/03-attack-surface-queue.md`).
- **Cara Menambah Metode Baru (`M-011`, dst.):** Cukup tambahkan 1 blok metode baru di bagian bawah berkas ini dan daftarkan ke Tabel Matriks Kelas di Bagian 1. Anda **TIDAK PERLU** mengubah `sc-phase2-hunt`, `sc-phase3-verify-and-poc`, `sc-autopilot`, atau `AGENTS.md`.

---

## 1. Kontrak Kelas Topologi Entitas (`CLASS-A`, `CLASS-B`, `CLASS-C`) & Matriks Routing Metode

Kelas ditentukan murni berdasarkan **jumlah entitas yang berinteraksi dan panjang alur eksekusi on-chain** pada unit `S-n`, **BUKAN** berdasarkan tingkat keparahan (severity) atau ukuran EV:

| Kelas Topologi | Definisi Boundary Entitas & Alur Eksekusi | Aturan Eksekusi Fase 2 | Paket Metode Wajib Minimum |
|---|---|---|---|
| **`[CLASS-A]`** *(Single-Entity Flow)* | **Satu entitas mandiri** memproses state, validasi guard, kalkulasi, dan transisi alur secara tertutup tanpa ketergantungan panggilan ke entitas lain. | **1 Pass Tajam Tuntas (*Single-Pass Deep Kill*):** Seluruh guard diuji *inline* saat itu juga karena variabel pembentuknya berada di entitas yang sama. | `M-001`, `M-002`, `M-004` *(View-vs-Write & Patch-Scar lokal)*, `M-005` *(Inline Guard-Inversion)*, `M-006` *(Prinsip B: Duplicate Reference `[A,A]`)*, `M-007`, `M-009` *(bila ada state pending lokal)* |
| **`[CLASS-B]`** *(Dual-Entity Interaction)* | **Dua entitas berinteraksi langsung** dalam satu jalur/jendela eksekusi (Kontrak Hulu $\leftrightarrow$ Hilir, Kontrak $\leftrightarrow$ Callback, Program $\leftrightarrow$ Target CPI, atau Akun A $\leftrightarrow$ Akun B). | Bedah internal tiap entitas **ditambah** bedah sambungan, asumsi caller-callee, callback, dan adu state 2 identitas. | Seluruh metode relevan `CLASS-A` + `M-003`, `M-006` *(Prinsip A: Stale Snapshot Write-Back & Prinsip B)*, `M-008`, `M-010` *(Residual Authority/Balance)* |
| **`[CLASS-C]`** *(Multi-Entity Long On-Chain Flow)* | **Tiga atau lebih entitas berinteraksi berantai** dalam alur on-chain panjang, lintas-domain, multi-hop (`User -> Router -> Pool -> Strategy -> Oracle/DEX/Bridge`), PTB kompleks, atau pesan asinkron. | Bedah paket penuh 100% metode dengan fokus pada rantai komposisi panjang, state menggantung lintas-modul, dan drift konfigurasi sistemik. | **Paket Penuh (`M-001` s/d `M-010`..`M-NNN`)** dengan penekanan khusus pada `M-003`, `M-004`, `M-005` *(Cross-Contract)*, `M-008`, `M-009`, `M-010` |

> **Catatan Anti-Low-Rate Reasoning:** `CLASS-A < CLASS-B < CLASS-C` hanya menunjukkan kompleksitas jumlah entitas, **bukan kasta nilai uang (EV)**. Satu kontrak vault mandiri di `CLASS-A` dapat memegang 100% TVL protokol.

---

## 2. Fondasi Wajib Sebelum Menjalankan Metode Apa Pun

Saat membedah setiap fungsi di unit antrean, selalu substitusikan **4 Kondisi Batas Konkret**:
1. Likuiditas realistis tanpa ilusi `totalSupply == 0` pada pool yang sudah *live* di produksi;
2. Batas bawah `0`, `1` unit terkecil (1 wei / 1 lamport / 1 mist), dan `batas_minimum - 1`;
3. Blok atau jendela waktu yang sama ($\Delta t = 0$);
4. Entitas kembar (`sender == recipient`, `source == destination`, `target == address(this)`, atau objek/akun yang sama dikirim dua kali);

terhadap **5 Primitif Universal**: (1) Kuantisasi Proporsi, (2) Transisi Paksa & Sabotase DoS, (3) Replay Otoritas/Signature, (4) Penyerahan Kontrol Eksekusi, dan (5) Lompatan Mesin Status.

---

## 3. Katalog Lengkap Metode Counter-Auditor (`M-001` s/d `M-010`)

### [M-001] / Metode 1 — Backward Sink-to-Source Tracing (Kebalikan Arah Baca Auditor)
- **Target Kelas:** `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]`
- **Prinsip Mekanis (Chain-Neutral):** Auditor standar membaca fungsi dari baris paling atas (validasi/guard) ke bawah sehingga mudah terhipnotis bahwa fungsi sudah terlindungi. Anda WAJIB membalik arah baca dari titik pengeluaran nilai paling bawah (*The Sink*) mundur ke atas (*The Source*).
- **Prosedur Bedah Fase 2:**
  1. Cari **Titik Kritis di Bawah (*The Sink*)**: baris pengiriman token/koin/aset/objek, pencetakan hak/share, penghapusan utang/kewajiban, atau penyitaan jaminan.
  2. Lacak mundur ke atas (*backward*) setiap variabel pembentuk angka di *Sink* tersebut: *"Bagaimana cara memperbesar angka yang keluar di Sink sambil memperkecil pengorbanan di Source menggunakan input yang diizinkan pada 3 Kasta Aset di `01-threat-and-env.md`?"*
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - `M-001` adalah metode pembacaan alur. Pastikan jalur dari *Source* ke *Sink* yang diklaim benar-benar dapat dicapai tanpa melanggar 4 Kemustahilan Fakta Dasar (Langkah 1c Fase 3).

---

### [M-002] / Metode 2 — State-Transition Differential Analysis (Expected vs. Actual Delta)
- **Target Kelas:** `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]`
- **Prinsip Mekanis (Chain-Neutral):** Setiap mutasi state harus menjaga keseimbangan antara perubahan hak dan perubahan kewajiban di seluruh variabel yang berpasangan (baik di dalam 1 entitas maupun lintas-entitas).
- **Prosedur Bedah Fase 2:**
  1. Untuk setiap aksi atau pasangan aksi (Masuk/Buat vs Keluar/Batal/Transfer/Sita dari `02-state-and-var-matrix.md`), bandingkan perubahan state yang seharusnya terjadi secara ekonomi vs yang benar-benar tertulis di kode:
     `State Awal -> Aksi -> Delta Ekspektasi (Hak vs Kewajiban) vs Delta Aktual di Kode -> Selisih Variabel yang Tidak Sinkron`.
  2. Periksa apakah ada variabel global yang berubah tanpa memperbarui variabel akun/posisi (atau sebaliknya), indeks akrual yang terlambat disinkronkan satu langkah, atau operasi batal/klaim sebagian yang lupa me-reset salah satu field.
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - Verifikasi langsung pada baris kode yang dikutip apakah variabel yang diklaim "lupa di-update/di-reset" memang tidak diperbarui di fungsi helper/internal/modifier yang dipanggil oleh transaksi tersebut. Jika sebenarnya sudah diperbarui di sub-fungsi -> gugur ke `06` (`REJECTED_MISMATCH`).

---
### [M-003] / Metode 3 — Irrational Multi-Identity Sybil & Zero-Time Loop
- **Target Kelas:** `[CLASS-B]`, `[CLASS-C]` *(serta `[CLASS-A]` bila kontrak memiliki fitur transfer/interaksi antar-akun internal)*
- **Prinsip Mekanis (Chain-Neutral — Anti-Lexical-Overfitting):**
  Jangan pernah menyempitkan metode ini hanya sebagai "dua EOA / dua wallet". Prinsip mekanis sebenarnya adalah:
  > **Dua atau lebih identitas, akun, objek, capability, atau kontrak yang dikendalikan satu penyerang dan dapat berinteraksi secara atomik atau dalam jendela eksekusi yang sama ($\Delta t = 0$), di mana kerugian pada satu identitas dikompensasi oleh keuntungan yang lebih besar pada identitas lainnya.**
- **Manifestasi Lintas-Paradigma:**
  - *EVM / Tron:* Dua EOA atau kontrak pembantu (`Attacker_A`, `Attacker_B`) dalam satu transaksi atau batch.
  - *Solana:* Dua signer, atau satu signer yang mengendalikan beberapa account / account alias dalam satu instruksi/transaksi.
  - *Move (Sui/Aptos):* Dua capability, dua posisi, atau dua object milik satu owner yang dioperasikan di dalam satu Programmable Transaction Block (PTB).
  - *TON:* Dua actor atau dua jalur pesan (*message path*) yang dikendalikan satu penyerang terhadap target yang sama.
- **Prosedur Bedah Fase 2:**
  1. **Self-Transfer & Ping-Pong Loop:** Apa yang terjadi jika identitas pertama memindahkan/mendelegasikan hak ke dirinya sendiri (`from == to`) atau memantulkannya `A -> B -> A` berulang kali dalam jendela eksekusi yang sama ($\Delta t = 0$)?
  2. **Self-Liquidation / Self-Penalty Arbitrage:** Apa yang terjadi jika identitas pertama sengaja membuat posisinya terkena likuidasi/slashing/lelang/bad-debt, sementara identitas kedua bertindak sebagai likuidator/penawar yang memanen bonus atau mengalihkan kerugian (*bad debt socialization*) ke kolam publik?
  3. **Zero / Boundary & Dust Amplification:** Masukkan nilai `0`, `1` unit terkecil, atau `batas_minimum - 1` antar-identitas untuk menguji apakah biaya/penalti terpotong jadi `0` karena pembulatan dan dapat di-loop.
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - PoC untuk `M-003` **WAJIB** menghadirkan minimal dua identitas/akun/objek/capability yang dikendalikan penyerang dalam satu jendela eksekusi (PoC satu identitas yang gagal tidak membuktikan gugurnya hipotesis multi-identitas).
  - Untuk sub-kasus *Self-Liquidation / Bad-Debt*, hitung dulu pertidaksamaan `Total_Jaminan_Tersita >= Bonus_Pelikuidasi + Utang_Dihapus` dengan parameter live; bila ruas kiri selalu lebih besar di semua kondisi batas -> `Negative-EV`, langsung ke `06`.

---
### [M-004] / Metode 4 — Patch-Scar, Periphery, & View-vs-Write Asymmetry
- **Target Kelas:** `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]`
- **Prinsip Mekanis (Chain-Neutral):** Auditor lelah saat memeriksa jalur periferal dan fungsi pembacaan (`view`/`preview`). Tambalan keamanan (*patch-scar*) atau pemotongan biaya yang dipasang di jalur utama sering terlupa di jalur sampingan atau berbeda rumusnya antara fungsi baca vs fungsi tulis.
- **Prosedur Bedah Fase 2:**
  1. **Bedah *Patch-Scar* (Bekas Tambalan):** Jika fungsi utama memiliki `if`/`require`/`assert!` khusus yang terlihat seperti tambalan audit (rujuk `01-threat-and-env.md` dan riwayat laporan di `audit/INTEL.md`), periksa apakah jalur sampingan (`transfer`, `migrate`, `rescue`, `sweep`, `emergencyWithdraw`, `batch`, hook/callback) yang menyentuh variabel yang sama lupa dipasang tambalan tersebut.
  2. **Desinkronisasi Rumus `View` vs `Write`:** Bandingkan baris demi baris rumus di fungsi `view`/`preview`/getter dengan fungsi tulis pasangannya di `02-state-and-var-matrix.md` (misal: perbedaan arah pembulatan `mulDivDown` vs `mulDivUp`, atau biaya yang dihitung di preview tetapi tidak dipotong di eksekusi).
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - Jika klaim berupa desinkronisasi `View` vs `Write`, periksa apakah ada fungsi tulis/eksternal (di kontrak itu atau kontrak pasangan) yang **benar-benar memanggil fungsi `view` tersebut untuk keputusan finansial** (pencetakan share, batas pinjaman, harga likuidasi). Jika fungsi `view` itu murni hanya untuk tampilan UI front-end tanpa menyentuh eksekusi on-chain -> buang ke `06` atau `08`.

---

### [M-005] / Metode 5 — Guard-Inversion (Membalik Guard Kode Menjadi Target Manipulasi)
- **Target Kelas:** `[CLASS-A]` *(Inline Lokal)*, `[CLASS-B]` *(Antar-2 Entitas)*, `[CLASS-C]` *(Lintas-Protokol/Alur Panjang)*
- **Prinsip Mekanis (Chain-Neutral):** Guard (`require`, `if (...) revert`, `assert!`, `constraint`) bukanlah tembok mati, melainkan rumus yang bergantung pada variabel pembentuknya. Jika variabel pembentuknya dapat digeser sebelum guard dieksekusi, guard tersebut dapat ditembus atau justru dipakai sebagai senjata DoS terhadap pengguna lain.
- **Prosedur Bedah Fase 2:**
  1. Setiap kali menemukan `require(Kondisi_X >= Kondisi_Y)` atau `if (...) revert`: identifikasi seluruh variabel yang menyusun `Kondisi_X` dan `Kondisi_Y`.
  2. Berdasarkan `02-state-and-var-matrix.md`, periksa: bisakah fungsi publik lain (di entitas yang sama pada `CLASS-A`, atau melalui entitas lain/flashloan/donasi/callback pada `CLASS-B/C`) mengubah nilai `X` atau `Y` sesaat sebelum baris guard ini dieksekusi?
  3. Untuk guard yang ditampung di `audit/04-code-guarded.md`, gunakan metode ini secara khusus untuk membongkar apakah guard tersebut dapat ditembus lintas-entitas.
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - Cek di `02-state-and-var-matrix.md` daftar penulis variabel pembentuk guard tersebut. Jika seluruh penulisnya terkunci `onlyAdmin`/`onlyOwner` dan tidak dipengaruhi oleh saldo/rasio eksternal yang bisa digeser publik -> gugur ke `06` (`REJECTED_PRIVILEGED_FANTASY` / `REJECTED_BY_DESIGN`).

---
### [M-006] / Metode 6 — Stale Local-Snapshot Write-Back & Duplicate-Reference Aliasing (`[A, A]`)
- **Target Kelas:** `[CLASS-A]` *(Prinsip B)*, `[CLASS-B]` & `[CLASS-C]` *(Prinsip A & B)*
- **Prinsip Mekanis (Chain-Neutral — Anti-Lexical-Overfitting):**
  Pisahkan secara tegas antara **prinsip mekanis universal** dan **istilah implementasi bahasa** (`memory`/`storage` adalah istilah Solidity/EVM, bukan prinsipnya):
  - **Prinsip A — Snapshot Lokal yang Stale Ditulis Kembali:**
    > **Snapshot lokal yang stale ditulis kembali setelah interaksi eksternal/lintas-komponen, sehingga perubahan terbaru pada state persisten terhapus secara senyap.**
    *(Urutan yang dicari: **baca ke variabel lokal -> mutasi state persisten via subcall/CPI/callback/fungsi lain -> tulis balik variabel lokal lama ke state persisten**).*
  - **Prinsip B — Referensi Kembar Diproses Dua Kali (`[A, A]`):**
    > **Dua argumen atau elemen daftar yang menunjuk ke identitas/akun/objek/resource yang sama diproses berulang sebelum state dimutasi atau tanpa deduplikasi.**
- **Manifestasi Lintas-Paradigma:**
  - *EVM / Tron:* (A) `Struct memory s = map[user]` -> panggilan keluar mengubah `map[user]` -> `map[user] = s`; (B) array input `[id, id]` atau `(from, to)` dengan alamat sama.
  - *Solana:* (A) Account data dideserialisasi sebelum CPI, lalu dipakai/ditulis balik setelah CPI tanpa `.reload()`; (B) duplicate writable account atau repeated `ctx.remaining_accounts`.
  - *Move (Sui/Aptos):* (A) Nilai objek/field dibaca ke variabel lokal sebelum memanggil modul lain, lalu menimpa field objek di akhir; (B) duplicate object reference atau duplicate recipient di dalam PTB/vector.
  - *TON:* (A) State dibaca sebelum rantai pesan mengubahnya lalu ditimpa kembali; (B) duplicate actor/message entry.
- **Prosedur Bedah Fase 2:**
  1. Cari fungsi yang menyalin struktur/saldo ke variabel lokal, melakukan panggilan keluar / memanggil helper yang memutasi state yang sama, lalu menulis balik salinan lokal ke state persisten di akhir fungsi.
  2. Pada setiap fungsi yang menerima >= 2 akun/objek atau parameter daftar/array, uji input dengan referensi kembar `[A, A]`. Periksa apakah ada pemeriksaan ketidaksetaraan / deduplikasi sebelum mutasi.
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - Untuk **Prinsip A**: pastikan urutan *baca-lokal -> mutasi-persisten -> tulis-balik* benar-benar terjadi di kode; jika tidak ada penulisan balik setelah interaksi -> gugur ke `06`.
  - Untuk **Prinsip B**: cek apakah sudah ada deduplikasi ketat (`ids[i] < ids[i+1]`, bitmap, atau constraint `account_a.key() != account_b.key()`); jika sudah ada -> `06`; jika belum -> PoC cukup 1 transaksi dengan input kembar `[A, A]`.

---

### [M-007] / Metode 7 — Metamorphic Split-vs-Bulk Asymmetry ($f(a + b) \neq f(a) + f(b)$)
- **Target Kelas:** `[CLASS-A]`, `[CLASS-B]`, `[CLASS-C]`
- **Prinsip Mekanis (Chain-Neutral):** Auditor menguji rumus dengan 1 angka tunggal. Anda WAJIB menguji apakah rumus bersifat non-linear ketika input dipecah menjadi potongan kecil atau digabung menjadi satu gelombang besar dalam 1 jendela eksekusi:
- **Prosedur Bedah Fase 2:**
  1. **Salami Slicing (Pecah Jadi $N$ Potongan Kecil):** Bandingkan 1 panggilan `aksi(1000)` vs 100 panggilan `aksi(10)`. Jika biaya/utang/share yang dibakar menggunakan pembulatan ke bawah (*round down* / *floor*), memecah transaksi dapat membuat kewajiban terpotong menjadi `0` atau berkurang 1 unit di setiap iterasi.
  2. **Bulk Consolidation (Gabung via Flashloan Lalu Pecah):** Bandingkan eksekusi terpisah vs menggabungkan likuiditas/posisi sesaat pada titik perhitungan bagi-hasil/reward/tier, lalu memecahnya kembali di blok yang sama.
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - Hitung selisih maksimum `N x aksi(kecil)` vs `1 x aksi(besar)` dalam batas gas/komputasi 1 blok (dan setelah melewati 3-Way EV Amplification: *Flashloan + Looping + Chaining*). Jika total selisih maksimum tetap lebih kecil dari biaya gas + fee protokol -> `REJECTED_DUST` / `REJECTED_NEGATIVE_EV` ke `06`.

---
### [M-008] / Metode 8 — Caller-Callee Assumption Seam & Direct Downstream Bypass
- **Target Kelas:** `[CLASS-B]`, `[CLASS-C]`
- **Prinsip Mekanis (Chain-Neutral — Anti-Lexical-Overfitting):**
  Jangan mengunci metode ini pada nama modifier seperti `onlyRouter` atau `onlyManager`. Aturan umumnya adalah:
  > **Periksa apakah jalur hilir (downstream) benar-benar membatasi caller yang sah DAN mengulang seluruh validasi kritis, atau hanya mempercayai secara buta bahwa pemanggil hulu (upstream) sudah melakukannya.**
- **Manifestasi Lintas-Paradigma:**
  - *EVM / Tron:* Hulu `Router/Gateway/Manager` -> Hilir `Pool/Vault/Strategy/Adapter` (contoh pemeriksaan cepat EVM: apakah hilir membatasi `msg.sender` seperti `onlyRouter`/`onlyManager`, dan apakah parameter seperti `from`/`onBehalfOf`/`receiver` divalidasi ulang).
  - *Solana:* Instruksi program hilir yang seharusnya hanya sah lewat CPI dari program hulu terverifikasi, tetapi dapat dipanggil langsung sebagai top-level instruction atau tidak memeriksa signer/authority pemilik akun.
  - *Move (Sui/Aptos):* Fungsi di modul hilir yang dideklarasikan `public` / `public entry` bebas tanpa menuntut objek otoritas (`Capability`) dari modul hulu.
  - *TON:* Handler penerima pesan (`recv_internal`) di actor hilir yang memproses opcode internal tanpa memverifikasi bahwa `sender_address` adalah actor hulu resmi (mis. Jetton Master / Router resmi).
- **Prosedur Bedah Fase 2:**
  1. **Unvalidated Seam (Celah Lempar Tanggung Jawab):** Pada titik panggilan `Hulu -> Hilir`, apakah Hulu meneruskan parameter (`receiver`, `from`, `onBehalfOf`, `token`, `data`, atau akun/objek) tanpa validasi karena mengira Hilir akan memvalidasinya — sementara Hilir percaya buta karena panggilan datang dari Hulu?
  2. **Direct Downstream Bypass:** Jika validasi keamanan (slippage, whitelist, fee, access check) hanya ada di Hulu, periksa apakah penyerang dapat memanggil fungsi publik di Hilir secara langsung dengan melompati Hulu.
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - Periksa dua syarat di komponen hilir: **(1) apakah jalur hilir benar-benar membatasi caller yang sah**, dan **(2) apakah seluruh validasi kritis atas parameter pengguna sudah dilakukan di hulu ATAU diulang di hilir**. Jika caller hilir sudah dibatasi secara ketat DAN tidak ada parameter bebas yang lolos tanpa validasi -> gugur ke `06`. Jika salah satu bocor -> PoC wajib memanggil hilir secara langsung (atau menyuntikkan parameter lewat seam hulu).

---
### [M-009] / Metode 9 — Half-Baked / Suspended Lifecycle State (Menyerang Saat Status "Menggantung")
- **Target Kelas:** `[CLASS-A]` *(State Machine Lokal)*, `[CLASS-B]`, `[CLASS-C]` *(Multi-Step / Async Lifecycle)*
- **Prinsip Mekanis (Chain-Neutral):** Auditor menguji siklus hidup yang selesai tuntas dari awal hingga akhir (`Request -> Finalize`). Anda WAJIB menguji siklus yang sengaja dihentikan di tengah jalan (*Pending / In-Flight / Cooldown*) lalu disusupi aksi dari jalur lain.
- **Prosedur Bedah Fase 2:**
  1. Mulai **Langkah 1** dari proses multi-tahap (misal: `requestWithdraw`, `initiateCooldown`, `createOrder`, `startAuction`, `propose`, `initiateMigration`, atau pengiriman pesan asinkron tahap pertama).
  2. **JANGAN** jalankan langkah penyelesaiannya. Saat akun/posisi/objek masih berada dalam status *"Pending / Menggantung"* tersebut, panggil fungsi dari jalur lain (`transfer`, `delegate`, `borrow`, `liquidate`, `emergencyWithdraw`, atau `cancel` berulang) untuk memeriksa apakah saldo/jaminan yang sedang menggantung belum dikunci sehingga bisa dipakai dua kali (*double-spend*) atau menghindari likuidasi.
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - Cek pada kode Langkah 1 (`request`/`initiate`/`createOrder`) apakah saldo/share/objek langsung dibakar, dipindahkan ke escrow, atau dikunci penuh oleh flag yang juga diperiksa di **seluruh** fungsi jalur sampingan (`transfer`, `borrow`, `liquidate`, `cancel`). Jika sudah terkunci rapat di semua jalur -> gugur ke `06`. Jika ada satu jalur sampingan yang tidak memeriksa kunci tersebut -> PoC wajib mengeksekusi urutan: `Langkah 1 (Gantung) -> Jalur Sampingan -> Langkah 2 (Penyelesaian/Klaim)`.

---

### [M-010] / Metode 10 — Live Residual State, Delegated Authority, & Post-Upgrade Drift
- **Target Kelas:** `[CLASS-B]`, `[CLASS-C]` *(serta `[CLASS-A]` bila kontrak merupakan proxy/upgraded contract yang berdiri sendiri)*
- **Prinsip Mekanis (Chain-Neutral — Anti-Lexical-Overfitting):**
  Auditor menguji pada *sandbox* kosong (`setUp()` bersih), sedangkan sistem di produksi membawa **state sisa dan riwayat migrasi yang nyata**. Jangan mengunci metode ini hanya pada istilah EVM (`allowance`, `cast call`, `slot proxy`). Lima konsep general yang wajib diperiksa lintas-rantai adalah:
  1. **Allowance atau Approval** yang masih aktif dari pengguna ke kontrak perantara;
  2. **Delegated Authority atau Capability** yang belum dicabut setelah transaksi/sesi selesai;
  3. **Residual Balance atau Asset Object** yang mengendap/tertinggal di kontrak/akun/objek perantara;
  4. **Stale Configuration** (konfigurasi lama yang tidak lagi sesuai dengan modul baru);
  5. **Storage Slot, Object Field, Account Data, atau Actor State** yang tidak sinkron atau belum terinisialisasi setelah upgrade/migration.
- **Tabel Padanan Lintas-Rantai:**

  | Konsep General | Manifestasi EVM / Tron | Manifestasi Solana (SVM) | Manifestasi Move (Sui/Aptos) | Manifestasi TON |
  |---|---|---|---|---|
  | **Otorisasi / Capability Tertunda** | `allowance` / `approve` / `Permit2` / `operator` | Delegated authority pada Token Account / PDA signer | Capability tertunda / dipinjamkan / tidak dihancurkan | Otoritas admin/wallet yang masih terikat ke kontrak lama |
  | **Residual Balance / Asset Object** | Saldo ERC20/ETH mengendap di Router/Helper/Migrator | Lamport / SPL token mengendap di PDA perantara | `Coin<T>` atau asset object tertinggal di shared object | Saldo TON / Jetton tersisa di actor perantara |
  | **State Drift Pasca-Upgrade/Migrasi** | Slot proxy EIP-1967 / variabel `V2` baru yang masih `0` | Ukuran/skema Account data lama vs versi program baru | Field dinamis (`dynamic_field`) atau versi `Package` tidak sinkron | Skema storage `c4` / konfigurasi actor tidak sinkron pasca-`set_code` |
  | **Alat Baca State Live (Fase 3)** | `cast call`, `cast storage`, `eth_getStorageAt` | RPC `getAccountInfo` / `solana account` | RPC `sui client object` / `getDynamicFields` | Toncenter / Liteclient `getAccountState` / `runGetMethod` |
- **Prosedur Bedah Fase 2:**
  1. **Delegated Authority & Residual Asset:** Apakah komponen perantara (Router/Helper/Migrator/Adapter) memiliki panggilan eksternal terbuka (`call`, `transferFrom`, `sweep`, `swap`, CPI, atau fungsi publik terbuka) yang dapat menarik aset tertinggal atau menyedot otorisasi/capability pengguna aktif?
  2. **Post-Upgrade / Migration State Drift:** Setelah peningkatan atau migrasi versi, apakah ada variabel/field/slot baru yang berasumsi sudah terisi saat inisialisasi padahal pada state produksi masih `0` / kosong — atau bertabrakan dengan layout state versi sebelumnya?
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - Sebelum menulis kode PoC, **wajib membaca state live produksi lebih dulu** (khusus EVM gunakan `cast call` / `cast storage` / `cast implementation`; untuk non-EVM gunakan pembacaan account data / object field / actor state yang setara).
  - Jika pada state produksi nyata terbukti tidak ada saldo/asset object tertinggal, tidak ada otorisasi/capability aktif yang bisa ditarik, dan seluruh slot/field pasca-upgrade sudah terisi dengan benar -> langsung buang ke `06` tanpa menulis PoC.

---

## 4. Template Plug-and-Play untuk Menambah Metode Baru (`M-011` .. `M-NNN`)

Saat ingin menambahkan metode pencarian baru di masa depan, salin blok di bawah ini tepat di atas bagian ini, lalu tambahkan kode `M-0XX` ke Tabel Matriks Kelas di Bagian 1:

```markdown
### [M-0XX] / Metode XX — <Nama Metode Baru (Bebas Bias Bahasa Rantai)>
- **Target Kelas:** `[CLASS-A]` / `[CLASS-B]` / `[CLASS-C]`
- **Prinsip Mekanis (Chain-Neutral):** <Jelaskan mekanisme dasar tanpa bergantung pada kata kunci satu bahasa>
- **Manifestasi Lintas-Paradigma:**
  - *EVM / Tron:* ...
  - *Solana:* ...
  - *Move:* ...
  - *TON:* ...
- **Prosedur Bedah Fase 2:**
  1. ...
  2. ...
- **Routing Uji Cepat Fase 3 (Pre-PoC Gate):**
  - <Pemeriksaan termurah untuk menggugurkan ke `06` atau syarat wajib PoC sebelum masuk ke simulasi penuh>
```
