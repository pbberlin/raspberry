# Connections:  
# GPIO5 (pin 29) is button input  
# GPIO22 (pin 15) is LED  
  
  
import time  
import curses  
import sys  
import RPi.GPIO as GPIO  

GPIO.setmode(GPIO.BCM)  
GPIO.setup(5, GPIO.IN)  
GPIO.setup(22, GPIO.OUT)  
tc=curses.initscr()  
tc.nodelay(1)  
old_button_status=GPIO.input(5)  
count=0  
  
  
tc.addstr(1, 0, "Press SPACE to quit:\n")  
tc.addstr(2, 0, str(count))  
  
  
while 1:  
  button_status=GPIO.input(5)  
  kbval=tc.getch()  
  GPIO.output(22, button_status)  
  if old_button_status != button_status:  
    time.sleep(0.02) # debounce period  
    button_status=GPIO.input(5) # re-read the input  
    if old_button_status != button_status:  
  
  
      if button_status == True:  
        tc.addstr(2, 10, "-") # pin is high, button unpressed  
        count=count+1  
      else:  
        tc.addstr(2, 10, "_") # pin is low, button pressed  
      old_button_status=button_status  
      tc.addstr(2, 0, str(count))  
  
  
  if kbval==0x20:  
    break  
  
  
time.sleep(1)  
GPIO.cleanup()  
curses.endwin()  
print("Goodbye" )
  
        