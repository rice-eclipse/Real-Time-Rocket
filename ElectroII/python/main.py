import altimeter as Altimeter
from time import time
from time import sleep
import datetime
import pandas as pd
import json
import os

"""
print("time interval >>> ")
interval = int(input())
print("runtime >>> ")
runtime = int(input())
"""

json_path = os.path.join(os.getcwd(), "config.json")
with open(json_path) as f:
  config = json.load(f)
interval = config["interval"]
runtime = config["runtime"]

alt = Altimeter.Altimeter()
alt.initialize()

labels = ["Timestamp", "Temperature", "Pressure", "Altitude"]
dataframe = pd.DataFrame(columns = labels)
starttime = time()

while True:
	currenttime = time()
	elapsedtime = currenttime - starttime
	if elapsedtime > runtime:
		print("Finished after " + str(elapsedtime) + " seconds.")
		break
	info = alt.get_data()
	timestamp = datetime.datetime.now()
	data = [timestamp, info["temp"], info["pressure"], info["altitude"]]
	dataframe.loc[len(dataframe)] = data
	print(timestamp)
	print(info)
	sleep(interval)

print(dataframe)
dataframe.to_csv(f"rtr-data-{datetime.date.today()}.csv")