# Reference: Execution Control Handoff, Authorities, & External Entities

> ATURAN REALITAS PRODUKSI (WAJIB DIBACA SEBELUM MENGGUNAKAN KAMUS INI!):
> Jangan pernah menerapkan daftar periksa token di bawah ini secara membabi buta! Selalu cek Kasta Realitas Aset di audit/01-threat-and-env.md:
> 1. LP Token / Share Token / Token Internal (Kasta 1): ADALAH ERC-20 STANDAR. DILARANG KERAS membuat hipotesis bahwa LP Token atau token internal memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau berperilaku seperti USDT!
> 2. Token Whitelist Produksi (Kasta 2): Hanya gunakan karakteristik token yang benar-benar diizinkan di produksi (catatan: USDT di produksi memiliki desimal 6, *blacklist*, dan tidak mengembalikan bool pada transfer, tetapi biaya transfernya 0 / BUKAN token *Fee-on-Transfer* aktif!).
> 3. Token Permissionless (Kasta 3): Menyuntikkan token kustom/FoT hanya valid jika sanggup menguras dana dari pengguna/pool LAIN.

---

## 1. Penyerahan Kontrol Eksekusi & Reentrancy Lintas Konteks
- State-Before-Interaction (CEI Violation): Apakah ada pengiriman native coin, pemanggilan hook/callback (onERC721Received, onERC1155Received, flashloan callback), atau panggilan eksternal sebelum state saldo/status/utang diperbarui?
- Cross-Function & Read-Only Reentrancy: Saat kontrol keluar ke pihak eksternal, apakah fungsi lain (atau kontrak eksternal yang membaca view function seperti harga share/LP) dapat dipanggil ketika total aset dan total pencatatan internal sedang tidak sinkron?

## 2. Eskalasi Otoritas, Batch Execution, & Signature Replay
- Self-Call Escalation (`msg.sender == address(this)`): Pada kontrak yang memiliki fitur multicall, executeBatch, atau router generik (seperti Smart Wallet / Account Abstraction), bisakah pengguna memasukkan target = address(this) untuk memanggil fungsi administratif internal yang dilindungi oleh onlySelf atau msg.sender == address(this)?
- Kelemahan Validasi Signature & Session Key (EIP-712 / EIP-1271):
  - Apakah *hash* pesan yang ditandatangani mengikat address(this), chainId, nonce yang langsung di-invalidasi, serta seluruh parameter kritis?
  - Pada Smart Wallet (EIP-1271) atau Session Key, apakah tanda tangan/kunci sesi dapat di-*replay* di dompet lain yang dimiliki pengguna yang sama, atau melampaui batas kuota/fungsi yang diizinkan?
## 3. Asimetri Aliran Aset (Hanya Jika Sesuai Kasta Realitas Aset!)
- Sabotase Penolakan Penerimaan (Push-Payment DoS): Pada fungsi kritikal seperti likuidasi, lelang, pelunasan pinjaman NFT, atau pembagian hadiah berantai, apakah pengiriman dana/aset dilakukan secara *push* ke alamat pihak lawan yang bisa menolak penerimaan (melalui fallback revert atau akun yang masuk daftar *blacklist* USDC/USDT) sehingga memblokir seluruh transaksi?
- Kebingungan Standar & Alamat Aset (Token Confusion): Pada protokol yang mendukung berbagai jenis aset (Native ETH, ERC-20, ERC-721, ERC-1155), bisakah pengguna memasukkan alamat kontrak dari tipe standar yang salah atau memasukkan amount vs tokenId secara tertukar?
- Akuntansi Aktual vs Input Parameter (Khusus Kasta 2/3 yang Terbukti Mendukung FoT/Deflasi): Hanya jika protokol secara eksplisit mengizinkan token *Fee-on-Transfer* tanpa *whitelist* ketat dan berinteraksi dengan pool bersama, periksa apakah kontrak mencatat amount parameter input alih-alih selisih balanceOf sebelum dan sesudah transfer.

---

## Katalog Generalized Attacker POV & Auditor Blindspots (Diisi Bertahap)

Entri di bawah ini adalah pola eksploitasi nyata yang telah digeneralisasi. Pakai pada Tahap B Fase 2: cocokkan **Kondisi Prasyarat** dan **Gejala di Kode** dengan fungsi yang sedang dibedah.
Indeks seluruh POV lintas file: `references/ref-attacker-pov.md`.

### [POV-02] Cross-Contract / Read-Only State Desync Saat Callback di Tengah Operasi

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

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika seluruh mutasi state internal dan akuntansi bersama diselesaikan 100% sebelum interaksi eksternal (CEI murni), atau jika terdapat *global reentrancy lock* yang juga diperiksa oleh seluruh fungsi pembaca (view check).

---

### [POV-05] Isolated Subcall (try/catch / Low-Level Call) State-Divergence & Returnbombing

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

- **Batas Realitas (Kapan Pola Ini GUGUR):**
  Gugur jika target panggilan adalah kontrak internal/tetap yang *immutable* dan tidak meneruskan eksekusi ke alamat pengguna, serta mutasi state pada cabang sukses maupun gagal tetap mempertahankan invarian akuntansi yang setara.

---

<!-- Sisipkan [POV-06], [POV-07], dst. di BAWAH baris ini, urut menaik -->
