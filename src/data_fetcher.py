import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class OrderFlowData:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.symbol = 'BTC/USDT'
        self.all_trades = pd.DataFrame(columns=['timestamp', 'price', 'size', 'side'])
        self.orderbook_history = []
        self.data_start_time = None
        self.last_update = None
        
    def fetch_new_data(self):
        """Fetch new trades and order book data"""
        try:
            # Fetch recent trades
            trades = self.exchange.fetch_trades(self.symbol, limit=200)
            new_trades = []
            
            for trade in trades:
                trade_time = datetime.fromtimestamp(trade['timestamp'] / 1000)
                
                # Only add new trades
                if len(self.all_trades) == 0 or trade_time > self.all_trades['timestamp'].max():
                    new_trades.append({
                        'timestamp': trade_time,
                        'price': float(trade['price']),
                        'size': float(trade['amount']),
                        'side': trade['side'],
                    })
            
            # Fetch order book
            orderbook = self.exchange.fetch_order_book(self.symbol, limit=50)
            orderbook_data = {
                'timestamp': datetime.now(),
                'bids': [(float(price), float(amount)) for price, amount in orderbook['bids'][:20]],
                'asks': [(float(price), float(amount)) for price, amount in orderbook['asks'][:20]]
            }
            
            # Update data stores
            if new_trades:
                self._update_trades_data(new_trades)
            
            self.orderbook_history.append(orderbook_data)
            self.orderbook_history = self.orderbook_history[-50:]  # Keep last 50 snapshots
            
            self.last_update = datetime.now()
            
            return len(new_trades)
            
        except Exception as e:
            print(f"❌ Data fetch error: {e}")
            return 0
    
    def _update_trades_data(self, new_trades):
        """Update trades data with new trades"""
        new_trades_df = pd.DataFrame(new_trades)
        
        if not self.all_trades.empty:
            self.all_trades = pd.concat([self.all_trades, new_trades_df], ignore_index=True)
        else:
            self.all_trades = new_trades_df
        
        # Remove duplicates and keep recent data
        self.all_trades = self.all_trades.drop_duplicates(subset=['timestamp', 'price', 'size'])
        cutoff_time = datetime.now() - timedelta(hours=4)
        self.all_trades = self.all_trades[self.all_trades['timestamp'] > cutoff_time]
    
    def calculate_metrics(self, trades, time_window_minutes):
        """Calculate market metrics for the given time window"""
        if len(trades) == 0:
            return {}
        
        df = trades.copy()
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        window_trades = df[df['timestamp'] > cutoff_time]
        
        if len(window_trades) == 0:
            return {}
        
        # Calculate basic metrics
        total_volume = window_trades['size'].sum()
        buy_volume = window_trades[window_trades['side'] == 'buy']['size'].sum()
        sell_volume = window_trades[window_trades['side'] == 'sell']['size'].sum()
        net_delta = buy_volume - sell_volume
        
        # Calculate price change
        current_price = window_trades['price'].iloc[-1]
        if len(window_trades) > 1:
            start_price = window_trades['price'].iloc[0]
            price_change_percent = ((current_price - start_price) / start_price) * 100
        else:
            price_change_percent = 0
        
        return {
            'current_price': current_price,
            'price_change_percent': price_change_percent,
            'total_volume': total_volume,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'net_delta': net_delta
        }