from datetime import datetime

def check_trade_day_conditions(prev_data):
    """Check if today qualifies as a trade day"""
    print("\n" + "="*60)
    print("Checking trade day conditions at 9:16:01...")
    print("="*60)
    
    prev_high = prev_data['prev_high']
    prev_low = prev_data['prev_low']
    prev_open = prev_data['prev_open']
    prev_close = prev_data['prev_close']
    today_open = prev_data['today_open']
    
    print(f"Previous Day - High: {prev_high}, Low: {prev_low}")
    print(f"Previous Day - Open: {prev_open}, Close: {prev_close}")
    print(f"Today's Open: {today_open}")
    
    # Condition 1: Today's open should be between prev high and low
    if not (prev_low <= today_open <= prev_high):
        print(f"❌ Today's open {today_open} is NOT between prev high {prev_high} and low {prev_low}")
        return False
    
    print(f"✓ Today's open is between prev high and low")
    
    # Condition 2: ((prev_open - prev_close) * 100) / prev_close < 0.5
    prev_day_change_pct = abs(((prev_open - prev_close) * 100) / prev_close)
    print(f"Previous day change %: {prev_day_change_pct:.2f}%")
    
    if prev_day_change_pct >= 0.5:
        print(f"❌ Previous day change {prev_day_change_pct:.2f}% >= 0.5%")
        return False
    
    print(f"✓ Previous day change {prev_day_change_pct:.2f}% < 0.5%")
    print("✓✓ Today is a TRADE DAY!")
    print("="*60 + "\n")
    return True

def check_entry_signal(ltp, prev_high, prev_low):
    """Check if entry conditions are met"""
    # Long condition: LTP crossed prev high
    if ltp > prev_high:
        return 'LONG'
    
    # Short condition: LTP crossed prev low
    if ltp < prev_low:
        return 'SHORT'
    
    return None

def enter_trade(fyers, symbol, quantity, trade_type, ltp, prev_high, prev_low):
    """Enter a trade and return trade details"""
    side = "BUY" if trade_type == "LONG" else "SELL"
    
    print(f"\n{'='*60}")
    print(f"🔔 ENTRY SIGNAL: {trade_type}")
    print(f"{'='*60}")
    
    response = place_order(fyers, symbol, side, quantity)
    
    if response and response.get('s') == 'ok':
        entry_datetime = datetime.now()
        entry_price = ltp
        
        trade_details = {
            'type': trade_type,
            'entry_price': entry_price,
            'entry_datetime': entry_datetime,
            'stop_loss': prev_low if trade_type == 'LONG' else prev_high
        }
        
        print(f"✓ Trade Executed Successfully")
        print(f"  Type: {trade_type}")
        print(f"  Entry Price: ₹{entry_price}")
        print(f"  Entry Time: {entry_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Stop Loss: ₹{trade_details['stop_loss']}")
        print(f"{'='*60}\n")
        
        return trade_details
    else:
        print(f"❌ Order placement failed")
        return None

def check_exit_signal(ltp, trade_type, prev_high, prev_low):
    """Check if stop loss is hit"""
    # Long position: exit if LTP breaches prev low
    if trade_type == 'LONG' and ltp <= prev_low:
        return True
    
    # Short position: exit if LTP breaches prev high
    if trade_type == 'SHORT' and ltp >= prev_high:
        return True
    
    return False

