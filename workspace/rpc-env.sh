#!/usr/bin/env bash
# =============================================================================
# rpc-env.sh — loader endpoint RPC publik untuk fork lokal read-only
# =============================================================================
# PEMISAHAN FILE (penting, jangan dicampur):
#   .env       -> SECRET (API key, bot token). JANGAN PERNAH di-commit.
#   .env.rpc   -> ENDPOINT PUBLIK no-key. Aman di-commit. File ini loader-nya.
#
# Pakai:
#   source ./rpc-env.sh                # tanpa argumen: muat ke shell saat ini
#   ./rpc-env.sh                       # dieksekusi: cetak daftar, tidak mengubah shell induk
#   ./rpc-env.sh ethereum              # cetak URL satu rantai (untuk $(...) di skrip)
#   ./rpc-env.sh list                  # tabel semua endpoint + status singkat
#
# Contoh:
#   forge test -j 1 --fork-url "$(./rpc-env.sh ethereum)"
#   anvil --fork-url "$(./rpc-env.sh base)" --port 8545
#   cast block-number --rpc-url "$(./rpc-env.sh arbitrum)"
#
# ATURAN KERAS (workspace/AGENTS.md Pasal 1.1):
#   Hanya LOCAL READ-ONLY FORK. DILARANG --broadcast, cast send, atau transaksi
#   apa pun yang mengubah state jaringan publik.
# =============================================================================

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RPC_FILE="${SCRIPT_DIR}/.env.rpc"

if [ ! -f "$RPC_FILE" ]; then
  echo "ERROR: $RPC_FILE tidak ditemukan." >&2
  return 1 2>/dev/null || exit 1
fi

_adv_load_rpc() {
  # set -a -> semua variabel otomatis di-export (terbaca subprocess forge/anvil/cast)
  set -a
  # shellcheck disable=SC1090
  . "$RPC_FILE"
  set +a
}

_adv_get() {
  local key
  key=$(echo "$1" | tr '[:lower:]' '[:upper:]')
  case "$key" in
    ETH|MAINNET)              key="ETHEREUM" ;;
    ARB)                      key="ARBITRUM" ;;
    OP)                       key="OPTIMISM" ;;
    MATIC|POL)                key="POLYGON" ;;
    AVAX|AVALANCHE_C)         key="AVALANCHE" ;;
    XDAI)                     key="GNOSIS" ;;
  esac
  # baca dari file tanpa mengekspor ke shell induk; buang komentar inline + spasi
  local val
  val=$(grep -E "^RPC_${key}=" "$RPC_FILE" 2>/dev/null | head -1 | cut -d= -f2-)
  val="${val%%#*}"
  val="$(echo "$val" | xargs)"
  if [ -z "$val" ]; then
    echo "ERROR: rantai '$1' tidak dikenal atau kosong. Coba: list" >&2
    return 1
  fi
  echo "$val"
}

_adv_list() {
  printf "%-14s %s\n" "ALIAS" "ENDPOINT"
  printf "%-14s %s\n" "------------" "------------------------------------------"
  grep -E '^RPC_[A-Z0-9_]+=' "$RPC_FILE" | while IFS='=' read -r k v; do
    v="${v%%#*}"; v="$(echo "$v" | xargs)"
    [ -z "$v" ] && v="(kosong — isi manual)"
    printf "%-14s %s\n" "${k#RPC_}" "$v"
  done
}

case "${1:-}" in
  "")
    if [ "${BASH_SOURCE[0]}" != "${0}" ]; then
      _adv_load_rpc
      echo "RPC dimuat ke shell ini. Coba: echo \$RPC_ETHEREUM"
      _adv_list
    else
      echo "Dieksekusi (bukan di-source) — shell induk tidak berubah."
      echo "Untuk memuat ke shell saat ini:  source ./rpc-env.sh"
      echo
      _adv_list
    fi
    ;;
  list|-l|--list)
    _adv_list
    ;;
  -h|--help|help)
    sed -n '2,30p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    ;;
  *)
    _adv_get "$1" || exit 1
    ;;
esac
