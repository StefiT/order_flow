import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from .data_fetcher import OrderFlowData
from .chart_builder import (
    create_candlestick_with_profile,
    create_clean_delta_chart,
    create_large_trades_chart,
    create_market_depth_chart
)

# Initialize data manager
data_manager = OrderFlowData()

# Initialize Dash app
app = dash.Dash(__name__, title="BTC Order Flow Analyzer")

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("BTC/USDT Professional Order Flow Analyzer", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Advanced trading analysis with real-time order flow visualization", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '20px'}),
    ]),
    
    # Controls Panel
    html.Div([
        html.Div([
            html.Label("📅 Time Window:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='time-window',
                options=[
                    {'label': 'Last 15 minutes', 'value': 15},
                    {'label': 'Last 30 minutes', 'value': 30},
                    {'label': 'Last 1 hour', 'value': 60},
                    {'label': 'Last 2 hours', 'value': 120},
                ],
                value=30,
                style={'width': '200px'}
            ),
        ], style={'display': 'inline-block', 'marginRight': '20px'}),
        
        html.Div([
            html.Label("🔄 Update Frequency:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='update-frequency',
                options=[
                    {'label': '10 seconds', 'value': 10000},
                    {'label': '30 seconds', 'value': 30000},
                    {'label': '1 minute', 'value': 60000},
                    {'label': '5 minutes', 'value': 300000},
                ],
                value=30000,
                style={'width': '200px'}
            ),
        ], style={'display': 'inline-block', 'marginRight': '20px'}),
        
        html.Div([
            html.Label("💰 Min Trade Size (BTC):", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='trade-size-filter',
                min=0.1,
                max=5,
                step=0.1,
                value=1.0,
                marks={0.1: '0.1', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5'},
            ),
        ], style={'width': '300px', 'display': 'inline-block', 'marginRight': '20px'}),
        
        html.Button('🔄 Update Now', id='update-button', n_clicks=0,
                   style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 
                          'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer',
                          'fontWeight': 'bold'}),
        
    ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px', 'marginBottom': '20px'}),
    
    # Market Statistics
    html.Div(id="market-stats", style={
        'backgroundColor': '#ecf0f1', 
        'padding': '15px', 
        'borderRadius': '5px',
        'marginBottom': '20px',
        'fontSize': '16px',
    }),
    
    # Auto-update interval
    dcc.Interval(
        id='interval-component',
        interval=30000,
        n_intervals=0
    ),
    
    # Main Charts Grid
    html.Div([
        # Row 1: Price Analysis
        html.Div([
            dcc.Graph(
                id='candlestick-chart', 
                style={'height': '500px'},
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ], style={'width': '100%', 'padding': '10px', 'marginBottom': '20px'}),
        
        # Row 2: Delta Analysis
        html.Div([
            dcc.Graph(
                id='delta-chart', 
                style={'height': '400px'},
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ], style={'width': '100%', 'padding': '10px', 'marginBottom': '20px'}),
        
        # Row 3: Order Flow & Market Depth
        html.Div([
            html.Div([
                dcc.Graph(
                    id='large-trades-chart', 
                    style={'height': '400px'},
                    config={'displayModeBar': True, 'scrollZoom': True}
                )
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            
            html.Div([
                dcc.Graph(
                    id='market-depth-chart', 
                    style={'height': '400px'},
                    config={'displayModeBar': True, 'scrollZoom': True}
                )
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
        ]),
    ]),
    
    # Data Summary Footer
    html.Div(id="data-summary", style={
        'backgroundColor': '#f8f9fa', 
        'padding': '15px', 
        'borderRadius': '5px',
        'marginTop': '20px',
        'fontSize': '14px',
        'color': '#7f8c8d'
    }),
    
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'maxWidth': '1400px', 'margin': '0 auto'})

# Callback to update all charts
@app.callback(
    [Output('market-stats', 'children'),
     Output('candlestick-chart', 'figure'),
     Output('delta-chart', 'figure'),
     Output('large-trades-chart', 'figure'),
     Output('market-depth-chart', 'figure'),
     Output('data-summary', 'children'),
     Output('interval-component', 'interval')],
    [Input('interval-component', 'n_intervals'),
     Input('update-button', 'n_clicks')],
    [State('time-window', 'value'),
     State('update-frequency', 'value'),
     State('trade-size-filter', 'value')]
)
def update_dashboard(n_intervals, n_clicks, time_window, update_frequency, min_trade_size):
    # Fetch new data
    new_trades_count = data_manager.fetch_new_data()
    
    trades = data_manager.all_trades
    orderbooks = data_manager.orderbook_history
    
    metrics = data_manager.calculate_metrics(trades, time_window)
    
    # Update market stats
    stats_display = create_market_stats(metrics)
    
    # Update all charts
    candlestick_fig = create_candlestick_with_profile(trades, time_window)
    delta_fig = create_clean_delta_chart(trades, time_window)
    large_trades_fig = create_large_trades_chart(trades, time_window, min_trade_size)
    depth_fig = create_market_depth_chart(orderbooks, metrics)
    
    # Update data summary
    summary_text = create_data_summary(trades, min_trade_size, new_trades_count)
    
    return stats_display, candlestick_fig, delta_fig, large_trades_fig, depth_fig, summary_text, update_frequency

def create_market_stats(metrics):
    """Create market statistics display"""
    if not metrics:
        return html.Div("📡 Connecting to exchange...")
    
    return html.Div([
        html.Div([
            html.Span(f"💰 Current Price: ${metrics['current_price']:,.2f} ", 
                     style={'color': '#2c3e50', 'fontSize': '20px', 'fontWeight': 'bold'}),
            html.Span(f"({metrics.get('price_change_percent', 0):+.2f}%)", 
                     style={'color': 'green' if metrics.get('price_change_percent', 0) >= 0 else 'red', 
                            'fontSize': '16px'}),
        ]),
        html.Div([
            html.Span(f"📊 Total Volume: {metrics['total_volume']:.1f} BTC", 
                     style={'marginRight': '20px'}),
            html.Span(f"🟢 Buy Volume: {metrics['buy_volume']:.1f} BTC", 
                     style={'marginRight': '20px', 'color': 'green'}),
            html.Span(f"🔴 Sell Volume: {metrics['sell_volume']:.1f} BTC", 
                     style={'marginRight': '20px', 'color': 'red'}),
            html.Span(f"Δ Net Delta: {metrics['net_delta']:+.1f} BTC", 
                     style={'color': 'green' if metrics['net_delta'] >= 0 else 'red', 'fontWeight': 'bold'}),
        ], style={'marginTop': '10px'})
    ])

def create_data_summary(trades, min_trade_size, new_trades_count):
    """Create data summary footer"""
    if len(trades) == 0:
        return "🔄 Collecting initial market data..."
    
    total_trades = len(trades)
    large_trades_count = len(trades[trades['size'] >= min_trade_size])
    
    return html.Div([
        f"📈 Data Summary: {total_trades:,} total trades | ",
        f"{large_trades_count:,} large trades (≥{min_trade_size}BTC) | ",
        f"🔄 {new_trades_count} new trades | ",
        f"🕒 Last update: {data_manager.last_update.strftime('%H:%M:%S') if data_manager.last_update else 'N/A'}"
    ])