def exit_trade(fyers, symbol, quantity, trade_details, ltp, reason="Stop Loss Hit"):
    """Exit the trade and log details"""
    side = "SELL" if trade_details['type'] == "LONG" else "BUY"
    exit_datetime = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"🔔 EXIT SIGNAL: {reason}")
    print(f"{'='*60}")
    
    response = place_order(fyers, symbol, side, quantity)
    
    if response and response.get('s') == 'ok':
        exit_price = ltp
        
        # Calculate profit
        if trade_details['type'] == 'LONG':
            profit = (exit_price - trade_details['entry_price']) * quantity
        else:
            profit = (trade_details['entry_price'] - exit_price) * quantity
        
        profit_pct = (profit / (trade_details['entry_price'] * quantity)) * 100
        
        # Create log entry
        log_entry = {
            'entry_datetime': trade_details['entry_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
            'entry_price': trade_details['entry_price'],
            'exit_datetime': exit_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'exit_price': exit_price,
            'profit_absolute': round(profit, 2),
            'profit_percentage': round(profit_pct, 2),
            'trade_type': trade_details['type'],
            'exit_reason': reason
        }
        
        log_trade(log_entry)
        
        return True
    else:
        print(f"❌ Exit order failed")
        return False

def log_trade(trade_data):
    """Log trade details to console and file"""
    print(f"✓ Exit Executed Successfully")
    print(f"  Entry DateTime: {trade_data['entry_datetime']}")
    print(f"  Entry Price: ₹{trade_data['entry_price']}")
    print(f"  Exit DateTime: {trade_data['exit_datetime']}")
    print(f"  Exit Price: ₹{trade_data['exit_price']}")
    print(f"  Profit (Absolute): ₹{trade_data['profit_absolute']}")
    print(f"  Profit (Percentage): {trade_data['profit_percentage']}%")
    print(f"  Trade Type: {trade_data['trade_type']}")
    print(f"  Exit Reason: {trade_data['exit_reason']}")
    print(f"{'='*60}\n")
    
    # Append to log file
    try:
        with open('trade_log.txt', 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Trade Log Entry - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            for key, value in trade_data.items():
                f.write(f"{key}: {value}\n")
            f.write(f"{'='*60}\n")
        print("✓ Trade logged to trade_log.txt")
    except Exception as e:
        print(f"Error writing to log file: {e}")


# =====================================================
# main.py
# =====================================================
import time
from datetime import datetime, time as dt_time
from config import load_config
from fyers_api import initialize_fyers, get_previous_day_data, get_ltp
from strategy import (
    check_trade_day_conditions, 
    check_entry_signal, 
    enter_trade,
    check_exit_signal,
    exit_trade
)

def wait_until_time(target_time):
    """Wait until a specific time"""
    while True:
        now = datetime.now().time()
        if now >= target_time:
            break
        time.sleep(0.1)

def is_market_closed():
    """Check if market is closed (after 3:15 PM)"""
    now = datetime.now().time()
    return now >= dt_time(15, 15, 0)

def main():
    print("="*60)
    print("Fyers Live Trading Strategy")
    print("="*60)
    
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
    quantity = config['quantity']
    
    print(f"\nTrading Symbol: {symbol}")
    print(f"Quantity: {quantity}")
    print(f"\nWaiting for 9:15 AM...\n")
    
    # Wait until 9:15 AM
    wait_until_time(dt_time(9, 15, 0))
    print("✓ Market opened at 9:15 AM")
    
    # Wait 1 minute until 9:16:01
    print("Waiting for 9:16:01...")
    wait_until_time(dt_time(9, 16, 1))
    
    # Get previous day data
    prev_data = get_previous_day_data(fyers, symbol)
    
    if not prev_data:
        print("Failed to get previous day data. Exiting.")
        return
    
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
            
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # If no trade taken yet, check for entry
            if not trade_taken:
                signal = check_entry_signal(ltp, prev_high, prev_low)
                
                if signal:
                    trade_details = enter_trade(fyers, symbol, quantity, signal, ltp, prev_high, prev_low)
                    
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
                    exit_trade(fyers, symbol, quantity, trade_details, ltp, "Stop Loss Hit")
                    print("Trade completed. Exiting strategy.")
                    return
                else:
                    print(f"[{current_time}] LTP: ₹{ltp} | Trade active, monitoring stop loss...")
            
            # Sleep for 1 second
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n\nStrategy interrupted by user")
            if trade_taken and trade_details:
                print("Attempting to exit open position...")
                ltp = get_ltp(fyers, symbol)
                if ltp:
                    exit_trade(fyers, symbol, quantity, trade_details, ltp, "Manual Exit")
            return
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)
    
    # Market closed at 3:15 PM
    if trade_taken and trade_details:
        print("\n⏰ Market closing at 3:15 PM")
        ltp = get_ltp(fyers, symbol)
        if ltp:
            exit_trade(fyers, symbol, quantity, trade_details, ltp, "Market Close - 3:15 PM")
    
    print("\n" + "="*60)
    print("Strategy completed for the day")
    print("="*60)

if __name__ == "__main__":
    main()