import requests
import datetime as dt

TZ_OFFSET = -6
SAT_RANGE = 5
ISS_API = 'http://api.open-notify.org/iss-now.json'
SUN_API = 'https://api.sunrise-sunset.org/json'
PARAMS = {
  'lat': 39.710999,
  'lng': -105.088867,
  'formatted': 0
}

response = requests.get(url='http://api.open-notify.org/iss-now.json')
response.raise_for_status()

result = response.json()
iss_lng = float(result['iss_position']['longitude'])
iss_lat = float(result['iss_position']['latitude'])

response = requests.get(url=f'{SUN_API}', params=PARAMS)
response.raise_for_status()

# print(response._content)
result = response.json()

sunrise_hour = (int(result['results']['sunrise'].split("T")[1].split(":")[0]) + TZ_OFFSET) % 24
sunset_hour = (int(result['results']['sunset'].split("T")[1].split(":")[0]) + TZ_OFFSET) % 24
local_hour = dt.datetime.now().hour


if local_hour >= sunset_hour or local_hour <= sunrise_hour:
  print('It is night!')
  if iss_lng - SAT_RANGE <= PARAMS['lng'] <= iss_lng + SAT_RANGE and iss_lat <= iss_lat - SAT_RANGE <= PARAMS['lat'] <= iss_lat + SAT_RANGE:
    print('correct lat/long')
  else:
    print('Not within range... restarting')
    print(f'Local lat/lng: {PARAMS["lat"]}, {PARAMS["lng"]}')
    print(f'ISS lat/lng: {iss_lat}, {iss_lng}')