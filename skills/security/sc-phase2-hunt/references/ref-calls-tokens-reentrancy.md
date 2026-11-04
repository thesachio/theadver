# Reference: Execution Control Handoff, Authorities, & External Entities

> ATURAN REALITAS PRODUKSI (WAJIB DIBACA SEBELUM MENGGUNAKAN KAMUS INI!):
> Jangan pernah menerapkan daftar periksa token di bawah ini secara membabi buta! Selalu cek Kasta Realitas Aset di audit/01-threat-and-env.md:
> 1. LP Token / Share Token / Token Internal (Kasta 1): ADALAH ERC-20 STANDAR. DILARANG KERAS membuat hipotesis bahwa LP Token atau token internal memiliki *Fee-on-Transfer*, *Rebase*, *Callback*, atau berperilaku seperti USDT!
> 2. Token Whitelist Produksi (Kasta 2): Gunakan 100% sifat nyata di produksi dari token yang benar-benar di-whitelist protokol! Menguji perilaku asli token Kasta 2 **BUKAN Fantasy Mock**, melainkan **FAKTA PRODUKSI yang WAJIB diuji**:
>    - **USDT**: desimal 6, *blacklistable*, tidak mengembalikan `bool` pada `transfer`, dan `approve(spender, newAmount)` akan `revert` jika `allowance` saat ini `!= 0` (wajib `approve(0)` dulu / `forceApprove`), meskipun biaya transfernya saat ini 0.
>    - **USDC**: desimal 6, *blacklistable*, dan *pausable* (dapat memicu Push-Payment DoS pada likuidasi/batch).
>    - **stETH / rETH / aTokens / Rebasing & Shares-Token**: kehilangan 1–2 wei saat transfer akibat pembulatan *shares-to-balance* (*1-wei corner case* yang merusak asumsi `balanceAfter == balanceBefore + amount`).
>    - **ERC-777 / Token Ber-Hook / SPL Token-2022**: memiliki hook `tokensReceived` atau ekstensi *Transfer Fee* / *Transfer Hook* aktif jika memang termasuk aset yang didukung protokol.
>    - **PAXG / Token Emas/RWA Berbiaya**: memiliki potongan *on-chain transfer fee* nyata di mainnet.
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
- **Callback & Hook Initiator Spoofing** (`onFlashLoan`, `swapCallback`, `onERC721Received`, `lzReceive`):
  - Ketika sebuah fungsi callback sudah memvalidasi `msg.sender == officialPool` / `officialVault` / `officialEndpoint` (permission yang tidak bisa dimanipulasi), **JANGAN berhenti!** Periksa apakah fungsi tersebut **juga** memvalidasi `initiator == address(this)` (atau operator / `srcSender` yang sah)! Jika tidak, penyerang *permissionless* dapat meminjam flashloan / melakukan swap pada Pool resmi dengan **mengarahkan callback ke kontrak protokol ini** untuk menguras dana atau memanipulasi state!
- **Cross-Whitelist / Factory Instance Confusion**:
  - Ketika fungsi memeriksa apakah sebuah alamat parameter (`pool`, `vault`, `oracle`, `adapter`) terdaftar di `isWhitelisted[target]` atau dibuat oleh Factory resmi, periksa apakah kontrak **juga** memverifikasi bahwa aset dasar (`underlying`/`token0`/`token1`/`marketId`) dari instansi tersebut **cocok dengan aset yang sedang ditransaksikan**! Tanpa validasi ikatan aset, penyerang dapat mengoper `Pool_Terdaftar_A` (mis. pool token murah/berdesimal beda yang sah di whitelist) saat bertransaksi pada `Aset_B`.
## 3. Asimetri Aliran Aset (Hanya Jika Sesuai Kasta Realitas Aset!)
- Sabotase Penolakan Penerimaan (Push-Payment DoS): Pada fungsi kritikal seperti likuidasi, lelang, pelunasan pinjaman NFT, atau pembagian hadiah berantai, apakah pengiriman dana/aset dilakukan secara *push* ke alamat pihak lawan yang bisa menolak penerimaan (melalui fallback revert atau akun yang masuk daftar *blacklist* USDC/USDT) sehingga memblokir seluruh transaksi?
- Kebingungan Standar & Alamat Aset (Token Confusion): Pada protokol yang mendukung berbagai jenis aset (Native ETH, ERC-20, ERC-721, ERC-1155), bisakah pengguna memasukkan alamat kontrak dari tipe standar yang salah atau memasukkan amount vs tokenId secara tertukar?
- Akuntansi Aktual vs Input Parameter (Khusus Kasta 2/3 yang Terbukti Mendukung FoT/Deflasi): Hanya jika protokol secara eksplisit mengizinkan token *Fee-on-Transfer* tanpa *whitelist* ketat dan berinteraksi dengan pool bersama, periksa apakah kontrak mencatat amount parameter input alih-alih selisih balanceOf sebelum dan sesudah transfer.
- **Kegagalan `approve` Non-Zero & Selisih 1-Wei Rebasing pada Kasta 2**: Jika protokol melakukan `token.approve(target, amount)` terhadap **USDT** tanpa me-reset ke 0 terlebih dahulu, atau menuntut kesamaan eksak `balanceBefore + amount == balanceAfter` pada token seperti **stETH/aToken**, tandai sebagai kandidat bug **DoS / akuntansi yang valid!**

---

---
## Katalog Generalized Attacker POV & Auditor Blindspots (Modular Lazy-Load)
Untuk mencocokkan gejala kode dengan pola serangan on-chain nyata tanpa membebani konteks:
1. Periksa **Tabel Router Gejala Kode** di `references/ref-attacker-pov.md`.
2. Jika gejala pemicunya cocok dengan fungsi yang sedang dibedah, muat katalog lengkapnya di `references/ref-pov-call.md`.
