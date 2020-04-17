import json
import requests
import os
import time
from datetime import datetime

db = mysql.connector.connect(
  host=os.getenv("DATABASE_HOST", default = 'database') + ":" + os.getenv("DATABASE_PORT", default = '3306')  ,
  user=os.getenv("DATABASE_USERNAME", default = 'test'),
  passwd=os.getenv("DATABASE_PASSWORD", default = 'test123),
  database=os.getenv("DATABASE_NAME", default = 'test_db')
)

process = b'{"wind_velocity": 0.0, "wind_gust": 0.0, "wind_direction": 0.0, "pressure": 90.932, "rain": 0.0, "temperature": null, "humidity": null, "sensor_id": "malbec-oeste", "sensor2": 13.0, "sensor1": 16.0, "sensor05": 9.0, "sensor005": 11.0, "hash": "15871252792.51475"}'
weather_station_info = process.decode("utf-8")
data = json.loads(weather_station_info)
data.update({"timestamp": datetime.fromtimestamp(time.time()).strftime("%Y-%m-%dT%H:%M:%S.00Z")})
print(data)

url = os.getenv("API_ENDPOINT", 
                default = 'http://10.112.48.25:4040') + "/sensor_data"
res = requests.post(url, json = data,
                headers= {'Content-type': 'application/json'})

if res.status_code == 200:

    cursor = db.cursor()
    sql = "INSERT INTO sensor_data (wind_velocity, wind_gust, wind_direction, pressure, rain, temperature, humidity, sensor_id, humidity2, humidity1, humidity05, humidity005, timestamp, hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = tuple([value for _, value in data.items()])
    cursor.execute(sql, val)
    db.commit()

print(x.content)