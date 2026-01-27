"""
layr0_imc Supertrend Strategy Example

A complete example showing how to implement a Supertrend-based trading strategy
using layr0_imc's technical indicators and trading API.
"""

from layr0_imc import api, ta
import pandas as pd
import numpy as np
import time

class SupertrendStrategy:
    """
    A simple Supertrend-based trading strategy
    
    Strategy Rules:
    - Buy when price closes above Supertrend and RSI < 70
    - Sell when price closes below Supertrend or RSI > 80
    - Additional filter: ATR-based position sizing
    """
    
    def __init__(self, api_key, host="http://127.0.0.1:5000"):
        """Initialize the strategy"""
        self.client = api(api_key=api_key, host=host)
        self.position = 0  # 0: No position, 1: Long, -1: Short
        self.entry_price = 0
        
        # Strategy parameters
        self.st_period = 10
        self.st_multiplier = 3.0
        self.rsi_period = 14
        self.atr_period = 14
        self.rsi_overbought = 80
        self.rsi_oversold = 20
        
        # Risk management
        self.max_position_size = 100
        self.risk_per_trade = 0.02  # 2% risk per trade
        
    def fetch_data(self, symbol, exchange, interval="5m", days=30):
        """
        Fetch historical data and calculate indicators
        """
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get historical data
            df = self.client.history(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            if isinstance(df, pd.DataFrame) and not df.empty:
                return self.calculate_indicators(df)
            else:
                print(f"No data received for {symbol}")
                return None
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def calculate_indicators(self, df):
        """
        Calculate all required technical indicators
        """
        # Supertrend
        supertrend, direction = ta.supertrend(
            df['high'], df['low'], df['close'], 
            self.st_period, self.st_multiplier
        )
        df['supertrend'] = supertrend
        df['trend'] = direction
        
        # RSI
        df['rsi'] = ta.rsi(df['close'], self.rsi_period)
        
        # ATR for position sizing
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], self.atr_period)
        
        # Moving averages for additional confirmation
        df['ema_20'] = ta.ema(df['close'], 20)
        df['ema_50'] = ta.ema(df['close'], 50)
        
        # Price position relative to Supertrend
        df['above_st'] = df['close'] > df['supertrend']
        df['below_st'] = df['close'] < df['supertrend']
        
        # Generate signals
        df['buy_signal'] = (
            (df['trend'] == -1) &  # Bullish Supertrend
            (df['rsi'] < 70) &     # Not overbought
            (df['close'] > df['ema_20'])  # Above short-term EMA
        )
        
        df['sell_signal'] = (
            (df['trend'] == 1) |   # Bearish Supertrend
            (df['rsi'] > self.rsi_overbought)  # Overbought
        )
        
        return df
    
    def calculate_position_size(self, current_price, atr, account_balance=100000):
        """
        Calculate position size based on ATR and risk management
        """
        # Risk per trade based on ATR
        stop_loss_distance = atr * 2  # 2x ATR stop loss
        
        if stop_loss_distance == 0:
            return 1  # Minimum position size
        
        # Calculate position size based on risk
        risk_amount = account_balance * self.risk_per_trade
        position_size = int(risk_amount / stop_loss_distance)
        
        # Limit position size
        return min(position_size, self.max_position_size)
    
    def execute_trade(self, symbol, exchange, action, quantity, strategy_name="Supertrend"):
        """
        Execute a trade using layr0_imc API
        """
        try:
            response = self.client.placeorder(
                symbol=symbol,
                action=action,
                exchange=exchange,
                price_type="MARKET",
                product="MIS",
                quantity=quantity,
                strategy=strategy_name
            )
            
            if response.get('status') == 'success':
                print(f"✅ {action} order placed: {quantity} shares of {symbol}")
                return response
            else:
                print(f"❌ Order failed: {response.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Trade execution error: {e}")
            return None
    
    def run_strategy(self, symbol, exchange="NSE", interval="5m"):
        """
        Run the strategy for a given symbol
        """
        print(f"🚀 Starting Supertrend Strategy for {symbol}")
        print(f"Parameters: ST({self.st_period}, {self.st_multiplier}), RSI({self.rsi_period})")
        print("-" * 60)
        
        # Fetch and analyze data
        df = self.fetch_data(symbol, exchange, interval)
        
        if df is None or len(df) < 50:
            print("❌ Insufficient data for analysis")
            return
        
        # Get latest values
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        current_price = latest['close']
        supertrend = latest['supertrend']
        trend = latest['trend']
        rsi = latest['rsi']
        atr = latest['atr']
        
        # Display current market state
        print(f"📊 Market Analysis for {symbol}:")
        print(f"   Current Price: ₹{current_price:.2f}")
        print(f"   Supertrend: ₹{supertrend:.2f}")
        print(f"   Trend: {'🟢 BULLISH' if trend == -1 else '🔴 BEARISH'}")
        print(f"   RSI: {rsi:.2f}")
        print(f"   ATR: {atr:.2f}")
        
        # Check for signals
        buy_signal = latest['buy_signal']
        sell_signal = latest['sell_signal']
        
        # Position management
        if buy_signal and self.position <= 0:
            # Enter long position
            quantity = self.calculate_position_size(current_price, atr)
            
            if self.position < 0:
                # Close short position first
                self.execute_trade(symbol, exchange, "BUY", abs(self.position), "Supertrend_Cover")
            
            # Open long position
            result = self.execute_trade(symbol, exchange, "BUY", quantity, "Supertrend_Long")
            if result:
                self.position = quantity
                self.entry_price = current_price
                print(f"📈 LONG position opened: {quantity} shares at ₹{current_price:.2f}")
                
        elif sell_signal and self.position >= 0:
            # Enter short position or close long
            if self.position > 0:
                # Close long position
                result = self.execute_trade(symbol, exchange, "SELL", self.position, "Supertrend_Exit")
                if result:
                    profit_loss = (current_price - self.entry_price) * self.position
                    print(f"📉 LONG position closed. P&L: ₹{profit_loss:.2f}")
                    self.position = 0
                    
            # Optional: Enter short position (uncomment if short selling is allowed)
            """
            quantity = self.calculate_position_size(current_price, atr)
            result = self.execute_trade(symbol, exchange, "SELL", quantity, "Supertrend_Short")
            if result:
                self.position = -quantity
                self.entry_price = current_price
                print(f"📉 SHORT position opened: {quantity} shares at ₹{current_price:.2f}")
            """
        
        # Display current position
        if self.position > 0:
            unrealized_pnl = (current_price - self.entry_price) * self.position
            print(f"💼 Current Position: LONG {self.position} shares")
            print(f"   Entry Price: ₹{self.entry_price:.2f}")
            print(f"   Unrealized P&L: ₹{unrealized_pnl:.2f}")
        elif self.position < 0:
            unrealized_pnl = (self.entry_price - current_price) * abs(self.position)
            print(f"💼 Current Position: SHORT {abs(self.position)} shares")
            print(f"   Entry Price: ₹{self.entry_price:.2f}")
            print(f"   Unrealized P&L: ₹{unrealized_pnl:.2f}")
        else:
            print("💼 Current Position: FLAT (No position)")
    
    def backtest_strategy(self, symbol, exchange="NSE", interval="5m", days=90):
        """
        Backtest the strategy on historical data
        """
        print(f"📊 Backtesting Supertrend Strategy for {symbol}")
        print("-" * 60)
        
        df = self.fetch_data(symbol, exchange, interval, days)
        
        if df is None or len(df) < 100:
            print("❌ Insufficient data for backtesting")
            return
        
        # Initialize backtest variables
        position = 0
        entry_price = 0
        trades = []
        equity_curve = [100000]  # Starting capital
        current_equity = 100000
        
        for i in range(50, len(df)):  # Start after indicators are valid
            row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            current_price = row['close']
            
            # Entry signals
            if row['buy_signal'] and position <= 0:
                if position < 0:
                    # Close short position
                    pnl = (entry_price - current_price) * abs(position)
                    current_equity += pnl
                    trades.append({
                        'type': 'SHORT_EXIT',
                        'price': current_price,
                        'quantity': abs(position),
                        'pnl': pnl,
                        'date': row.name
                    })
                
                # Open long position
                position = 100  # Fixed size for backtesting
                entry_price = current_price
                trades.append({
                    'type': 'LONG_ENTRY',
                    'price': current_price,
                    'quantity': position,
                    'pnl': 0,
                    'date': row.name
                })
                
            elif row['sell_signal'] and position >= 0:
                if position > 0:
                    # Close long position
                    pnl = (current_price - entry_price) * position
                    current_equity += pnl
                    trades.append({
                        'type': 'LONG_EXIT',
                        'price': current_price,
                        'quantity': position,
                        'pnl': pnl,
                        'date': row.name
                    })
                    position = 0
            
            # Update equity curve
            if position > 0:
                unrealized_pnl = (current_price - entry_price) * position
                equity_curve.append(current_equity + unrealized_pnl)
            elif position < 0:
                unrealized_pnl = (entry_price - current_price) * abs(position)
                equity_curve.append(current_equity + unrealized_pnl)
            else:
                equity_curve.append(current_equity)
        
        # Calculate performance metrics
        total_trades = len([t for t in trades if 'EXIT' in t['type']])
        winning_trades = len([t for t in trades if 'EXIT' in t['type'] and t['pnl'] > 0])
        total_pnl = sum([t['pnl'] for t in trades if 'EXIT' in t['type']])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_return = (current_equity - 100000) / 100000 * 100
        
        print(f"📈 Backtest Results:")
        print(f"   Total Trades: {total_trades}")
        print(f"   Winning Trades: {winning_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total P&L: ₹{total_pnl:.2f}")
        print(f"   Total Return: {total_return:.2f}%")
        print(f"   Final Equity: ₹{current_equity:.2f}")
        
        return trades, equity_curve


