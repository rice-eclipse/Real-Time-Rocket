import time
import board
import digitalio

print("hello blinky!")

led_red = digitalio.DigitalInOut(board.D8)
led_green = digitalio.DigitalInOut(board.D7)
led_red.direction = digitalio.Direction.OUTPUT
led_green.direction = digitalio.Direction.OUTPUT

while True:
    led_red.value = True
    led_green.value = False
    time.sleep(0.5)
    led_red.value = False
    led_green.value = True
    time.sleep(0.5)
