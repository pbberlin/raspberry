import RPi.GPIO as GPIO  
from time import sleep
# pip install RPi.GPIO
  
# As printed next to the board - i.e. 17, 27, 22
GPIO.setmode(GPIO.BCM)



def readInput(parameter_list):

    in1 = 17

    # Set pio as input
    GPIO.setup(in1, GPIO.IN)


    # Inputs are Boolean values: 1 or 0, GPIO.HIGH or GPIO.LOW, True or False
    # (this corresponds to the voltage on the port: 0V=0 or 3.3V=1).
    # You can read the value of a port with this code…
    inpt = GPIO.input(in1)

    try:
        while True:            # until you hit CTRL+C
            if GPIO.input(in1):  # if port engineOne == 1
                print("Port %d is 1 / GPIO.HIGH / True" % in1)
            else:
                print("Port %d is 0 / GPIO.LOW / False" % in1)
            sleep(0.1)         # 0.1 seconds

    except KeyboardInterrupt:
        GPIO.cleanup()



# Motor A:
# PWM =  4  # GPIO  #4   PIN  7
IN1 = 17  # GPIO #17   PIN 11
IN2 = 18  # GPIO #18   PIN 12

# STBY = 21 # GPIO #21   PIN 13

# GPIO.setup(PWM, GPIO.OUT)  
GPIO.setup(IN1, GPIO.OUT)  
GPIO.setup(IN2, GPIO.OUT)  

# GPIO.setup(STBY, GPIO.OUT)  


GPIO.output(IN1, GPIO.HIGH) 
GPIO.output(IN2, GPIO.LOW)  
sleep(0.5)         

GPIO.output(IN1, GPIO.LOW) 
GPIO.output(IN2, GPIO.LOW)  
sleep(0.5)         

GPIO.output(IN1, GPIO.LOW) 
GPIO.output(IN2, GPIO.HIGH)  
sleep(0.5)         

GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.LOW)
sleep(0.5)