def main():
    """
    Main function to run the Supertrend strategy
    """
    # Configuration
    API_KEY = "your_api_key_here"  # Replace with your actual API key
    SYMBOL = "RELIANCE"
    EXCHANGE = "NSE"
    
    print("layr0_imc Supertrend Strategy")
    print("============================\n")
    
    # Initialize strategy
    strategy = SupertrendStrategy(api_key=API_KEY)
    
    # Run backtest first
    print("1. Running Backtest...")
    strategy.backtest_strategy(SYMBOL, EXCHANGE, days=60)
    
    print("\n" + "="*60 + "\n")
    
    # Run live strategy (single execution)
    print("2. Running Live Analysis...")
    strategy.run_strategy(SYMBOL, EXCHANGE)
    
    print("\n" + "="*60 + "\n")
    
    # For continuous monitoring, uncomment the following:
    """
    print("3. Starting Continuous Monitoring...")
    while True:
        try:
            strategy.run_strategy(SYMBOL, EXCHANGE)
            print(f"\\n⏰ Waiting 5 minutes for next analysis...")
            time.sleep(300)  # Wait 5 minutes
        except KeyboardInterrupt:
            print("\\n🛑 Strategy stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in strategy loop: {e}")
            time.sleep(60)  # Wait 1 minute before retrying
    """


if __name__ == "__main__":
    main()
