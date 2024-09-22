import RPi.GPIO as GPIO
import time
import traceback

channel = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)


def relaisOn(pin):
        GPIO.output(pin, GPIO.HIGH)

def relaisOff(pin):
        GPIO.output(pin, GPIO.LOW)


if __name__ == '__main__':
    try:
        relaisOn(channel)
        time.sleep(1110*100)
        relaisOff(channel)
        time.sleep(1)
    except Exception as e:
        print("camLoop: Problems starting camera")
        print(traceback.format_exc())
    finally:
        GPIO.cleanup()
        print("cleaned up")
