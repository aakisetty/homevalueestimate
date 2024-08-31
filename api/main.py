from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import json
from datetime import datetime
import requests
import re
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(
    title="Home Value Estimator",
    description="An API for estimating home values based on user input and multiple data sources.",
    version="1.0.0",
)

class EstimateRequest(BaseModel):
    user_estimate: float
    address: str
   

class EstimateResponse(BaseModel):
    address: str
    user_estimate: float
    estimate: float
    percentage_match: str

import time
from typing import Optional
import requests
import json
import os
import logging

def get_house_price_datafiniti(address: str, max_retries: int = 3, retry_delay: int = 5) -> Optional[float]:
    api_token = os.getenv("DATAFINITI_API_TOKEN")

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    url = 'https://api.datafiniti.co/v4/properties/search'
    data = {
        'query': f'address:{address}',
        'format': 'JSON',
        'num_records': 1,
        'download': False
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'records' in data and len(data['records'][0].get('prices', [])) >= 2:
                prices = data['records'][0].get('prices', [])
                logger.info(f"Retrieved {len(prices)} prices for address: {address}")
                
                if len(prices) > 2:
                    total_price = 0
                    count = 0
                    for price in prices:
                        if 'amountMax' in price:
                            total_price += price['amountMax']
                            count += 1
                        elif 'amountMin' in price:
                            total_price += price['amountMin']
                            count += 1
                    
                    if count > 0:
                        average_price = total_price / count
                        logger.info(f"Calculated average price: {average_price}")
                        return average_price
                else:
                    logger.warning(f"Not enough prices found. Retrying... (Attempt {attempt + 1}/{max_retries})")
            else:
                logger.warning(f"No records found. Retrying... (Attempt {attempt + 1}/{max_retries})")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making API request: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing API response: {e}")
        except KeyError as e:
            logger.error(f"Unexpected response structure: {e}")
        
        if attempt < max_retries - 1:
            logger.info(f"Retrying in {retry_delay} seconds... (Attempt {attempt + 2}/{max_retries})")
            time.sleep(retry_delay)

    logger.error(f"Failed to retrieve valid data after {max_retries} attempts")
    return None

@app.post("/estimate", response_model=EstimateResponse, tags=["Estimates"])
async def estimate_home_value(request: EstimateRequest):
    estimate = get_house_price_datafiniti(request.address)

    if estimate is None:
        logger.error(f"Unable to estimate home value for address: {request.address}")
        raise HTTPException(status_code=404, detail="Unable to estimate home value due to lack of data.")

    # Calculate the percentage match
    if request.user_estimate > estimate:
        percentage_match = (estimate / request.user_estimate) * 100
    else:
        percentage_match = (request.user_estimate / estimate) * 100

    pm = f"{percentage_match:.2f}%"

    logger.info(f"Estimate calculated for {request.address}: User estimate: {request.user_estimate}, API estimate: {estimate}, Match: {pm}")

    return EstimateResponse(
        address=request.address,
        user_estimate=request.user_estimate,
        estimate=estimate,
        percentage_match=pm
    )

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Welcome to the Home Value Estimator API 2024"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)