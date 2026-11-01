# Checklist Paradigma Rantai: Solana (SVM — Anchor & Native Rust)

Gunakan daftar periksa ini saat mengaudit program Rust di ekosistem Solana:

1. **Akun Dinamis Tak Terverifikasi (`ctx.remaining_accounts` Spoofing):**
   - Akun yang dilewatkan melalui `ctx.remaining_accounts` TIDAK divalidasi secara otomatis oleh makro `#[derive(Accounts)]` Anchor!
   - Setiap akun yang dibaca/ditulis dari `remaining_accounts` wajib diperiksa secara manual: (a) kepemilikan programnya (`owner`), (b) tipe diskriminator datanya, dan (c) ikatan kuncinya (`key()`) terhadap `Pool` atau `State` utama yang sedang diproses (mencegah penyisipan akun *tick/bitmap* milik pool palsu).

2. **Ketiadaan Pemeriksaan Signer, Owner, & Ikatan Data (`has_one` / `constraint`):**
   - Pastikan setiap akun otoritas telah divalidasi sebagai penanda tangan (`Signer<'info>` atau `account.is_signer`).
   - Pastikan akun data yang saling berelasi (misal `UserPosition` dan `LendingMarket`) memiliki validasi ikatan (`has_one = market` atau `constraint = user_position.market == market.key()`). Tanpa ini, penyerang dapat memasangkan akun posisi dari pasar palsu ke pasar utama.

3. **Data Akun Basi Setelah CPI (Missing `.reload()` After Cross-Program Invocation):**
   - Di Anchor, struktur `Account<'info, T>` mendeserialisasi data akun ke memori hanya pada awal instruksi.
   - Jika fungsi melakukan CPI (misal memanggil program Token untuk `transfer` atau `mint`), nilai `token_account.amount` di memori lokal **TIDAK berubah otomatis**! Jika kode membaca `token_account.amount` setelah CPI tanpa memanggil `token_account.reload()?` terlebih dahulu, kode akan menggunakan saldo lama sebelum transfer!

4. **Tabrakan Benih PDA & Penyalahgunaan `init_if_needed`:**
   - Periksa pembentukan benih PDA (`seeds = [...]`): apakah seluruh parameter kunci (seperti `user.key()`, `mint.key()`, atau `pool.key()`) sudah dimasukkan ke dalam benih agar akun satu pengguna tidak bertabrakan dengan pengguna lain?
   - Jika menggunakan `init_if_needed`, pastikan fungsi tidak mengizinkan inisialisasi ulang atau penimpaan otoritas pada akun yang sudah pernah dibuat.

5. **Penutupan Akun Cacat (Account Revival) & Arbitrer CPI:**
   - Pada Native Rust, saat menutup akun dengan menguras lamport ke `0`, pastikan data akun juga dihapus dan pemiliknya diubah ke System Program agar akun tidak bisa dihidupkan kembali (*revived*) dengan menyetor lamport di instruksi berikutnya dalam transaksi yang sama.
   - Pada setiap panggilan `invoke` / `invoke_signed`, pastikan `program_id` target telah dikunci ke program resmi (bukan akun program sembarang yang dikirim oleh pemanggil).

6. **Perangkap Token-2022 Extensions & Overflow Rust:**
   - Jika program mendukung SPL Token-2022, periksa bagaimana program menangani ekstensi *Transfer Fee* (potongan biaya saat transfer) dan *Transfer Hook*.
   - Jika `Cargo.toml` tidak mengaktifkan `overflow-checks = true`, setiap operasi `+`, `-`, `*` biasa di Rust berisiko mengalami *wrapping overflow* di mode rilis.

---

## Katalog Generalized Attacker POV & Auditor Blindspots (Diisi Bertahap)

Entri di bawah ini adalah pola eksploitasi nyata yang telah digeneralisasi. Pakai pada Tahap B Fase 2: cocokkan **Kondisi Prasyarat** dan **Gejala di Kode** dengan fungsi yang sedang dibedah.
Indeks seluruh POV lintas file: `references/ref-attacker-pov.md`.

### [POV-SOL-01] Cross-CPI Stale AccountInfo & Duplicate Writable Alias

- **Kondisi Prasyarat (State Condition):**
  Instruksi program menerima $\ge 2$ akun yang dapat dimutasi (`mut` atau lewat `ctx.remaining_accounts`) dengan tipe serupa, ATAU melakukan *Cross-Program Invocation* (CPI) di tengah fungsi lalu kembali membaca field dari struct akun di memori lokal.

- **Kacamata Attacker (Gejala di Kode):**
  1. Tidak ada constraint `constraint = account_a.key() != account_b.key()` pada pasangan akun sumber/tujuan atau daftar `remaining_accounts`.
  2. Setelah mengeksekusi CPI (yang mengubah saldo/state akun di runtime), kode langsung membaca field `account.amount` atau `state.value` dari variabel Rust yang dideserialisasi di awal fungsi tanpa memanggil `.reload()?`, atau menulis kembali struct lama sehingga menimpa hasil CPI.
  *Prinsip umumnya adalah **padanan Solana dari Metode 6**: (a) referensi kembar yang diproses dua kali, dan (b) snapshot lokal basi yang dipakai atau ditulis balik setelah interaksi eksternal.*

- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang menyiapkan satu akun valid miliknya.
  2. **[Pemicu Asimetri]** Penyerang memanggil instruksi dengan memasukkan alamat akun yang sama untuk parameter `source` dan `destination` (atau duplikat di `remaining_accounts`), atau memicu CPI yang mengubah saldo akun.
  3. **[Ekstraksi Nilai]** Program memproses penjumlahan/klaim di atas snapshot memori yang belum diperbarui (atau menimpa pengurangan saldo), menggandakan hak penyerang dalam satu instruksi.

- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor melihat deklarasi tipe `Account<'info, ...>` di Anchor sudah memeriksa pemilik dan diskriminator tipe, sehingga berasumsi dua variabel parameter dengan nama berbeda pasti menunjuk ke dua akun berbeda dan nilainya selalu mutakhir sepanjang fungsi.

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika terdapat validasi ketidaksetaraan kunci (`key() != ...`) pada seluruh pasangan akun `mut`/`remaining_accounts`, serta `.reload()?` dipanggil setiap kali data akun dibaca ulang pasca-CPI.

---

<!-- Sisipkan [POV-SOL-02], [POV-SOL-03], dst. di BAWAH baris ini, urut menaik -->
