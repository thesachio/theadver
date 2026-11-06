# FACTS — Fakta Mekanisme Proyek (hidup, terverifikasi)

Berisi **fakta tentang bagaimana proyek bekerja**, yang membuat Fase 3 bisa merancang uji tajam.
Bukan hipotesis, bukan status deployment, bukan catatan aktivitas.

> **Mengapa file ini ada.** `00-project-map.md` ditulis di Fase 1, sebelum ada yang benar-benar
> memahami proyek. Pemahaman terdalam muncul saat membedah unit di Fase 2 — dan dulu hilang
> bersama konteks. Akibatnya Fase 3 merancang harness dari peta basi.
> Bukti: di Across `02-state-and-var-matrix.md` terakhir disentuh 09:20, eksplorasi berjalan
> sampai 15:01 (5 jam 41 menit) tanpa satu pun pembaruan pemahaman.

---

## HUKUM

1. **FAKTA SAJA.** Uji setiap kalimat: *"apakah ini tetap benar walau kontrak tidak punya bug?"*
   - **Ya** → boleh masuk FACTS.
   - **Tidak** (hanya masuk akal bila ada celah) → itu hipotesis, tempatnya `05-raw-leads.md`.
2. **DILARANG memuat status deployment.** `CYCLE`, `ENTRYPOINT`, `Mode Uji`, `FORK_LIVE`,
   `LIVE_MATCH`, hash/identitas live → **milik `notes/deploy-parity-<ID>.json`** dan field
   `Deployment` di `05`. Jangan disalin ke sini; rujuk artefaknya.
3. **`patch` per baris.** Dilarang tulis ulang penuh (`open("w")`/`>`). Maks **12 baris per
   domain**, tambahan **≤3 baris per unit**.
4. **`UNKNOWN` wajib ditulis**, bukan dihilangkan. Fakta yang tidak diukur adalah titik buta —
   dan titik buta sering justru celahnya.
5. **Maksimal 2 `M-FACT` per unit.** Pilih yang paling mengubah cara menguji, bukan yang paling banyak.
6. **Gerbang masuk:** fakta hanya layak bila *"tanpa fakta ini, Fase 3 akan merancang uji yang berbeda?"*
   - `relayerFeePct int64` → ya (batas tipe) ✅
   - `quoteTimestamp uint32, satuan DETIK` → ya (detik vs ms = 1000×) ✅
   - `fungsi ada di baris 340` → tidak ❌
   - `memakai SafeERC20` → tidak ❌

---

## BENTUK BLOK (7 komponen wajib)

```markdown
## D3: chain-adapters
BERKAS    : contracts/chain-adapters/*.sol, contracts/hub-pool/HubPool.sol (delegatecall)
MEKANISME : adapter dipanggil HubPool via delegatecall; alamat adapter dibaca dari
            storage HubPool, bukan parameter → HubPool.sol:678
CHAINING  : deposit(SpokePool.sol:812) → fill → proposeRootBundle(:560)
            → executeRootBundle(:612) → adapter.bridge
            state bertahan lintas-hop:
              unclaimedPoolRebalanceLeafCount  HubPool.sol:653
              claimedBitMap                    HubPool.sol:650
DATA      : amount uint256 (desimal token asal) · relayerFeePct int64
            quoteTimestamp uint32 — SATUAN: DETIK, bukan ms · recipient bytes32
            sentinel sah: amount=0, feePct=±int64.max, timestamp=0
INVARIAN  : tiap leaf dieksekusi sekali — ditegakkan _setClaimed1D HubPool.sol:650
INVARIAN  : total bridged ≤ pooledTokens — TIDAK ditegakkan
LINGKUNGAN:
  [ETH:0x5c7B..35C5] proxy admin = EOA (bukan kontrak) | cast code → 0x | @19.2M | VERIFIED
  [ETH:0x5c7B..35C5] paused = false | paused() → false | @19.2M | VERIFIED
  [ARB:0xD1..aa] proxy admin = 3-of-5 multisig | threshold() → 3 | @521M | VERIFIED
ASUMSI    : [A] desimal semua token 6 atau 18 — BELUM diverifikasi
```

**`BERKAS` wajib** — ini satu-satunya kunci yang membuat Fase 3 bisa menemukan blok dari
`File:Baris` lead. Tanpa itu, blok tidak bisa dicari dan model tidak terpakai.

---

## PROTOKOL PENEMUAN (bagaimana fakta dicari)

| Komponen | Pertanyaan pemandu | Cara mencari | Bukti wajib | Metode |
|---|---|---|---|---|
**MEKANISME** | *Siapa bisa memanggil ini, lewat pintu mana?* | baca fungsi **utuh** (A0); catat modifier, `msg.sender`, `delegatecall`/`call` keluar | `File:Baris` tiap entrypoint + guard | M-001, M-008 |
**CHAINING** | *Setelah fungsi kembali, state apa yang tertinggal — dan siapa membacanya?* | tiap variabel yang **ditulis**, lacak pembacanya (`grep` nama variabel) | `penulis :X` → `pembaca :Y` | M-009, M-002 |
**DATA** | *Tipe apa, satuan apa, sentinel apa?* | signature + struct + constant; cari `mulDiv`, `1e18`, `10**`, `block.timestamp` | deklarasi tipe + baris konversi | M-007, M-004 |
**INVARIAN** | *Apa yang harus selalu benar sesudah ini?* | cari `require`/`assert` yang mengikat **relasi antar-state** | `File:Baris` penegak, atau `TIDAK ditegakkan` | M-002, M-005 |
**LINGKUNGAN** | *Siapa pemegang otoritas, sekuat apa?* | `cast code` admin (kontrak?), `threshold()`, `paused()`, `delay()` | perintah + hasil + **blok** + status | `deploy_parity.py` (alamat) |
**ASUMSI** | *Apa yang saya andalkan tapi belum saya periksa?* | catat setiap "karena X, maka Y" tanpa bukti | `BELUM` / `VERIFIED` / `GUGUR` | — |

