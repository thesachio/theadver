# Katalog Generalized Attacker POV — Domain Penyerahan Kontrol, Subcall, & Otoritas (`[POV-CALL-XX]`)

Berkas ini menyimpan pola eksploitasi on-chain nyata pada penyerahan kontrol eksekusi, callback, dan isolasi sub-panggilan.
- **Indeks & Router Gejala:** `references/ref-attacker-pov.md`
- **Checklist Prinsip Dasar:** `references/ref-calls-tokens-reentrancy.md`

---

### [POV-CALL-01] State Desynchronization pada Penyerahan Kontrol
- **Target Kelas:** `[CLASS-B]` *(Dual-Entity: Kontrak Utama <-> Penerima Kontrol/Kontrak Pasangan)*, `[CLASS-C]` *(Multi-Entity Cross-Module Read-Only Reentrancy)*
- **Metode Terkait:** `M-002` (State-Transition Differential), `M-006` (Stale Snapshot), `M-008` (Caller-Callee Seam)
- **Gejala Pemicu di Kode (Trigger Symptom):** Terjadi panggilan eksternal / pengiriman native coin / hook NFT-token / CPI di tengah fungsi ketika variabel pertama (`totalAssets` / `collateral`) sudah berubah tetapi variabel pasangannya (`totalSupply` / `debt`) belum diperbarui.
- **Kondisi Prasyarat (State Condition):**
  Kontrak utama memiliki modifier `nonReentrant` lokal, namun menghitung nilai/kesehatan posisi menggunakan lebih dari satu variabel state (misal: `totalAssets` dan `totalSupply`, atau `collateral` dan `debt`) atau membagi state dengan kontrak pasangan (Adapter/Strategy/Router/Oracle View).
- **Kacamata Attacker (Gejala di Kode):**
  Di tengah fungsi (sebelum baris terakhir selesai), terjadi penyerahan kontrol eksternal (pengiriman native coin/ETH, `safeTransferFrom` ERC-721/ERC-1155, hook token whitelist, atau panggilan ke kontrak eksternal) ketika variabel pertama sudah diperbarui tetapi variabel pasangannya belum diperbarui.
  *Prinsip umumnya berlaku untuk **setiap penyerahan kontrol di tengah pembaruan dua variabel berpasangan** — bukan hanya callback EVM: termasuk CPI di tengah instruksi Solana, atau pengiriman pesan sebelum kunci state diperbarui di TON.*
- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang membuka posisi di Kontrak A dan menyiapkan posisi terungkit di Kontrak B (atau fungsi lain yang tidak berbagi kunci `nonReentrant` yang sama).
  2. **[Pemicu Asimetri]** Penyerang memicu penarikan/likuidasi/aksi yang mengeksekusi panggilan keluar tepat di tengah pembaruan dua variabel.
  3. **[Ekstraksi Nilai]** Di dalam callback, penyerang memanggil fungsi di Kontrak B (atau fungsi lain) yang membaca nilai rasio yang sedang timpang sementara (*inflated/deflated mid-tx state*) untuk meminjam berlebih atau melikuidasi secara tidak sah.
- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor melihat kata kunci `nonReentrant` pada fungsi tersebut lalu langsung menandainya aman dari reentrancy, tanpa memeriksa apakah ada kontrak/fungsi lain di ekosistem yang membaca state yang baru setengah selesai diperbarui tersebut.
- **Batas Realitas (Kapan Pola Ini GUGUR) & Routing Uji Cepat Fase 3:**
  - *Batas Realitas:* Gugur jika seluruh mutasi state internal dan akuntansi bersama diselesaikan 100% sebelum interaksi eksternal (CEI murni), atau jika terdapat *global reentrancy lock* yang juga diperiksa oleh seluruh fungsi pembaca (*view check*).
  - *Routing Uji Cepat Fase 3:* Cek apakah benar ada kontrak/fungsi lain di dalam scope (atau integrasi produksi nyata) yang membaca rasio *mid-tx* tersebut tanpa terhalang *reentrancy lock* yang sama. Jika tidak ada pembaca eksternal/internal yang terpengaruh -> tidak ada korban -> langsung ke `06` (`REJECTED_NO_VICTIM`).

---

