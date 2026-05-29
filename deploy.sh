#!/usr/bin/env bash
# Switch the live site to a tagged version and deploy it to GitHub Pages.
# Usage: ./deploy.sh v1.0     (any tag from `git tag`)
#        ./deploy.sh          (lists available versions)
set -euo pipefail
cd "$(dirname "$0")"

list() { echo "Available versions:"; git tag | sed 's/^/  /'; }

if [ $# -ne 1 ]; then list; exit 1; fi

TAG="$1"
if ! git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "Unknown version: $TAG"; list; exit 1
fi

git checkout main >/dev/null 2>&1
# Restore only the site content; CNAME and deploy.sh are left untouched.
# Wipe images first so files a newer version added don't linger after a rollback.
git checkout "$TAG" -- index.html styles.css script.js
git rm -rf --quiet images >/dev/null 2>&1 || true
git checkout "$TAG" -- images

if git diff --cached --quiet; then
  echo "$TAG is already live — nothing to deploy."; exit 0
fi

git -c commit.gpgsign=false commit -m "Deploy $TAG"
git push
echo "Deployed $TAG. GitHub Pages will refresh www.fantonphotography.com in ~1 min."
