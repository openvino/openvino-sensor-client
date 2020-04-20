#!/usr/bin/python3 -u

import sys
import os
import json
import serial

import time
from datetime import datetime

import subprocess
import requests
import mysql.connector

print("\nSetting up enviroment for vinduinos and weather station")

db = mysql.connector.connect(
  host=os.getenv("DATABASE_HOST", default = 'localhost'),
  user=os.getenv("DATABASE_USERNAME", default = 'test'),
  passwd=os.getenv("DATABASE_PASSWORD", default = 'test123'),
  database=os.getenv("DATABASE_NAME", default = 'test_db'0),
  auth_plugin='mysql_native_password'
)

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

  data.update({"humidity2": float(splitted_line[2])})
  data.update({"humidity1": float(splitted_line[3])})
  data.update({"humidity05": float(splitted_line[4])})
  data.update({"humidity005": float(splitted_line[5])})
  data.update({"timestamp": datetime.fromtimestamp(time.time()).strftime("%Y-%m-%dT%H:%M:%S.00Z")})
  data.update({"hash": str(time.time())}) #temporal

  url = os.getenv("API_ENDPOINT", default = 'https://localhost:4040') + "/sensor_data"
  res = requests.post(url, data = data)

  if res.status_code != 200:

    cursor = db.cursor()
    sql = "INSERT INTO sensor_data (wind_velocity, wind_gust, wind_direction, pressure, rain, temperature, humidity, sensor_id, humidity2, humidity1, humidity05, humidity005, timestamp, hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = tuple([value for _, value in data.items()])
    cursor.execute(sql, val)
    db.commit()

  print("Line was read and preprocessed: " + json.dumps(data))

  #battery     = splitted_line[6]

