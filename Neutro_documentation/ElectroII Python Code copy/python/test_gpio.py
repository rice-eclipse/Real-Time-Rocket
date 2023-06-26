import board
import digitalio
import time
import RPi.GPIO

print("Hello!")

led = digitalio.DigitalInOut(board.D17)
led.direction = digitalio.Direction.OUTPUT

print("Press CTRL-C to exit.")
try:
    while True:
        led.value = True
        time.sleep(0.5)
        led.value = False
        time.sleep(0.5)
except KeyboardInterrupt:
    RPi.GPIO.cleanup()
    print("\nCleaned up GPIO resources.")
