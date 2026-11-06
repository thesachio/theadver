#!/usr/bin/env python3
"""merge_audit.py — pencocok staging vs file audit hasil merge.

Masalah yang diselesaikan: `audit/notes/staging-<unit>.md` menumpuk (puluhan file),
dihapus setelah merge tanpa jejak, sehingga tidak ada cara membuktikan bahwa
(a) setiap staging benar-benar sudah di-merge, (b) tidak ada entri yang hilang,
(c) tidak ada merge ganda, (d) yang di-merge adalah versi file yang benar.

Solusi: satu log append-only `audit/notes/MERGE-LOG.tsv` = manifes dari manifes.
Setiap merge mencatat: item, path staging, sha256, dan jumlah entri per wadah target.

Pemakaian:
    python3 verify/tools/merge_audit.py --audit-dir audit
    python3 verify/tools/merge_audit.py --audit-dir audit --strict

Keluar dengan kode 1 bila ada masalah (kecuali hanya peringatan).
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

LOG_NAME = "MERGE-LOG.tsv"
LOG_COLS = ["timestamp", "phase", "item", "staging", "sha256",
            "n04", "n05", "n06", "n07", "n09", "status"]
TARGETS = {"n04": "04-code-guarded.md", "n05": "05-raw-leads.md",
           "n06": "06-refuted-invalid.md", "n07": "07-needs-next-step.md",
           "n09": "09-confirmed-findings.md"}
ENTRY_RE = re.compile(r"^##\s*\[([^\]]+)\]", re.M)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def count_entries(path: Path) -> int:
    if not path.exists():
        return 0
    return len(ENTRY_RE.findall(path.read_text(encoding="utf-8", errors="replace")))


def entry_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [m.strip() for m in ENTRY_RE.findall(
        path.read_text(encoding="utf-8", errors="replace"))]


def parse_log(log: Path) -> tuple[list[dict], list[str]]:
    rows, problems = [], []
    if not log.exists():
        return rows, problems
    lines = log.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != len(LOG_COLS):
            problems.append(
                f"{LOG_NAME}:{i}: kolom {len(parts)}, harus {len(LOG_COLS)} "
                f"({', '.join(LOG_COLS)})")
            continue
        rows.append(dict(zip(LOG_COLS, (p.strip() for p in parts))))
    return rows, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-dir", default="audit")
    ap.add_argument("--strict", action="store_true",
                    help="peringatan juga menggagalkan (exit 1)")
    args = ap.parse_args()

    audit = Path(args.audit_dir)
    if not audit.is_dir():
        print(f"ERROR: {audit} bukan direktori")
        return 2

    notes = audit / "notes"
    log_path = notes / LOG_NAME
    errors: list[str] = []
    warns: list[str] = []

    # --- 1. baca log -------------------------------------------------------
    rows, log_problems = parse_log(log_path)
    errors.extend(log_problems)
    if not rows:
        warns.append(f"{LOG_NAME} belum ada / kosong — tidak ada jejak merge sama sekali")

    # --- 2. staging yatim: ada file, tidak ada di log ----------------------
    staging_files = sorted(notes.glob("staging-*.md")) if notes.is_dir() else []
    logged = {r["staging"].lstrip("./") for r in rows}
    orphans = [p for p in staging_files
               if str(p.relative_to(audit)).lstrip("./") not in logged
               and p.name not in {Path(x).name for x in logged}]
    for p in orphans:
        errors.append(f"STAGING YATIM: {p.name} tidak tercatat di {LOG_NAME} "
                      f"(belum di-merge atau log tidak ditulis)")

    # --- 3. hash: apakah file yang di-merge = file sekarang? --------------
    for r in rows:
        sp = audit / r["staging"]
        if not sp.exists():
            sp2 = notes / Path(r["staging"]).name
            sp = sp2 if sp2.exists() else sp
        if not sp.exists():
            continue  # sudah dihapus setelah merge: normal
        actual = sha256_of(sp)
        if r["sha256"] and actual != r["sha256"]:
            errors.append(
                f"HASH BERUBAH: {Path(r['staging']).name} sha256 sekarang "
                f"{actual[:12]}… != tercatat {r['sha256'][:12]}… "
                f"(file diubah setelah merge → isi hasil merge tidak terverifikasi)")

    # --- 4. jumlah entri: klaim log vs kenyataan --------------------------
    declared = {k: 0 for k in TARGETS}
    for r in rows:
        for k in TARGETS:
            try:
                declared[k] += int(r[k] or 0)
            except ValueError:
                errors.append(f"ANGKA BURUK: kolom {k} = '{r[k]}' bukan bilangan")
    for k, fname in TARGETS.items():
        actual = count_entries(audit / fname)
        if actual < declared[k]:
            errors.append(
                f"ENTRI HILANG: {fname} berisi {actual} entri, "
                f"log mengklaim {declared[k]} → {declared[k] - actual} hilang")
        elif actual > declared[k]:
            warns.append(
                f"ENTRI EKSTRA: {fname} berisi {actual} entri, log mengklaim "
                f"{declared[k]} → {actual - declared[k]} entri masuk tanpa log "
                f"(merge manual / tulisan langsung)")

    # --- 5. merge ganda: ID sama dua kali di satu file --------------------
    for fname in TARGETS.values():
        ids = entry_ids(audit / fname)
        seen, dup = set(), set()
        for i in ids:
            (dup if i in seen else seen).add(i)
        if dup:
            errors.append(f"MERGE GANDA: {fname} memuat ID duplikat: "
                          f"{', '.join(sorted(dup))}")

    # --- 6. ringkasan ------------------------------------------------------
    print(f"== merge_audit: {audit} ==")
    print(f"  log          : {len(rows)} baris" + ("" if log_path.exists() else " (TIDAK ADA)"))
    print(f"  staging ada  : {len(staging_files)} file | yatim: {len(orphans)}")
    for k, fname in TARGETS.items():
        print(f"  {fname:<26} klaim={declared[k]:<4} nyata={count_entries(audit / fname)}")
    print()
    for e in errors:
        print(f"  [ERROR] {e}")
    for w in warns:
        print(f"  [WARN ] {w}")
    if not errors and not warns:
        print("  [OK] semua staging tercatat, jumlah cocok, tidak ada ID ganda")
    print()
    print(f"  hasil: {len(errors)} error, {len(warns)} peringatan")

    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
