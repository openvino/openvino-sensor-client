#!/usr/bin/python3 -u

import sys
import os
import json
import serial
import time
import subprocess
import requests

print("\nSetting up enviroment for vinduinos and weather station")

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=900)

while True:

  line = ser.readline();

  if len(line)==0:
      print("Error: Time out")
      sys.exit()

  script = ["python2", "weather-station.py"]    
  process = subprocess.check_output(" ".join(script),
                                    shell=True,  
                                    env={"PYTHONPATH": "weather-station/"})
  weather_station_info = process.decode("utf-8")

  data = json.loads(weather_station_info)

  line=line.decode("utf-8")
  splitted_line = line.split(",")

  if(splitted_line[1] == "V55XYQX29JTFWNVR"):
    data.update({"sensor_id": "petit-verdot"})

  if(splitted_line[1] == "2MFWMJNVGMWMNEFO"):
    data.update({"sensor_id": "cabernet-sauvignon"})

  if(splitted_line[1] == "IORG1AH0DC1B56LL"):
    data.update({"sensor_id": "malbec-este"})

  if(splitted_line[1] == "XBA5TPH2RV65Q52K"):
    data.update({"sensor_id": "malbec-oeste"})

  data.update({"sensor2": float(splitted_line[2])})
  data.update({"sensor1": float(splitted_line[3])})
  data.update({"sensor05": float(splitted_line[4])})
  data.update({"sensor005": float(splitted_line[5])})
  data.update({"timestamp": int(time.time())})

  url = os.getenv("API_ENDPOINT", default = 'https://localhost:4040') + "/sensor_data"
  x = requests.post(url, data = data)

  print("Line was read and preprocessed: " + json.dumps(data))

  #battery     = splitted_line[6]

