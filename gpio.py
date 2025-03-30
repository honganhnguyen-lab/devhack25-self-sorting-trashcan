import RPi.GPIO as GPIO
from time import sleep

DIR = 10
STEP = 8
CW = 1
CCW = 0

GPIO.setmode(GPIO.BOARD)

GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

GPIO.output(DIR, CW)
try:
	while True:

		"""Change Direction: Changing direction requires time to switch. The
		time is dictated by the stepper motor and controller. """
		sleep(0.5)
		GPIO.output(DIR,CW)

		for x in range(200):

			GPIO.output(STEP,GPIO.HIGH)
			sleep(.005)
			GPIO.output(STEP,GPIO.LOW)
			sleep(.005)

		"""Change Direction: Changing direction requires time to switch. The
		time is dictated by the stepper motor and controller. """
		sleep(0.5)
		GPIO.output(DIR,CCW)
		for x in range(200):
			GPIO.output(STEP,GPIO.HIGH)
			sleep(.005)
			GPIO.output(STEP,GPIO.LOW)
			sleep(.005)

except KeyboardInterrupt:
	print("cleanup")
	GPIO.cleanup()
