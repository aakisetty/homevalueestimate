from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime
import requests
import re

app = FastAPI(
    title="Home Value Estimator",
    description="An API for estimating home values based on user input and multiple data sources.",
    version="1.0.0",
)

class EstimateRequest(BaseModel):
    user_estimate: float
    address1: str
    address2: str

class EstimateResponse(BaseModel):
    address: str
    user_estimate: float
    estimate: float
    percentage_match: str

def clean_price(price_str):
    cleaned = re.sub(r'[^\d.]', '', str(price_str))
    try:
        return float(cleaned)
    except ValueError:
        return None

def get_house_price_AttomData(address1, address2):
    url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
    api_key = "6300621eea66a16daa96f042358517bd"
    
    headers = {
        "Accept": "application/json",
        "apikey": api_key
    }
    params = {
        "address1": address1,
        "address2": address2
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        # print(data)
        # Try to get the sale amount, if available
        sale_amount = data["property"][0]["sale"]["saleAmountData"].get("saleAmt")
        
        # If sale amount is not available, use the total assessed value
        if sale_amount is None:
            sale_amount = data["property"][0]["assessment"]["assessed"]["assdTtlValue"]
        return clean_price(sale_amount)
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing API response: {e}")
        return None



@app.post("/estimate", response_model=EstimateResponse, tags=["Estimates"])
async def estimate_home_value(request: EstimateRequest):
    """
    Estimate home value based on user input and compare it with data from AttomData.
    - **user_estimate**: User's estimated value of the property
    - **address1**: First line of the property address
    - **address2**: Second line of the property address (city, state)

    Returns:
    - **address**: The full address of the property
    - **user_estimate**: The user's input estimate
    - **estimate**: The estimate from combined data sets.
    - **percentage_match**: How close the user's estimate is to the AttomData estimate (as a percentage)
    """
    attom_estimate = get_house_price_AttomData(request.address1, request.address2)

    if attom_estimate is None:
        raise HTTPException(status_code=404, detail="Unable to estimate home value due to lack of data.")

    percentage_match = (request.user_estimate / attom_estimate) * 100
    pm = str(f"{percentage_match:.2f}%")
    return EstimateResponse(
        address=f"{request.address1}, {request.address2}",
        user_estimate=request.user_estimate,
        estimate=attom_estimate,
        percentage_match = pm
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