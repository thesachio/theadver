#!/usr/bin/env python3
"""
deploy_parity.py — Gerbang Siklus Deployment & Kesetaraan Entrypoint.

Menjawab satu pertanyaan yang selama ini dijawab dengan asumsi:
    "Apakah entrypoint yang diserang PoC benar-benar ADA dan BERPERILAKU SAMA
     pada objek deployment yang diklaim (live mainnet / testnet / belum deploy)?"

Tiga kelas strategi (jangan dipaksakan seragam):
    A. REGISTRY   (Sui, Aptos)      -> exposed_functions dibaca literal.  confidence EXACT
    B. ATTESTATION(Solana)          -> hash ProgramData + slot + authority. confidence EXACT
    C. PROBE      (EVM, TON)        -> probe berlapis + heuristik.        confidence HEURISTIC

Aturan keras:
    * ABSENT hanya boleh disimpulkan bila SEMUA metode gagal DAN bukti tambahan ada.
    * RPC gagal 2x -> ENV_ERROR, BUKAN bukti ketiadaan.
    * Semua keputusan ditulis ke artefak JSON agar bisa diaudit ulang.

Pemakaian:
    python3 deploy_parity.py --paradigm evm --chain mainnet \
        --addr 0x... --entrypoints "supply(address,uint256,address,uint16)" \
        --rpc https://... [--artifact out/Nexus.json] [--repo /path/to/repo]

    python3 deploy_parity.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Any

# --------------------------------------------------------------------------
# Konstanta
# --------------------------------------------------------------------------

EIP1967_IMPL = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
EIP1967_BEACON = "0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50"
EIP1967_ADMIN = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"

# Selector yang tidak mungkin ada: kontrol negatif universal.
NEGATIVE_SELECTOR = "deadbeef"

# Selector kalibrasi: harus ada di mayoritas kontrak token; kalau tidak, ENV_ERROR.
# (Dipakai hanya bila pengguna tidak menyediakan --calibration)
DEFAULT_CALIBRATION = "06fdde03"  # name()

CONF_EXACT = "EXACT"
CONF_HEURISTIC = "HEURISTIC"
CONF_UNVERIFIABLE = "UNVERIFIABLE"

CYCLE_PRE = "P1_PRE_DEPLOY"
CYCLE_TESTNET = "P2_TESTNET_ONLY"
CYCLE_PARTIAL = "P3_LIVE_PARTIAL"
CYCLE_FULL = "P4_LIVE_FULL"
CYCLE_UNKNOWN = "P0_UNKNOWN"

# --------------------------------------------------------------------------
# Model hasil
# --------------------------------------------------------------------------


@dataclass
class Probe:
    """Satu hasil panggilan mentah."""

    method: str
    target: str
    ok: bool
    detail: str = ""
    data_prefix: str = ""


@dataclass
class EntrypointResult:
    name: str
    selector: str | None = None
    verdict: str = "UNKNOWN"
    evidence: list[str] = field(default_factory=list)


@dataclass
class ParityReport:
    paradigm: str
    chain: str
    address: str
    cycle: str = CYCLE_UNKNOWN
    strategy: str = ""
    confidence: str = CONF_UNVERIFIABLE
    overall: str = "UNVERIFIABLE"
    resolved_targets: dict[str, str] = field(default_factory=dict)
    prerequisites: dict[str, Any] = field(default_factory=dict)
    entrypoints: list[EntrypointResult] = field(default_factory=list)
    probes: list[Probe] = field(default_factory=list)
    env_attempts: list[dict[str, str]] = field(default_factory=list)
    repo_ref: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    generated_at: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# Transport
# --------------------------------------------------------------------------


def http_json(url: str, payload: dict | None = None, timeout: int = 25) -> tuple[bool, Any]:
    """POST/GET JSON via curl (urllib diblokir 403 oleh beberapa RPC publik).

    Return (transport_ok, data|errmsg). transport_ok=True berarti respons HTTP
    diterima dan dapat di-parse; kesalahan logika RPC ada di dalam 'data'.
    """
    try:
        if payload is None:
            cmd = ["curl", "-sS", "--max-time", str(timeout), url]
        else:
            cmd = [
                "curl",
                "-sS",
                "--max-time",
                str(timeout),
                "-H",
                "content-type: application/json",
                url,
                "-d",
                json.dumps(payload),
            ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode != 0:
            return False, f"curl exit {r.returncode}: {r.stderr.strip()[:160]}"
        body = r.stdout.strip()
        if not body:
            return False, "empty response"
        return True, json.loads(body)
    except json.JSONDecodeError as e:
        return False, f"json decode: {e}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def rpc(ep: str, method: str, params: list, timeout: int = 25) -> tuple[bool, Any]:
    """JSON-RPC dengan retry sekali (aturan: RPC gagal 2x => ENV_ERROR)."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    last = ""
    for _ in range(2):
        ok, data = http_json(ep, payload, timeout)
        if ok:
            if isinstance(data, dict) and "error" in data:
                return False, data["error"]
            return True, data.get("result")
        last = str(data)
        time.sleep(0.6)
    return False, last


def cast(*args: str, timeout: int = 40) -> tuple[bool, str]:
    """Jalankan `cast`. Return (ok, stdout|stderr)."""
    try:
        r = subprocess.run(
            ["cast", *args], capture_output=True, text=True, timeout=timeout
        )
        return (r.returncode == 0), (r.stdout.strip() or r.stderr.strip())
    except FileNotFoundError:
        return False, "cast: NOT FOUND"
    except subprocess.TimeoutExpired:
        return False, "cast: TIMEOUT"


# --------------------------------------------------------------------------
# Util
# --------------------------------------------------------------------------


def sel_from_sig(sig: str) -> str | None:
    """Hitung selector EVM 4-byte dari signature. None bila bukan signature."""
    sig = sig.strip()
    if re.fullmatch(r"[0-9a-fA-F]{8}", sig):
        return sig.lower()
    if "(" not in sig:
        return None
    try:
        from Crypto.Hash import keccak  # type: ignore

        k = keccak.new(digest_bits=256)
        k.update(sig.encode())
        return k.hexdigest()[:8]
    except Exception:  # noqa: BLE001
        pass
    # fallback: cast keccak
    ok, out = cast("keccak", sig)
    if ok and len(out) >= 10:
        return out[2:10].lower()
    return None


