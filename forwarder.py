#!/usr/bin/python3 -u

import sys
import json
import serial
import time
import subprocess

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
    data.append("sensor_id", "petit-verdot")

  if(splitted_line[1] == "2MFWMJNVGMWMNEFO"):
    data.append("sensor_id", "cabernet-sauvignon")

  if(splitted_line[1] == "IORG1AH0DC1B56LL"):
    data.append("sensor_id", "malbec-este")

  if(splitted_line[1] == "XBA5TPH2RV65Q52K"):
    data.append("sensor_id", "malbec-oeste")

  data.append("sensor2", splitted_line[2])
  data.append("sensor1", splitted_line[3])
  data.append("sensor05", splitted_line[4])
  data.append("sensor005", splitted_line[5])
  data.append("timestamp", int(time.time()))

  print("Line was read and preprocessed: " + json.dumps(data))

  #battery     = splitted_line[6]

