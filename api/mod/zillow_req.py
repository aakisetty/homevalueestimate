import requests
import pandas as pd
from datetime import datetime
import time
import requests
import re 

def clean_price(price_str):
    # Remove any non-digit characters except for decimal points
    cleaned = re.sub(r'[^\d.]', '', price_str)
    
    # Convert to float if possible, otherwise return None
    try:
        return float(cleaned)
    except ValueError:
        return None

def get_zillow_data(location, max_retries=3, delay=5):
    url = "https://zillow56.p.rapidapi.com/search"
    querystring = {
        "location": location,
        "output": "json",
        "status": "forSale",
        "sortSelection": "priorityscore",
        "listing_type": "by_agent",
        "doz": "any"
    }
    headers = {
        "x-rapidapi-host": "zillow56.p.rapidapi.com",
        "x-rapidapi-key": "d9725d8ae0msh9cc08f8d952a3c4p1ef844jsn4f55ced906d0"
    }

    # for attempt in range(max_retries):
    response = requests.get(url, headers=headers, params=querystring)
    print(response)
        # if response.status_code == 200:
        #     data = response.json()
        #     print(data['results']['lastSoldPrice'])
        #     price = data['results']['lastSoldPrice']
        #     price = clean_price(price)
        #     return pd.DataFrame({
        #         'Date': datetime.now(),
        #         'Zillow_Value': price
        #     })
        # elif response.status_code == 429:
        #     print(f"Rate limit exceeded. Retrying in {delay} seconds...")
        #     time.sleep(delay)
        # else:
        #     print(f"Zillow API request failed with status code {response.status_code}")

    # print("Max retries reached. Unable to fetch Zillow data.")
    # return pd.DataFrame(columns=['Date', 'Zillow_Value'])

get_zillow_data("4529 Winona")