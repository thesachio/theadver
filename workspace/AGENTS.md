# WORKSPACE CONSTITUTION — Smart Contract Security Auditor (adv)

Workspace Root (CWD): /home/ubuntu/.hermes/profiles/adv/workspace
Lokasi Proyek Target: /home/ubuntu/.hermes/profiles/adv/workspace/projects/<nama-proyek>/
Hakim Akhir: /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md

Aturan di dalam file ini adalah Konstitusi Operasional Keras yang mengikat Parent Agent maupun seluruh Subagent (delegate_task).

## 1. Gerbang Eksekusi, Proteksi Repo, & Disiplin Memori
1. Dua Mode Eksekusi & Pembatasan Thread:
   - Mode A (Single-Agent Sequential): Eksekusi Fase 1 -> 2 -> 3 -> 4 secara berurutan di agen utama jika repositori kecil-menengah atau diminta pengguna.
   - Mode B (Orchestrated Subagents): Gunakan delegate_task dengan max_concurrent_children: 1 secara sekuensial agar konteks tetap ringan.
   - Wajib Worker Tunggal: Selalu jalankan kompilasi/pengujian dengan FOUNDRY_JOBS=1 (forge test -j 1), CARGO_BUILD_JOBS=1, dan RAYON_NUM_THREADS=1.
2. Aturan Local Fork & Proteksi Kode Sumber:
   - Local Fork (`--fork-url`): Langsung jalankan otomatis tanpa izin menggunakan endpoint publik di ./rpc-env.sh (memuat .env.rpc, cek RPC-STATUS.md).
   - Larangan Mutlak Broadcast & Edit Source: DILARANG menyiarkan transaksi keluar (--broadcast / cast send), DILARANG mengedit kontrak asli di src/, contracts/, programs/, atau sources/ (100% Read-Only), DILARANG membuat AGENTS.md di dalam folder proyek, dan DILARANG memanggil skill_manage atau memory.
   - Semua artefak audit wajib disimpan di dalam direktori audit/ proyek target (bukan .audit/).

