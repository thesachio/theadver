# Katalog Generalized Attacker POV — Domain Matematika, Pembulatan, & Akuntansi Share (`[POV-MATH-XX]`)

Berkas ini menyimpan pola eksploitasi on-chain nyata pada domain matematika/vault yang telah digeneralisasi.
- **Indeks & Router Gejala:** `references/ref-attacker-pov.md`
- **Checklist Prinsip Dasar:** `references/ref-math-and-vaults.md`

---

### [POV-MATH-01] Desinkronisasi Indeks Akrual pada Transfer/Mutasi Pokok
- **Target Kelas:** `[CLASS-B]` *(Dual-Entity: interaksi antara 2 identitas akun `from` <-> `to` terhadap state kontrak)*
- **Metode Terkait:** `M-002` (State-Transition Differential), `M-003` (Multi-Identity Sybil), `M-006` (Stale Snapshot)
- **Gejala Pemicu di Kode (Trigger Symptom):** Kontrak melacak `globalIndex` & `userIndex[u]` DAN memiliki fungsi pemindah saldo/posisi antar-akun (`transfer`, `transferFrom`, `delegate`, `migrate`, `merge`) di luar fungsi deposit/withdraw tunggal.
- **Kondisi Prasyarat (State Condition):**
  Kontrak melacak pertumbuhan hak/bunga/kewajiban menggunakan indeks global (`globalIndex`) dan titik catat per akun (`userIndex[u]`), serta memiliki fungsi pemindahan saldo/posisi antar-akun (pemindahan, delegasi, migrasi, atau penggabungan posisi) di luar fungsi masuk/keluar tunggal.
- **Kacamata Attacker (Gejala di Kode):**
  Fungsi pemindahan mengubah saldo akun pengirim (`from`) dan penerima (`to`) — atau menyalin saldo ke variabel memori sementara sebelum ditulis balik — tetapi tidak menyinkronkan/mengklaim hak tertunda pada KEDUA akun sebelum saldo berubah, atau tidak menolak kondisi `from == to`.
- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** `Attacker_A` mengakumulasi selisih indeks yang belum diklaim (`globalIndex > userIndex[Attacker_A]`), sementara `Attacker_B` memiliki `userIndex` lama yang rendah.
  2. **[Pemicu Asimetri]** `Attacker_A` memindahkan saldo pokok ke `Attacker_B` (atau memindahkan ke dirinya sendiri `Attacker_A -> Attacker_A` bila kontrak memakai variabel memori sementara).
  3. **[Ekstraksi Nilai]** Akun penerima mengeklaim hak penuh menggunakan saldo baru dikalikan selisih indeks lama, lalu mengembalikan pokoknya untuk diulang (*loop*).
- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor memeriksa fungsi masuk, keluar, dan klaim utama (1-aktor) lalu melihat ketiganya sudah memanggil modifier/fungsi penyinkron indeks untuk `msg.sender`. Auditor lupa bahwa penyinkron 1-argumen tersebut tidak memperbarui akun kedua (`to`) pada fungsi 2-aktor, atau luput melihat variabel memori yang saling menimpa saat `from == to`.
- Batas Realitas (Kapan Pola Ini GUGUR) & Routing Simulasi Fase 3:
  - *Batas Realitas:* **DILARANG gugur tanpa test.** Gugur (`REJECTED_POC_FAILS`) **hanya setelah simulator membuktikan** bahwa, meskipun sinkronisasi indeks dipanggil untuk kedua akun, hasil `pendingReward(from) + pendingReward(to)` dan `balances` **identik 100%** dengan eksekusi referensi pada seluruh kondisi batas (`reward == 0`, `from == to`, `globalIndex` berubah di tengah) — buktikan dengan **Strike 3 Fuzz** (`testFuzz_`) yang mengacak `lastAccrualTime`, `globalIndex`, dan urutan sinkronisasi. Klaim "kode sudah menyinkronkan kedua akun" **BUKAN** bukti sah untuk menggugurkan (`REJECTED_MISMATCH` hanya sah bila `File:Baris` yang diklaim benar-benar tidak memuat fungsi pemindah — bukan karena kode terlihat benar).
  - *Routing Simulasi Fase 3:* Jika sinkronisasi indeks berada di dalam **cabang kondisional (`if`)**, hanya menyinkronkan **salah satu akun**, memakai **struct/variabel memori lokal**, atau **tidak memiliki `require(from != to)` eksplisit**, **DILARANG menggugurkan di atas kertas** — WAJIB langsung tulis **PoC 2-Identitas** (`Attacker_A -> Attacker_B`) dan **Self-Transfer** (`Attacker_A -> Attacker_A`) di simulator!

