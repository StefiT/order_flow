#!/usr/bin/env python3
"""
BTC Order Flow Analyzer - Production Version for Render.com
"""

from app import app
import warnings
import os

warnings.filterwarnings('ignore')

def main():
    print("🚀 Starting BTC Order Flow Analyzer...")
    print("📊 Initializing application...")
    
    # Get port from environment variable (required for Render)
    port = int(os.environ.get("PORT", 8050))
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        dev_tools_ui=False,
        dev_tools_props_check=False
    )

if __name__ == '__main__':
    main()
