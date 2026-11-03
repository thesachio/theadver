#!/usr/bin/env python3
"""verify07.py — Validator entri 07-needs-next-step.md (fence-aware, Pernyataan #11).

Kenapa alat ini ada:
  `grep -c '^## \\['` MENTAH salah hitung karena ikut menghitung heading contoh
  yang berada di dalam blok kode ```...``` di dalam file template maupun file audit.
  Alat ini menghormati code fence, lalu memvalidasi setiap entri terhadap #11.

Pemakaian:
  python3 verify07.py <file.md>            # ringkasan + exit code
  python3 verify07.py <file.md> --json     # keluaran mesin

Exit code:
  0 = semua entri sah (atau file kosong / tidak ada entri)
  1 = ada pelanggaran LAZY_BAILOUT_DETECTED
  2 = file tidak ditemukan / tidak terbaca
"""
from __future__ import annotations

import json
import re
import sys

ALLOWED_DISPOSITIONS = {"NEXT_EXPLORE", "NEXT_MAINNET", "TOOL_BLOCKED"}

# Satu entri dimulai pada heading level-2 bernomor-bracket, DI LUAR code fence.
ENTRY_HEADING = re.compile(r"^##\s+\[(?P<id>[^\]]+)\]")

# Field boleh dibungkus bold (**) dan/atau backtick; boleh ada bullet di depan.
# Contoh nyata di audit: `- **Disposition:** `NEXT_MAINNET` — ...`
DISPOSITION_LINE = re.compile(
    r"^[\s\-*]*\**Disposition\**\s*:\s*\**\s*`?\s*(?P<val>[^\s`*]+)",
    re.IGNORECASE | re.MULTILINE,
)
PERCOBAAN_LINE = re.compile(r"^[\s\-*]*\**PERCOBAAN\**\s*:", re.IGNORECASE | re.MULTILINE)
LANGKAH_LINE = re.compile(
    r"^[\s\-*]*\**(?:Langkah\s+Konkret\s+Berikutnya|LANGKAH\s+BERIKUTNYA)\**\s*:",
    re.IGNORECASE | re.MULTILINE,
)
# Bukti percobaan nyata: baris perintah `$ ...` atau `Perintah yang dijalankan: ...`
CMD_LINE = re.compile(
    r"(?:^\s*\$\s+\S|^[\s\-*]*\**Perintah\s+yang\s+dijalankan\**\s*:\s*\S)",
    re.IGNORECASE | re.MULTILINE,
)


def strip_fences(lines: list[str]) -> list[str]:
    """Ganti isi code fence dengan string kosong, mempertahankan nomor baris."""
    out, in_fence, fence_marker = [], False, ""
    for line in lines:
        stripped = line.lstrip()
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_fence, fence_marker = True, stripped[:3]
            out.append("")
            continue
        if in_fence and stripped.startswith(fence_marker):
            in_fence = False
            out.append("")
            continue
        out.append("" if in_fence else line)
    return out


def split_entries(clean: list[str]) -> list[dict]:
    """Pisahkan entri berdasarkan heading `## [ID]` di luar code fence.

    `end` = indeks baris heading entri BERIKUTNYA (atau panjang file), sehingga
    pemotongan isi entri selalu memakai koordinat file mentah yang sama.
    """
    entries: list[dict] = []
    for idx, line in enumerate(clean, start=1):
        m = ENTRY_HEADING.match(line)
        if m:
            entries.append({"id": m.group("id").strip(), "start": idx, "end": len(clean) + 1})
    for i in range(len(entries) - 1):
        entries[i]["end"] = entries[i + 1]["start"]
    return entries