def push4_selectors(code_hex: str) -> set[str]:
    """Ekstrak semua PUSH4 (opcode 0x63) dari bytecode. Heuristik EVM."""
    b = code_hex.lower()
    if b.startswith("0x"):
        b = b[2:]
    out: set[str] = set()
    for i in range(0, len(b) - 8, 2):
        if b[i : i + 2] == "63":
            out.add(b[i + 2 : i + 10])
    return out


def decode_ck256(data: str) -> list[str]:
    """Pecah hex return-data menjadi word 32-byte."""
    d = data[2:] if data.startswith("0x") else data
    return [d[i : i + 64] for i in range(0, len(d) - 63, 64)]


# --------------------------------------------------------------------------
# Strategi A — REGISTRY (Sui, Aptos)
# --------------------------------------------------------------------------


def strategy_registry_aptos(ep: str, addr: str, entrypoints: list[str], rep: ParityReport) -> None:
    """Aptos: baca exposed_functions literal dari module ABI."""
    if "::" not in addr:
        rep.notes.append("Aptos butuh alamat berformat 0xADDR::module")
        return
    account, module = addr.split("::", 1)
    url = f"{ep.rstrip('/')}/accounts/{account}/module/{module}"
    ok, data = http_json(url)
    if not ok or not isinstance(data, dict):
        rep.notes.append(f"REGISTRY gagal: {data}")
        rep.env_attempts.append({"endpoint": url, "result": "fail", "detail": str(data)[:120]})
        return
    abi = data.get("abi") or {}
    exposed = {f.get("name"): f for f in abi.get("exposed_functions", [])}
    rep.prerequisites["module"] = f"{account}::{module}"
    rep.prerequisites["exposed_count"] = len(exposed)
    rep.prerequisites["bytecode_present"] = bool(data.get("bytecode"))
    for name in entrypoints:
        base = name.split("(")[0].strip()
        hit = base in exposed
        rep.entrypoints.append(
            EntrypointResult(
                name=name,
                verdict="PRESENT" if hit else "ABSENT",
                evidence=[f"registry:{len(exposed)} fungsi", "source:move_abi"],
            )
        )
    rep.strategy = "registry"
    rep.confidence = CONF_EXACT


