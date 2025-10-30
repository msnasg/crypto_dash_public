# python -m venv env
# run & ./env/Scripts/Activate.ps1
# then pip install -r requirements.txt
import sys
import os
import websocket
# Add the parent directory (binance-trading-system) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
from datetime import datetime

from binance.client import Client
from dotenv import load_dotenv

import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from src.layout import create_layout
from dash import dash_table
import logging

# Logging
log_file = os.path.join(os.getcwd(), 'app.log')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file, 
                    filemode='a')  

logger = logging.getLogger(__name__)
logger.info('Starting the Trading Dashboard app')


app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Trading Dashboard",
    external_scripts=["https://s3.tradingview.com/tv.js"], 
)

app.layout = create_layout()

if __name__ == "__main__":
    app.run(debug=True)

# ------------------------------------------------------------------------------------- #
# Code tree format
# from pathlib import Path
# def print_tree(start_path, prefix="", exclude_dirs=None):
#     """
#     Print a directory tree starting from start_path, excluding specified directories.
#     """
#     exclude_dirs = exclude_dirs or ['env', '__pycache__']
#     start_path = Path(start_path)

#     def _print(dir_path, prefix=""):
#         entries = [p for p in sorted(dir_path.iterdir()) if p.name not in exclude_dirs]
#         entries_count = len(entries)

#         for i, path in enumerate(entries):
#             connector = "└── " if i == entries_count - 1 else "├── "
#             print(prefix + connector + path.name)

#             if path.is_dir():
#                 extension = "    " if i == entries_count - 1 else "│   "
#                 _print(path, prefix + extension)

#     print(start_path.name)
#     _print(start_path, prefix)

# # # Example usage
# if __name__ == "__main__":
#     print("Project Directory Structure:")
#     # Go to PowerShell or cmd and run: python app.py
#     # .\env\Scripts\activate
#     # python app.py
#     print_tree(r"D:\_Trading_Business\Python\crypto_dash")


# crypto_dash
# ├── .env
# ├── .gitignore
# ├── analytics
# │   ├── data_processing.py
# │   └── market_liquidity
# │       └── exchange_netflow.py
# ├── app.log
# ├── app.py
# ├── assets
# │   └── styles
# │       └── styles.css
# ├── config
# │   └── settings.py
# ├── data_sources
# │   └── dune_client.py
# ├── LICENSE
# ├── pages
# │   ├── __init__.py
# │   ├── home.py
# │   ├── on_chain_analysis.py
# │   ├── options_analysis.py
# │   ├── pair_analysis.py
# │   ├── portfolio.py
# │   ├── price_analysis.py
# │   ├── settings.py
# │   ├── signals.py
# │   ├── strategy.py
# │   ├── trade_assistant.py
# │   ├── trade_summary.py
# │   └── transactions.py
# ├── README.md
# ├── requirements.txt
# ├── src
# │   ├── layout.py
# │   ├── navbar.py
# │   └── sidebar.py
# └── utils
#     ├── binance_data.py
#     ├── helpers.py
#     ├── options_data.py
#     └── trading_functions.py