def strip_fences_keep_commands(lines: list[str]) -> list[str]:
    """Seperti strip_fences, tetapi isi fence yang memuat baris perintah `$ ...` DIPERTAHANKAN.

    PENTING: panjang list keluaran SELALU sama dengan masukan (satu slot per baris
    sumber), supaya indeks `start`/`end` dari split_entries tetap valid. Baris pembuka
    dan penutup fence dikosongkan, isi fence dipertahankan apa adanya.
    """
    out: list[str] = []
    in_fence, marker, buf_idx = False, "", []
    for line in lines:
        s = line.lstrip()
        if not in_fence and (s.startswith("```") or s.startswith("~~~")):
            in_fence, marker, buf_idx = True, s[:3], []
            out.append("")
            continue
        if in_fence and s.startswith(marker):
            in_fence = False
            if not any(_looks_like_command(out[i]) for i in buf_idx):
                for i in buf_idx:
                    out[i] = ""
            out.append("")
            continue
        if in_fence:
            buf_idx.append(len(out))
            out.append(line)
        else:
            out.append(line)
    assert len(out) == len(lines), "panjang list harus identik dengan sumber"
    return out


def _looks_like_command(line: str) -> bool:
    return bool(re.match(r"^\s*\$\s+\S", line)) or bool(
        re.match(r"^[\s\-*]*\**Perintah\s+yang\s+dijalankan\**\s*:", line, re.IGNORECASE)
    )


def check_entry(entry: dict) -> list[str]:
    body = "\n".join(entry["lines"])
    problems: list[str] = []

    disp = [v.strip("`*").upper() for v in DISPOSITION_LINE.findall(body)]
    disp = [d for d in disp if d in ALLOWED_DISPOSITIONS]
    if not disp:
        problems.append("missing/!!invalid `Disposition:` (NEXT_EXPLORE | NEXT_MAINNET | TOOL_BLOCKED)")
    elif len(set(disp)) > 1:
        problems.append(f"multiple `Disposition:` values {sorted(set(disp))} — exactly one required")

    if not PERCOBAAN_LINE.search(body):
        problems.append("missing `PERCOBAAN:` block")
    else:
        pg = PERCOBAAN_LINE.search(body)
        tail = body[pg.end():]
        if not CMD_LINE.search(tail.split("\n## ")[0]):
            problems.append("`PERCOBAAN:` has no executed command line (`$ ...` or `Perintah yang dijalankan: ...`)")

    if not LANGKAH_LINE.search(body):
        problems.append("missing next-step field (`Langkah Konkret Berikutnya` / `LANGKAH BERIKUTNYA`)")

    return problems


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    as_json = "--json" in argv
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read().splitlines()
    except OSError as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    clean = strip_fences(raw)
    entries = split_entries(clean)
    # Heading dihitung fence-aware (contoh di dalam ``` tidak dianggap entri), tetapi
    # isi entri diambil dari file MENTAH agar bukti `$ ...` di dalam blok kode tetap terbaca.
    body_source = strip_fences_keep_commands(raw)
    for e in entries:
        e["lines"] = body_source[e["start"] - 1: e["end"] - 1]
    report = []
    for e in entries:
        problems = check_entry(e)
        report.append({
            "id": e["id"],
            "line": e["start"],
            "valid": not problems,
            "problems": problems,
            "verdict": "OK" if not problems else "LAZY_BAILOUT_DETECTED",
        })

    invalid = [r for r in report if not r["valid"]]
    if as_json:
        print(json.dumps({"file": path, "entries": len(entries),
                          "invalid": len(invalid), "report": report}, indent=2, ensure_ascii=False))
    else:
        # Catatan: heading contoh DI DALAM code fence sengaja tidak dihitung.
        print(f"file      : {path}")
        print(f"entries   : {len(entries)} (fence-aware)")
        print(f"invalid   : {len(invalid)}")
        for r in report:
            mark = "OK  " if r["valid"] else "FAIL"
            print(f"  [{mark}] line {r['line']:>4}  {r['id']}")
            for p in r["problems"]:
                print(f"         - {p}")
        if not entries:
            print("  (tidak ada entri — target akhir `07` = 0 entri, status PASS)")

    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
