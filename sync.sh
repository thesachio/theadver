#!/usr/bin/env bash
# Sinkronisasi artefak workflow: profil aktif (sumber kebenaran) -> repo ini.
#
# AMAN SECARA DEFAULT: tanpa argumen, skrip ini HANYA menampilkan apa yang akan
# berubah. Tidak menyalin, tidak commit, tidak push.
#
#   ./sync.sh                       lihat saja (dry-run, tidak mengubah apa pun)
#   ./sync.sh --apply               salin profil -> repo, BELUM commit
#   ./sync.sh --commit "pesan"      commit lokal, BELUM push
#   ./sync.sh --push                push ke GitHub (minta konfirmasi ketik 'push')
#   ./sync.sh --all "pesan"         apply + commit + push (juga minta konfirmasi)
#
set -euo pipefail

PROFILE="${PROFILE:-/home/ubuntu/.hermes/profiles/adv}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PATHS=(
  "skills/security/sc-autopilot"
  "skills/security/sc-phase1-recon"
  "skills/security/sc-phase2-hunt"
  "skills/security/sc-phase3-verify-and-poc"
  "skills/security/sc-phase4-report"
  "verify/VERDICT.md"
  "verify/templates"
  "verify/tools"
  "workspace/AGENTS.md"
  "workspace/rpc-env.sh"
  "workspace/rpc-free-tier.md"
  "workspace/RPC-STATUS.md"
  "workspace/.env.rpc"
  "SOUL.md"
)

MODE="dry"; MSG=""
case "${1:-}" in
  ""|--dry)  MODE="dry" ;;
  --apply)   MODE="apply" ;;
  --commit)  MODE="commit"; MSG="${2:-}" ;;
  --push)    MODE="push" ;;
  --all)     MODE="all"; MSG="${2:-}" ;;
  -h|--help) sed -n '2,15p' "${BASH_SOURCE[0]}"; exit 0 ;;
  *) echo "ERROR: argumen tidak dikenal: $1 (pakai --help)"; exit 1 ;;
esac

if { [ "$MODE" = "commit" ] || [ "$MODE" = "all" ]; } && [ -z "$MSG" ]; then
  echo "ERROR: mode $MODE butuh pesan commit. Contoh: ./sync.sh --commit \"feat(pov): [POV-04]\""; exit 1
fi

echo "== sumber: $PROFILE"
echo "== tujuan: $REPO"
echo "== mode  : $MODE"
echo

if [ "$MODE" = "dry" ]; then
  echo "-- perubahan yang AKAN disalin (belum diterapkan) --"
  ada=0
  for p in "${PATHS[@]}"; do
    src="$PROFILE/$p"; dst="$REPO/$p"
    [ -e "$src" ] || continue
    if [ -d "$src" ]; then
      out="$(rsync -an --itemize-changes --exclude '*.bak' --exclude '.DS_Store' "$src/" "$dst/" | grep -v '^\.d' || true)"
      if [ -n "$out" ]; then echo "$out" | sed "s|^|  [$p] |"; ada=1; fi
    else
      if ! cmp -s "$src" "$dst" 2>/dev/null; then echo "  [$p] berbeda"; ada=1; fi
    fi
  done
  echo
  if [ "$ada" = "0" ]; then
    echo "Tidak ada perbedaan — repo sudah sinkron dengan profil. Tidak ada yang diubah."
  else
    echo "Tidak ada yang diubah. Langkah berikutnya (pilih satu):"
    echo "  ./sync.sh --apply               salin ke repo saja"
    echo "  ./sync.sh --commit \"pesan\"      salin + commit lokal (tanpa push)"
    echo "  ./sync.sh --all \"pesan\"         salin + commit + push"
  fi
  exit 0
fi

if [ "$MODE" = "apply" ] || [ "$MODE" = "commit" ] || [ "$MODE" = "all" ]; then
  echo "-- menyalin dari profil --"
  n=0
  for p in "${PATHS[@]}"; do
    src="$PROFILE/$p"; dst="$REPO/$p"
    [ -e "$src" ] || { echo "  ! tidak ada di profil, dilewati: $p"; continue; }
    mkdir -p "$(dirname "$dst")"
    if [ -d "$src" ]; then
      rsync -a --exclude '*.bak' --exclude '.DS_Store' "$src/" "$dst/"
    else
      cp -p "$src" "$dst"
    fi
    n=$((n+1))
  done
  echo "  $n jalur disalin (backup *.bak selalu dilewati)"
  echo
fi

cd "$REPO"

if [ "$MODE" = "apply" ]; then
  echo "-- status repo (BELUM di-commit) --"
  [ -z "$(git status --porcelain)" ] && echo "  (tidak ada perubahan)" || git status --short
  echo
  echo "Tinjau dengan: git diff"
  echo "Lalu:          ./sync.sh --commit \"pesan\""
  exit 0
fi

if [ "$MODE" = "commit" ] || [ "$MODE" = "all" ]; then
  if [ -z "$(git status --porcelain)" ]; then
    echo "tidak ada perubahan untuk di-commit."
    [ "$MODE" = "commit" ] && exit 0
  else
    git add -A
    git commit -q -m "$MSG"
    echo "-- commit lokal --"
    git log --oneline -1
    echo
  fi
fi

if [ "$MODE" = "commit" ]; then
  echo "Commit ini BELUM dikirim ke GitHub."
  echo "Untuk mengirim: ./sync.sh --push"
  exit 0
fi

BRANCH="$(git branch --show-current)"
LOCAL="$(git rev-parse --short HEAD)"
REMOTE="$(git ls-remote origin "$BRANCH" | cut -c1-7)"
echo
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "remote sudah sama ($LOCAL) — tidak perlu push."
  exit 0
fi
echo "-- akan mengirim $LOCAL ke origin/$BRANCH (remote sekarang $REMOTE) --"
printf "Ketik 'push' untuk melanjutkan: "
read -r konfirmasi
if [ "$konfirmasi" != "push" ]; then
  echo "dibatalkan. Commit tetap aman di lokal."
  exit 0
fi
git push origin "$BRANCH"
echo "-- ter-push: $LOCAL --"