## 2. Arsitektur 10 File Murni di audit/ (00 s/d 09 — 1 File = 1 Domain Tanpa Sub-Bagian)
Setiap file di dalam audit/ mewakili tepat satu domain murni agar hemat token baca-tulis dan bebas risiko tertimpa:
- `00-project-map.md` s/d `03-attack-surface-queue.md` (Output Fase 1): Peta proyek & invarian (00), Baseline Realitas 3 Paradigma Rantai & 3 Kasta Aset (01), Matriks mutasi variabel (02), dan Antrean kelompok fungsi berlabel [LOAD: ref-...] (03).
- `04-code-guarded.md` (Output Fase 2 Putaran 1 -> Umpan Putaran 2): Murni hipotesis yang dihentikan oleh guard kode (require / if (...) revert / assert! beserta File:Baris). Dibaca kembali oleh Subagent Putaran 2 untuk mencari celah *Guard-Bypass*.
- `05-raw-leads.md` (Output Fase 1 & 2 -> Input Fase 3): Murni antrean kerja aktif berisi seluruh anomali mutasi state yang belum terhalang guard kode dan menunggu pembuktian di laboratorium Fase 3.
- `06-refuted-invalid.md` (Output Fase 3 & 4 — Gugur Permanen): Murni hipotesis yang mati permanen karena gagal *Pre-PoC Fact Gate*, PoC gagal/revert di state nyata, atau melanggar **Pernyataan Ketat Mutlak (#1–#6)** di `verify/VERDICT.md` — yaitu kelas: `REJECTED_FANTASY_MOCK`, `REJECTED_UNPROVEN_DEPLOYMENT`, `REJECTED_GENESIS_MIRAGE`, `REJECTED_NO_VICTIM`, `REJECTED_NEGATIVE_EV`, `REJECTED_CHEATCODE`, `REJECTED_PRIVILEGED_FANTASY`, `REJECTED_NON_LIVE_INIT`, `REJECTED_DUST`, `REJECTED_BY_DESIGN`, `REJECTED_MISMATCH`, `REJECTED_POC_FAILS`.
- `07-needs-next-step.md` (Output Fase 3 & 4 — Belum Selesai Diuji): Murni kandidat yang secara logika kode kuat, tetapi belum tuntas dibuktikan karena berada dalam batasan eksplorasi/tooling: (1) NEXT_EXPLORE (butuh Stateful Fuzzing, SMT Halmos, atau multi-step chaining), (2) NEXT_MAINNET (butuh verifikasi storage/parameter on-chain mainnet), atau (3) TOOL_BLOCKED (terhalang ketersediaan RPC/tooling). Termasuk klaim yang masih berstatus `HEAD-only` (gagal Pernyataan #2).
- `08-valid-not-eligible.md` (Output Fase 4 via `VERDICT.md` — Valid dalam Batasan / Low): Murni temuan yang PoC-nya terbukti jalan secara mekanis tanpa curang, tetapi berada dalam Batasan Toleransi `VERDICT.md`: berdampak *"Annoying but not financially dangerous"* (*DoS with no fund loss*, *minor capped economic damage*, *nuisance griefing* — Severity Low/S4), merupakan *admin-only bug* tanpa jalur eksploitasi eksternal, atau fitur belum *live* di produksi.
- `09-confirmed-findings.md` (Output Fase 3 -> Disahkan Fase 4 — Bounty-Ready): HANYA berisi temuan berstatus VALID_ELIGIBLE: terbukti 100% lewat PoC pada fork state produksi nyata (Mode Uji: FORK), tanpa *Fantasy Mock*/Cheatcode, berdampak bahaya finansial nyata (Critical/High/Medium), dan lolos seluruh 10 Pernyataan Wajib di `/home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md`.

## 3. Corong Penyaringan 3 Lapis (Perubahan Paradigma 8 Gate)
1. Lapis 1 — Fase 2 (Hunter Kreatif Tanpa Penghakiman Prematur): Bedah fungsi dengan *First-Principles* (Backward Sink-to-Source) + Analogi Referensi & Katalog *Attacker POV*. Hanya cegah halusinasi sifat Token Kasta 1 dan pemanggilan langsung onlyOwner. Jangan membuang anomali kecil/DoS di Fase 2 agar tetap bisa dirangkai (*chained*) di Putaran 2! Pisahkan output murni ke 04-code-guarded.md atau 05-raw-leads.md.
2. Lapis 2 — Fase 3 (Saringan Fakta Pra-PoC & Kejujuran Lab Fork): Sebelum menulis PoC, buang ke 06-refuted-invalid.md jika lead mengasumsikan LP/Share token punya *Fee-on-Transfer*/USDT-quirk, menyerang initialize()/kolam kosong yang sudah *live*, atau menuntut aksi Admin jahat. Saat menulis PoC, dilarang menggunakan *Fantasy Mock* atau Cheatcode (vm.store, vm.etch, vm.prank(admin)), dan wajib coba amplifikasi dampak pada Fork produksi.
3. Lapis 3 — Fase 4 (Hakim Akhir via `verify/VERDICT.md`): Wajib membaca dan menerapkan /home/ubuntu/.hermes/profiles/adv/verify/VERDICT.md untuk memisahkan hasil ke 06-refuted-invalid.md (Ketat Mutlak), 07-needs-next-step.md, 08-valid-not-eligible.md (Dalam Batasan/Low), dan 09-confirmed-findings.md (Valid Eligible).

## 4. Protokol Wajib Delegasi Subagent (delegate_task)
Setiap panggilan delegate_task WAJIB menyertakan di parameter context: (1) Path Absolut Proyek, (2) Paradigma Rantai & Core Invariants, (3) Path File audit/00 s/d 09 yang relevan, (4) Instruksi memanggil skill_view, dan (5) Perintah agar Subagent menulis detail ke audit/notes/ serta mengembalikan ringkasan maksimal 12 baris.

## 5. Tangga Bukti & Aturan Anti-False-Negative (rujuk `verify/VERDICT.md`)
1. **Tangga Bukti** wajib dicantumkan pada setiap verdict: `A` FORK (bytecode ter-deploy, `[PASS]`, tanpa cheatcode) -> boleh `09`; `B` LOKAL dengan kontrak asli -> maksimal `08`; `C` STRUKTURAL atau mock pihak ketiga -> maksimal `07`; `D` asumsi tanpa eksekusi -> `06`.
2. **Langkah 0 — Rekonsiliasi Deployment** wajib sebelum menilai klaim apa pun: ambil source terverifikasi explorer, baca slot EIP-1967 untuk proxy, bandingkan `sha256` dengan repo. Kode berbeda => tandai `HEAD-only`, verdict maksimal `07`.
3. **Kegagalan query bukan bukti ketiadaan.** `status: 0` dari explorer (mis. chain tidak didukung paket gratis), timeout RPC, atau `eth_getLogs` terbatas rentang wajib diulang lewat sumber lain sebelum menyimpulkan.
4. **Perilaku off-chain diuji black-box lebih dulu** (rekonstruksi event on-chain) sebelum menyatakan "butuh repo privat".
5. **Mock pihak ketiga** (CCTP/LayerZero/precompile) hanya menopang bukti struktural; dilarang menaikkan verdict ke `09`.
