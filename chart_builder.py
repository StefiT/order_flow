import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_candlestick_data(trades, timeframe_minutes=1):
    """Convert trades to candlestick data"""
    if len(trades) == 0:
        return pd.DataFrame()
    
    df = trades.copy()
    df = df.set_index('timestamp')
    
    # Resample to create OHLC data
    ohlc = df['price'].resample(f'{timeframe_minutes}T').ohlc()
    volume = df['size'].resample(f'{timeframe_minutes}T').sum()
    
    # Combine OHLC and volume
    candlestick_data = pd.concat([ohlc, volume], axis=1)
    candlestick_data.columns = ['open', 'high', 'low', 'close', 'volume']
    candlestick_data = candlestick_data.dropna()
    
    return candlestick_data

def calculate_volume_profile(trades, price_levels=20):
    """Calculate volume profile for current data"""
    if len(trades) == 0:
        return pd.DataFrame()
    
    # Create price levels
    min_price = trades['price'].min()
    max_price = trades['price'].max()
    price_range = max_price - min_price
    bin_size = price_range / price_levels
    
    # Calculate volume at each price level
    volume_profile = []
    for i in range(price_levels):
        price_level = min_price + (i * bin_size)
        next_price_level = price_level + bin_size
        
        # Volume in this price range
        volume_in_range = trades[
            (trades['price'] >= price_level) & 
            (trades['price'] < next_price_level)
        ]['size'].sum()
        
        volume_profile.append({
            'price': (price_level + next_price_level) / 2,
            'volume': volume_in_range
        })
    
    return pd.DataFrame(volume_profile)

def create_candlestick_with_profile(trades, time_window_minutes):
    """Create candlestick chart with volume profile"""
    if len(trades) == 0:
        return _create_empty_chart("Collecting trade data...", "Price Chart - Loading...")
    
    # Filter by time window
    cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
    window_trades = trades[trades['timestamp'] > cutoff_time]
    
    if len(window_trades) == 0:
        return _create_empty_chart(f"No trades in last {time_window_minutes} minutes", "Price Chart")
    
    # Create candlestick data
    candlestick_data = create_candlestick_data(window_trades, timeframe_minutes=1)
    
    if len(candlestick_data) == 0:
        return _create_empty_chart("Not enough data for candlesticks", "Price Chart")
    
    # Create volume profile
    volume_profile = calculate_volume_profile(window_trades)
    
    # Create subplot figure
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.7, 0.3],
        shared_yaxes=True,
        horizontal_spacing=0.02,
        subplot_titles=('Price Chart', 'Volume Profile')
    )
    
    # Add candlesticks
    fig.add_trace(
        go.Candlestick(
            x=candlestick_data.index,
            open=candlestick_data['open'],
            high=candlestick_data['high'],
            low=candlestick_data['low'],
            close=candlestick_data['close'],
            name='BTC/USDT'
        ),
        row=1, col=1
    )
    
    # Add volume profile
    if len(volume_profile) > 0:
        fig.add_trace(
            go.Bar(
                x=volume_profile['volume'],
                y=volume_profile['price'],
                orientation='h',
                marker_color='rgba(100, 100, 255, 0.6)',
                name='Volume Profile'
            ),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        title=f'BTC/USDT Price & Volume Profile - Last {time_window_minutes} Minutes',
        height=500,
        showlegend=False,
        xaxis_rangeslider_visible=False
    )
    
    # Update axes
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_xaxes(title_text="Volume (BTC)", row=1, col=2)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    
    return fig

def create_clean_delta_chart(trades, time_window_minutes):
    """Create clean delta visualization"""
    if len(trades) == 0:
        return _create_empty_chart("Collecting delta data...", "Delta Analysis - Loading...")

    # Filter by time window
    cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
    window_trades = trades[trades['timestamp'] > cutoff_time]

    if len(window_trades) == 0:
        return _create_empty_chart(f"No data in last {time_window_minutes} minutes", "Delta Analysis")

    window_trades = window_trades.set_index('timestamp')
    window_trades['delta'] = np.where(window_trades['side'] == 'buy', window_trades['size'], -window_trades['size'])

    # Calculate cumulative delta
    cumulative_delta = window_trades['delta'].cumsum()
    
    # Calculate 1-minute delta
    delta_1min = window_trades['delta'].resample('1min').sum()
    
    fig = go.Figure()
    
    # Add cumulative delta as main line
    fig.add_trace(go.Scatter(
        x=cumulative_delta.index,
        y=cumulative_delta.values,
        mode='lines',
        line=dict(color='blue', width=3),
        name='Cumulative Delta',
        hovertemplate='Time: %{x}<br>Cumulative Delta: %{y:.2f} BTC<extra></extra>'
    ))
    
    # Add 1-minute delta as background bars
    colors_1min = ['rgba(0, 255, 0, 0.3)' if x >= 0 else 'rgba(255, 0, 0, 0.3)' for x in delta_1min]
    fig.add_trace(go.Bar(
        x=delta_1min.index,
        y=delta_1min.values,
        marker_color=colors_1min,
        name='Delta (1min)',
        hovertemplate='Time: %{x}<br>Delta: %{y:.2f} BTC<extra></extra>',
        opacity=0.5
    ))

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.5)

    fig.update_layout(
        title=f'Delta Analysis - Last {time_window_minutes} Minutes',
        xaxis_title='Time',
        yaxis_title='Delta (BTC)',
        height=400,
        showlegend=True,
        bargap=0
    )
    
    return fig