def strategy_registry_sui(ep: str, addr: str, entrypoints: list[str], rep: ParityReport) -> None:
    """
    Sui: baca daftar fungsi eksplisit dari MovePackage lewat GraphQL.

    JSON-RPC lama (suix_getNormalizedMoveModule) SUDAH DEPRECATED di fullnode publik,
    jadi jalur yang reproducible adalah GraphQL. Bila endpoint bukan GraphQL,
    tool WAJIB gagal keras (UNVERIFIABLE) - tidak boleh menyimpulkan ABSENT.
    """
    if "::" not in addr:
        rep.notes.append("Sui butuh alamat berformat 0xPKG::module")
        return
    pkg, module = addr.split("::", 1)

    query = (
        "{ object(address: \"%s\") { asMovePackage { modules(first: 50) { pageInfo "
        "{ hasNextPage endCursor } nodes { name functions(first: 50) { pageInfo { hasNextPage } nodes { name } } } "
        "} } } }" % pkg
    )
    ok, data = http_json(ep, {"query": query})
    if not ok or not isinstance(data, dict):
        rep.notes.append(f"REGISTRY gagal (transport): {str(data)[:120]}")
        rep.env_attempts.append({"endpoint": ep, "result": "fail", "detail": str(data)[:120]})
        return
    if data.get("errors"):
        rep.notes.append(f"GraphQL error: {str(data['errors'])[:140]}")
        rep.env_attempts.append({"endpoint": ep, "result": "graphql_error"})
        return

    obj = (data.get("data") or {}).get("object") or {}
    pkgd = obj.get("asMovePackage") or {}
    mods = pkgd.get("modules") or {}
    nodes = list(mods.get("nodes") or [])
    page = mods.get("pageInfo") or {}

    # Paginasi: telusuri seluruh halaman modul agar ABSENT tidak pernah diklaim prematur.
    seen_cursors: set[str] = set()
    while page.get("hasNextPage"):
        cur = page.get("endCursor")
        if not cur or cur in seen_cursors:
            break
        seen_cursors.add(cur)
        q2 = (
            '{ object(address: "%s") { asMovePackage { modules(first: 50, after: "%s") '
            "{ pageInfo { hasNextPage endCursor } nodes { name functions(first: 50) "
            "{ pageInfo { hasNextPage } nodes { name } } } } } } }" % (pkg, cur)
        )
        ok2, d2 = http_json(ep, {"query": q2})
        if not ok2 or not isinstance(d2, dict) or d2.get("errors"):
            rep.notes.append("Paginasi modul gagal -> UNVERIFIABLE (ABSENT dilarang)")
            rep.strategy = "registry"
            rep.confidence = CONF_UNVERIFIABLE
            return
        m2 = (((d2.get("data") or {}).get("object") or {}).get("asMovePackage") or {}).get("modules") or {}
        nodes.extend(m2.get("nodes") or [])
        page = m2.get("pageInfo") or {}
    rep.prerequisites["modules_scanned"] = len(nodes)

    target_mod = next((m for m in nodes if m.get("name") == module), None)
    if not target_mod:
        rep.notes.append(f"modul '{module}' tidak ditemukan pada paket {pkg} (semua halaman ditelusuri)")
        rep.cycle = CYCLE_PARTIAL
        rep.strategy = "registry"
        rep.confidence = CONF_EXACT
        rep.overall = "ENTRYPOINT_ABSENT"
        return

    fn_page = (target_mod.get("functions") or {}).get("pageInfo") or {}
    fn_nodes = ((target_mod.get("functions") or {}).get("nodes") or [])
    # Paginasi fungsi: halaman pertama modul ini mungkin saja sudah menyentuh
    # batas 50 tanpa pageInfo.hasNextPage terisi benar; verifikasi eksplisit
    # dengan query modul khusus (module(name:)) sebelum menyimpulkan ABSENT.
    if not fn_page.get("hasNextPage"):
        q_chk = (
            '{ object(address: "%s") { asMovePackage { module(name: "%s") { functions('
            "first: 50) { pageInfo { hasNextPage endCursor } nodes { name } } } } } }" % (pkg, module)
        )
        okc, dc = http_json(ep, {"query": q_chk})
        if okc and isinstance(dc, dict) and not dc.get("errors"):
            mc = ((dc.get("data") or {}).get("object") or {}).get("asMovePackage") or {}
            modc = mc.get("module") or {}
            pc = (modc.get("functions") or {}).get("pageInfo") or {}
            if pc.get("hasNextPage"):
                fn_page = pc
                fn_nodes = list((modc.get("functions") or {}).get("nodes") or [])
            else:
                fn_nodes = list((modc.get("functions") or {}).get("nodes") or []) or fn_nodes
    # Batas keras API = 50 node. Bila daftar tepat 50, kelengkapan TIDAK dapat
    # dipastikan (API bisa melaporkan hasNextPage=False pada halaman terakhir
    # tepat-penuh) -> ABSENT dilarang, verdict harus UNVERIFIABLE.
    if len({f.get("name") for f in fn_nodes}) >= 50:
        rep.notes.append(
            f"Daftar fungsi menyentuh batas 50 node (modul {module}); "
            "kelengkapan tidak dapat dipastikan -> ABSENT dilarang"
        )
        rep.strategy = "registry"
        rep.confidence = CONF_UNVERIFIABLE
        return

    fn_seen: set[str] = set()
    while fn_page.get("hasNextPage"):
        cur2 = fn_page.get("endCursor")
        if not cur2 or cur2 in fn_seen:
            break
        fn_seen.add(cur2)
        q3 = (
            '{ object(address: "%s") { asMovePackage { module(name: "%s") { functions('
            'first: 50, after: "%s") { pageInfo { hasNextPage endCursor } nodes { name } } } } } }'
            % (pkg, module, cur2)
        )
        ok3, d3 = http_json(ep, {"query": q3})
        if not ok3 or not isinstance(d3, dict) or d3.get("errors"):
            rep.notes.append("Paginasi fungsi gagal -> UNVERIFIABLE (ABSENT dilarang)")
            rep.strategy = "registry"
            rep.confidence = CONF_UNVERIFIABLE
            return
        m3 = ((d3.get("data") or {}).get("object") or {}).get("asMovePackage") or {}
        mod3 = m3.get("module") or {}
        fn_nodes.extend((mod3.get("functions") or {}).get("nodes") or [])
        fn_page = (mod3.get("functions") or {}).get("pageInfo") or {}
        if not fn_nodes:
            rep.notes.append("Paginasi fungsi tidak mengembalikan node -> UNVERIFIABLE")
            rep.strategy = "registry"
            rep.confidence = CONF_UNVERIFIABLE
            return

    fns = {f.get("name") for f in fn_nodes}
    rep.prerequisites["package"] = pkg
    rep.prerequisites["module"] = module
    rep.prerequisites["module_count"] = len(nodes)
    rep.prerequisites["exposed_count"] = len(fns)
    # Modul ketemu & daftar fungsi lengkap -> paket sudah ter-deploy dan terverifikasi
    rep.cycle = CYCLE_FULL if not fn_page.get("hasNextPage") else CYCLE_PARTIAL

    for name in entrypoints:
        base = name.split("(")[0].split("::")[-1].strip()
        rep.entrypoints.append(
            EntrypointResult(
                name=name,
                verdict="PRESENT" if base in fns else "ABSENT",
                evidence=[f"registry:{len(fns)} fungsi di {module}", "source:sui_graphql"],
            )
        )
    rep.strategy = "registry"
    rep.confidence = CONF_EXACT
    rep.cycle = CYCLE_FULL if all(e.verdict == "PRESENT" for e in rep.entrypoints) else CYCLE_PARTIAL


# --------------------------------------------------------------------------
# Strategi B — ATTESTATION (Solana)
# --------------------------------------------------------------------------