### [POV-CALL-02] Subcall Success/Failure State Divergence
- **Target Kelas:** `[CLASS-B]` *(Dual-Entity: Kontrak Pemanggil <-> Target Subcall)*, `[CLASS-C]` *(Multi-Entity Batch Settlement)*
- **Metode Terkait:** `M-002` (State-Transition Differential), `M-008` (Caller-Callee Seam), `M-009` (Suspended Lifecycle)
- **Gejala Pemicu di Kode (Trigger Symptom):** Kontrak membungkus panggilan eksternal dengan `try/catch`, `.call()` tanpa `require(success)`, atau mengabaikan kegagalan sub-eksekusi lalu melanjutkan mutasi state berbeda antara cabang sukses vs gagal.
- **Kondisi Prasyarat (State Condition):**
  Kontrak mengisolasi panggilan eksternal ke alamat pengguna, penerima, atau kontrak pihak ketiga menggunakan blok `try/catch` atau panggilan level rendah `.call()` tanpa `require(success)` agar kegagalan sub-panggilan tidak membatalkan transaksi utama.
- **Kacamata Attacker (Gejala di Kode):**
  1. **Divergensi state antar-cabang (prinsip universal):** Cabang sukses (`try` / `if (success)`) dan cabang gagal (`catch` / `else`) memutasi state secara tidak simetris (misal: cabang gagal melewati pemotongan penalti, membatalkan penyitaan kewajiban, atau memberikan jalur keluar tanpa beban). Ini berlaku untuk **setiap isolasi sub-eksekusi** — termasuk penanganan fallback/error, *partial settlement* lintas modul, atau lanjutan eksekusi setelah panggilan antar-komponen gagal.
  2. **Returnbombing (manifestasi khusus EVM):** Panggilan `.call()` ke alamat yang dapat dikendalikan pemanggil menyalin nilai balik ke variabel `bytes memory` atau menangkap `catch (bytes memory reason)` tanpa membatasi ukuran returndata di level assembly, sehingga biaya ekspansi memori dibebankan ke pemanggil.
- **Padanan non-EVM:**
  **Solana** — CPI yang gagal lalu dilanjutkan tanpa menggulung state, atau hasil `Result` yang diabaikan · **Move** — `abort`/error yang ditangkap lalu jalur sukses tetap diambil · **TON** — eksekusi lanjutan setelah pesan gagal terkirim, atau penanganan `ok:false` yang tidak membalik state.
- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang mengatur kontrak miliknya sebagai alamat target/penerima callback atau mengatur takaran gas transaksi induk secara presisi (aturan 63/64 EIP-150).
  2. **[Pemicu Asimetri]** Untuk eksploitasi divergensi state, penyerang sengaja membuat sub-panggilan gagal (*revert* di penerima atau kehabisan gas di sub-konteks) agar eksekusi masuk ke cabang `catch`/`!success`. Untuk *Returnbombing*, kontrak penyerang mengembalikan payload memori raksasa pada returndata.
  3. **[Ekstraksi Nilai]** Transaksi induk tetap berhasil dengan state menguntungkan dari cabang gagal, atau seluruh gas pemanggil terkuras habis oleh biaya ekspansi memori kuadratik sebelum blok `catch` dapat menyelamatkan transaksi (DoS permanen pada fungsi likuidasi/penyelesaian).
- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor menganggap keberadaan `try/catch` atau pembatasan `.call{gas: X}()` sudah otomatis menjamin keamanan dari kegagalan pihak ketiga, sehingga tidak membandingkan selisih akuntansi antara cabang sukses vs gagal dan lupa bahwa biaya penyalinan returndata ke memori dibebankan ke kontrak pemanggil.
- **Batas Realitas (Kapan Pola Ini GUGUR) & Routing Uji Cepat Fase 3:**
  - *Batas Realitas:* Gugur jika target panggilan adalah kontrak internal/tetap yang *immutable* dan tidak meneruskan eksekusi ke alamat pengguna, serta mutasi state pada cabang sukses maupun gagal tetap mempertahankan invarian akuntansi yang setara.
  - *Routing Uji Cepat Fase 3:* Cek pengendali alamat target pada panggilan eksternal tersebut. Jika target adalah kontrak internal/tetap *immutable* yang tidak bisa dibuat gagal oleh penyerang dan tidak meneruskan panggilan ke alamat pengguna -> langsung ke `06`.

---

## Penanda Sisipan Entri Baru (`[POV-CALL-03]` .. `[POV-CALL-NN]`)
*(Tambahkan entri baru di atas baris ini dengan 8 field wajib, lalu daftarkan 1 baris di `references/ref-attacker-pov.md`).*
