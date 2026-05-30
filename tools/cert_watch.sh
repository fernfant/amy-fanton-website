#!/bin/bash
# Watches the GitHub Pages cert, writes status to cert-update/, commits+pushes every 30 min.
# Exits (and notifies) once the cert leaves authorization_created.
cd /Users/fernando/Projects/amy-fanton-website || exit 1
REPO=fernfant/amy-fanton-website
OUT=cert-update/STATUS.md
HIST=cert-update/history.log

doh() { curl -s -H 'accept: application/dns-json' "https://cloudflare-dns.com/dns-query?name=$1&type=$2" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(', '.join(a['data'] for a in d.get('Answer',[])) or 'none')"; }

for i in $(seq 1 200); do
  ts=$(date '+%Y-%m-%d %H:%M:%S %Z')
  state=$(gh api repos/$REPO/pages 2>/dev/null | python3 -c 'import sys,json;print(json.load(sys.stdin).get("https_certificate",{}).get("state",""))')
  enforced=$(gh api repos/$REPO/pages 2>/dev/null | python3 -c 'import sys,json;print(json.load(sys.stdin).get("https_enforced"))')
  www_cf=$(doh www.fantonphotography.com CNAME)
  apex_cf=$(doh fantonphotography.com A)
  https=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 https://www.fantonphotography.com/ 2>/dev/null)

  {
    echo "# Cert provisioning status"
    echo
    echo "_Last checked: ${ts}_"
    echo
    echo "| field | value |"
    echo "|---|---|"
    echo "| cert state | \`${state}\` |"
    echo "| https_enforced | \`${enforced}\` |"
    echo "| live HTTPS code | \`${https}\` |"
    echo "| www -> (Cloudflare) | ${www_cf} |"
    echo "| apex A (Cloudflare) | ${apex_cf} |"
    echo
    if [ "$state" = "approved" ]; then
      echo "**APPROVED** — cert issued. Next: enable repo Settings -> Pages -> Enforce HTTPS."
    else
      echo "Waiting on Let's Encrypt to validate against clean DNS. No manual re-triggers (they reset the clock)."
    fi
  } > "$OUT"
  echo "[${ts}] cert=${state} https=${https} enforced=${enforced}" >> "$HIST"

  git add cert-update/ >/dev/null 2>&1
  git commit -m "cert-update: ${ts} (state=${state})" >/dev/null 2>&1
  git pull --rebase origin main >/dev/null 2>&1
  git push origin main >/dev/null 2>&1
  echo "pushed update $i: state=$state https=$https"

  if [ -n "$state" ] && [ "$state" != "authorization_created" ]; then
    echo "STATE CHANGED -> $state"
    break
  fi
  sleep 1800
done
