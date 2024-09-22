""" 
gpiozero.readthedocs.io/en/stable/development.html
www.bluetin.io/python/gpio-pwm-raspberry-pi-h-bridge-dc-motor-control/

"""
from gpiozero import PWMOutputDevice
from time import sleep



# Motor A, left side
PWM_FORWARD_LEFT_PIN = 26	# IN1 - Forward Drive
PWM_REVERSE_LEFT_PIN = 19	# IN2 - Reverse Drive

# Motor B, right side
PWM_FORWARD_RIGHT_PIN =  6	# IN1 - Forward Drive
PWM_REVERSE_RIGHT_PIN = 13	# IN2 - Reverse Drive


# Initialise objects for H-Bridge PWM pins
# Set initial duty cycle to 0 and frequency to 1000
leftFW = PWMOutputDevice(PWM_FORWARD_LEFT_PIN, True, 0, 1000)
leftBW = PWMOutputDevice(PWM_REVERSE_LEFT_PIN, True, 0, 1000)

righFW = PWMOutputDevice(PWM_FORWARD_RIGHT_PIN, True, 0, 1000)
righBW = PWMOutputDevice(PWM_REVERSE_RIGHT_PIN, True, 0, 1000)



def allStop():
	# print("all stopped - start")
	leftFW.value = 0
	leftBW.value = 0
	righFW.value = 0
	righBW.value = 0
	print("all stopped - stop")


def combined(fw,lr):

	lr = lr * 0.7 # less sharp turns, always a little f/b thrust - asymmetetrically applied left/right offset

	if fw < -1.0 or fw > 1.0:
		return ("combined() - invalid fw %s" % str(fw))
	if lr < -1.0 or lr > 1.0:
		return ("combined() - invalid lr %s" % str(fw))

	leftVal =  	0
	righVal =  	0

	if fw >= 0:
		leftVal = min(fw - lr, 1)
		righVal = min(fw + lr, 1)
	else:
		leftVal = max(fw + lr, -1)
		righVal = max(fw - lr, -1)


	if leftVal >= 0:
		leftFW.value = +leftVal
		leftBW.value = 0
	if leftVal < 0:
		leftFW.value = 0
		leftBW.value = -leftVal

	if righVal >= 0:
		righFW.value = +righVal
		righBW.value = 0
	if righVal < 0:
		righFW.value = 0
		righBW.value = -righVal


	return ("fw %s - lr %s" % (leftVal, righVal))



def forwardDrive(zeroToOne):
	if zeroToOne < 0.0:
		# print("forward drive - invalid %s" % str(zeroToOne))
		return
	if zeroToOne > 1.0:
		# print("forward drive - invalid %s" % str(zeroToOne))
		return
	# print("forward drive - start")
	leftFW.value = zeroToOne
	leftBW.value = 0
	righFW.value = zeroToOne
	righBW.value = 0
	# print("forward drive - stop")


def reverseDrive(zeroToOne):
	if zeroToOne < 0.0:
		# print("reverse drive - invalid %s" % str(zeroToOne))
		return
	if zeroToOne > 1.0:
		# print("reverse drive - invalid %s" % str(zeroToOne))
		return
	# print("reverse drive - start")
	leftFW.value = 0
	leftBW.value = zeroToOne
	righFW.value = 0
	righBW.value = zeroToOne
	# print("reverse drive - stop")


def forwardTurnLeft():
	leftFW.value = 0.2
	leftBW.value = 0
	righFW.value = 0.8
	righBW.value = 0


def forwardTurnRight():
	leftFW.value = 0.8
	leftBW.value = 0
	righFW.value = 0.2
	righBW.value = 0


def reverseTurnLeft():
	leftFW.value = 0
	leftBW.value = 0.2
	righFW.value = 0
	righBW.value = 0.8


def reverseTurnRight():
	leftFW.value = 0
	leftBW.value = 0.8
	righFW.value = 0
	righBW.value = 0.2


def spinLeft():
	leftFW.value = 0
	leftBW.value = 1.0
	righFW.value = 1.0
	righBW.value = 0


def SpinRight():
	leftFW.value = 1.0
	leftBW.value = 0
	righFW.value = 0
	righBW.value = 1.0

