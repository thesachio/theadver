#!/usr/bin/env bash
# Sinkronkan artefak workflow dari profil aktif (sumber kebenaran) ke repo ini.
#
#   ./sync.sh                       -> salin + tampilkan perubahan (belum commit)
#   ./sync.sh "feat(pov): [POV-04]" -> salin + commit + push
#
set -euo pipefail

PROFILE="${PROFILE:-/home/ubuntu/.hermes/profiles/adv}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Yang dilacak: skill workflow, standar hakim, template, konstitusi, persona.
PATHS=(
  "skills/security/sc-autopilot"
  "skills/security/sc-phase1-recon"
  "skills/security/sc-phase2-hunt"
  "skills/security/sc-phase3-verify-and-poc"
  "skills/security/sc-phase4-report"
  "verify/VERDICT.md"
  "verify/templates"
  "workspace/AGENTS.md"
  "workspace/rpc-env.sh"
  "workspace/.env.rpc"
  "SOUL.md"
)

echo "== sumber: $PROFILE"
echo "== tujuan: $REPO"
echo

n=0
for p in "${PATHS[@]}"; do
  src="$PROFILE/$p"
  dst="$REPO/$p"
  [ -e "$src" ] || { echo "  ! tidak ada di profil, dilewati: $p"; continue; }
  mkdir -p "$(dirname "$dst")"
  if [ -d "$src" ]; then
    rsync -a --exclude '*.bak' --exclude '.DS_Store' "$src/" "$dst/"
  else
    cp -p "$src" "$dst"
  fi
  n=$((n+1))
done
echo "  $n jalur disalin (backup *.bak tidak ikut)"

cd "$REPO"
echo
echo "== status =="
if [ -z "$(git status --porcelain)" ]; then
  echo "  tidak ada perubahan — repo sudah sinkron dengan profil."
  exit 0
fi
git status --short
echo
git diff --stat

if [ $# -ge 1 ]; then
  git add -A
  git commit -q -m "$1"
  echo
  echo "== commit =="
  git log --oneline -1
  git push origin "$(git branch --show-current)"
  echo "== ter-push: $(git rev-parse --short HEAD) =="
else
  echo
  echo "Tinjau perubahan di atas, lalu jalankan:"
  echo '  ./sync.sh "feat(pov): [POV-04] judul singkat"'
fi
