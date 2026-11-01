# Katalog Generalized Attacker POV & Auditor Blindspots (Diisi Bertahap)

Katalog **terpusat** untuk Tahap B Fase 2. Entri di sini bersifat lintas-domain: satu POV bisa dipakai
bersamaan dengan `ref-math-and-vaults.md` maupun `ref-calls-tokens-reentrancy.md`. Karena itu katalog
tidak diduplikasi ke tiap file referensi domain.

**Cara pakai:** setelah menerjemahkan referensi domain menjadi Pola Mekanis Abstrak (Tahap B butir 1),
cocokkan gejala kode fungsi target dengan kolom *Kacamata Attacker* di bawah. Jika prasyarat state
terpenuhi DAN gejala kode terlihat, pola ini layak diangkat menjadi lead di `audit/05-raw-leads.md`
dengan mencantumkan nomor `[POV-XX]` di kolom Metode Pencarian.

**Cara menambah entri:** tambahkan di atas baris penanda terakhir, satu entri = satu nomor urut baru.
Jangan pernah memakai nomor yang belum terdaftar di file ini (larangan halusinasi nomor POV).

---

## Daftar Entri

### [POV-01] Desinkronisasi Indeks Akrual Melalui Self-Transfer atau Mutasi Pihak Ketiga

- **Kondisi Prasyarat (State Condition):**
  Kontrak melacak hak klaim/bunga/poin menggunakan indeks global (`globalIndex`) dan titik catat per
  pengguna (`userIndex[u]`), serta memiliki fungsi pemindahan hak (`transfer`, `delegate`, `migrate`,
  `merge`) selain fungsi masuk/keluar utama.

- **Kacamata Attacker (Gejala di Kode):**
  Fungsi pemindahan memperbarui `balance[from]` dan `balance[to]` (atau menyalin saldo ke variabel memori
  sementara `uint256 balFrom = balance[from]`), tetapi **tidak** menyinkronkan/mengklaim hak tertunda pada
  KEDUA akun sebelum saldo berubah, atau tidak menolak kondisi `from == to`.

- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Attacker_A mengakumulasi hak/bunga yang belum diklaim (`globalIndex > userIndex[Attacker_A]`).
  2. **[Pemicu Asimetri]** Attacker_A memindahkan saldo ke Attacker_B (yang masih memiliki `userIndex` rendah)
     atau mentransfer ke dirinya sendiri (Attacker_A -> Attacker_A).
  3. **[Ekstraksi Nilai]** Attacker_B (atau Attacker_A) mengeklaim hak penuh menggunakan saldo baru dikalikan
     selisih indeks lama, lalu mengembalikan pokoknya untuk diulang (*loop*).

- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor memeriksa `stake()`, `unstake()`, dan `claim()` lalu melihat ketiganya sudah memanggil modifier
  `updateReward(msg.sender)`. Auditor lupa bahwa modifier tersebut hanya menerima 1 argumen (`msg.sender`),
  sehingga pada fungsi 2-aktor seperti `transfer(to, amount)`, akun `to` tidak ikut ter-update — atau variabel
  memori menimpa nilai saat `from == to`.

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika fungsi transfer secara eksplisit memanggil sinkronisasi indeks untuk `from` DAN `to` sebelum
  mengubah saldo, serta menggunakan pengurangan/penambahan langsung di storage (bukan menyalin variabel
  memori yang saling menimpa saat `from == to`).

---

<!-- Tambahkan [POV-02], [POV-03], dst. di atas baris ini -->
