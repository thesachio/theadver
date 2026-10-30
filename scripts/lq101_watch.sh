#!/usr/bin/env bash
# Monitor L-Q10-1 (shortfall no-debit credit) — tanpa LLM.
# Senyap (stdout kosong) bila tidak ada perubahan.
#
# Sinyal A: fundingPoolFactory / poolDrawResolver muncul di prod/stag
#           -> celah menjadi LIVE, saatnya kirim follow-up PoC on-chain.
# Sinyal B: PoolResolverBase.sol berubah
#           -> cek apakah celah sudah ditambal ("fix already deployed" memotong klaim).
set -uo pipefail

PROFILE="${HOME}/.hermes/profiles/adv"
STATE_DIR="${PROFILE}/state/lq101-monitor"
mkdir -p "$STATE_DIR"

REPO="relayprotocol/relay-settlement"
BRANCH="main"
BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}/smart-contracts"
STATE_FILE="${STATE_DIR}/last-alert.txt"
BASE_H_FILE="${STATE_DIR}/poolresolverbase.baseline.sha256"

alerts=""

# ---------- Sinyal A: deployment produksi ----------
for env in prod stag; do
  body=$(curl -fsS -m 25 "${BASE}/deployments/contracts/${env}.json" 2>/dev/null) || continue
  for key in fundingPoolFactory poolDrawResolver; do
    if printf '%s' "$body" | grep -q "\"${key}\""; then
      addr=$(printf '%s' "$body" \
        | grep -o "\"${key}\"[[:space:]]*:[[:space:]]*\"0x[0-9a-fA-F]\{40\}\"" \
        | head -1 | grep -o '0x[0-9a-fA-F]\{40\}')
      alerts+="[LQ101] DEPLOYED di ${env}: ${key} = ${addr:-<alamat tidak terbaca>}"
      alerts+=$'\n'
    fi
  done
done

# ---------- Sinyal B: source fungsi rentan berubah ----------
src_url="${BASE}/contracts/call-resolvers/PoolResolverBase.sol"
if src=$(curl -fsS -m 25 "$src_url" 2>/dev/null); then
  h=$(printf '%s' "$src" | sha256sum | cut -d' ' -f1)
  if [ -f "$BASE_H_FILE" ]; then
    prev=$(cat "$BASE_H_FILE")
    if [ "$h" != "$prev" ]; then
      alerts+="[LQ101] PATCH: PoolResolverBase.sol berubah (baseline ${prev:0:12} -> ${h:0:12})"
      alerts+=$'\n'
      alerts+="        Cek apakah _runShortfallLeg masih meng-credit tanpa syarat amountDrawn."
      alerts+=$'\n'
      printf '%s' "$h" > "$BASE_H_FILE"
    fi
  else
    printf '%s' "$h" > "$BASE_H_FILE"
  fi
fi

# Senyap bila tidak ada sinyal
[ -z "$alerts" ] && exit 0

# Dedupe: jangan kirim alert yang sama dua kali
if [ -f "$STATE_FILE" ] && [ "$(cat "$STATE_FILE")" = "$alerts" ]; then
  exit 0
fi
printf '%s' "$alerts" > "$STATE_FILE"

printf '%s\n' "=== LQ101 MONITOR ==="
printf '%s' "$alerts"
printf '%s\n' "Repo: https://github.com/${REPO}"
printf '%s\n' "Catatan kerja: audit/notes/verify-LQ101-shortfall-credit.md"
