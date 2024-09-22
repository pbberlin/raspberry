# https://ssh-tunnel.de/ssh-tunnel-mit-linux/
# ssh -L localport:zielrechner:dest_port -l username gateway/relais
# ssh -L 1119:news.uni-rostock.de:119    -l cb000 cksz.rz.uni-rostock.de

sudo ssh   -L  80:0.0.0.0:80            -l pbu   192.168.0.100

