from datetime import datetime
from fyers_api import place_order

def calculate_quantity(capital, risk_pct, entry_price, stop_loss_price):
    """Calculate quantity based on capital and risk percentage"""
    risk_amount = capital * (risk_pct / 100)
    price_diff = abs(entry_price - stop_loss_price)
    
    if price_diff == 0:
        return 1
    
    quantity = int(risk_amount / price_diff)
    
    # Minimum 1 quantity
    if quantity < 1:
        quantity = 1
    
    print(f"\nQuantity Calculation:")
    print(f"  Capital: ₹{capital}")
    print(f"  Risk %: {risk_pct}%")
    print(f"  Risk Amount: ₹{risk_amount}")
    print(f"  Entry Price: ₹{entry_price}")
    print(f"  Stop Loss: ₹{stop_loss_price}")
    print(f"  Price Difference: ₹{price_diff}")
    print(f"  Calculated Quantity: {quantity}")
    
    return quantity

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

def enter_trade(fyers, symbol, capital, risk_pct, trade_type, ltp, prev_high, prev_low):
    """Enter a trade and return trade details"""
    """
    stop_loss = prev_low if trade_type == 'LONG' else prev_high
    
    # Calculate quantity dynamically
    quantity = calculate_quantity(capital, risk_pct, ltp, stop_loss)
    
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
            'stop_loss': stop_loss,
            'quantity': quantity
        }
        
        print(f"✓ Trade Executed Successfully")
        print(f"  Type: {trade_type}")
        print(f"  Quantity: {quantity}")
        print(f"  Entry Price: ₹{entry_price}")
        print(f"  Entry Time: {entry_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Stop Loss: ₹{stop_loss}")
        print(f"{'='*60}\n")
        
        return trade_details
    else:
        print(f"❌ Order placement failed")
        return None
    """

    stop_loss = prev_low if trade_type == 'LONG' else prev_high
    
    # Calculate quantity dynamically
    quantity = 1
    
    side = "BUY" if trade_type == "LONG" else "SELL"
    
    print(f"\n{'='*60}")
    print(f"🔔 ENTRY SIGNAL: {trade_type}")
    print(f"{'='*60}")
    
    #response = place_order(fyers, symbol, side, quantity)
    
    #if response and response.get('s') == 'ok':
    entry_datetime = datetime.now()
    entry_price = ltp
    
    trade_details = {
        'type': trade_type,
        'entry_price': entry_price,
        'entry_datetime': entry_datetime,
        'stop_loss': stop_loss,
        'quantity': quantity
    }
    
    print(f"✓ Trade Executed Successfully")
    print(f"  Type: {trade_type}")
    print(f"  Quantity: {quantity}")
    print(f"  Entry Price: ₹{entry_price}")
    print(f"  Entry Time: {entry_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Stop Loss: ₹{stop_loss}")
    print(f"{'='*60}\n")
        
    return trade_details
    


def check_exit_signal(ltp, trade_type, prev_high, prev_low):
    """Check if stop loss is hit"""
    # Long position: exit if LTP breaches prev low
    if trade_type == 'LONG' and ltp <= prev_low:
        return True
    
    # Short position: exit if LTP breaches prev high
    if trade_type == 'SHORT' and ltp >= prev_high:
        return True
    
    return False

def exit_trade(fyers, symbol, trade_details, ltp, reason="Stop Loss Hit"):
  
    """Exit the trade and log details"""
    """
    # Safety check - ensure trade_details exists
    if trade_details is None:
        print("⚠️  No active position to exit")
        return False
    
    side = "SELL" if trade_details['type'] == "LONG" else "BUY"
    quantity = trade_details['quantity']
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
            'quantity': quantity,
            'profit_absolute': round(profit, 2),
            'profit_percentage': round(profit_pct, 2),
            'trade_type': trade_details['type'],
            'exit_reason': reason
        }
        
        log_trade(log_entry)
        
        return True  # Successfully exited
    else:
        print(f"❌ Exit order failed")
        return False  # Exit failed
    """
    if trade_details is None:
        print("⚠️  No active position to exit")
        return False
    
    side = "SELL" if trade_details['type'] == "LONG" else "BUY"
    quantity = trade_details['quantity']
    exit_datetime = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"🔔 EXIT SIGNAL: {reason}")
    print(f"{'='*60}")
    
    #response = place_order(fyers, symbol, side, quantity)
    
    #if response and response.get('s') == 'ok':
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
        'quantity': quantity,
        'profit_absolute': round(profit, 2),
        'profit_percentage': round(profit_pct, 2),
        'trade_type': trade_details['type'],
        'exit_reason': reason
    }
    
    log_trade(log_entry)
    
    return True  # Successfully exited
  

def log_trade(trade_data):
    """Log trade details to console and file"""
    print(f"✓ Exit Executed Successfully")
    print(f"  Entry DateTime: {trade_data['entry_datetime']}")
    print(f"  Entry Price: ₹{trade_data['entry_price']}")
    print(f"  Exit DateTime: {trade_data['exit_datetime']}")
    print(f"  Exit Price: ₹{trade_data['exit_price']}")
    print(f"  Quantity: {trade_data['quantity']}")
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