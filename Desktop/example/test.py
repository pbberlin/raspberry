import datetime
import time

score = "myScore"

while True:

    print("oh yeah")
    time.sleep(2.5)

    with open("/var/log/test.log", mode='a') as file:
        file.write("My score '%s' - recorded at %s.\n" % (score, datetime.datetime.now()))
        time.sleep(30.5)


