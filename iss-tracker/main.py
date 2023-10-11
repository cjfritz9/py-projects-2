import requests

response = requests.get(url='http://api.open-notify.org/iss-now.json')
response.raise_for_status()

result = response.json()
longitude = result['iss_position']['longitude']
latitude = result['iss_position']['latitude']
print(longitude, latitude)