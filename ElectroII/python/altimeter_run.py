import altimeter as Altimeter
from time import time
from time import sleep
import datetime

print("time interval >>> ")
interval = int(input())
print("runtime >>> ")
runtime = int(input())
alt = Altimeter.Altimeter()
alt.initialize()

starttime = time()

while True:
	currenttime = time()
	elapsedtime = currenttime - starttime
	if elapsedtime > runtime:
		print("Finished after " + str(elapsedtime) + " seconds.")
		break
	info = alt.get_data()
	timestamp = datetime.datetime.now()
	print(timestamp)
	print(info)
	sleep(interval)
