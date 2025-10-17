#!/usr/bin/env python3
"""
BTC Order Flow Analyzer - Main Entry Point
"""

from src.app import app
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    print("🚀 Starting BTC Order Flow Analyzer...")
    print("📊 Open your browser to: http://127.0.0.1:8050")
    print("💡 Waiting for initial data...")
    
    app.run(debug=True, host='127.0.0.1', port=8050)