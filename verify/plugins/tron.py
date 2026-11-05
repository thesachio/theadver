#!/usr/bin/env python3
"""
Plugin paradigma TRON untuk deploy_parity.

Menunjukkan cara menambah rantai baru TANPA mengedit deploy_parity.py.

Pemakaian:
    python3 deploy_parity.py --plugin-dir ../plugins --paradigm tron \
        --addr TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t \
        --rpc https://api.trongrid.io \
        --entrypoints 'name();symbol();decimals()'

Karakteristik Tron yang membuatnya berbeda dari EVM:
  * eth_call tidak tersedia secara native (TronWeb/JSON-RPC Tron punya kosakata sendiri).
  * Untuk view function: POST /wallet/triggerconstantcontract
    -> response punya `result.result` (bool) + `constant_result` (hex) + `result.message` (hex).
  * Bytecode diambil via /wallet/getcontract -> `bytecode` (hex).
  * Bila `result.message` ada, itu revert BUKAN berarti fungsi tidak ada.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

import deploy_parity as dp

PARADIGM = "tron"


def _post(url: str, path: str, payload: dict, timeout: int = 25) -> tuple[bool, Any]:
    """POST ke Tron HTTP API lewat curl (konsisten dengan transport induk)."""
    full = url.rstrip("/") + path
    r = subprocess.run(
        ["curl", "-sS", "--max-time", str(timeout), "-H", "content-type: application/json",
         full, "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout + 5,
    )
    if r.returncode != 0:
        return False, f"curl exit {r.returncode}: {r.stderr[:120]}"
    try:
        return True, json.loads(r.stdout or "{}")
    except json.JSONDecodeError as e:
        return False, f"json: {e}"


def strategy_tron(ep: str, addr: str, entrypoints: list[str], rep: "dp.ParityReport") -> None:
    rep.strategy = "triggerconstantcontract"
    rep.confidence = dp.CONF_HEURISTIC

    ok, contract = _post(ep, "/wallet/getcontract", {"value": addr, "visible": True})
    if not ok or not isinstance(contract, dict):
        rep.notes.append(f"getcontract gagal: {str(contract)[:120]}")
        rep.env_attempts.append({"endpoint": ep, "result": "fail", "detail": str(contract)[:120]})
        return

    if not contract or not contract.get("bytecode"):
        rep.cycle = dp.CYCLE_PRE
        rep.overall = "HEAD_ONLY_PROVEN"
        rep.notes.append("Kontrak tidak ditemukan / tanpa bytecode -> P1_PRE_DEPLOY")
        rep.confidence = dp.CONF_EXACT
        return

    code = str(contract.get("bytecode") or "")
    rep.prerequisites["codesize"] = len(code) // 2
    rep.prerequisites["contract_name"] = contract.get("name")
    disp = dp.push4_selectors("0x" + code)

    # Kalibrasi negatif: selector yang mustahil ada.
    okn, neg = _post(
        ep,
        "/wallet/triggerconstantcontract",
        {"owner_address": addr, "contract_address": addr, "function_selector": "deadbeef()", "parameter": "", "visible": True},
    )
    neg_ok = False
    if okn and isinstance(neg, dict):
        nr = neg.get("result") or {}
        nmsg_raw = str(nr.get("message", ""))
        try:
            nmsg = bytes.fromhex(nmsg_raw).decode(errors="ignore") if nmsg_raw else ""
        except Exception:  # noqa: BLE001
            nmsg = nmsg_raw
        neg_ok = bool(nr.get("result") is True) and "REVERT" not in nmsg.upper()
    rep.probes.append(dp.Probe("triggerconstantcontract", addr, neg_ok, f"neg:{'SUCCESS' if neg_ok else 'REVERT'}"))

    for name in entrypoints:
        sel = dp.sel_from_sig(name)
        if not sel:
            rep.entrypoints.append(
                dp.EntrypointResult(name=name, verdict="UNVERIFIABLE", evidence=["selector gagal dihitung"])
            )
            continue

        okc, res = _post(
            ep,
            "/wallet/triggerconstantcontract",
            {
                "owner_address": addr,
                "contract_address": addr,
                "function_selector": name,
                "parameter": "",
                "visible": True,
            },
        )
        r = (res or {}).get("result") or {} if isinstance(res, dict) else {}
        msg_raw = str(r.get("message", ""))
        # Tron meng-encode message sebagai hex; decode agar bisa dibaca.
        try:
            msg = bytes.fromhex(msg_raw).decode(errors="ignore") if msg_raw else ""
        except Exception:  # noqa: BLE001
            msg = msg_raw
        success = bool(r.get("result") is True) and "REVERT" not in msg.upper()
        in_disp = sel in disp

        rep.probes.append(
            dp.Probe("triggerconstantcontract", addr, success, f"{name}:{'OK' if success else 'REVERT'} {msg[:30]}")
        )

        ev = [f"tron:{'OK' if success else 'REVERT'}", f"push4:{'ADA' if in_disp else 'TIDAK'}"]
        if success and not neg_ok:
            verdict = "PRESENT"
        elif success and neg_ok:
            verdict = "PRESENT" if in_disp else "FALLBACK_PERMISSIVE_UNKNOWN"
        elif in_disp:
            verdict = "PRESENT_STATEFUL"  # revert karena parameter/state, fungsi ada di dispatcher
        else:
            # Tron tidak membedakan "tidak ada" vs "revert tanpa pesan" dari eth_call;
            # wajib bukti tambahan sebelum menyimpulkan ABSENT.
            verdict = "ABSENT_OR_PATCHED"
            ev.append(f"msg:{msg[:30]}")

        rep.entrypoints.append(dp.EntrypointResult(name=name, selector=sel, verdict=verdict, evidence=ev))

    rep.cycle = dp.CYCLE_PARTIAL
    if rep.entrypoints and all(e.verdict in ("PRESENT", "PRESENT_STATEFUL") for e in rep.entrypoints):
        rep.cycle = dp.CYCLE_FULL


dp.register(PARADIGM, "triggerconstantcontract", dp.CONF_HEURISTIC, strategy_tron, ("tronlink",))
