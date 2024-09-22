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


def gamut(neuPos, maxPos, chan=1, steps=8, slp=0.1):
    print("Moving from %3d to %3d" % (neuPos, maxPos))
    for idx in range(0, steps):
        pos = neuPos + int((idx+1)/steps*(maxPos-neuPos))
        print("%2d - moving to %3d, sleeping %d..." % (idx, pos, slp))
        pwm.set_pwm(chan, 0, pos)
        time.sleep(slp)
    pwm.set_pwm(chan, 0, neuPos)
    time.sleep(slp)



# servo pulse lengths
minPos = int(0.029 * 4096)  # min pulse length - out of 4096
neuPos0 = int(0.046 * 4096) - 90  
neuPos1 = int(0.046 * 4096)  # neutral pos
maxPos = int(0.130 * 4096)  # max pos


pwm.set_pwm(0, 0, neuPos0)
time.sleep(0.8)
gamut(neuPos0,maxPos,0,28,0.15)
pwm.set_pwm(0, 0, 300)

gamut(neuPos1,maxPos,1)