def strategy_attestation_solana(ep: str, addr: str, entrypoints: list[str], rep: ParityReport) -> None:
    """
    Solana: identitas deployment = sha256(bytecode) + slot + upgrade authority
    dari ProgramData. Entrypoint per-instruction (discriminator) TIDAK dapat
    didaftar tanpa IDL, jadi kita laporkan 'UNRESOLVED_EXACT' untuk tiap nama
    entrypoint — TAPI identitas deployment-nya EXACT.
    """
    ok, acc = rpc(ep, "getAccountInfo", [addr, {"encoding": "jsonParsed"}])
    if not ok or not acc:
        rep.notes.append(f"attestation gagal: {acc}")
        return
    # Solana membungkus hasil: {"context":..., "value": {...}}
    if isinstance(acc, dict) and "value" in acc:
        acc = acc.get("value") or {}
    if not acc:
        rep.cycle = CYCLE_PRE
        rep.overall = "HEAD_ONLY_PROVEN"
        rep.notes.append("Akun program tidak ada di rantai -> P1_PRE_DEPLOY")
        rep.strategy = "attestation"
        rep.confidence = CONF_EXACT
        return
    rep.prerequisites["executable"] = acc.get("executable")
    rep.prerequisites["owner_program"] = acc.get("owner")
    rep.prerequisites["lamports"] = acc.get("lamports")
    rep.prerequisites["data_len"] = acc.get("space")

    pd_addr = None
    parsed = acc.get("data")
    if isinstance(parsed, dict):
        pd_addr = ((parsed.get("parsed") or {}).get("info") or {}).get("programData")
    if not pd_addr:
        rep.notes.append("ProgramData tidak ditemukan (mungkin non-upgradeable)")
        rep.strategy = "attestation"
        rep.confidence = CONF_HEURISTIC
        return

    rep.resolved_targets["program_data"] = pd_addr
    ok2, pd = rpc(ep, "getAccountInfo", [pd_addr, {"encoding": "base64"}])
    if not ok2 or not pd:
        rep.notes.append("gagal membaca ProgramData")
        return
    if isinstance(pd, dict) and "value" in pd:
        pd = pd.get("value") or {}
    if not pd or not pd.get("data"):
        rep.notes.append("ProgramData kosong")
        return
    import base64

    raw = base64.b64decode(pd["data"][0])
    if len(raw) < 45:
        rep.notes.append("ProgramData terlalu pendek")
        return
    slot = int.from_bytes(raw[4:12], "little")
    authority = raw[12:44]
    code = raw[45:]
    rep.prerequisites["last_deploy_slot"] = slot
    rep.prerequisites["upgrade_authority"] = (
        "IMMUTABLE" if authority == b"\x00" * 32 else authority.hex()
    )
    rep.prerequisites["bytecode_sha256"] = hashlib.sha256(code).hexdigest()
    rep.prerequisites["bytecode_size"] = len(code)

    for name in entrypoints:
        rep.entrypoints.append(
            EntrypointResult(
                name=name,
                verdict="UNRESOLVED_EXACT",
                evidence=["attestation:ok", "discriminator:butuh IDL"],
            )
        )
    rep.strategy = "attestation"
    # Identitas EXACT; status entrypoint per-nama belum pasti.
    rep.confidence = CONF_EXACT
    rep.cycle = CYCLE_FULL if rep.chain == "mainnet" else CYCLE_TESTNET
    rep.notes.append(
        "Identitas deployment EXACT (sha256+slot+authority). "
        "Discriminator instruction perlu IDL/source untuk diverifikasi per-nama."
    )


# --------------------------------------------------------------------------
# Strategi C — PROBE (EVM, TON)
# --------------------------------------------------------------------------


def resolve_evm_targets(address: str, rpcurl: str, rep: ParityReport) -> str:
    """Resolusi proxy EIP-1967 & beacon. Return alamat yang dianalisis."""
    ok, impl = cast("storage", address, EIP1967_IMPL, "--rpc-url", rpcurl)
    if ok and impl and int(impl, 16) != 0:
        target = "0x" + impl[-40:]
        rep.resolved_targets["proxy_impl"] = target
        rep.prerequisites["proxy"] = True
        okb, beacon = cast("storage", address, EIP1967_BEACON, "--rpc-url", rpcurl)
        if okb and beacon and int(beacon, 16) != 0:
            rep.resolved_targets["beacon"] = "0x" + beacon[-40:]
            rep.prerequisites["beacon"] = True
    else:
        rep.prerequisites["proxy"] = False
        target = address
    oka, adm = cast("storage", address, EIP1967_ADMIN, "--rpc-url", rpcurl)
    if oka and adm and int(adm, 16) != 0:
        rep.resolved_targets["proxy_admin"] = "0x" + adm[-40:]
        rep.prerequisites["proxy_admin"] = True
    return target


