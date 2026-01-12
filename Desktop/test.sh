FRITZBOX="http://fritz.box"
USER="pbu"
PASS="Pb165205."
AIN="15282 0563726"

Challenge=$(curl -sS "$FRITZBOX/login_sid.lua" | sed -n 's/.*<Challenge>\(.*\)<\/Challenge>.*/\1/p')
ResponseHash=$(printf "%s-%s" "$Challenge" "$PASS" | iconv -t UTF-16LE | md5sum | awk '{print $1}')
Sid=$(curl -sS "$FRITZBOX/login_sid.lua?username=$USER&response=$Challenge-$ResponseHash" | sed -n 's/.*<SID>\(.*\)<\/SID>.*/\1/p')

echo "SID=$Sid"

curl -sS -o - -w "\nHTTP:%{http_code}\n" \
  "$FRITZBOX/webservices/homeautoswitch.lua" \
  --data-urlencode "sid=$Sid" \
  --data-urlencode "ain=$AIN" \
  --data-urlencode "switchcmd=gethkrtsoll"
