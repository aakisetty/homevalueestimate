import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import re

def clean_price(price_str):
    cleaned = re.sub(r'[^\d.]', '', str(price_str))
    try:
        return float(cleaned)
    except ValueError:
        return None

def get_house_price_AttomData(api_key, address1, address2):
    # API endpoint
    url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
    
    # Headers
    headers = {
        "Accept": "application/json",
        "apikey": api_key
    }
    
    # Query parameters
    params = {
        "address1": address1,
        "address2": address2
    }
    
    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the sale amount
        sale_amount = data["property"][0]["sale"]["saleAmountData"]["saleAmt"] 
        sale_amount = clean_price(sale_amount)
        return sale_amount
    
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing API response: {e}")
        return None



# Example usage
api_key = "2b1e86b638620bf2404521e6e9e1b19e"

# address1 = "4529 Winona Court"
# address2 = "Denver, CO"

v2address1 = "Houston, TX"
v2address2 = "3120 Southwest Fwy Ste 101"

price = get_house_price_AttomData(api_key, v2address1, v2address2)
if price is not None:
    print(price)
    print(f"The house price is: ${price:,}")
else:
    print("Unable to retrieve the house price.")