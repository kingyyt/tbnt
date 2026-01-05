from typing import Any, List
from fastapi import APIRouter, HTTPException
import requests
import json

router = APIRouter()

STOCK_CODES = {
    "gold": "sz159812",
    "nasdaq": "sz159509"
}

@router.get("/trend", response_model=Any)
def get_investment_trend(type: str) -> Any:
    """
    Get investment trend data (Gold or Nasdaq ETF).
    """
    if type not in STOCK_CODES:
        raise HTTPException(status_code=400, detail="Invalid investment type. Use 'gold' or 'nasdaq'.")
    
    symbol = STOCK_CODES[type]
    # Fetch 60-minute K-line data for a good trend view (last 100 points)
    url = f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale=60&ma=no&datalen=100"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://finance.sina.com.cn/"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Sina returns a JSON list
        data = response.json()
        
        # Format for frontend
        formatted_data = []
        for item in data:
            formatted_data.append({
                "time": item["day"],
                "value": float(item["close"])
            })
            
        return formatted_data
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch investment data")
