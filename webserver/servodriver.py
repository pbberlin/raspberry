from __future__ import division
import time
import Adafruit_PCA9685


#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 to default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()
# Alternatively specify a different address and/or bus:
# pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

pwm.set_pwm_freq(50)   # Set frequency to 60hz, good for servos.


def rangeServo(chan, neutralPos, maxPos, steps=8, slp=0.1):
    print("\tservo move %3d to %3d" % (neutralPos, maxPos))
    for idx in range(0, steps):
        pos = neutralPos + int((idx+1)/steps*(maxPos-neutralPos))
        print("\t  step %2d to %3d - sleep %d..." % (idx, pos, slp))
        pwm.set_pwm(chan, 0, pos)
        time.sleep(slp)
    pwm.set_pwm(chan, 0, neutralPos)
    time.sleep(slp)

def pwmSet(chan, pos):
    pwm.set_pwm(chan, 0, pos)
