import json

process = b'{"wind_velocity":0.0,"wind_gust":0.0,"wind_direction":0.0,"pressure":90.897,"rain":0.0}'
weather_station_info = process.decode("utf-8")
print(weather_station_info)
data = json.loads(weather_station_info)

data.update({"sensor2": 3.7})
print(json.dumps(data))