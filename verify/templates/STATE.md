# AUDIT EXECUTION STATE (CHECKPOINT)

- Target Repo: <nama_repo_atau_path>
- Last Updated: <timestamp_atau_step>
- Active Phase: PHASE_0_INTEL | PHASE_1_RECON | PHASE_2_HUNT | PHASE_3_VERIFY | PHASE_4_VERDICT
- Active Sub-Stage: STEP_0_PROJECT_INTEL | STEP_0_INVENTORY | ROUND_1_MICRO | ROUND_2_MACRO | STEP_0_BATCH | POC_EXECUTION

## 1. Cursor Position (Titik Lanjut Eksak)
- Last Completed Item: S-07 (Domain: spoke-pools) -> Hasil: ATTESTED_CLEAN + LEAD-09
- CURRENT_ACTIVE_ITEM: S-08 (Domain: chain-adapters)
- Active Files in Scope: WormholeAdapter.sol, BridgeRelay.sol
- Active Strike Count (Fase 3): 0/3 (2 Manual + 1 Mandatory Fuzz; kosongkan jika masih di Fase 2)
- Cognitive Load (Fase 3): NORMAL | FATIGUE (≥2 kegagalan mekanis berturut) -> WAJIB checkpoint & sesi baru
- Lead Sequence Basis: EV_DESC (lead EV tertinggi WAJIB dikerjakan paling awal, bukan di ekor)

## 2. Domain Coverage Meter (Syarat Gate = 100% `[MUST-AUDIT]`)
| Domain | Total [MUST-AUDIT] | Selesai (Lead/Attested) | Persentase | Status |
|---|---|---|---|---|
| D1: hub-pool | 18 | 15 | 83% | PASS |
| D2: spoke-pools | 24 | 20 | 83% | PASS |
| D3: chain-adapters | 30 | 12 | 40% | IN_PROGRESS |
| D4: SVM | 14 | 0 | 0% | PENDING |

## 3. Working Memory Scratchpad (Maks 10 Baris — Konteks Sementara Unit Aktif)
- Di WormholeAdapter.sol:L142, payload pesan didekode tanpa cek sourceChainId di fungsi hilir.
- Baru selesai cek Metode 1, 2, 3. Saat resume, langsung lanjut ke Metode 6 & 7 pada S-08.

## 4. Do-Not-Reopen List (Sudah Final, Dilarang Dibaca Ulang)
- Completed Units: S-01, S-02, S-03, S-04, S-05, S-06, S-07
- Dead-End Leads (06): LEAD-01, LEAD-02, LEAD-04, LEAD-06
- Verified Leads (08): LEAD-03, LEAD-05

---

## 5. Aturan Pengisian (hapus bagian ini saat disalin ke proyek)

- **Cursor Position** — hanya SATU item aktif. `Active Files in Scope` wajib berisi path nyata dari berkas di dalam unit tersebut, bukan nama generik.
- **Domain Coverage Meter** — angkanya HARUS bisa direproduksi dari `00b-file-inventory.md` + tabel cakupan `03-attack-surface-queue.md`. Jangan menulis persentase perkiraan.
- **Working Memory Scratchpad** — maksimal 10 baris, hanya untuk unit aktif. Temuan yang sudah final pindah ke `05-raw-leads.md`, bukan ditinggal di sini.
- **Do-Not-Reopen List** — tulis ID saja beserta kelas vonisnya. Alasannya ada di `06` / `08`; jangan diduplikasi di sini.
- **Write-Ahead Rule** — perbarui file ini SEBELUM memulai item berikutnya, bukan sesudah selesai.
- **Bila Fase 3** — `Active Strike Count` **wajib diisi** (`0/3`, `1/3`, `2/3`, `3/3`); sebuah lead **DILARANG** dipindah ke `06` sebagai `REJECTED_POC_FAILS` / `REJECTED_NEGATIVE_EV` / `REJECTED_DUST` sebelum mencapai **3/3** (**Strike 1** Manual + *Victim Seeding*, **Strike 2** Perbaikan Urutan + *3-Way Amplification*, dan **Strike 3** Mandatory Fuzzing `testFuzz_`/`proptest`/`halmos`) beserta lampiran log di `BUKTI_SIMULASI:` (#11e).
- **Cognitive Load** — isi `FATIGUE` begitu terjadi **≥2 kegagalan mekanis berturut-turut** dalam satu sesi (patch/`old_string` gagal berulang, salah baca statis yang langsung terbantah, atau kontradiksi dengan kesimpulan sendiri sebelumnya). Saat `FATIGUE`, **DILARANG** memulai lead baru: tulis checkpoint ini lalu lanjutkan di sesi baru. Alasan: ketajaman penalaran menurun seiring panjang sesi, dan lead yang dikerjakan di ekor sesi dinilai paling rendah (`sc-phase3` Langkah 2 — Urutan Eksekusi PoC).
- **Lead Sequence Basis** — `EV_DESC` wajib. Meletakkan lead EV tertinggi di akhir antrean ("nanti saja karena besar") adalah pelanggaran, karena lead terbaik akan diuji saat ketajaman paling rendah. Aktivitas non-penemuan (setup build, remapping, debug tooling, RPC) **tidak** boleh menggeser lead ber-EV tinggi ke ekor.
