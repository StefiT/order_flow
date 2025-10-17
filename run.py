#!/usr/bin/env python3
"""
BTC Order Flow Analyzer - Production Ready
"""

from src.app import app
import warnings

warnings.filterwarnings('ignore')

if __name__ == '__main__':
    # For production use
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=False  # Set to False in production
    )
