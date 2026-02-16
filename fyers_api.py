from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta

def initialize_fyers(client_id, access_token):
    """Initialize Fyers API client"""
    return fyersModel.FyersModel(
        client_id=client_id, 
        token=access_token, 
        is_async=False, 
        log_path=""
    )

def get_previous_day_data(fyers, symbol):
    """Get previous day OHLC data"""
    try:
        today = datetime.now()
        range_from = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        range_to = today.strftime("%Y-%m-%d")
        
        data = {
            "symbol": symbol,
            "resolution": "D",
            "date_format": "1",
            "range_from": range_from,
            "range_to": range_to,
            "cont_flag": "1"
        }
        
        response = fyers.history(data=data)
        print("---historical data---")
        print(response['candles'])
        
        if response['s'] == 'ok' and len(response['candles']) >= 1:
            prev_candle = response['candles'][-1]  # Last complete day
            
            return {
                'prev_open': prev_candle[1],
                'prev_high': prev_candle[2],
                'prev_low': prev_candle[3],
                'prev_close': prev_candle[4]
            }
        else:
            print(f"Error getting historical data: {response}")
            return None
    except Exception as e:
        print(f"Exception in get_previous_day_data: {e}")
        return None

def get_today_open(fyers, symbol):
    """Get today's opening price from live quotes"""
    try:
        data = {"symbols": symbol}
        response = fyers.quotes(data=data)
        
        if response['s'] == 'ok' and len(response['d']) > 0:
            today_open = response['d'][0]['v']['open_price']
            return today_open
        else:
            print(f"Error getting today's open: {response}")
            return None
    except Exception as e:
        print(f"Exception in get_today_open: {e}")
        return None

def get_ltp(fyers, symbol):
    """Get Last Traded Price"""
    try:
        data = {"symbols": symbol}
        response = fyers.quotes(data=data)
        
        if response['s'] == 'ok' and len(response['d']) > 0:
            return response['d'][0]['v']['lp']
        else:
            print(f"Error getting LTP: {response}")
            return None
    except Exception as e:
        print(f"Exception in get_ltp: {e}")
        return None

def place_order(fyers, symbol, side, quantity):
    """Place market order - side should be 'BUY' or 'SELL'"""
    try:
        data = {
            "symbol": symbol,
            "qty": quantity,
            "type": 2,  # Market order
            "side": 1 if side == "BUY" else -1,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False
        }
        
        response = fyers.place_order(data=data)
        print(f"Order Response: {response}")
        return response
    except Exception as e:
        print(f"Exception in place_order: {e}")
        return None
    
def get_option_chain_expiries(fyers):
    try:
        data = {
        "symbol":"NSE:NIFTY50-INDEX",
        "strikecount":2,
        "timestamp": ""
        }
        response = fyers.optionchain(data=data)
        return response['data']['expiryData']
    except Exception as e:
        print(f"Exception in return option chain expiries {e}")
        return None
    
def get_option_chain_expiry(fyers,expiry):
    try:
        data = {
        "symbol":"NSE:NIFTY50-INDEX",
        "strikecount":2,
        "timestamp": expiry
        }
        response = fyers.optionchain(data=data)
        return response['data']['optionsChain']
    except Exception as e:
        print(f"Exception in return option chain for a given expiry {e}")
        return None
    




