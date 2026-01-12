#!/bin/sh


FRITZBOX="http://fritz.box"
USER="pbu"
PASS="Pb165205."
# AIN="12345 6789012"
AIN="15282 0563726"
TEMP_DEFAULT="22.0"

TempArg="$1"

if [ -z "$TempArg" ]; then
  TEMP="$TEMP_DEFAULT"
else
  TEMP="$TempArg"
fi

# AIN normalisieren: Leerzeichen raus (API ist damit am stabilsten)
AIN_NO_SPACE=$(printf "%s" "$AIN" | tr -d ' ')

# TEMP (z.B. 22.0) -> Param (z.B. 44)
PARAM=$(awk -v t="$TEMP" 'BEGIN { printf "%d", (t * 2) }')

if [ "$PARAM" -lt 16 ]; then
  echo "Temperatur zu niedrig: $TEMP (min 8.0)"
  exit 1
fi

# Login: Challenge holen
CHALLENGE=$(curl -sS "$FRITZBOX/login_sid.lua" | sed -n 's/.*<Challenge>\(.*\)<\/Challenge>.*/\1/p')
if [ -z "$CHALLENGE" ]; then
  echo "Konnte Challenge nicht lesen"
  exit 1
fi

# Response berechnen
RESPONSE=$(printf "%s-%s" "$CHALLENGE" "$PASS" | iconv -t UTF-16LE | md5sum | awk '{print $1}')
SID=$(curl -sS "$FRITZBOX/login_sid.lua?username=$USER&response=$CHALLENGE-$RESPONSE" \
  | sed -n 's/.*<SID>\(.*\)<\/SID>.*/\1/p')

if [ -z "$SID" ]; then
  echo "Konnte SID nicht lesen"
  exit 1
fi

if [ "$SID" = "0000000000000000" ]; then
  echo "Login fehlgeschlagen"
  exit 1
fi


echo "SID    --$SID--"
echo "AIN    --$AIN--"
echo "PARAM  --$PARAM--"

RespFile=$(mktemp)

HttpCode=$(curl -sS --get -o "$RespFile" -w "%{http_code}" \
  "$FRITZBOX/webservices/homeautoswitch.lua" \
  --data-urlencode "sid=$SID" \
  --data-urlencode "ain=$AIN" \
  --data-urlencode "switchcmd=sethkrtsoll" \
  --data-urlencode "param=$PARAM")

Result=$(cat "$RespFile")
rm -f "$RespFile"



if [ "$HttpCode" != "200" ]; then
  echo "Setzen fehlgeschlagen (HTTP $HttpCode)"
  echo "$Result"
  exit 1
fi

echo "Thermostat $AIN (ain=$AIN_NO_SPACE) auf $TEMP °C gesetzt (param=$PARAM)"



