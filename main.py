import requests
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import os

load_dotenv()

# Twilio credentials (if using for email-based notifications)
EMAIL_ADDRESS = os.environ.get('email')
EMAIL_PASSWORD = os.environ.get('password')

# SMS Gateway address (replace with your carrier's SMS gateway)
TO_PHONE_NUMBER_1 = os.environ.get('phone')  # Account 1's phone number and carrier
TO_PHONE_NUMBER_2 = os.environ.get('phone')  # Account 2's phone number and carrier

API_TOKEN = os.environ.get('token')
PLAYER_TAGs = os.environ.get('tag')

# Function to send SMS via email
def send_sms_via_email(subject, message, to_phone_number):
    # Create message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_phone_number
    msg['Subject'] = subject

    # Add the message body
    msg.attach(MIMEText(message, 'plain'))

    # Send email via SMTP
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_phone_number, msg.as_string())
        server.quit()
        print(f"SMS sent successfully to {to_phone_number}!")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

# Clash of Clans data fetching function
def get_clash_data(account_tag):
    url = f'https://api.clashofclans.com/v1/players/%23{account_tag.strip("#")}'
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for account {account_tag}: {response.status_code}")
        return None

# Function to monitor upgrades and send notifications when completed
def monitor_upgrades(player_tags):
    while True:
        for idx, tag in enumerate(player_tags):
            data = get_clash_data(tag)
            if data:
                upgrades = data.get('upgrading', [])
                for upgrade in upgrades:
                    # Assuming 'timeLeft' field indicates how much time is left for the upgrade
                    if upgrade.get('timeLeft', 0) == 0:  # Upgrade is completed
                        message = f"Upgrade completed for {upgrade['name']} in account {tag}!"
                        subject = f"Clash of Clans Upgrade Notification for {tag}"

                        # Send SMS to appropriate phone number
                        to_phone_number = TO_PHONE_NUMBER_1 if idx == 0 else TO_PHONE_NUMBER_2
                        send_sms_via_email(subject, message, to_phone_number)

        # Check every hour (3600 seconds) for upgrade status
        time.sleep(5)


# Schedule a job to run every minute for testing
schedule.every(1).minutes.do(lambda: send_sms_via_email("Test Subject", "This is a test message!", TO_PHONE_NUMBER_1))
while True:
    print("Checking for scheduled jobs...")
    schedule.run_pending()
    time.sleep(1)

# Start monitoring for upgrades
#monitor_upgrades(player_tags=PLAYER_TAGs.split(','))
