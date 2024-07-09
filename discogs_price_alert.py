import requests
import smtplib
from email.mime.text import MIMEText
import random
import datetime

# Link to create app password :
# https://myaccount.google.com/u/1/apppasswords?rapt=AEjHL4OGwnPxnZqMGA3_wZqHE4J9rn9siiesyEqH0vL_SAQ7XqMug7jkTv63tooMtThDhk8YdX70MN5vuzoJhA5Z9CBqIXqtC8Fx4576a1IjUbDeAkLS7jA

# Personal access token
token = 'KUmZmunHJTvgHCiWhEylYrHvbYwEFYKzQJIGeyXi'

# Function to log messages with timestamp
def log_message(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"\n[{current_time}] {message}"
    print(formatted_message)

def send_email(subject, body, to_email):
    from_email = 'goprodronebali1@gmail.com'
    app_password = 'hasb squx zsjc fkaq'
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, app_password)
    server.sendmail(from_email, to_email, msg.as_string())
    server.quit()

def get_discogs_marketplace_stats(release_id, token, currency='USD'):
    url = f"https://api.discogs.com/marketplace/stats/{release_id}"
    headers = {
        'Authorization': f'Discogs token={token}',
        'User-Agent': 'YourAppName/1.0'
    }
    params = {
        'curr_abbr': currency
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    # Print to ensure the request was made
    print(f"Fetching marketplace stats for release ID: {release_id}")
    print("Response status code:", response.status_code)
    
    if response.status_code != 200:
        print(f"Error: Unable to fetch marketplace stats (status code {response.status_code}) for release ID: {release_id}")
        return None
    
    stats = response.json()
    
    # Convert lowest_price from dict to float if it's a dict
    if stats.get('lowest_price') and isinstance(stats['lowest_price'], dict):
        stats['lowest_price'] = stats['lowest_price'].get('value')

    # Print the stats for debugging
    print(f"Marketplace stats for release ID {release_id}: {stats}")
    
    return stats

def get_discogs_price(release_id, token):
    url = f"https://api.discogs.com/marketplace/search?release_id={release_id}&currency=USD"
    headers = {
        'Authorization': f'Discogs token={token}',
        'User-Agent': 'YourAppName/1.0'
    }
    
    response = requests.get(url, headers=headers)
    
    # Print to ensure the request was made
    print(f"Fetching release ID: {release_id}")
    print("Response status code:", response.status_code)
    
    if response.status_code != 200:
        print(f"Error: Unable to fetch marketplace listings (status code {response.status_code}) for release ID: {release_id}")
        return None
    
    listings = response.json().get('results', [])
    prices = [listing['price']['value'] for listing in listings if 'price' in listing]
    
    if prices:
        min_price = min(prices)
        # Print to ensure the price was extracted correctly
        print(f"Extracted price for release ID {release_id}: ${min_price}")
        return min_price
    
    print(f"Error: No listings found for release ID: {release_id}")
    return None

# List of records to track
records = [
    {
        'release_name': 'DJ Hal - Aphrodisiac',
        'release_id': 340369,
        'threshold': 30.0,
        'currency': 'USD'
    },
    {
        'release_name': 'ODE - A9E4FF',
        'release_id': 10751701,
        'threshold': 100.0,
        'currency': 'USD'
    },
    {
        'release_name': 'Petre Inspirescu – Grădina Onirică (Part II)',
        'release_id': 6649851,
        'threshold': 50.0,
        'currency': 'USD'
    },
    {
        'release_name': 'Petre Inspirescu – Grădina Onirică',
        'release_id': 4111078,
        'threshold': 30.0,
        'currency': 'USD'
    },
    {
        'release_name': 'Aline Brooklyn – Aline Brooklyn 001',
        'release_id': 9226618,
        'threshold': 35.0,
        'currency': 'USD'
    },
    # Add more records here
]

# Print to ensure the script is starting
log_message("\nScript started. Checking prices for records...")

# Loop through each record and check the price
for record in records:
    release_id = record['release_id']
    release_name = record['release_name']
    threshold_price = record['threshold']
    currency = record.get('currency', 'USD')
    
    # Print a random message before fetching the price
    print(f"\nChecking {release_id}")
    
    stats = get_discogs_marketplace_stats(release_id, token, currency)
    
    if stats:
        num_for_sale = stats['num_for_sale']
        lowest_price = stats['lowest_price']
        
        if lowest_price is not None and lowest_price < threshold_price:
            subject = f'Price Alert: **{release_name}** dropped below ${threshold_price:.2f}'
            body = f'The current lowest price is ${lowest_price:.2f}\nNumber of items for sale: {num_for_sale}\n\nCheck the record on Discogs: https://www.discogs.com/release/{release_id}'
            
            # Print to ensure the email alert is about to be sent
            print(f"Sending email alert for release ID {release_id} with current price ${lowest_price:.2f}")
            
            send_email(subject, body, 'tanguy.verdoodt@gmail.com')
            
            print(f'Email alert sent for release ID: {release_id}')
        else:
            print(f'No price drop or unable to fetch price for release ID: {release_id}')
    else:
        print(f'No data returned for release ID: {release_id}')
