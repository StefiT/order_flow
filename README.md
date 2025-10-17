# BTC/USDT Order Flow Analyzer

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Dash](https://img.shields.io/badge/Dash-2.14.1-green.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.17.0-orange.svg)

A professional web-based order flow analysis tool for BTC/USDT trading pair. Visualize real-time market data, order flow, and liquidity analysis in a TradingView-style interface.

## 🚀 Features

- **📊 Real-time Price Charts**: Candlestick charts with volume profile
- **🔍 Order Flow Analysis**: Delta analysis and cumulative delta tracking
- **💰 Large Trade Detection**: Filter and visualize significant market moves
- **📈 Market Depth**: Real-time bid/ask spread visualization
- **⚡ Interactive Interface**: Zoom, pan, and hover for detailed analysis
- **🔄 Live Updates**: Configurable update frequency (10s to 5min)

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/btc-order-flow-analyzer.git
   cd btc-order-flow-analyzer
   
 
##Usage Guide
Dashboard Overview
The application consists of four main sections:

Price Chart with Volume Profile

Left: Real-time candlestick chart

Right: Volume profile showing trading activity at price levels

Delta Analysis

Blue line: Cumulative delta (net buying pressure)

Background bars: 1-minute delta values

Green/red coloring for buy/sell pressure

Large Trades Visualization

Green triangles: Large buy orders

Red triangles: Large sell orders

Marker size indicates trade size

Market Depth

Green area: Buy orders (bids)

Red area: Sell orders (asks)

Blue line: Current market price

Controls
Time Window: Select historical period (15min to 2 hours)

Update Frequency: Set data refresh rate (10s to 5min)

Min Trade Size: Filter for significant trades (0.1 to 5 BTC)

Update Now: Manual refresh button

Interacting with Charts
Zoom: Use mouse wheel or touchpad

Pan: Click and drag to move around

Hover: See detailed information for any data point

Reset View: Double-click to reset zoom

## Key Components
Data Fetcher: Handles real-time data from Binance exchange

Chart Builder: Creates interactive Plotly visualizations

Dash App: Web framework for the user interface


## Key Features Summary:
🎯 Professional Interface: TradingView-style layout

📊 Multiple Chart Types: Candlesticks, volume profile, delta, market depth

⚡ Real-time Data: Live updates from Binance exchange

🔧 Customizable: Adjustable timeframes, update frequencies, trade filters

📱 Interactive: Zoom, pan, hover tooltips

🏗 Modular Architecture: Clean, organized code structure

📚 Comprehensive Documentation: Easy setup and usage instructions