**Metode bukan pekerjaan tambahan** — FACTS memanen hasil `M-001..M-NNN` yang sudah dijalankan
di Fase 2. Tidak ada langkah baru, hanya pencatatan hasil.

### Tiga titik waktu
1. **Sebelum unit** — baca blok domain yang ada, tulis **prediksi**: *"invarian apa yang saya
   harap ditegakkan di sini, di mana kemungkinan patah?"*
2. **Saat unit** — kumpulkan fakta; tulis sebagai `M-FACT` di staging (blok `USULAN`), bukan langsung ke FACTS.
3. **Sesudah unit** — bandingkan prediksi vs temuan. Prediksi **meleset** → fakta penyebabnya
   wajib masuk. Prediksi **tepat** → jangan tambah baris.

### Batas pelacakan `CHAINING`
Lacak hanya berkas `[MUST-AUDIT]` (bukan `lib/`), hentikan setelah **2 hop**.
Lebih dari itu → tulis `CHAINING: >2 hop, belum ditelusuri` dan daftarkan sinyalnya ke `RADAR`.

---

## PROTOKOL AKSES (bagaimana Fase 3 memakainya)

Fase 3 bekerja dari **`File:Baris`**, bukan dari nama domain:

```bash
# 1. Cetak blok domain yang memuat path berkas lead (berhenti di heading berikutnya)
awk -v pat="<NamaBerkas>.sol" '/^## D/{if(hit){print head;printf "%s",buf;done=1;exit} head=$0;buf="";hit=0;next}{buf=buf $0 ORS; if(index($0,pat))hit=1} END{if(hit&&!done){print head;printf "%s",buf}}' audit/FACTS.md

# 2. RADAR yang menyentuh berkas yang sama (seam yang mungkin memperkuat)
grep -n -B1 -A8 "<NamaBerkas>.sol" audit/RADAR.md

# 3. RADAR yang menyebut lead/unit ini
grep -n "<LEAD-xx>\|S-<nn>" audit/RADAR.md

# 4. Entri lead lengkap
grep -n -A10 "^## \[<LEAD-xx>\]" audit/05-raw-leads.md
```

Total ±400–600 token — cukup untuk menyusun harness tanpa memuat seluruh audit.

### Pemetaan komponen → rancangan serangan

| Komponen | Yang dilakukan Fase 3 |
|---|---|
`MEKANISME` | pilih **entrypoint** + **siapa penyerang** → `vm.prank(attacker)` tepat |
`CHAINING` | rancang **uji multi-langkah**: state apa di-seed di hop 1 agar hop 3 rentan |
`DATA` | susun **korpus fuzz**: limit tipe, desimal, satuan waktu, sentinel |
`INVARIAN` | jadi **assertion test**; yang `TIDAK ditegakkan` = target utama |
`LINGKUNGAN` | tentukan apakah `ADMIN_ONLY`/privilese — **bukan** menentukan `Mode Uji` |
`ASUMSI` | urutan verifikasi: `BELUM` diperiksa dulu; `GUGUR` → lead baru |

### Pemetaan RADAR → kombinasi
| Kondisi | Tindakan |
|---|---|
`Lokasi` beririsan dengan lead | uji **kombinasi** — seam itu mungkin yang membuat lead bisa dieksploitasi |
`Tujuan` = unit lead ini | sinyal unit lain yang bertemu di sini |
`Pemicu` terpenuhi | promosikan saat itu juga, uji bersamaan |
`RESOLVED-REFUTED` + alasan | hindari mengulang jalan buntu yang sama |

### Bila blok FACTS tidak ada untuk domain lead
Fase 3 **wajib backfill dulu**: baca fungsi utuh → tulis blok 12 baris → baru menulis harness.
Dilarang menulis harness tanpa blok — itu menguji tanpa tahu mekanismenya.

---

## ANTI-POLA (dilarang)

| Anti-pola | Mengapa |
|---|---|
Menulis *"mungkin bisa di-reentrancy"* | hipotesis → tempatnya `05`, bukan FACTS |
Menyalin `CYCLE`/`ENTRYPOINT`/`Mode Uji` | duplikasi dengan `deploy-parity-*.json` |
`LINGKUNGAN` tanpa tag `[chain:alamat]` | akan terbawa ke chain lain → vonis palsu |
Menghilangkan fakta yang tidak diketahui | Fase 3 akan menganggapnya tidak ada; tulis `UNKNOWN` |
Menambah 10 baris per unit | batas 3. Model bengkak = tidak terbaca = nol |
Menyalin fakta dari `00 §4` | `00` baseline Fase 1; bila berbeda, **FACTS menang** (lebih baru) |

---

## Hubungan dengan wadah lain

| Wadah | Pertanyaan | Sifat |
|---|---|---|
| `audit/FACTS.md` | *bagaimana cara kerjanya, apa yang seharusnya?* | hidup, `patch` |
`audit/RADAR.md` | *apa yang janggal tapi belum terbukti?* | hidup, `append` |
`audit/05-raw-leads.md` | *hipotesis mana yang harus diuji?* | antrean |
`notes/deploy-parity-*.json` | *kode ini live atau HEAD?* | per-lead |
`audit/00-project-map.md` | baseline Fase 1 (beku) | arsip |
