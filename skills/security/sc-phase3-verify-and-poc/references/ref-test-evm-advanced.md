# Referensi Pengujian Lanjut EVM & Tron TVM (Tier 1 s/d Tier 5)

Gunakan pola pengujian di bawah ini saat menyusun file AdvVerify_<Target>.t.sol di Foundry. Selalu jalankan dengan worker tunggal: forge test --match-contract AdvVerify_<Target> -vvvv -j 1.

---

## 1. TIER 1: Multi-Actor Sequence & Net-Profit Accounting Pattern
Gunakan pola ini untuk menguji urutan transaksi 3-langkah (Aktor A -> Aktor B -> Callback) dengan perhitungan keuntungan bersih yang jujur (tanpa curang memakai vm.deal sebagai klaim keuntungan):

    // Pola Struktur Tier 1 (Solidity Foundry):
    address attacker = makeAddr("attacker");
    address victim = makeAddr("victim");

    function test_AdvVerify_SequenceExploit() public {
        // 1. Berikan modal awal yang realistis dan catat saldo awal
        deal(address(token), attacker, 1000e18);
        uint256 initialBalance = token.balanceOf(attacker);

        // 2. Eksekusi aksi menggunakan prank murni sebagai attacker (BUKAN admin/owner!)
        vm.startPrank(attacker);
        // Langkah A: Masuk / Manipulasi state awal
        // Langkah C: Transisi / Transfer / Split / Callback
        // Langkah B: Keluar / Tarik klaim berlebih
        vm.stopPrank();

        // 3. Verifikasi Keuntungan Bersih (Net Profit) atau Patahnya Invarian
        uint256 finalBalance = token.balanceOf(attacker);
        assertGt(finalBalance, initialBalance, "INVARIANT BROKEN: Attacker gained net profit");
    }

---

## 2. TIER 2: Handler-Based Stateful Invariant Fuzzing + Ghost Variables
Gunakan pola ini ketika Fase 2 tidak menemukan bug kasatmata, agar mesin fuzzer mengacak urutan panggilan fungsi dan menguji apakah hukum kekekalan nilai patah:
// 1. Buat Kontrak Handler yang membungkus fungsi protokol & mencatat Ghost Variables:
    contract AdvProtocolHandler is Test {
        TargetProtocol public target;
        IERC20 public asset;
        uint256 public ghost_totalDeposited;
        uint256 public ghost_totalWithdrawn;
        address[] public users;

        constructor(TargetProtocol _target, IERC20 _asset) {
            target = _target;
            asset = _asset;
            users.push(makeAddr("user1"));
            users.push(makeAddr("user2"));
        }

        function handler_inflow(uint256 userIdx, uint256 amount) external {
            address user = users[bound(userIdx, 0, users.length - 1)];
            amount = bound(amount, 1, 1_000_000e18);
            deal(address(asset), user, amount);

            vm.startPrank(user);
            asset.approve(address(target), amount);
            target.deposit(amount, user);
            vm.stopPrank();

            ghost_totalDeposited += amount;
        }

        function handler_outflow(uint256 userIdx, uint256 shares) external {
            address user = users[bound(userIdx, 0, users.length - 1)];
            uint256 userShares = target.balanceOf(user);
            if (userShares == 0) return;
            shares = bound(shares, 1, userShares);

            uint256 balBefore = asset.balanceOf(user);
            vm.prank(user);
            target.redeem(shares, user, user);
            uint256 received = asset.balanceOf(user) - balBefore;

            ghost_totalWithdrawn += received;
        }
    }

    // 2. Di dalam Kontrak Test Utama, arahkan targetContract ke Handler:
    // targetContract(address(handler));
    // Lalu tulis fungsi invariant_:
    function invariant_ConservationOfAssets() public view {
        uint256 vaultBalance = asset.balanceOf(address(target));
        assertGe(
            vaultBalance + handler.ghost_totalWithdrawn(),
            handler.ghost_totalDeposited(),
            "INVARIANT BROKEN: Total withdrawn + vault balance exceeds deposits"
        );
    }

    function invariant_ShareAccountingConsistency() public view {
        uint256 sumShares = target.balanceOf(handler.users(0)) + target.balanceOf(handler.users(1));
        assertEq(sumShares, target.totalSupply(), "INVARIANT BROKEN: Share sum mismatch");
    }

---

## 3. TIER 3: Differential & Round-Trip Symmetry Fuzzing
Gunakan untuk membongkar kesalahan pembulatan (*rounding direction*) atau *custom math library*:

    // 1. Round-Trip Test (Deposit lalu langsung Redeem tidak boleh menghasilkan > amount awal):
    function testFuzz_RoundTripDepositRedeem(uint256 amount) public {
        amount = bound(amount, 1, 100_000_000e18);
        deal(address(asset), attacker, amount);

        vm.startPrank(attacker);
        asset.approve(address(vault), amount);
        uint256 shares = vault.deposit(amount, attacker);
        uint256 assetsBack = vault.redeem(shares, attacker, attacker);
        vm.stopPrank();

        assertLe(assetsBack, amount, "ROUNDING BUG: User extracted free assets via deposit->redeem");
    }

    // 2. Differential Test (Bandingkan fungsi Math Kustom Kontrak vs Perhitungan Referensi):
    function testFuzz_DifferentialCustomMath(uint128 a, uint128 b) public {
        vm.assume(b > 0);
        uint256 actual = CustomMathLib.optimizedMulDiv(a, b);
        uint256 expected = (uint256(a) * uint256(b)) / 1e18;
        assertEq(actual, expected, "MATH DIVERGENCE DETECTED");
    }

---

## 4. TIER 4: Ephemeral Local Read-Only Fork & Stress Simulation
Jika URL RPC tersedia di .env atau foundry.toml:
- Gunakan vm.createSelectFork(vm.envString("RPC_URL")) di dalam setUp().
- Uji integrasi nyata dengan token seperti USDC (6 desimal), USDT, atau Oracle Chainlink/Uniswap V3 Pool tanpa pernah mengirim transaksi keluar.
- Simulasikan skenario *Flash Loan* lokal dan uji apakah manipulasi cadangan spot di dalam 1 transaksi mampu mengelabui perhitungan harga atau kesehatan agunan kontrak target.

---
## 5. TIER 5: Symbolic Execution & Formal Counterexample (Halmos)
Jika fuzzer acak tidak menemukan angka spesifik pemicu bug pada rumus matematika rumit:
- Buat fungsi dengan awalan check_ (misal function check_NoRoundingProfit(uint256 amount) public).
- Gunakan vm.assume(amount > 0 && amount < type(uint128).max).
- Jika halmos terpasang di sistem, jalankan halmos --function check_NoRoundingProfit untuk membuktikan secara simbolik (SMT Solver) apakah ada satu nilai amount yang melanggar assert(assetsOut <= amount).
