import subprocess

# res = subprocess.Popen(["sudo","fswebcam", "-r 640x480", "grab.jpeg"], shell=False, stdout=subprocess.PIPE, cwd="/var/www/pics")
res = subprocess.Popen(["fswebcam", "-r 640x480", "grab.jpg"], shell=False, stdout=subprocess.PIPE, cwd="/home/pi")
output = res.communicate()[0]