def probe_evm_call(rpcurl: str, target: str, sel: str) -> tuple[str, str]:
    """Return (status, detail) dengan status: OK|REVERT_DATA|REVERT_EMPTY|RPC_FAIL."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [{"to": target, "data": "0x" + sel}, "latest"],
    }
    for _ in range(2):
        ok, data = http_json(rpcurl, payload)
        if not ok:
            rep_detail = str(data)
            continue
        if "result" in data:
            return "OK", data["result"]
        err = data.get("error") or {}
        raw = str(err.get("data", ""))
        msg = str(err.get("message", ""))
        # Custom error: selector 4 byte pertama. Bandingkan dengan yang dikenal.
        sel4 = raw[2:10].lower() if raw.startswith("0x") and len(raw) >= 10 else ""
        KNOWN_CUSTOM = {
            "08c63e27": "MissingFallbackHandler",  # Biconomy Nexus FallbackManager
            "118cdaa7": "OwnableUnauthorizedAccount",
            "82b42900": "Unauthorized",
            "4e487b71": "Panic",
        }
        if sel4 in KNOWN_CUSTOM:
            return "CUSTOM_ERROR", f"{KNOWN_CUSTOM[sel4]} data={raw[:74]}"
        if "MissingFallbackHandler" in raw:
            return "CUSTOM_ERROR", f"MissingFallbackHandler data={raw[:74]}"
        if raw in ("0x", "") and "revert" in msg.lower():
            return "REVERT_EMPTY", f"{msg} data=0x"
        return "REVERT_DATA", f"{msg} data={raw[:74]}"
    return "RPC_FAIL", rep_detail


def strategy_probe_evm(ep: str, addr: str, entrypoints: list[str], rep: ParityReport) -> None:
    target = resolve_evm_targets(addr, ep, rep)

    ok_code, code = cast("code", target, "--rpc-url", ep)
    if not ok_code:
        rep.notes.append(f"cast code gagal: {code[:100]}")
        rep.env_attempts.append({"endpoint": ep, "result": "fail", "detail": code[:100]})
        return
    if code in ("0x", ""):
        rep.cycle = CYCLE_PRE
        rep.notes.append("Tidak ada bytecode di alamat ini -> P1_PRE_DEPLOY")
        rep.strategy = "probe"
        rep.confidence = CONF_EXACT  # ketiadaan bytecode bersifat pasti
        rep.overall = "HEAD_ONLY_PROVEN"
        return

    rep.prerequisites["codesize"] = (len(code) - 2) // 2
    disp = push4_selectors(code)

    # Kalibrasi negatif
    neg_status, neg_detail = probe_evm_call(ep, target, NEGATIVE_SELECTOR)
    rep.probes.append(Probe("eth_call", target, neg_status == "OK", f"neg:{neg_status} {neg_detail[:60]}"))
    fallback_permissive = neg_status == "OK"

    for name in entrypoints:
        sel = sel_from_sig(name)
        if not sel:
            rep.entrypoints.append(
                EntrypointResult(name=name, verdict="UNVERIFIABLE", evidence=["selector gagal dihitung"])
            )
            continue
        status, detail = probe_evm_call(ep, target, sel)
        rep.probes.append(Probe("eth_call", target, status == "OK", f"{name}:{status}", str(detail)[:42]))
        in_disp = sel in disp

        ev = [f"eth_call:{status}", f"push4:{'ADA' if in_disp else 'TIDAK'}", f"neg:{neg_status}"]
        if status == "CUSTOM_ERROR" and "MissingFallbackHandler" in str(detail):
            verdict = "RELAYED_VIA_HANDLER"
            ev.append("custom:MissingFallbackHandler")
        elif status == "OK" and not fallback_permissive:
            verdict = "PRESENT"
        elif status == "OK" and fallback_permissive:
            # fallback permisif: eth_call tak bisa dipercaya; pakai dispatcher
            verdict = "PRESENT" if in_disp else "FALLBACK_PERMISSIVE_UNKNOWN"
        elif status in ("REVERT_EMPTY", "REVERT_DATA") and in_disp:
            verdict = "PRESENT_STATEFUL"
        elif status in ("REVERT_EMPTY", "REVERT_DATA") and not in_disp:
            verdict = "ABSENT_OR_PATCHED"
        elif status == "CUSTOM_ERROR":
            verdict = "PRESENT_STATEFUL" if in_disp else "ABSENT_OR_PATCHED"
        else:
            verdict = "UNVERIFIABLE"
        rep.entrypoints.append(EntrypointResult(name=name, selector=sel, verdict=verdict, evidence=ev))

    rep.strategy = "probe+push4"
    rep.confidence = CONF_HEURISTIC
    rep.cycle = CYCLE_PARTIAL
    verdicts = {e.verdict for e in rep.entrypoints}
    if verdicts and verdicts <= {"PRESENT", "PRESENT_STATEFUL"}:
        rep.cycle = CYCLE_FULL


def strategy_probe_ton(ep: str, addr: str, entrypoints: list[str], rep: ParityReport) -> None:
    """TON: runGetMethod. exit_code 0 = ada; 11 = ambigu (ada-tapi-salah ATAU tidak ada)."""
    base = ep.rstrip("/")
    # kontrak ada?
    ok, info = http_json(f"{base}/getAddressInformation?address={addr}")
    if not ok or not isinstance(info, dict) or not info.get("ok"):
        rep.notes.append(f"getAddressInformation gagal: {str(info)[:120]}")
        rep.env_attempts.append({"endpoint": base, "result": "fail", "detail": str(info)[:120]})
        return
    res = info.get("result") or {}
    state = res.get("state")
    rep.prerequisites["state"] = state
    rep.prerequisites["code_present"] = bool(res.get("code"))
    if state != "active":
        rep.cycle = CYCLE_PRE
        rep.overall = "HEAD_ONLY_PROVEN"
        rep.strategy = "runGetMethod"
        rep.confidence = CONF_EXACT
        return

    for name in entrypoints:
        method = name.split("(")[0].strip()
        ok2, out = http_json(
            f"{base}/runGetMethod",
            {"address": addr, "method": method, "stack": []},
        )
        if not ok2 or not isinstance(out, dict):
            rep.probes.append(Probe("runGetMethod", addr, False, f"{method}:RPC_FAIL"))
            rep.entrypoints.append(
                EntrypointResult(name=name, verdict="UNVERIFIABLE", evidence=["rpc_fail"])
            )
            continue
        r = out.get("result") or {}
        if not isinstance(r, dict):
            # TON mengembalikan result sebagai string pada error (mis. "Ratelimit exceed")
            txt = str(r)
            if "ratelimit" in txt.lower():
                rep.notes.append(f"ENV_ERROR: rate limit pada {method} - hasil tidak dipakai sebagai bukti")
                rep.entrypoints.append(
                    EntrypointResult(name=name, verdict="ENV_ERROR", evidence=[f"ratelimit:{txt[:40]}"])
                )
            else:
                rep.notes.append(f"{method}: result non-dict -> {txt[:80]}")
                rep.entrypoints.append(
                    EntrypointResult(name=name, verdict="UNVERIFIABLE", evidence=[f"result:{txt[:40]}"])
                )
            continue
        ec = r.get("exit_code")
        rep.probes.append(Probe("runGetMethod", addr, ec == 0, f"{method}:exit={ec}"))
        if ec == 0:
            v = "PRESENT"
        elif ec == 11:
            v = "AMBIGUOUS_EXIT11"  # TON tidak membedakan "tidak ada" vs "stack salah"
        else:
            v = "PRESENT_REVERTING"
        rep.entrypoints.append(
            EntrypointResult(name=name, verdict=v, evidence=[f"exit_code:{ec}"])
        )
    rep.strategy = "runGetMethod"
    rep.confidence = CONF_HEURISTIC
    rep.cycle = CYCLE_PARTIAL


# --------------------------------------------------------------------------
# REGISTRY PARADIGMA — rantai baru didaftarkan, bukan ditambahkan ke if/elif
# --------------------------------------------------------------------------

STRATEGIES: dict[str, dict[str, Any]] = {}


def register(paradigm: str, strategy: str, confidence: str, fn, aliases: tuple[str, ...] = ()) -> None:
    """Daftarkan strategi untuk paradigma. Rantai baru = satu panggilan register."""
    entry = {"strategy": strategy, "confidence": confidence, "fn": fn}
    STRATEGIES[paradigm.lower()] = entry
    for a in aliases:
        STRATEGIES[a.lower()] = entry


def strategies_available() -> list[str]:
    return sorted({k for k in STRATEGIES})


def strategy_generic_explorer(ep: str, addr: str, entrypoints: list[str], rep: ParityReport) -> None:
    """
    Paradigma GENERIC untuk rantai yang BELUM DIKENALI.

    Prinsip: JANGAN menebak. Ambil apa pun yang bisa diambil (endpoint hidup?
    kode/akun ada?). Bila hanya bisa membuktikan KEBERADAAN kode tetapi TIDAK
    bisa membuktikan keberadaan entrypoint -> IDENTITY_ONLY + PARTIAL.

    DILARANG menyimpulkan ABSENT untuk paradigma generic.
    """
    rep.strategy = "generic"
    rep.confidence = "PARTIAL"

    ok, info = http_json(ep)
    rep.prerequisites["endpoint_reachable"] = ok
    # Probe JSON-RPC apa pun yang mungkin didukung; endpoint JSON-RPC memang tidak
    # menjawab GET biasa, jadi kegagalan GET BUKAN bukti endpoint mati.
    if not ok:
        rep.prerequisites["get_root_failed"] = True

    probes = [
        ("getAccountInfo", [addr, {"encoding": "base64"}]),
        ("eth_getCode", [addr, "latest"]),
        ("getAccount", [addr]),
        ("query_account", [addr]),
    ]
    found_code = False
    for method, params in probes:
        okp, res = rpc(ep, method, params)
        if not okp:
            continue
        rep.prerequisites[f"{method}_ok"] = True
        if isinstance(res, str) and res not in ("0x", ""):
            found_code = True
            rep.prerequisites["code_len"] = (len(res) - 2) // 2
            break
        if isinstance(res, dict) and res:
            found_code = True
            rep.prerequisites["account_object"] = True
            break

    if not found_code:
        rep.notes.append(
            "Tidak dapat membuktikan keberadaan kode maupun ketiadaannya. "
            "Verdict ABSENT DILARANG untuk paradigma generic."
        )
        rep.overall = "UNVERIFIABLE"
        rep.confidence = CONF_UNVERIFIABLE
        return

    rep.cycle = CYCLE_PARTIAL
    rep.overall = "IDENTITY_ONLY"
    rep.notes.append(
        "Kode/akun TERBUKTI ADA, tetapi daftar entrypoint tidak dapat dibaca otomatis. "
        "Wajib verifikasi manual atau tambahkan plugin paradigma (--plugin-dir)."
    )
    for name in entrypoints:
        rep.entrypoints.append(
            EntrypointResult(name=name, verdict="IDENTITY_ONLY", evidence=["generic:no-entrypoint-registry"])
        )


# Daftar strategi resmi (alias memungkinkan --paradigm ethereum/arbitrum/base dst.)
register("evm", "probe+push4", CONF_HEURISTIC, None, ("ethereum", "arbitrum", "base", "optimism", "polygon", "bsc", "avalanche", "blast", "linea", "scroll"))
register("solana", "attestation", CONF_EXACT, None, ("svm",))
register("sui", "registry", CONF_EXACT, None, ("move-sui",))
register("aptos", "registry", CONF_EXACT, None, ("move-aptos",))
register("ton", "runGetMethod", CONF_HEURISTIC, None, ("telegram",))
register("generic", "generic", "PARTIAL", None, ("unknown", "auto"))


def load_plugins(dirs: list[str]) -> int:
    """
    Muat plugin paradigma dari folder luar TANPA mengedit skrip ini.

    Plugin adalah file .py yang mendaftarkan strateginya sendiri:
        import deploy_parity as dp
        dp.register("tron", "probe", dp.CONF_HEURISTIC, my_strategy_fn)
    """
    import importlib.util

    # Saat skrip dijalankan sebagai __main__, modul ini TIDAK terdaftar sebagai
    # 'deploy_parity' di sys.modules. Tanpa pendaftaran ini, plugin yang menulis
    # `import deploy_parity as dp` akan memuat instance KEDUA dengan STRATEGIES
    # kosong -> register() tidak berpengaruh ke proses utama.
    this = sys.modules.get("deploy_parity")
    if this is None and "__main__" in sys.modules:
        sys.modules["deploy_parity"] = sys.modules["__main__"]

    loaded = 0
    for d in dirs:
        if not d or not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py") or fn.startswith("_"):
                continue
            path = os.path.join(d, fn)
            try:
                spec = importlib.util.spec_from_file_location(f"dp_plugin_{fn[:-3]}", path)
                if not spec or not spec.loader:
                    continue
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if getattr(mod, "PARADIGM", None):
                    loaded += 1
            except Exception as e:  # noqa: BLE001
                print(f"WARN plugin gagal: {fn}: {e}", file=sys.stderr)
    return loaded


# --------------------------------------------------------------------------
# Orkestrasi
# --------------------------------------------------------------------------


def _default_fn_for(par: str):
    """Peta paradigma -> fungsi strategi (dipakai registry saat fn belum diisi)."""
    return {
        "evm": strategy_probe_evm,
        "ton": strategy_probe_ton,
        "solana": strategy_attestation_solana,
        "aptos": strategy_registry_aptos,
        "sui": strategy_registry_sui,
        "generic": strategy_generic_explorer,
    }.get(par)


def analyse(rep: ParityReport, ep: str, addr: str, entrypoints: list[str]) -> None:
    par = rep.paradigm.lower().strip()

    entry = STRATEGIES.get(par)
    if not entry:
        # Rantai belum dikenal: JANGAN mati, jalankan strategi generic yang jujur.
        rep.notes.append(
            f"Paradigma '{rep.paradigm}' belum terdaftar -> memakai strategi generic "
            f"(tersedia: {', '.join(strategies_available())})"
        )
        entry = STRATEGIES["generic"]

    fn = entry.get("fn") or _default_fn_for(rep.paradigm.lower())
    if fn is None:
        # Registry menyimpan fn=None untuk strategi bawaan; resolusi via nama strategi.
        by_strategy = {
            "probe+push4": strategy_probe_evm,
            "runGetMethod": strategy_probe_ton,
            "attestation": strategy_attestation_solana,
            "registry": None,  # ambigu (aptos vs sui) -> pakai paradigma
            "generic": strategy_generic_explorer,
        }
        fn = by_strategy.get(entry["strategy"])
        if fn is None and entry["strategy"] == "registry":
            fn = {"aptos": strategy_registry_aptos, "sui": strategy_registry_sui}.get(par)
        if fn is None:
            fn = strategy_generic_explorer
            rep.notes.append(
                f"Tidak ada implementasi spesifik untuk '{rep.paradigm}'; memakai generic"
            )
    fn(ep, addr, entrypoints, rep)
    # Strategi boleh menimpa confidence; kalau tidak, pakai default registry.
    if rep.confidence in ("", CONF_UNVERIFIABLE) and rep.entrypoints:
        rep.confidence = entry["confidence"]
    if not rep.strategy:
        rep.strategy = entry["strategy"]

    # Kesimpulan agregat
    verdicts = [e.verdict for e in rep.entrypoints]
    if rep.overall == "IDENTITY_ONLY":
        # Paradigma generic: kode terbukti ada, entrypoint tidak dapat dibuktikan.
        # ABSENT DILARANG; jangan ditimpa oleh logika agregat di bawah.
        rep.cycle = rep.cycle if rep.cycle != CYCLE_UNKNOWN else CYCLE_PARTIAL
    elif not verdicts:
        rep.overall = "UNVERIFIABLE"
    elif any(v in ("ENV_ERROR", "UNVERIFIABLE") for v in verdicts):
        # Kegagalan lingkungan / tidak terverifikasi TIDAK PERNAH menjadi bukti ketiadaan
        rep.overall = "UNVERIFIABLE"
    elif all(v in ("PRESENT", "PRESENT_STATEFUL") for v in verdicts):
        rep.overall = "LIVE_MATCH"
    elif any(v in ("AMBIGUOUS_EXIT11", "FALLBACK_PERMISSIVE_UNKNOWN") for v in verdicts):
        rep.overall = "UNVERIFIABLE"
    elif any(v == "UNRESOLVED_EXACT" for v in verdicts) and rep.confidence == CONF_EXACT:
        # Identitas deployment EXACT (Solana): entrypoint belum per-nama, tapi identitas sah
        rep.overall = "LIVE_MATCH"
    elif any(v in ("RELAYED_VIA_HANDLER", "PRESENT_STATEFUL") for v in verdicts):
        rep.overall = "ENTRYPOINT_RELOCATED"
    else:
        rep.overall = "ENTRYPOINT_ABSENT"


def git_ref_info(repo: str) -> dict[str, Any]:
    """Ambil HEAD, tag terdekat, dan jarak commit — untuk artefak."""
    info: dict[str, Any] = {}
    try:
        r = subprocess.run(
            ["git", "-C", repo, "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=20
        )
        if r.returncode == 0:
            info["head"] = r.stdout.strip()
        r = subprocess.run(
            ["git", "-C", repo, "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if r.returncode == 0:
            info["describe"] = r.stdout.strip()
    except Exception as e:  # noqa: BLE001
        info["error"] = str(e)
    return info


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Gerbang Siklus Deployment & Kesetaraan Entrypoint")
    p.add_argument("--paradigm", help="evm|solana|sui|aptos|ton|generic|<plugin> (bebas, tak dikenal -> generic)")
    p.add_argument("--chain", default="mainnet", choices=["mainnet", "testnet", "local"])
    p.add_argument("--addr", help="Alamat kontrak / program / module id")
    p.add_argument("--rpc", help="Endpoint RPC")
    p.add_argument("--entrypoints", default="", help="Daftar signature/fungsi")
    p.add_argument("--calibration", default=DEFAULT_CALIBRATION)
    p.add_argument("--artifact", help="Path repo/artefak build yang diuji (opsional)")
    p.add_argument("--repo", help="Path repo git untuk info HEAD/tag")
    p.add_argument("--out", help="Tulis laporan JSON ke path ini")
    p.add_argument("--plugin-dir", action="append", default=[], help="Folder plugin paradigma (bisa berkali-kali)")
    p.add_argument("--list-paradigms", action="store_true", help="Tampilkan paradigma terdaftar")
    p.add_argument("--selftest", action="store_true")
    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)

    if args.plugin_dir:
        n = load_plugins(args.plugin_dir)
        if n:
            print(f"plugin dimuat: {n}", file=sys.stderr)

    if args.list_paradigms:
        for k in strategies_available():
            e = STRATEGIES[k]
            print(f"{k:12s} strategy={e['strategy']:12s} confidence={e['confidence']}")
        return 0

    if args.selftest:
        return selftest(args.plugin_dir)

    if not (args.paradigm and args.addr and args.rpc):
        print("ERROR: --paradigm, --addr, --rpc wajib", file=sys.stderr)
        return 2

    # Entrypoint dengan parameter bertanda koma harus dikutip; deteksi pemisahan rusak.
    # ';' adalah pemisah aman; ',' hanya aman di luar tanda kurung.
    def _split_sigs(s: str) -> list[str]:
        out: list[str] = []
        depth = 0
        cur = ""
        for ch in s:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            if ch == ";" or (ch == "," and depth == 0):
                if cur.strip():
                    out.append(cur.strip())
                cur = ""
            else:
                cur += ch
        if cur.strip():
            out.append(cur.strip())
        return out

    eps = _split_sigs(args.entrypoints)
    if not eps:
        print("ERROR: --entrypoints wajib minimal satu", file=sys.stderr)
        return 2

    # Entrypoint dengan parameter bertanda koma harus dikutip; deteksi pemisahan rusak.
    broken = [e for e in eps if "(" in e and ")" not in e]
    if broken:
        print(
            "ERROR: entrypoint terpotong (koma di dalam tanda kurung). "
            "Gunakan pemisah ';' atau kutip tiap signature.\n"
            f"  terpotong: {broken}\n"
            f"  contoh  : --entrypoints 'setRegistry(address,address[],uint8);getRegistry()'",
            file=sys.stderr,
        )
        return 2

    rep = ParityReport(
        paradigm=args.paradigm,
        chain=args.chain,
        address=args.addr,
        generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )
    rep.env_attempts.append({"endpoint": args.rpc, "result": "attempted"})
    if args.repo:
        rep.repo_ref = git_ref_info(args.repo)

    analyse(rep, args.rpc, args.addr, eps)

    text = rep.to_json()
    if args.out:
        tmp = args.out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, args.out)
        print(f"artefak: {args.out}")
    else:
        print(text)

    # Exit code: non-zero bila tidak match (memaksa pemanggil memperhatikan)
    return 0 if rep.overall in ("LIVE_MATCH", "ENTRYPOINT_RELOCATED", "HEAD_ONLY_PROVEN") else 1


# --------------------------------------------------------------------------
# Selftest — 7 kasus kontrol yang sudah diukur di mainnet
# --------------------------------------------------------------------------

SELFTEST_CASES = [
    # (label, paradigm, addr, rpc_var, entrypoint, expected_overall)
    ("usdc-proxy", "evm", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "RPC_ETH", "name()", "LIVE_MATCH"),
    ("weth-fallback", "evm", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "RPC_ETH", "name()", "LIVE_MATCH"),
    ("nexus-execute", "evm", "0x0000B1c01cB3b5770D8806f0D214d50131a08a5B", "RPC_ETH", "execute(bytes32,bytes)", "LIVE_MATCH"),
    ("nexus-owner", "evm", "0x0000B1c01cB3b5770D8806f0D214d50131a08a5B", "RPC_ETH", "owner()", "ENTRYPOINT_RELOCATED"),
    ("aave-supply", "evm", "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2", "RPC_ETH", "supply(address,uint256,address,uint16)", "LIVE_MATCH"),
    ("aave-owner", "evm", "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2", "RPC_ETH", "owner()", "ENTRYPOINT_ABSENT"),
    ("aptos-coin", "aptos", "0x1::coin", "RPC_APTOS", "transfer", "LIVE_MATCH"),
    # Non-EVM: identitas deployment (attestation) — TIDAK butuh CLI
    ("solana-token", "solana", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", "RPC_SOL", "Transfer", "LIVE_MATCH"),
    # TON: exit_code 0 = ada; method tak dikenal = ENV/ambigu, bukan ABSENT
    ("ton-jetton", "ton", "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs", "RPC_TON", "get_jetton_data", "LIVE_MATCH"),
    # Sui: registry fungsi eksplisit (modul kecil -> EXACT, bisa klaim ABSENT)
    ("sui-balance", "sui", "0x2::balance", "RPC_SUI", "value", "LIVE_MATCH"),
    ("sui-absent", "sui", "0x2::balance", "RPC_SUI", "nonexistent_zzz", "ENTRYPOINT_ABSENT"),
    # Sui modul besar (50+ fungsi) -> kelengkapan tak pasti -> WAJIB UNVERIFIABLE
    ("sui-bigmod", "sui", "0x2::coin", "RPC_SUI", "nonexistent_zzz", "UNVERIFIABLE"),
    # Rantai tak dikenal -> generic IDENTITY_ONLY (ABSENT DILARANG)
    ("generic-known-code", "customchain", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "RPC_ETH", "name()", "IDENTITY_ONLY"),
    # Plugin eksternal (Tron) — hanya bila plugin berhasil dimuat
    ("tron-usdt", "tron", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t", "RPC_TRON", "decimals()", "LIVE_MATCH"),
]


def load_env_rpc() -> dict[str, str]:
    """Baca .env.rpc dari beberapa lokasi kandidat."""
    cands = [
        os.path.join(os.path.dirname(__file__), "..", "..", "workspace", ".env.rpc"),
        os.path.expanduser("~/.hermes/profiles/adv/workspace/.env.rpc"),
        "/home/ubuntu/repos/theadver/workspace/.env.rpc",
    ]
    out: dict[str, str] = {}
    for c in cands:
        if os.path.isfile(c):
            for line in open(c, encoding="utf-8", errors="ignore"):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.split("#")[0].strip()
    return out


def selftest(plugin_dirs: list[str] | None = None) -> int:
    env = load_env_rpc()
    if plugin_dirs:
        load_plugins(plugin_dirs)
    eth = env.get("RPC_ETHEREUM") or env.get("RPC_ETH") or "https://ethereum-rpc.publicnode.com"
    endpoints = {
        "RPC_APTOS": env.get("RPC_APTOS_REST", ""),
        "RPC_SOL": env.get("RPC_SOLANA", "") or "https://api.mainnet-beta.solana.com",
        "RPC_TON": env.get("RPC_TON_CENTER", "") or "https://toncenter.com/api/v2",
        "RPC_SUI": env.get("RPC_SUI_GRAPHQL", "") or "https://graphql.mainnet.sui.io/graphql",
        "RPC_TRON": env.get("RPC_TRON_HTTP", "") or "https://api.trongrid.io",
    }

    passed = failed = skipped = 0
    for label, par, addr, rpcvar, ep, expected in SELFTEST_CASES:
        if par == "aptos":
            rpcurl = endpoints["RPC_APTOS"]
        elif par in ("solana", "ton", "sui", "tron"):
            rpcurl = endpoints.get(rpcvar, "")
        else:
            rpcurl = eth
        if not rpcurl:
            print(f"[SKIP] {label:18s} endpoint {rpcvar} tidak tersedia")
            skipped += 1
            continue
        # Paradigma non-bawaan harus terdaftar; kalau tidak, lewati (bukan gagal).
        if par not in STRATEGIES and par != "customchain":
            print(f"[SKIP] {label:18s} paradigma '{par}' belum terdaftar (plugin diperlukan)")
            skipped += 1
            continue
        rep = ParityReport(paradigm=par, chain="mainnet", address=addr)
        analyse(rep, rpcurl, addr, [ep])
        status = "PASS" if rep.overall == expected else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1
        detail = ", ".join(f"{e.name}={e.verdict}" for e in rep.entrypoints)
        print(f"[{status}] {label:18s} got={rep.overall:22s} exp={expected:22s} {detail}")

    print(f"\nSELFTEST: {passed} passed, {failed} failed, {skipped} skipped")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
