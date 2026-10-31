# Referensi Pengujian Lanjut Non-EVM (Tier 6: Solana, Sui/Aptos Move, & TON Async)

Gunakan panduan ini saat membuktikan hipotesis atau menguji invarian pada rantai Solana, Sui/Aptos, dan TON.

---

## 1. SOLANA (Rust / Anchor / LiteSVM / ProgramTest / Kani)
Jalankan pengujian dengan worker tunggal: cargo test <nama_test> -j 1 -- --nocapture.

1. Pengujian Spoofing `ctx.remaining_accounts` & Substitution:
   - Buat 2 Pool berbeda di dalam test: Pool_Utama (berisi likuiditas besar) dan Pool_Palsu (dibuat oleh attacker dengan token tidak berharga).
   - Buka posisi/tick di Pool_Palsu, lalu panggil instruksi pada Pool_Utama dengan menyisipkan akun posisi/tick milik Pool_Palsu ke dalam vektor remaining_accounts.
   - Periksa apakah instruksi berhasil dieksekusi tanpa *revert* (ConstraintHasOne / InvalidAccountData).

2. Pengujian Missing `.reload()` Pasca-CPI:
   - Panggil instruksi yang memicu CPI transfer/mint token di tengah fungsi lalu menghitung rasio atau batas penarikan setelahnya. Verifikasi apakah perhitungan pasca-CPI membaca saldo basi.

3. Rust Symbolic Proof / Property Testing (Kani / Proptest):
   - Untuk fungsi matematika di dalam crate Rust (perhitungan bunga, *bonding curve*, atau *bit shift*), tulis unit test di dalam modul #[cfg(test)] yang menguji batas u64::MAX, u128::MAX, dan pembagian menghasilkan 0.

---

## 2. SUI & APTOS (Move test_scenario Multi-PTB & Move Prover)
Jalankan pengujian dengan: sui move test <nama_test> atau aptos move test.

1. Simulasi Multi-Command Programmable Transaction Block (PTB) & Hot Potato:
   - Gunakan sui::test_scenario untuk menyimulasikan 1 transaksi PTB yang memanggil beberapa fungsi publik secara berangkai tanpa kontrak perantara:

    #[test]
    fun test_adv_verify_cross_pool_or_hot_potato() {
        let admin = @0xAD;
        let attacker = @0xCAFE;
        let mut scenario = test_scenario::begin(admin);

        // Setup Pool A (Target) dan Pool B (Attacker Pool)
        test_scenario::next_tx(&mut scenario, attacker);
        {
            // Dalam 1 blok PTB:
            // 1. Pinjam Hot Potato / Receipt atau buat Position di Pool B
            // 2. Coba gunakan Position / Receipt tersebut pada fungsi di Pool A
            // 3. Verifikasi apakah assert!(pool_id == object::id(pool)) absen!
        };
        test_scenario::end(scenario);
    }

2. Pengujian Bitwise Shift Overflow (`<<` / `>>`) & Custom CLMM Math:
   - Tulis #[test] yang memasukkan nilai tepat di batas bit tinggi (misal (1u128 << 64) + 1 atau nilai mendekati mask maksimum pada fungsi checked_shlw / mul_shr) untuk membuktikan apakah bit teratas terpotong secara diam-diam tanpa memicu abort.

---

## 3. TON (FunC / Tact / Tolk — @ton/sandbox & Blueprint Jest)
Jalankan pengujian dengan: npx jest <nama_test> --runInBand atau npx blueprint test.
1. Simulasi Kegagalan Hilir & Batas 256-Bit Handler `bounced`:
   - Di dalam @ton/sandbox, kirim pesan dari attacker ke ContractA yang mengubah state di ContractA dan meneruskan pesan ke ContractB.
   - Buat pesan ke ContractB gagal (*bounce*), lalu periksa transaksi di dalam result.transactions:
     *(a)* Apakah ContractA memulihkan saldo/state ke kondisi semula saat menerima pesan bounced?
     *(b)* Apakah data krusial (jumlah token / alamat penerima) yang ditaruh setelah bit ke-224 atau di dalam referensi cell gagal terbaca saat bounced?

2. Simulasi Kekurangan Gas di Tengah Rantai Pesan (`msg_value` Exhaustion):
   - Kirim transaksi multi-hop dengan nilai value: toNano('0.03') (cukup untuk melewati Kontrak Pertama, tetapi kurang untuk membiayai *forward fee* di Kontrak Kedua).
   - Periksa apakah Kontrak Pertama sudah telanjur mengurangi/menambah state permanen sementara pesan berhenti di tengah jalan!

3. Simulasi Async Race Condition & Fake Jetton Spoofing:
   - Kirim pesan transfer_notification (op 0x7362d09c) langsung dari dompet attacker (bukan dari kontrak JettonWallet resmi milik protokol) ke kontrak target. Periksa apakah kontrak target menolak pesan tersebut dengan exit code error otorisasi, atau justru tertipu dan mengkreditkan saldo palsu!
