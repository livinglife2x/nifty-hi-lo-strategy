import time
from datetime import datetime, time as dt_time
import pytz
from config import load_config
from fyers_api import initialize_fyers, get_previous_day_data, get_today_open, get_ltp
from strategy import (
    check_trade_day_conditions, 
    check_entry_signal, 
    enter_trade,
    check_exit_signal,
    exit_trade
)

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

def wait_until_time(target_time):
    """Wait until a specific time in IST"""
    while True:
        now = get_ist_time().time()
        if now >= target_time:
            break
        time.sleep(0.1)

def is_market_closed():
    """Check if market is closed (after 3:15 PM IST)"""
    now = get_ist_time().time()
    return now >= dt_time(15, 15, 0)

def main():
    print("="*60)
    print("Fyers Live Trading Strategy")
    print("="*60)
    
    # Show current time in both local and IST
    local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
    ist_time = get_ist_time().strftime('%Y-%m-%d %H:%M:%S %Z')
    print(f"\nLocal Time: {local_time}")
    print(f"IST Time: {ist_time}")
    
    # Load configuration
    config = load_config()
    
    if not config:
        print("Failed to load configuration. Please check config.json")
        return
    
    if config['client_id'] == "YOUR_CLIENT_ID" or config['access_token'] == "YOUR_ACCESS_TOKEN":
        print("\n⚠️  Please update config.json with your Fyers credentials!")
        return
    
    # Initialize Fyers API
    fyers = initialize_fyers(config['client_id'], config['access_token'])
    
    symbol = config['symbol']
    capital = config['capital']
    risk_pct = config['risk_per_trade_pct']
    
    print(f"\nTrading Symbol: {symbol}")
    print(f"Capital: ₹{capital}")
    print(f"Risk Per Trade: {risk_pct}%")
    print(f"\nWaiting for 9:15 AM IST...\n")
    
    # Wait until 9:15 AM IST
    wait_until_time(dt_time(9, 15, 0))
    print(f"✓ Market opened at 9:15 AM IST (Local: {datetime.now().strftime('%H:%M:%S')})")
    
    # Wait 1 minute until 9:16:01 IST
    print("Waiting for 9:16:01 IST...")
    wait_until_time(dt_time(9, 16, 1))
    
    # Get previous day data
    prev_data = get_previous_day_data(fyers, symbol)
    
    if not prev_data:
        print("Failed to get previous day data. Exiting.")
        return
    
    # Get today's opening price from live quotes
    today_open = get_today_open(fyers, symbol)
    
    if not today_open:
        print("Failed to get today's opening price. Exiting.")
        return
    
    # Add today's open to prev_data
    prev_data['today_open'] = today_open
    
    # Check if today is a trade day
    is_trade_day = check_trade_day_conditions(prev_data)
    
    if not is_trade_day:
        print("Today is NOT a trade day. Exiting strategy.")
        return
    
    # Trade day - start monitoring
    print("Starting live monitoring every 1 second...")
    
    prev_high = prev_data['prev_high']
    prev_low = prev_data['prev_low']
    
    trade_taken = False
    trade_details = None
    
    while not is_market_closed():
        try:
            # Get current LTP
            ltp = get_ltp(fyers, symbol)
            
            if ltp is None:
                print("Failed to get LTP, retrying...")
                time.sleep(1)
                continue
            
            current_time = get_ist_time().strftime('%H:%M:%S')
            
            # If no trade taken yet, check for entry
            if not trade_taken:
                signal = check_entry_signal(ltp, prev_high, prev_low)
                
                if signal:
                    trade_details = enter_trade(fyers, symbol, capital, risk_pct, signal, ltp, prev_high, prev_low)
                    
                    if trade_details:
                        trade_taken = True
                    else:
                        print("Entry failed, continuing to monitor...")
                else:
                    print(f"[{current_time}] LTP: ₹{ltp} | Waiting for entry signal...")
            
            # If trade is active, check for exit
            else:
                # Check stop loss
                if check_exit_signal(ltp, trade_details['type'], prev_high, prev_low):
                    success = exit_trade(fyers, symbol, trade_details, ltp, "Stop Loss Hit")
                    if success:
                        trade_taken = False  # Mark position as closed
                        trade_details = None
                        print("Trade completed. No more trades today. Monitoring until market close...")
                    else:
                        print("Exit failed, retrying...")
                # Don't print every second - only print every 10 seconds or on significant price moves
                # Removed the else block to reduce console spam
            
            # Sleep for 1 second
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n\nStrategy interrupted by user")
            if trade_taken and trade_details:
                print("Attempting to exit open position...")
                ltp = get_ltp(fyers, symbol)
                if ltp:
                    exit_trade(fyers, symbol, trade_details, ltp, "Manual Exit")
            return
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)
    
    # Market closed at 3:15 PM
    if trade_details is not None:  # Check if position still exists
        print("\n⏰ Market closing at 3:15 PM - Open position detected")
        ltp = get_ltp(fyers, symbol)
        if ltp:
            exit_trade(fyers, symbol, trade_details, ltp, "Market Close - 3:15 PM")
    else:
        print("\n⏰ Market closed at 3:15 PM - No open positions")
    
    print("\n" + "="*60)
    print("Strategy completed for the day")
    print("="*60)

if __name__ == "__main__":
    main()