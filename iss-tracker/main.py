from email.mime.text import MIMEText 
from time import sleep
from math import floor
import requests
import smtplib
import datetime as dt

TZ_OFFSET = -6
ISS_OK_RANGE = 5
ISS_API = 'http://api.open-notify.org/iss-now.json'
SUN_API = 'https://api.sunrise-sunset.org/json'
MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = 587
PARAMS = {
  'lat': 39.710999,
  'lng': -105.088867,
  'formatted': 0
}

# ---------------------------- UTILITIES ------------------------------- #
def format_times(sunrise_hour: int, sunrise_mins: int, sunset_hour: int, sunset_mins: int):
  global f_sunrise_hour, f_sunrise_mins, f_sunset_hour, f_sunset_mins
  f_sunrise_hour = f"{sunrise_hour}"
  f_sunrise_mins = f"{sunrise_mins}"
  f_sunset_hour = f"{sunset_hour}"
  f_sunset_mins = f"{sunset_mins}"

  if sunrise_hour < 10:
    f_sunrise_hour = f"0{sunrise_hour}"
  
  if sunrise_mins < 10:
    f_sunrise_mins = f"0{sunrise_mins}"
  
  if sunset_hour < 10:
    f_sunset_hour = f"0{sunset_hour}"

  if sunset_mins < 10:
    f_sunset_mins = f"0{sunset_mins}"

  return {
    'sunrise': f"{f_sunrise_hour}:{f_sunrise_mins}",
    'sunset': f"{f_sunset_hour}:{f_sunset_mins}"
  }



# ---------------------------- API REQUESTS ------------------------------- #
def get_iss_in_range():
  response = requests.get(url='http://api.open-notify.org/iss-now.json')
  response.raise_for_status()

  result = response.json()
  iss_lng = float(result['iss_position']['longitude'])
  iss_lat = float(result['iss_position']['latitude'])

  return iss_lng - ISS_OK_RANGE <= PARAMS['lng'] <= iss_lng + ISS_OK_RANGE and iss_lat <= iss_lat - ISS_OK_RANGE <= PARAMS['lat'] <= iss_lat + ISS_OK_RANGE

def get_night_cycle():
  response = requests.get(url=f'{SUN_API}', params=PARAMS)
  response.raise_for_status()


  result = response.json()

  sunrise_hour = (int(result['results']['sunrise'].split("T")[1].split(":")[0]) + TZ_OFFSET) % 24
  sunrise_mins = int(result['results']['sunrise'].split("T")[1].split(":")[1])
  sunset_hour = (int(result['results']['sunset'].split("T")[1].split(":")[0]) + TZ_OFFSET) % 24
  sunset_mins = int(result['results']['sunset'].split("T")[1].split(":")[1])
  local_hour = dt.datetime.now().hour
  local_mins = dt.datetime.now().minute

  is_night = local_hour >= sunset_hour or local_hour <= sunrise_hour
  sleep_timer = sunset_hour * 60 - local_hour * 60 + sunset_mins - local_mins
  formatted_times = format_times(sunrise_hour, sunrise_mins, sunset_hour, sunset_mins)

  return {
    'is_night': is_night,
    'sleep_timer': sleep_timer,
    'sunrise': formatted_times['sunrise'],
    'sunset': formatted_times['sunset']
  }


# ---------------------------- MAIL SENDER ------------------------------- #
def send_mail():
  try:
    email = open('email.txt').read().strip()

  except OSError:
    email = input('Enter Email:\n')

  try:
    password = open('password.txt').read().strip()

  except OSError:
    password = input('Enter Application Password:\n')
  
  message = MIMEText(f'Look Up! The ISS is somewhere overhead!')
  message['Subject'] = 'Automated ISS Notification'

  connection = smtplib.SMTP(host=MAIL_HOST, port=MAIL_PORT)
  connection.starttls()
  connection.login(user=email, password=password)
  connection.sendmail(from_addr=email, to_addrs=email, msg=message)
  connection.close()

# ---------------------------- MAIL SENDER ------------------------------- #
while True:
  night_data = get_night_cycle()

  if night_data['is_night']:
    if get_iss_in_range():
      send_mail()
    else:
      print('Not within range, checking again in 3 minutes.')
      sleep(90)
  else:
    timer = night_data['sleep_timer']
    print(f"Daytime, sleeping until {night_data['sunset']}")
    print(f"({floor(timer / 60)} hours and {timer % 60} minutes from now)")
    sleep(timer * 60)

