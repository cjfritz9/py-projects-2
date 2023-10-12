# ---------------------------- MAIL SENDER ------------------------------- #
from email.mime.text import MIMEText 
import datetime as dt
import smtplib
import random
import pandas
# ---------------------------- CONSTANTS ------------------------------- #
MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = 587
BDAY_DATA = 'birthdays.csv'
TEMPLATE_CHOICE = random.randint(1, 3)
NOW = dt.datetime.now()

# ---------------------------- UTILITIES ------------------------------- #
def format_age(age: int):
  last_digit = age % 10
  if last_digit == 0 or last_digit > 3:
    return f"{age}th"
  elif last_digit == 3:
    return f"{age}rd"
  elif last_digit == 2:
    return f"{age}nd"
  else:
    return f"{age}st"

# ---------------------------- MAIL SENDER ------------------------------- #
def send_email(message_data):
  try:
    email = open('email.txt').read().strip()

  except OSError:
    email = input('Enter Email:\n')

  try:
    password = open('password.txt').read().strip()

  except OSError:
    password = input('Enter Application Password:\n')

  connection = smtplib.SMTP(host=MAIL_HOST, port=MAIL_PORT)
  connection.starttls()
  connection.login(user=email, password=password)
  connection.sendmail(from_addr=email, to_addrs=message_data['To'], msg=message_data.as_string())
  connection.close()

# ---------------------------- MESSAGE COMPOSER ------------------------------- #
def compose_message(person_data):
  global quote, message
  quote = ''
  message = ''

  try:
    with open(f"templates/letter_{TEMPLATE_CHOICE}.txt") as template_file:
      template_text = template_file.read()

  except FileNotFoundError:
    print(f"File not found: templates/letter_{TEMPLATE_CHOICE}.txt")
  else:
    message = template_text.replace('[NAME]', person_data[0])

  try:
    with open('quotes.txt') as quotes_file:
      quotes_list = []
      for line in quotes_file:
        quotes_list.append(line)
      

  except FileNotFoundError:
    print('No quote data file to read from')

  else:
    quote = random.choice(quotes_list).strip()
    message = message.replace('[QUOTE]', quote)
    message_data = MIMEText(message)
    formatted_age = format_age(NOW.year - person_data[2])
    message_data['Subject'] = f'Happy {formatted_age} Birthday!'
    message_data['To'] = person_data[1]
    send_email(message_data)

# ---------------------------- BIRTHDAY DATA ------------------------------- #
def check_birthdays(now: dt.datetime):
  birthday_matches = []
  try:
    bday_df = pandas.read_csv(BDAY_DATA)

  except FileNotFoundError:
    print(f'No Birthday Data ({BDAY_DATA})')

  else:
    bday_dict = bday_df.to_dict('split')
    data = bday_dict['data']

    for person in data:
      if now.day == person[4] and now.month == person[3]:
        birthday_matches.append(person)

  if len(birthday_matches) == 0:
    print('No birthdays today!')
  else:
    for match in birthday_matches:
      compose_message(match)

# ---------------------------- PROGRAM CYCLE ------------------------------- #
check_birthdays(NOW)
