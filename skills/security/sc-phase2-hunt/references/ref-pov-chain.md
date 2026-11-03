# Katalog Generalized Attacker POV — Spesifik Paradigma Rantai (`[POV-EVM/SOL/MOVE/TON-XX]`)

Berkas ini menyimpan pola eksploitasi on-chain nyata yang bertumpu pada perilaku mesin virtual atau runtime rantai spesifik.
- **Indeks & Router Gejala:** `references/ref-attacker-pov.md`
- **Checklist Dasar per Rantai:** `ref-chain-evm-tron.md`, `ref-chain-solana.md`, `ref-chain-sui-move.md`, `ref-chain-ton-async.md`

---

### [POV-EVM-01] Multicall Context Reuse & Residual Authority Exploitation
- **Target Kelas:** `[CLASS-A]` *(Batch/Loop Internal)*, `[CLASS-B]` *(Router/Multicall <-> Target)*
- **Metode Terkait:** `M-003` (Zero-Time Loop), `M-007` (Split-vs-Bulk), `M-010` (Residual Authority)
- **Gejala Pemicu di Kode (Trigger Symptom):** Kontrak mewarisi `Multicall` (`delegatecall`), memiliki loop batch, atau memakai `TSTORE`/`TLOAD`, SERTA memiliki fungsi yang membaca `msg.value` atau flag otorisasi sementara.
- **Kondisi Prasyarat (State Condition):**
  Kontrak menyediakan mekanisme eksekusi jamak dalam satu transaksi (pewarisan Multicall berbasis `delegatecall`, loop batch internal, atau pemakaian *Transient Storage* `TSTORE`/`TLOAD`) DAN memiliki fungsi yang membaca `msg.value` atau flag otorisasi sementara.
- **Kacamata Attacker (Gejala di Kode):**
  Fungsi satuan memeriksa `require(msg.value == requiredAmount)` atau memakai `msg.value` untuk mencatat pembayaran tanpa mengurangi penghitung global per-transaksi, atau menetapkan flag sementara di *Transient Storage* yang tidak dihapus (`TSTORE(slot, 0)`) sebelum sub-eksekusi berikutnya dimulai.
  *Prinsip umumnya: **satu konteks luar (nilai pembayaran, otorisasi sementara, atau status sesi) dipakai ulang oleh N sub-panggilan** sementara kontrak menganggapnya sekali pakai. TVM Tron memiliki perilaku `msg.value` yang sama; pada Solana padanannya adalah konteks instruksi/akun yang dipakai ulang di dalam satu transaksi.*
- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang menyusun payload panggilan batch berisi $N$ panggilan berulang ke fungsi pembayaran/pencetakan yang sama.
  2. **[Pemicu Asimetri]** Penyerang memanggil fungsi pembungkus batch (multicall) sambil mengirimkan `msg.value` hanya sebesar 1 kali nilai pembayaran ($1 \times X$).
  3. **[Ekstraksi Nilai]** Karena setiap sub-panggilan `delegatecall` membaca konteks `msg.value` yang sama ($X$), kontrak mengkreditkan nilai sebesar $N \times X$ kepada penyerang dengan modal hanya $1 \times X$.
- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor menguji fungsi pembayaran secara terpisah (1 transaksi = 1 panggilan) di mana `msg.value` memang valid, dan menganggap kontrak pembungkus Multicall dari library standar sudah aman tanpa melihat efek penggabungan keduanya.
- **Batas Realitas (Kapan Pola Ini GUGUR) & Routing Uji Cepat Fase 3:**
  - *Batas Realitas:* Gugur jika fungsi pembungkus batch tidak `payable`, atau kontrak melacak total pemakaian pembayaran dalam akumulator per-transaksi, atau setiap slot *Transient Storage* selalu di-reset sebelum keluar dari masing-masing aksi.
  - *Routing Uji Cepat Fase 3:* Cek apakah fungsi batch benar-benar `payable` dan memakai `delegatecall` (atau loop internal yang membaca `msg.value`), atau tidak me-reset slot transient. Jika multicall tidak `payable` atau fungsi target tidak membaca `msg.value` -> langsung ke `06`.

---

### [POV-SOL-01] Cross-CPI Stale AccountInfo & Duplicate Writable Alias
- **Target Kelas:** `[CLASS-B]` *(Dual-Entity: Program Utama <-> Target CPI atau 2 Akun Alias)*, `[CLASS-C]`
- **Metode Terkait:** `M-003` (Multi-Identity/Alias), `M-006` (Stale Snapshot Write-Back & Duplicate Reference `[A, A]`)
- **Gejala Pemicu di Kode (Trigger Symptom):** Instruksi Solana menerima $\ge 2$ akun `mut` / `ctx.remaining_accounts` bertipe serupa tanpa constraint `key() !=`, ATAU melakukan CPI lalu membaca/menulis variabel akun lokal tanpa `.reload()?`.
- **Kondisi Prasyarat (State Condition):**
  Instruksi program menerima $\ge 2$ akun yang dapat dimutasi (`mut` atau lewat `ctx.remaining_accounts`) dengan tipe serupa, ATAU melakukan *Cross-Program Invocation* (CPI) di tengah fungsi lalu kembali membaca field dari struct akun di memori lokal.
