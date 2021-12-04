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
run_indefinite = config["run_indefinite"]
file_refresh_time = datetime.timedelta(seconds=config["csv_save_interval"])

alt = Altimeter.Altimeter()
alt.initialize()

labels = ["Timestamp", "Temperature", "Pressure", "Altitude"]
dataframe = pd.DataFrame(columns = labels)
starttime = time()
tic = datetime.datetime.now()
dirname = tic
os.makedirs(f"logs/{dirname}", exist_ok = True)

while True:
	currenttime = time()
	elapsedtime = currenttime - starttime
	if (elapsedtime > runtime) and not run_indefinite:
		print("Finished after " + str(elapsedtime) + " seconds.")
		break
	info = alt.get_data()
	timestamp = datetime.datetime.now()
	data = [timestamp, info["temp"], info["pressure"], info["altitude"]]
	dataframe.loc[len(dataframe)] = data
	print(timestamp)
	print(info)

	if datetime.datetime.now() - tic > file_refresh_time:
		print("Saving to file...")
		dataframe.to_csv(f"logs/{dirname}/rtr-data-{datetime.datetime.now()}.csv")
		print("Done saving.")
		tic = datetime.datetime.now()
	sleep(interval)

print(dataframe)
dataframe.to_csv(f"logs/{dirname}/rtr-data-{datetime.datetime.now()}.csv")
