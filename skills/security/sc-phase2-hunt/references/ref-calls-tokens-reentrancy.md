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
