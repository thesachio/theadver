#!/usr/bin/env python3
"""
ingest.py — Penyaring mekanis untuk repo bounty-inbox.

Tujuan: memindahkan SEMUA pekerjaan yang tidak butuh penilaian ke skrip,
sehingga model (mahal) hanya melihat klaim yang sudah lolos saringan.

Yang diperiksa skrip ini (nol token LLM):
  1. MANIFEST.json ada & schema valid
  2. commit sumber di repo == commit yang dipin di manifest
  3. file yang dirujuk benar-benar ada
  4. rentang baris valid (start <= end <= jumlah baris file)
  5. snippet (opsional) benar-benar ada di rentang itu
  6. file PoC ada
  7. perintah uji tidak kosong
  8. duplikasi id & field wajib

Output: tabel ringkas + verify/queue.json (hanya klaim MECH-OK).

Pakai:
  python3 ingest.py <url-atau-path> [--dest DIR]
  python3 ingest.py --selftest        # uji internal, tanpa jaringan
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

REQUIRED_TOP = ["version", "project", "sources", "findings"]
REQUIRED_SRC = ["name", "url", "commit"]
REQUIRED_FINDING = [
    "id", "title", "file", "lines", "claim",
    "impact", "victim", "actor", "live",
    "poc", "cmd", "severity_claimed",
]
VALID_IMPACT = {"theft", "grief", "dos", "design", "none"}
VALID_VICTIM = {"sponsor", "user", "protocol", "third-party", "none"}
VALID_ACTOR = {"unprivileged", "solver", "oracle", "admin"}
VALID_SEV = {"S1", "S2", "S3", "S4"}


def sh(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def clone_or_pull(url: str, dest: str) -> tuple[bool, str]:
    if os.path.isdir(os.path.join(dest, ".git")):
        code, out = sh(["git", "-C", dest, "fetch", "--all", "--quiet"])
        if code != 0:
            return False, f"fetch gagal: {out[:200]}"
        code, out = sh(["git", "-C", dest, "reset", "--hard", "origin/HEAD", "--quiet"])
        return (code == 0), (out[:200] if code else "")
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    code, out = sh(["git", "clone", "--quiet", url, dest])
    return (code == 0), (out[:200] if code else "")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def check_finding(f: dict, root: str, nfile: dict[str, int]) -> list[str]:
    """Kembalikan daftar masalah mekanis. Kosong = lolos."""
    bad: list[str] = []

    for k in REQUIRED_FINDING:
        if k not in f:
            bad.append(f"field hilang: {k}")
    if bad:
        return bad

    if f["impact"] not in VALID_IMPACT:
        bad.append(f"impact tidak dikenal: {f['impact']}")
    if f["victim"] not in VALID_VICTIM:
        bad.append(f"victim tidak dikenal: {f['victim']}")
    if f["actor"] not in VALID_ACTOR:
        bad.append(f"actor tidak dikenal: {f['actor']}")
    if f["severity_claimed"] not in VALID_SEV:
        bad.append(f"severity tidak dikenal: {f['severity_claimed']}")
    if not isinstance(f["live"], bool):
        bad.append("live harus boolean")

    lines = f["lines"]
    if not (isinstance(lines, list) and len(lines) == 2
            and all(isinstance(x, int) for x in lines)):
        bad.append("lines harus [start, end] integer")
        return bad
    a, b = lines
    if a < 1 or b < a:
        bad.append(f"rentang baris tidak valid: {a}-{b}")

    path = os.path.join(root, f["file"])
    if not os.path.isfile(path):
        bad.append(f"file tidak ada: {f['file']}")
    else:
        if f["file"] not in nfile:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                nfile[f["file"]] = sum(1 for _ in fh)
        total = nfile[f["file"]]
        if b > total:
            bad.append(f"rentang {a}-{b} melebihi {total} baris")

        snip = f.get("snippet")
        if snip:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                block = "".join(fh.readlines()[a - 1:b])
            if norm(snip) not in norm(block):
                bad.append("snippet tidak cocok di rentang yang diklaim")

    if not f.get("poc") or not os.path.isfile(os.path.join(root, f["poc"])):
        bad.append("file PoC tidak ada")
    if not str(f.get("cmd", "")).strip():
        bad.append("cmd kosong")

    return bad


def ingest(src: str, dest: str) -> int:
    if os.path.isdir(src):
        root = src
        msg = f"sumber lokal: {src}"
    else:
        ok, err = clone_or_pull(src, dest)
        if not ok:
            print(f"[FATAL] clone gagal: {err}", file=sys.stderr)
            return 2
        root = dest
        msg = f"clone: {src}"

    mpath = os.path.join(root, "MANIFEST.json")
    if not os.path.isfile(mpath):
        print(f"[FATAL] MANIFEST.json tidak ada di {root}", file=sys.stderr)
        return 2
    try:
        m = json.load(open(mpath, encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[FATAL] MANIFEST.json bukan JSON valid: {e}", file=sys.stderr)
        return 2

    for k in REQUIRED_TOP:
        if k not in m:
            print(f"[FATAL] manifest tanpa field: {k}", file=sys.stderr)
            return 2
    if m.get("version") != 1:
        print(f"[FATAL] version tidak didukung: {m.get('version')}", file=sys.stderr)
        return 2

    # --- commit pin check ---
    pin_issues: list[str] = []
    for s in m["sources"]:
        for k in REQUIRED_SRC:
            if k not in s:
                pin_issues.append(f"source tanpa {k}: {s}")
        sub = os.path.join(root, s.get("name", ""))
        if os.path.isdir(os.path.join(sub, ".git")):
            code, head = sh(["git", "-C", sub, "rev-parse", "HEAD"])
            if code != 0:
                pin_issues.append(f"{s['name']}: rev-parse gagal")
            elif not head.lower().startswith(s["commit"].lower()[:12]):
                pin_issues.append(
                    f"{s['name']}: HEAD {head[:8]} != pin {s['commit'][:8]}")

    # --- per-finding ---
    nfile: dict[str, int] = {}
    seen: set[str] = set()
    rows, queue = [], []
    for f in m["findings"]:
        fid = f.get("id", "?")
        if fid in seen:
            bad = ["id duplikat"]
        else:
            seen.add(fid)
            bad = check_finding(f, root, nfile)
        rows.append((fid, f.get("file", "?"), f.get("lines", []),
                     f.get("actor", "?"), f.get("live", "?"),
                     f.get("victim", "?"), bad))
        if not bad:
            queue.append(f)

    # --- laporan ringkas ---
    total = len(rows)
    ok = len(queue)
    print(f"=== INGEST {m['project']} v{m['version']} · {msg} ===")
    print(f"klaim: {total} | lolos mekanis: {ok} | gugur mekanis: {total - ok}")
    if pin_issues:
        print("PERINGATAN PIN COMMIT:")
        for p in pin_issues:
            print(f"  - {p}")
    print()
    print(f"{'ID':<14} {'LOKASI':<44} {'AKTOR':<13} {'LIVE':<5} {'KORBAN':<12} HASIL")
    for fid, fpath, lines, actor, live, victim, bad in rows:
        loc = f"{os.path.basename(str(fpath))}:{lines[0]}-{lines[1]}" if lines else str(fpath)
        loc = loc[:43]
        verdict = "MECH-OK" if not bad else "GUGUR: " + "; ".join(bad)
        print(f"{fid:<14} {loc:<44} {str(actor):<13} {str(live):<5} {str(victim):<12} {verdict}")

    os.makedirs(os.path.join(root, ".verify"), exist_ok=True)
    out = os.path.join(root, ".verify", "queue.json")
    json.dump({"project": m["project"], "sources": m["sources"],
               "findings": queue}, open(out, "w", encoding="utf-8"), indent=1)
    print(f"\nantrean untuk penilai manusia/model: {out}")
    print(f"({ok} klaim siap dinilai; {total - ok} sudah gugur tanpa biaya)")

    return 0 if ok else 1


def selftest() -> int:
    d = tempfile.mkdtemp(prefix="ingest-selftest-")
    os.makedirs(os.path.join(d, "src", "contracts"), exist_ok=True)
    code = "".join(f"line{i}\n" for i in range(1, 21))
    open(os.path.join(d, "src", "contracts", "A.sol"), "w").write(code)
    os.makedirs(os.path.join(d, "poc"), exist_ok=True)
    open(os.path.join(d, "poc", "P.t.sol"), "w").write("// poc\n")

    base = {"impact": "theft", "victim": "sponsor", "actor": "solver",
            "live": False, "cmd": "forge test -j 1", "severity_claimed": "S2",
            "claim": "x", "title": "t", "file": "src/contracts/A.sol",
            "poc": "poc/P.t.sol"}
    good = dict(base, id="F-OK", lines=[5, 10], snippet="line5 line6")
    bad_line = dict(base, id="F-RANGE", lines=[90, 99])
    bad_snip = dict(base, id="F-SNIP", lines=[5, 10], snippet="tidak-ada-di-sini")
    bad_poc = dict(base, id="F-POC", lines=[5, 10], poc="poc/HILANG.t.sol")
    dup = dict(good, id="F-OK")

    m = {"version": 1, "project": "selftest", "sources": [],
         "findings": [good, bad_line, bad_snip, bad_poc, dup]}
    json.dump(m, open(os.path.join(d, "MANIFEST.json"), "w"))

    print("--- SELFTEST ---")
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ingest(d, d)
    out = buf.getvalue()
    print(out)

    q = json.load(open(os.path.join(d, ".verify", "queue.json")))
    checks = []
    checks.append(("rc==0 (ada yang lolos)", rc == 0))
    checks.append(("hanya 1 lolos", len(q["findings"]) == 1))
    checks.append(("yang lolos = F-OK", q["findings"][0]["id"] == "F-OK"))
    checks.append(("rentang ditolak", "F-RANGE" in out and "melebihi" in out))
    checks.append(("snippet ditolak", "snippet tidak cocok" in out))
    checks.append(("PoC hilang ditolak", "PoC tidak ada" in out))
    checks.append(("duplikat ditolak", "id duplikat" in out))

    fail = [n for n, c in checks if not c]
    for n, c in checks:
        print(f"  {'PASS' if c else 'FAIL'}  {n}")
    print(f"--- SELFTEST {'LOLOS' if not fail else 'GAGAL'} ---")
    return 0 if not fail else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("--dest", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.src:
        ap.error("butuh <url-atau-path>")
    dest = a.dest or os.path.join(
        os.path.expanduser("~/.hermes/profiles/adv/cache/inbox"),
        os.path.basename(a.src.rstrip("/")).removesuffix(".git"))
    sys.exit(ingest(a.src, dest))
