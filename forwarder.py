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


from enchaintesdk import EnchainteClient, Message, EnchainteSDKException

print("\nSetting up enviroment for vinduinos and weather station")

sleep_timer = 2
sleep_max = 128

apiKey = os.getenv("ENCHAINTE_APIKEY", default='hola')

try:
    db = mysql.connector.connect(
        host=os.getenv("DATABASE_HOST", default='localhost'),
        user=os.getenv("DATABASE_USERNAME", default='test'),
        passwd=os.getenv("DATABASE_PASSWORD", default='test123'),
        database=os.getenv("DATABASE_NAME", default='test_db'),
        auth_plugin='mysql_native_password'
    )
except mysql.connector.Error as err:
    disconnected = True

redundant_db = mysql.connector.connect(
    host='database',
    user=os.getenv("DATABASE_USERNAME", default='test'),
    passwd=os.getenv("DATABASE_PASSWORD", default='test123'),
    database=os.getenv("DATABASE_NAME", default='test_db'),
)

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=900)
disconnected = False

enchainte = EnchainteClient(apiKey)

print("\nSet up ready")

while True:
    try:
        line = ser.readline()

        if len(line) == 0:
            print("Error: Time out")
            sys.exit()

        script = ["python2", "weather-station.py"]
        process = subprocess.check_output(" ".join(script),
                                          shell=True,
                                          env={"PYTHONPATH": "weather-station/"})
        weather_station_info = process.decode("utf-8")

        data = json.loads(weather_station_info)

        line = line.decode("utf-8")
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
        data.update({"irradiance_uv": float(splitted_line[6])})
        data.update({"irradiance_ir": float(splitted_line[7])})
        data.update({"irradiance_vi": float(splitted_line[8])})
        data.update({"timestamp": datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')})

        print(data)

        print('Sending to Enchainte')
        try:
            message = Message.fromDict(data)
            enchainte.sendMessages([message])
            data.update({"hash": message.getHash()})
        except EnchainteSDKException as e:
            print("Error sending value to Enchainte api.")
            print(e)
        print('sending to DB')

        try:
            if (disconnected):
                db = mysql.connector.connect(
                    host=os.getenv("DATABASE_HOST", default='localhost'),
                    user=os.getenv("DATABASE_USERNAME", default='test'),
                    passwd=os.getenv("DATABASE_PASSWORD", default='test123'),
                    database=os.getenv("DATABASE_NAME", default='test_db'),
                    auth_plugin='mysql_native_password'
                )
                disconnected = False

            cursor = db.cursor()
            sql = "INSERT INTO sensor_records (wind_velocity, wind_gust, wind_direction, pressure, rain, temperature, humidity, irradiance_uv, irradiance_ir, irradiance_vi, sensor_id, humidity2, humidity1, humidity05, humidity005, timestamp, hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = tuple([value for _, value in data.items()])
            cursor.execute(sql, val)
            db.commit()
            print("Inserted into echo database: " + json.dumps(data) +
                  " [battery = " + splitted_line[9] + "]")

        except BaseException as e:
            try:
                redundant_db.ping(reconnect=True, attempts=3, delay=5)
            except mysql.connector.Error as err:
                redundant_db = mysql.connector.connect(
                    host='database',
                    user=os.getenv("DATABASE_USERNAME", default='test'),
                    passwd=os.getenv("DATABASE_PASSWORD", default='test123'),
                    database=os.getenv("DATABASE_NAME", default='test_db'),
                )
            disconnected = True
            print("Inserted into redundant database: " +
                  json.dumps(data) + " [battery = " + splitted_line[9] + "]")
            redundant_cursor = redundant_db.cursor()
            redundant_sql = "INSERT INTO sensor_records (wind_velocity, wind_gust, wind_direction, pressure, rain, temperature, humidity, irradiance_uv, irradiance_ir, irradiance_vi, sensor_id, humidity2, humidity1, humidity05, humidity005, timestamp, hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            redundant_val = tuple([value for _, value in data.items()])
            redundant_cursor.execute(redundant_sql, redundant_val)
            redundant_db.commit()

        sleep_timer = 2

    except BaseException as e:
        print("Error while running the forwarder:")
        print(e)
        sleep_timer *= 2
        if sleep_timer > sleep_max:
            time.sleep(sleep_max)
        else:
            time.sleep(sleep_timer)