---

### [POV-MATH-02] Inverse-Function Rounding & Multi-Hop Fee Truncation
- **Target Kelas:** `[CLASS-A]` *(Single-Entity: asimetri rumus di dalam 1 entitas)*, dapat dirangkai ke `[CLASS-B]`/`[CLASS-C]`
- **Metode Terkait:** `M-001` (Backward Sink-to-Source), `M-004` (View-vs-Write Asymmetry), `M-007` (Split-vs-Bulk)
- **Gejala Pemicu di Kode (Trigger Symptom):** Kontrak menyediakan pasangan fungsi konversi dua arah (*Exact-Input* seperti `deposit`/`swapExactIn` vs *Exact-Output* seperti `mint`/`withdraw`/`swapExactOut`) ATAU menghitung proporsi/fee melalui $\ge 2$ tahap pembagian integer beruntun.
- **Kondisi Prasyarat (State Condition):**
  Kontrak menyediakan pasangan fungsi konversi dua arah — yaitu fungsi Berbasis Input Eksak (*Exact-Input*, pemanggil menentukan jumlah yang diserahkan, kontrak menghitung hasil) dan fungsi Berbasis Target Output Eksak (*Exact-Output*, pemanggil menentukan jumlah hasil yang diminta, kontrak menghitung balik beban biayanya) — atau melakukan konversi proporsi melewati $\ge 2$ tahap pembagian integer beruntun.
- **Kacamata Attacker (Gejala di Kode):**
  Meskipun fungsi searah (*Exact-Input*, mis. setor aset atau tukar share) sudah membulatkan ke arah yang menguntungkan protokol, fungsi kebalikannya (*Exact-Output*, mis. cetak share eksak atau tarik aset eksak) atau perhitungan potongan biaya perantara `(amount * feeBps / 10000) * totalShares / totalAssets` melakukan pembagian integer yang membulatkan ke bawah di langkah tengah sebelum pembulatan akhir.
- **Rangkaian Peristiwa Serangan (Generalized Event Sequence):**
  1. **[Siapkan State]** Penyerang mencari atau menciptakan rasio nilai tukar di mana total aset dan total pencatatan bagian (*shares/units*) tidak berkelipatan bulat sempurna.
  2. **[Pemicu Asimetri]** Penyerang memanggil fungsi *Exact-Output* berulang kali dengan nilai target kecil tepat di bawah ambang pembulatan (`M-007` — *Split-vs-Bulk*: $f(a) + f(b) < f(a+b)$).
  3. **[Ekstraksi Nilai]** Potongan biaya atau beban bagian yang harus dibakar terpangkas menjadi 0 atau berkurang 1 unit di setiap iterasi, lalu dilipatgandakan dalam satu transaksi batch/multicall.
- **Mengapa Lolos dari Auditor Biasa (Auditor Blindspot):**
  Auditor terpaku memeriksa fungsi *Exact-Input* utama serta proteksi pendeposit pertama (`totalSupply == 0`), lalu menganggap fungsi *Exact-Output* pasangannya sudah simetris tanpa menguji apakah pembagian antara (*intermediate division*) memotong penyebut atau biaya sebelum langkah pembulatan terakhir.
- Batas Realitas (Kapan Pola Ini GUGUR) & Routing Simulasi Fase 3:
  - *Batas Realitas:* Gugur jika seluruh tahap pembagian pada fungsi *Exact-Output* terbukti membulatkan beban pengguna ke atas (`Rounding.Up` / *ceil*) tanpa pemangkasan di langkah tengah, **DAN** setelah disimulasikan dengan *3-Way EV Amplification* + *Strike 3 Fuzzing* hasilnya tetap merugi (`REJECTED_DUST` / `REJECTED_NEGATIVE_EV`).
  - *Routing Simulasi Fase 3:* **DILARANG menghitung pembulatan di atas kertas lalu membuang ke `06`!** Wajib tulis fungsi `testFuzz_` di simulator yang menguji rasio pool tidak bulat dan membandingkan $N \times \text{aksi}(a)$ terhadap $1 \times \text{aksi}(N \cdot a)$. Hanya boleh masuk `06` bila log eksekusi test dan fuzz dilampirkan (`BUKTI_SIMULASI:` sesuai Pernyataan #11e).

---

## Penanda Sisipan Entri Baru (`[POV-MATH-03]` .. `[POV-MATH-NN]`)
*(Tambahkan entri baru di atas baris ini dengan 8 field wajib, lalu daftarkan 1 baris di `references/ref-attacker-pov.md`).*
