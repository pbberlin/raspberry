echo "start"
echo q | htop | aha --black --line-fix > /home/pi/webserver/dump-htop.html
# bash -c 'echo q | htop | aha --black --line-fix > /home/pi/webserver/dump-htop.html'
echo "end"