- **Kacamata Attacker (Gejala di Kode):**
  1. Tidak ada constraint `constraint = account_a.key() != account_b.key()` pada pasangan akun sumber/tujuan atau daftar `remaining_accounts`.
  2. Setelah mengeksekusi CPI (yang mengubah saldo/state akun di runtime), kode langsung membaca field `account.amount` atau `state.value` dari variabel Rust yang dideserialisasi di awal fungsi tanpa memanggil `.reload()?`, atau menulis kembali struct lama sehingga menimpa hasil CPI.
  *Prinsip umumnya adalah **padanan Solana dari `M-006`**: (a) referensi kembar yang diproses dua kali, dan (b) snapshot lokal basi yang dipakai atau ditulis balik setelah interaksi eksternal.*
- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang menyiapkan satu akun valid miliknya.
  2. **[Pemicu Asimetri]** Penyerang memanggil instruksi dengan memasukkan alamat akun yang sama untuk parameter `source` dan `destination` (atau duplikat di `remaining_accounts`), atau memicu CPI yang mengubah saldo akun.
  3. **[Ekstraksi Nilai]** Program memproses penjumlahan/klaim di atas snapshot memori yang belum diperbarui (atau menimpa pengurangan saldo), menggandakan hak penyerang dalam satu instruksi.
- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor melihat deklarasi tipe `Account<'info, ...>` di Anchor sudah memeriksa pemilik dan diskriminator tipe, sehingga berasumsi dua variabel parameter dengan nama berbeda pasti menunjuk ke dua akun berbeda dan nilainya selalu mutakhir sepanjang fungsi.
- **Batas Realitas (Kapan Pola Ini GUGUR) & Routing Uji Cepat Fase 3:**
  - *Batas Realitas:* Gugur jika terdapat validasi ketidaksetaraan kunci (`key() != ...`) pada seluruh pasangan akun `mut`/`remaining_accounts`, serta `.reload()?` dipanggil setiap kali data akun dibaca ulang pasca-CPI.
  - *Routing Uji Cepat Fase 3:* Cek pada struct `#[derive(Accounts)]` dan tubuh instruksi: jika constraint `key() !=` sudah terpasang pada akun `mut` DAN `.reload()?` sudah dipanggil pasca-CPI sebelum pembacaan ulang -> langsung ke `06`.

---

### [POV-MOVE-01] Programmable Transaction Block (PTB) Capability & Object Splitting
- **Target Kelas:** `[CLASS-B]` *(2 Objek Mandiri)*, `[CLASS-C]` *(Rantai Panggilan PTB Multi-Objek)*
- **Metode Terkait:** `M-006` (Duplicate/Cross-Object Alias), `M-007` (Bit-Shift Truncation), `M-008` (Capability Bypass)
- **Gejala Pemicu di Kode (Trigger Symptom):** Fungsi Move menerima $\ge 2$ objek (`&mut Pool` + `&mut Position`/`Receipt`) tanpa `assert!(receipt.pool_id == object::id(pool))`, ATAU memakai geser bit kiri `<<` pada matematika kustom (`u128`/`u256`).
- **Kondisi Prasyarat (State Condition):**
  Modul Move menerima lebih dari satu objek mandiri (misal objek wadah utama `&mut Container` bersama objek bukti `&mut Position` / struct *Hot Potato* `Receipt`), ATAU menggunakan operasi geser bit kiri (`<<`) dalam perhitungan matematika kustom (`u128`/`u256`).
- **Kacamata Attacker (Gejala di Kode):**
  1. Fungsi memverifikasi kesamaan tipe generik `<T>`, tetapi lupa memeriksa ikatan ID objek induk (`assert!(receipt.container_id == object::id(container))`), atau menyediakan fungsi publik alternatif yang dapat menghancurkan *Hot Potato* dengan syarat lebih ringan.
  2. Fungsi matematika kustom melakukan `value << shift` di mana pemeriksaan batas mask overflow meleset 1 bit (tidak menangkap bit tinggi yang terbuang, karena operasi `<<` di Move tidak otomatis *abort* saat bit signifikan tergeser keluar).
  *Prinsip umumnya: (1) adalah **padanan Move dari aliasing referensi** (`[POV-SOL-01]` / `M-006`) — tipe sama tidak menjamin objek sama; (2) adalah **padanan Move dari pemangkasan di langkah antara** (`[POV-MATH-02]` / `M-007`) — bit tinggi hilang sebelum validasi akhir.*
- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Dalam satu *Programmable Transaction Block* (PTB), penyerang membuat atau mengakses `Container_Palsu` dengan rasio ekstrem (atau menyiapkan angka input tepat di batas bit-mask).
  2. **[Pemicu Asimetri]** Penyerang mencetak `Position` / `Receipt` bernominal besar dari `Container_Palsu` (atau memicu pemotongan bit atas pada `<<` sehingga kewajiban setor terhitung sangat kecil).
  3. **[Ekstraksi Nilai]** Masih di PTB yang sama, penyerang menyerahkan `Position` / `Receipt` tersebut ke `Container_Utama` untuk menguras aset riil.
- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor mengandalkan jaminan keamanan tipe Move (`has key`, linear *Hot Potato*, dan *auto-overflow check* pada `+`/`*`), tanpa menyadari bahwa tipe yang sama bisa berasal dari instansi objek yang berbeda dan operator `<<` di Move dapat memangkas bit tinggi secara diam-diam.
- **Batas Realitas (Kapan Pola Ini GUGUR) & Routing Uji Cepat Fase 3:**
  - *Batas Realitas:* Gugur jika setiap objek bukti/posisi mengikat dan memverifikasi `object::id` dari objek wadah induknya di setiap fungsi, serta operasi `<<` memeriksa batas atas secara presisi sebelum digeser.
  - *Routing Uji Cepat Fase 3:* Cek apakah sudah ada `assert!(receipt.pool_id == object::id(pool))` dan apakah batas mask `<<` sudah menolak bit tertinggi yang akan tergeser keluar. Jika keduanya sudah ada -> langsung ke `06`.

---

### [POV-TON-01] Async Message Interleaving & Bounce Payload Truncation
- **Target Kelas:** `[CLASS-C]` *(Multi-Entity Async Actor Chain: Sender -> Actor A -> Actor B -> Bounce)*
- **Metode Terkait:** `M-002` (State Delta), `M-007` (Payload Truncation), `M-009` (Suspended In-Flight Lifecycle State)
- **Gejala Pemicu di Kode (Trigger Symptom):** Kontrak TON mengubah state lokal lalu mengirim pesan (`send_raw_message`) dengan mengandalkan handler `bounced` (>224 bit / `ref`) atau tanpa mengunci state pengguna selama pesan masih *in-flight*.
- **Kondisi Prasyarat (State Condition):**
  Kontrak pada arsitektur aktor asinkron (TON) mengubah state lokal terlebih dahulu lalu mengirim pesan keluar ke kontrak lain, dan mengandalkan handler pesan pantulan (*bounced message*) untuk memulihkan (*rollback*) state jika kontrak tujuan gagal.
- **Kacamata Attacker (Gejala di Kode):**
  1. Pesan keluar menaruh data penting untuk pemulihan (jumlah nilai, ID posisi, atau alamat pemilik) **setelah bit ke-224** dari body pesan utama atau di dalam referensi *child cell* (`ref`), padahal jaringan memotong pesan bounced hanya menyisakan 224 bit data pertama tanpa `ref`.
  2. Selama pesan pertama masih dalam perjalanan (*in-flight*) menunggu balasan, status akun/posisi pengirim tidak dikunci (*pending lock*), sehingga pengguna dapat mengirim pesan kedua yang memodifikasi state yang sama.
  *Prinsip umumnya: (1) adalah **padanan asinkron dari pemangkasan data di langkah antara** (`[POV-MOVE-01]` / `M-007`) — payload hilang sebelum rollback sempat berjalan; (2) adalah **padanan asinkron dari status menggantung** (`M-009`) — state tidak terkunci selama siklus belum selesai.*
- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang menyiapkan state awal pada kontrak asal dan mengatur kondisi (atau takaran `msg_value` gas) agar pesan gagal di kontrak tujuan, atau menyiapkan pesan kedua saat pesan pertama masih *in-flight*.
  2. **[Pemicu Asimetri]** Kontrak tujuan menolak pesan dan memantulkan pesan bounced yang telah terpotong (atau memproses dua pesan *in-flight* secara berurutan terhadap state yang sama).
  3. **[Ekstraksi Nilai]** Handler bounced membaca nilai yang terpotong/rusak (atau gagal berjalan), menyebabkan pengembalian saldo berlebih atau penghapusan kewajiban tanpa membatalkan hak yang sudah dicetak.
- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor melihat kontrak sudah menyediakan fungsi `on_bounce` lalu menganggap mekanisme *rollback* asinkron sudah tuntas, tanpa menghitung offset bit pada skema serialisasi pesan yang dikirim.
- **Batas Realitas (Kapan Pola Ini GUGUR) & Routing Uji Cepat Fase 3:**
  - *Batas Realitas:* Gugur jika seluruh data pemulihan disimpan di storage lokal kontrak pengirim (diindeks dengan `query_id` yang muat di dalam 224 bit pertama) DAN entitas dikunci penuh selama status *in-flight* belum selesai.
  - *Routing Uji Cepat Fase 3:* Hitung total bit field sebelum data pemulihan pada payload pesan keluar (apakah $\le 224$ bit tanpa `ref`?) dan periksa apakah state dikunci berdasarkan `query_id` / `is_locked` selama *in-flight*. Jika muat $\le 224$ bit DAN terkunci -> langsung ke `06`.

---

## Penanda Sisipan Entri Baru (`[POV-EVM/SOL/MOVE/TON-02]` .. `NN`)
*(Tambahkan entri baru di atas baris ini dengan 8 field wajib, lalu daftarkan 1 baris di `references/ref-attacker-pov.md`).*