def create_large_trades_chart(trades, time_window_minutes, min_trade_size):
    """Create chart showing only large trades"""
    if len(trades) == 0:
        return _create_empty_chart("Collecting trade data...", "Large Trades - Loading...")
    
    # Filter by time window and minimum size
    cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
    window_trades = trades[trades['timestamp'] > cutoff_time]
    large_trades = window_trades[window_trades['size'] >= min_trade_size]
    
    if len(large_trades) == 0:
        return _create_empty_chart(
            f"No large trades (≥{min_trade_size}BTC) in last {time_window_minutes} minutes", 
            f"Large Trades (≥{min_trade_size}BTC)"
        )
    
    # Separate buys and sells
    buys = large_trades[large_trades['side'] == 'buy']
    sells = large_trades[large_trades['side'] == 'sell']
    
    fig = go.Figure()
    
    # Add large buy trades
    if len(buys) > 0:
        buy_sizes = [max(10, min(50, size * 3)) for size in buys['size']]
        
        fig.add_trace(go.Scatter(
            x=buys['timestamp'],
            y=buys['price'],
            mode='markers',
            marker=dict(
                size=buy_sizes,
                color='green',
                symbol='triangle-up',
                line=dict(width=2, color='darkgreen'),
                opacity=0.8
            ),
            name=f'Large Buys ({len(buys)})',
            hovertemplate='<b>LARGE BUY</b><br>Price: $%{y:.2f}<br>Size: %{text} BTC<br>Time: %{x}<extra></extra>',
            text=[f'{size:.3f}' for size in buys['size']]
        ))
    
    # Add large sell trades
    if len(sells) > 0:
        sell_sizes = [max(10, min(50, size * 3)) for size in sells['size']]
        
        fig.add_trace(go.Scatter(
            x=sells['timestamp'],
            y=sells['price'],
            mode='markers',
            marker=dict(
                size=sell_sizes,
                color='red',
                symbol='triangle-down',
                line=dict(width=2, color='darkred'),
                opacity=0.8
            ),
            name=f'Large Sells ({len(sells)})',
            hovertemplate='<b>LARGE SELL</b><br>Price: $%{y:.2f}<br>Size: %{text} BTC<br>Time: %{x}<extra></extra>',
            text=[f'{size:.3f}' for size in sells['size']]
        ))
    
    # Add price trend for context
    if len(window_trades) > 1:
        window_trades = window_trades.set_index('timestamp')
        price_trend = window_trades['price'].resample('1min').mean()
        price_trend = price_trend.dropna()
        
        if len(price_trend) > 1:
            fig.add_trace(go.Scatter(
                x=price_trend.index,
                y=price_trend.values,
                mode='lines',
                line=dict(color='blue', width=1, dash='dot'),
                name='Price Trend',
                opacity=0.5
            ))
    
    fig.update_layout(
        title=f'Large Trades Only (≥{min_trade_size}BTC) - Last {time_window_minutes} Minutes',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        hovermode='closest',
        showlegend=True,
        height=400
    )
    
    return fig

def create_market_depth_chart(orderbooks, metrics):
    """Create market depth visualization"""
    if not orderbooks:
        return _create_empty_chart("Loading market depth...", "Market Depth - Loading...")
    
    orderbook = orderbooks[-1]
    
    if not orderbook.get('bids') or not orderbook.get('asks'):
        return _create_empty_chart("No depth data", "Market Depth")
    
    bids = orderbook['bids']
    asks = orderbook['asks']
    
    # Sort data
    bids_sorted = sorted(bids, key=lambda x: x[0], reverse=True)
    asks_sorted = sorted(asks, key=lambda x: x[0])
    
    bid_prices, bid_amounts = zip(*bids_sorted)
    ask_prices, ask_amounts = zip(*asks_sorted)
    
    # Calculate cumulative amounts
    bid_cumulative = np.cumsum(bid_amounts)
    ask_cumulative = np.cumsum(ask_amounts)
    
    fig = go.Figure()
    
    # Add bid depth
    fig.add_trace(go.Scatter(
        x=bid_cumulative,
        y=bid_prices,
        mode='lines',
        fill='tozerox',
        line=dict(color='green', width=2),
        fillcolor='rgba(0, 255, 0, 0.3)',
        name='Bid Depth'
    ))
    
    # Add ask depth
    fig.add_trace(go.Scatter(
        x=ask_cumulative,
        y=ask_prices,
        mode='lines',
        fill='tozerox',
        line=dict(color='red', width=2),
        fillcolor='rgba(255, 0, 0, 0.3)',
        name='Ask Depth'
    ))
    
    # Add current price line
    current_price = metrics.get('current_price', (bid_prices[0] + ask_prices[0]) / 2) if metrics else (bid_prices[0] + ask_prices[0]) / 2
    fig.add_hline(y=current_price, line_dash="dash", line_color="blue")
    
    # Calculate spread
    spread = ask_prices[0] - bid_prices[0]
    
    fig.update_layout(
        title=f'Market Depth | Spread: ${spread:.2f}',
        xaxis_title='Cumulative Size (BTC)',
        yaxis_title='Price (USD)',
        showlegend=True,
        height=400
    )
    
    return fig

def _create_empty_chart(message, title):
    """Create an empty chart with a message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, xanchor='center', yanchor='middle',
        showarrow=False,
        font=dict(size=16)
    )
    fig.update_layout(title=title)
    return fig