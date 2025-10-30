# pages/trade-assistant.py

import dash
from dash import html, dcc, Output, Input, State, dash_table, callback
import dash_bootstrap_components as dbc
import pandas as pd
from utils.binance_data import get_recent_trades, fetch_data_binance, fetch_data_binance_candles
from config.settings import default_symbols
from utils import trading_functions as tf
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# for large transactions monitoring
import websocket
import json
import requests
from datetime import datetime
import pytz
from threading import Thread, Lock
import plotly.express as px


dash.register_page(__name__, path="/trade-assistant")

# --- UI Config ---
TABLE_HEIGHT = "410px"
FONT_SIZE = "15px"
CELL_PADDING = "10px"
REFRESH_INTERVAL = 10 * 1000
timeframes = {"Trigger": "5m", "Pattern": "15m", "Master": "1h"}

# Lock for thread safety
tx_data_lock = Lock()

# Shared list to store large transactions (persists across tab switches)
tx_data_list = []

# Shared list to store notifications for special transactions (>1000 BTC)
notification_list = []

# Global variable to control WebSocket monitoring (persists across tab switches)
global_monitoring_active = [True]  # Using a list to allow modification in WebSocket thread

# Supported symbols (currently only BTC, can be expanded)
supported_symbols = ['BTC']  # Placeholder for future expansion


def get_base_symbol(full_symbol: str) -> str:
    """Derive base symbol from pair-like symbol strings.

    Examples:
      BTCUSDC -> BTC
      ETHUSDT -> ETH
      BTC/USDT -> BTC
    """
    if not full_symbol or not isinstance(full_symbol, str):
        return 'BTC'
    # Remove common separators and split
    for sep in ['/', '-', '_']:
        if sep in full_symbol:
            return full_symbol.split(sep)[0]
    # If symbol ends with known quote currencies, strip them
    for quote in ['USDT', 'USDC', 'BTC', 'USD', 'EUR']:
        if full_symbol.endswith(quote):
            return full_symbol[: -len(quote)]
    # Fallback: return original
    return full_symbol

# ----------------------------- Global Settings Panel -----------------------------
global_settings = html.Div(
    [
        dbc.Button("⚙", id="open-settings-btn", className="btn btn-dark"), 
        dbc.Collapse(
            dbc.Card(
                dbc.CardBody([
                    #html.H5("Global Parameters", className="mb-3", style={"color": "white"}),
                    # html.Label("Default Symbols", style={"color": "white"}),
                    dbc.Row([
                    dbc.Col([
                        html.Label("Select symbols"),
                        dcc.Dropdown(
                            options=[{'label': sym, 'value': sym} for sym in default_symbols],
                            value=['BTCUSDC', 'BNBUSDC', 'SOLUSDC', 'LTCUSDC','ETHUSDC', 'DOGEUSDC', 'ADAUSDC', 'XRPUSDC'],
                            multi=True,
                            id='trade-symbol-dropdown',
                            placeholder="Choose symbols",
                            style={
                                    'border': '1px solid white',     # ✅ رنگ سفید دور کادر
                                    'borderRadius': '8px',           # گوشه‌های گرد (اختیاری)
                                    'backgroundColor': '#1e1e2f',    # رنگ پس‌زمینه تیره برای کنتراست (اختیاری)
                                    'color': 'white'                 # رنگ نوشته‌ها
                                }
                        )
                    ], width=9),
                    dbc.Col([
                        html.Label("Signal symbol"),
                        dcc.Dropdown(
                            id="signal-symbol-dropdown",
                            options=[{"label": s, "value": s} for s in default_symbols],
                            value=default_symbols[0],
                            clearable=False,
                            style={
                                    'border': '1px solid white',     # ✅ رنگ سفید دور کادر
                                    'borderRadius': '8px',           # گوشه‌های گرد (اختیاری)
                                    'backgroundColor': '#1e1e2f',    # رنگ پس‌زمینه تیره برای کنتراست (اختیاری)
                                    'color': 'white'                 # رنگ نوشته‌ها
                                }
                        )
                    ], width=3)
                    ]),                    
                    html.Br(),
                     # --- Inputs ---
                    dbc.Row([
                        # ---- Number of recent trades ----
                        dbc.Col(
                            [
                                html.Label(
                                    "Number of recent trades",
                                    htmlFor="trade-limit-input",
                                    style={
                                        "color": "white",
                                        "fontSize": "14px",
                                        "marginBottom": "6px",
                                        "display": "block",
                                        "fontWeight": "500",
                                    },
                                ),
                                dcc.Input(
                                    id="trade-limit-input",
                                    type="number",
                                    value=500,
                                    min=50,
                                    max=1000,
                                    step=50,
                                    className="custom-input",  # ✅ استایل از CSS مشترک
                                ),
                            ],
                            width=3,
                        ),

                        # ---- Top trades count for avg ----
                        dbc.Col(
                            [
                                html.Label(
                                    "Top trades count for avg",
                                    htmlFor="trade-head-input",
                                    style={
                                        "color": "white",
                                        "fontSize": "14px",
                                        "marginBottom": "6px",
                                        "display": "block",
                                        "fontWeight": "500",
                                    },
                                ),
                                dcc.Input(
                                    id="trade-head-input",
                                    type="number",
                                    value=20,
                                    min=5,
                                    max=100,
                                    step=5,
                                    className="custom-input",
                                ),
                            ],
                            width=3,
                        ),

                        # ---- Update interval ----
                        dbc.Col(
                            [
                                html.Label(
                                    "Update interval (seconds)",
                                    htmlFor="trade-interval-input",
                                    style={
                                        "color": "white",
                                        "fontSize": "14px",
                                        "marginBottom": "6px",
                                        "display": "block",
                                        "fontWeight": "500",
                                    },
                                ),
                                dcc.Input(
                                    id="trade-interval-input",
                                    type="number",
                                    value=10,
                                    min=2,
                                    max=120,
                                    step=2,
                                    className="custom-input",
                                ),
                            ],
                            width=3,
                        ),
                    ],
                    className="g-3",  # ✅ فاصله بین ستون‌ها
                ),
                html.Br(),
                # --- Large Transactions parameters moved to global settings ---
                dbc.Row([
                    dbc.Col([
                        html.Label("Large Tx Threshold", style={'color': 'white'}),
                        dcc.Input(
                            id='threshold-input',
                            type='number',
                            value=500,
                            min=1,
                            step=1,
                            className="custom-input",
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Monitoring", style={'color': 'white'}),
                        dcc.RadioItems(
                            options=[
                                {'label': 'Active', 'value': True},
                                {'label': 'Inactive', 'value': False}
                            ],
                            value=global_monitoring_active[0],
                            id='monitoring-toggle',
                            labelStyle={'display': 'inline-block', 'marginRight': '10px', 'marginTop': '10px','color': 'white'}
                        )
                    ], width=4)
                ], className="mb-3"),
                ]),
                # Make the card fill the available column width
                style={"backgroundColor": "#1e1e2f", "border": "1px solid #444", "width": "100%"}
            ),
            id="settings-collapse",
            is_open=False,
        )
    ],
    style={'backgroundColor': '#1e1e2f', 'padding': '20px'}
)

# --- UI ---
layout = html.Div([
    dbc.Container([
        # html.H2("Trading Assistant", className="my-3 text-center"),               
        # # --- Dropdowns ---
        # Title and settings button on the same row. Title on left, settings controls on right.


        # dbc.Row([
        #     dbc.Col(
        #         html.H2("Trading Assistant", className="my-0", style={"color": "white", "marginTop": "6px", "marginBottom": "0"}),
        #         width=3)
        #          ], className="mb-4"),
            
        #     dbc.Row([                
        #         dbc.Col(global_settings, width=9, style={"textAlign": "left"}) ,
        #     ], className="mb-4"),

        dbc.Row([
            dbc.Col(
                html.Div(
                    html.H2("Crypto Trading Assistant (Binance API)", className="my-0", style={"color": "white", "marginTop": "6px", "marginBottom": "0"})
                ),
                width=3,
                #     style={"display": "flex", "alignItems": "center", "textAlign": "left"}
            ),
            dbc.Col(
                html.Div(global_settings, style={"display": "flex", "justifyContent": "flex-end", "width": "100%"}),
                width=9,
                #style={"textAlign": "right", "display": "flex", "alignItems": "center", "justifyContent": "flex-end", "width": "100%"}
            ),
        ], className="mb-4"),            

        # ------
        dbc.Row([
            dbc.Col([
                html.H4("Volume", className="mt-4"),
                html.Div(id="trade-summary-table"),
                html.Br(),
                # --- نمودار کندل استیک تعاملی ---              
                #html.H4(id="chart-title", className="mt-4"), #   
                # html.H4("Chart (Last 100, 5m)", className="mt-4"),
                html.H4("Multi Time Frames", className="mt-4"),  # NEW: عنوان کوچکتر کردم
                # dcc.Graph(id="candlestick-graph", style={"height": "350px"}),
                
                # ردیف اول: دو نمودار
                dbc.Row([
                    dbc.Col(dcc.Graph(id="candlestick-graph_1", style={"height": "400px"}), width=6),
                    dbc.Col(dcc.Graph(id="candlestick-graph_2", style={"height": "400px"}), width=6),
                ], className="mb-4"),  # فاصله پایین ردیف
                html.Br(),
                # ردیف دوم: دو نمودار دیگر
                dbc.Row([
                    dbc.Col(dcc.Graph(id="candlestick-graph_3", style={"height": "400px"}), width=6),
                    dbc.Col(dcc.Graph(id="candlestick-graph_4", style={"height": "400px"}), width=6),
                ], className="mb-4"),

                dcc.Interval(id="trade-update-interval", interval=REFRESH_INTERVAL, n_intervals=0)
            ], width=6, style={"paddingRight": "10px"}),

            dbc.Col([
                html.H4(id="signal-table-title", children=f"Signals: {default_symbols[0]}", className="mt-4"),
                dash_table.DataTable(
                    id="signal-analysis-table",
                    data=[],
                    columns=[],
                    style_table={
                        "overflowX": "auto",
                        "overflowY": "auto",
                        "height": TABLE_HEIGHT,
                        "minWidth": "100%"
                    },
                    # force fixed row height/line-height to keep tables aligned
                    style_cell={
                        "backgroundColor": "#1e1e2f",
                        "color": "white",
                        "textAlign": "center",
                        "padding": CELL_PADDING,
                        "border": "1px solid #444",
                        "fontSize": FONT_SIZE,
                        "whiteSpace": "normal",
                        "height": "40px",
                        "lineHeight": "20px",
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                    },
                    style_header={
                        "fontWeight": "bold", 
                        "backgroundColor": "#333", 
                        "color": "white"
                        },
                         # ----------------------------------------------------
                        # اضافه کردن قوانین استایل‌دهی شرطی (Conditional Styling)
                        # ----------------------------------------------------
                        style_data_conditional=(
                            # 1. Style the signal column header cells
                            [{'if': {'column_id': 'signal'},
                              'fontWeight': 'bold',
                              'color': '#aaaaaa',
                              'textAlign': 'right'}]

                            # 2. RSI: RED when >70
                            + [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "RSI (14)" && {' + c + '} > 70'
                                    },
                                    #'backgroundColor': '#F6465D',
                                    'color': '#F6465D'
                                } for c in timeframes.keys()
                            ]

                            # RSI: GREEN when <30
                            + [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "RSI (14)" && {' + c + '} < 30'
                                    },
                                    #'backgroundColor': '#00C176',
                                    'color': '#00C176'
                                } for c in timeframes.keys()
                            ]

                            # Regression Bands: Above -> RED, Below -> GREEN
                            + [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "Regr. Bands" && {' + c + '} = "Above"'
                                    },
                                    #'backgroundColor': '#F6465D',
                                    'color': '#F6465D'
                                } for c in timeframes.keys()
                            ]
                            + [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "Regr. Bands" && {' + c + '} = "Below"'
                                    },
                                    #'backgroundColor': '#00C176',
                                    'color': '#00C176'
                                } for c in timeframes.keys()
                            ]

                            # Donchian: several positive/negative keywords grouped
                            + [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "Donchian (48)" && ({' + c + '} = "Below" || {' + c + '} = "Lower" || {' + c + '} = "Bottom")'
                                    },
                                    #'backgroundColor': '#00C176',
                                    'color': '#00C176'
                                } for c in timeframes.keys()
                            ]
                            + [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "Donchian (48)" && ({' + c + '} = "Above" || {' + c + '} = "Upper" || {' + c + '} = "Top")'
                                    },
                                    'backgroundColor': '#F6465D',
                                    'color': 'white'
                                } for c in timeframes.keys()
                            ]
                            # VWAP Above & Below
                            + [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "VWAP Bands" && {' + c + '} = "Above"'
                                    },
                                    #'backgroundColor': '#F6465D',
                                    'color': '#F6465D'
                                } for c in timeframes.keys()
                            ] 
                            + [
                                {  
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "VWAP Bands" && {' + c + '} = "Below"'
                                    },
                                    #'backgroundColor': '#00C176',
                                    'color': '#00C176'
                                } for c in timeframes.keys() 
                            ]
                            # Z-Score (20) > 1.5 RED & Z-Score (20) < -1.5 GREEN
                            + [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "Z-Score (20)" && {' + c + '} > 1.5'
                                    },
                                    'color': '#F6465D'
                                } for c in timeframes.keys()
                            ] +
                            [
                                {
                                    'if': {
                                        'column_id': c,
                                        'filter_query': '{signal} = "Z-Score (20)" && {' + c + '} < -1.5'
                                    },
                                    'color': '#00C176'
                                } for c in timeframes.keys()
                            ]


                        ),
                        # ----------------------------------------------------
                        # پایان قوانین استایل‌دهی شرطی
                        # ----------------------------------------------------
                ),
                html.Br(),
                # --- Large Transactions Section ---        
                html.H4("Large Transactions", className="mt-4"),
                # html.P("This page displays large Bitcoin transactions detected in real-time.", style={'color': '#ffffff'}),
                dcc.Interval(id="update-interval", interval=10*1000, n_intervals=0),  # Update every 10 seconds
                dcc.Interval(id="notification-interval", interval=5*1000, n_intervals=0),  # Check for notification expiration every 5 seconds
                dcc.Store(id="large-transactions-store", data={"transactions": [], "threshold": 50}),
                html.Div(id="notifications-container", style={'marginBottom': '20px'}),  # Container for notifications
                dcc.Graph(id="large-transactions-chart", style={'height': '400px'}),  # Chart above the table (small until data arrives)
                html.Div(id="large-transactions-table"),
                html.Div(id="error-message", style={'color': '#ff0000'})

            ], width=6, style={"paddingLeft": "10px"}),
        ], style={"display": "flex", "align-items": "stretch"}, className="mb-4"),

        
         # NEW: Row جدید برای بخش معاملات بزرگ (گوشه پایین سمت راست)
        # dbc.Row([
        #     dbc.Col(width=6),  # فضای خالی سمت چپ برای offset
        #     dbc.Col([
           
        #         dcc.Interval(id="update-interval", interval=10*1000, n_intervals=0),  # Update every 10 seconds
        #         dcc.Interval(id="notification-interval", interval=5*1000, n_intervals=0),  # Check for notification expiration every 5 seconds
        #         dcc.Store(id="large-transactions-store", data={"transactions": [], "threshold": 50}),
        #         html.Div(id="notifications-container", style={'marginBottom': '20px'}),  # Container for notifications
        #         dcc.Graph(id="large-transactions-chart", style={'height': '100px'}),  # Chart above the table (small until data arrives)
        #         html.Div(id="large-transactions-table"),
        #         html.Div(id="error-message", style={'color': '#ff0000'})
        #     ], width=6, style={"paddingLeft": "10px"}),  # NEW: width=6 برای سمت راست
        # ], className="mb-4"),  # NEW: Row جدید


        # dbc.Row([
        #     dbc.Col([
        #         html.Label("Indicator on Candle"),
        #         dcc.Dropdown(
        #             id="candle-indicator-dropdown",
        #             options=[
        #                 {"label": "None", "value": "none"},
        #                 {"label": "Regression Bands", "value": "regression"},
        #                 {"label": "Bollinger Bands", "value": "bollinger"},
        #             ],
        #             value="none",
        #             clearable=False
        #         ),
        #     ], width=6),
        #     dbc.Col([
        #         html.Label("Indicator below Candle"),
        #         dcc.Dropdown(
        #             id="subchart-indicator-dropdown",
        #             options=[
        #                 {"label": "None", "value": "none"},
        #                 {"label": "RSI", "value": "rsi"},
        #                 {"label": "MACD", "value": "macd"},
        #                 {"label": "Volume", "value": "volume"},
        #             ],
        #             value="rsi",
        #             clearable=False
        #         ),
        #     ], width=6),
        # ], className="mb-2"),

        
    ], fluid=True)
], style={'backgroundColor': '#1e1e2f', 'padding': '20px',  "minHeight": "100vh"})


# ----------------------------- CALLBACKS -----------------------------
@callback(
    Output("settings-collapse", "is_open"),
    Input("open-settings-btn", "n_clicks"),
    State("settings-collapse", "is_open"),
)
def toggle_settings_panel(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("chart-title", "children"),
    Input("signal-symbol-dropdown", "value")
)
def update_chart_title(symbol):
    return f"{symbol} (5m, Last 100 Candles)"
# -------------------- Callbacks --------------------

@callback(
    Output("trade-summary-table", "children"),
    Output("trade-update-interval", "interval"),
    Input("trade-update-interval", "n_intervals"),
    State("trade-symbol-dropdown", "value"),
    State("trade-limit-input", "value"),
    State("trade-head-input", "value"),
    State("trade-interval-input", "value"),
)
def update_trade_summary(n, selected_symbols, limit_sort, head_show, interval_sec):
    if not selected_symbols:
        return html.Div("Please select at least one symbol.", className="text-danger"), interval_sec * 1000

    rows = []
    for symbol in selected_symbols:
        trades = get_recent_trades(symbol, limit=limit_sort)
        if not trades:
            continue

        df = pd.DataFrame(trades)
        df['qty'] = pd.to_numeric(df['qty'], errors='coerce')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['direction'] = df['isBuyerMaker'].map({True: 'Sell', False: 'Buy'})

        buy_volume = df.loc[df['direction'] == 'Buy', 'qty'].sum()
        sell_volume = df.loc[df['direction'] == 'Sell', 'qty'].sum()

        top_df = df.sort_values(by='qty', ascending=False).head(head_show)
        avg_buy = top_df.loc[top_df['direction'] == 'Buy', 'qty'].mean()
        avg_sell = top_df.loc[top_df['direction'] == 'Sell', 'qty'].mean()

        signals = []
        if buy_volume > sell_volume:
            signals.append("🟢⬆ Total")
        else:
            signals.append("🔴⬇ Total")

        if (avg_buy if pd.notna(avg_buy) else 0) > (avg_sell if pd.notna(avg_sell) else 0):
            signals.append("🟢⬆ Avg")
        else:
            signals.append("🔴⬇ Avg")

        signal_str = " | ".join(signals)

        rows.append({
            "Symbol": symbol,
            f"Total Buy ({limit_sort})": round(buy_volume, 2),
            f"Total Sell ({limit_sort})": round(sell_volume, 2),
            f"Avg Top {head_show} Buys": round(avg_buy, 2) if pd.notna(avg_buy) else 0,
            f"Avg Top {head_show} Sells": round(avg_sell, 2) if pd.notna(avg_sell) else 0,
            "Signal": signal_str
        })

    if not rows:
        return html.Div("No data available.", className="text-warning"), interval_sec * 1000

    df_out = pd.DataFrame(rows)
    return dash_table.DataTable(
        data=df_out.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df_out.columns],
        style_table={
            "overflowX": "auto",
            "overflowY": "auto",
            "lineHeight": "1.2em",  # یا "20px" برای فیکس دقیق‌تر
            "height": TABLE_HEIGHT,
            "minWidth": "100%"
        },
        # force fixed row height/line-height to keep tables aligned with signal table
        style_cell={
            "backgroundColor": "#1e1e2f",
            "color": "white",
            "textAlign": "center",
            "padding": CELL_PADDING,
            "border": "1px solid #444",
            "fontSize": FONT_SIZE,
            "whiteSpace": "normal",
            "height": "40px",
            "lineHeight": "20px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        style_header={
            "fontWeight": "bold",
            "backgroundColor": "#333",
            "color": "white",
            "border": "1px solid #444"
        }
    ), interval_sec * 1000


# --- Callback برای آپدیت عنوان جدول سمت راست ---
@callback(
    Output("signal-table-title", "children"),
    Input("signal-symbol-dropdown", "value")
)
def update_signal_title(symbol):
    return f"Signals: {symbol}"


@callback(
    Output("signal-analysis-table", "data"),
    Output("signal-analysis-table", "columns"),
    Input("trade-update-interval", "n_intervals"),
    State("signal-symbol-dropdown", "value"),
)

# def update_signal_table(n, symbol):
#     dfs = {key: fetch_data_binance(symbol, tfreq, lookback_days=10) for key, tfreq in timeframes.items()}

#     rows = []

#     reg_results = {}
#     for key, df in dfs.items():
#         df_reg = tf.calculate_regression_bands(df, window=100)
#         pos = tf.check_band_position(df_reg, "regression")
#         reg_results[key] = "Above" if pos["above_upper"] else "Below" if pos["below_lower"] else "Inside"
#     rows.append({"Signal": "Regr. Bands", **reg_results})

#     slope_results = {}
#     for key, df in dfs.items():
#         df_reg = tf.calculate_regression_bands(df, window=100)
#         slope = df_reg["reg_slope"].iloc[-1]
#         slope_results[key] = f"{slope:.5f}"
#     rows.append({"Signal": "Regr. Slope", **slope_results})

#     donchian_results = {}
#     for key, df in dfs.items():
#         df_dc = tf.calculate_donchian_channel(df, window=48)
#         donchian_results[key] = tf.donchian_position_relative_to_middle(df_dc)
#     rows.append({"Signal": "Donchian (48)", **donchian_results})

#     vwap_results = {}
#     for key, df in dfs.items():
#         df_vwap = tf.calculate_vwap_bands(df)
#         pos = tf.check_band_position(df_vwap, "vwap")
#         vwap_results[key] = "Above" if pos["above_upper"] else "Below" if pos["below_lower"] else "Inside"
#     rows.append({"Signal": "VWAP Bands", **vwap_results})

#     rsi_results = {}
#     for key, df in dfs.items():
#         rsi_val = tf.rsi_sma(df, 14).iloc[-1]
#         rsi_results[key] = f"{rsi_val:.2f}"
#     rows.append({"Signal": "RSI (14)", **rsi_results})

#     zscore_results = {}
#     for key, df in dfs.items():
#         zs = tf.z_score(df, column="close", window=20).iloc[-1]
#         zscore_results[key] = f"{zs:.2f}"
#     rows.append({"Signal": "Z-Score (20)", **zscore_results})

#     nvi_results = {}
#     for key, df in dfs.items():
#         _, _, status = tf.nvi(df)
#         nvi_results[key] = status
#     rows.append({"Signal": "NVI", **nvi_results})

#     macd_results = {}
#     for key, df in dfs.items():
#         _, _, hist, trend, hist_trend = tf.macd(df)
#         macd_results[key] = f"{trend} | {hist_trend} ({hist.iloc[-1]:.2f})"
#     rows.append({"Signal": "MACD", **macd_results})

#     df = pd.DataFrame(rows)
#     columns = [{"name": f"{key} ({timeframes[key]})" if key in timeframes else key, "id": key} for key in df.columns]

#     return df.to_dict("records"), columns


def update_signal_table(n, symbol):
    dfs = {key: fetch_data_binance(symbol, tfreq, lookback_days=10) for key, tfreq in timeframes.items()}
    
    rows = []
    # Dictionaries to hold results for different timeframes
    reg_results, slope_results, donchian_results, vwap_results, rsi_results, zscore_results, nvi_results, macd_results = {}, {}, {}, {}, {}, {}, {}, {}

    for key, df in dfs.items():
        if df.empty:
            continue
            
        # Calculation Logic (using mock or real tf functions)
        df_reg = tf.calculate_regression_bands(df, window=100)
        pos = tf.check_band_position(df_reg, "regression")
        reg_results[key] = "Above" if pos["above_upper"] else "Below" if pos["below_lower"] else "Inside"
        slope_results[key] = f"{df_reg['reg_slope'].iloc[-1]:.2f}"
        
        df_dc = tf.calculate_donchian_channel(df, window=48)
        # خروجی‌های Donchian: Upper, Lower, Middle
        donchian_results[key] = tf.donchian_position_relative_to_middle(df_dc) 

        df_vwap = tf.calculate_vwap_bands(df)
        pos_vwap = tf.check_band_position(df_vwap, "vwap")
        vwap_results[key] = "Above" if pos_vwap["above_upper"] else "Below" if pos_vwap["below_lower"] else "Inside"
        
        # 🟢 تغییر: بازگرداندن مقدار RSI به صورت Float برای فعال کردن مقایسه عددی در استایل‌دهی شرطی
        rsi_results[key] = round(tf.rsi_sma(df, 14).iloc[-1] ,2)
        
        zscore_results[key] = round(tf.z_score(df, column='close', window=20).iloc[-1],2)
        
        _, _, status = tf.nvi(df)
        nvi_results[key] = status
        
        _, _, hist, trend, hist_trend = tf.macd(df)
        macd_results[key] = f"{trend} | {hist_trend} ({hist.iloc[-1]:.2f})"


    # Formatting the output table rows
    rows = [
        {"signal": "Regr. Bands", **reg_results},
        {"signal": "Regr. Slope", **slope_results},
        {"signal": "Donchian (48)", **donchian_results},
        {"signal": "VWAP Bands", **vwap_results},
        {"signal": "RSI (14)", **rsi_results},
        {"signal": "Z-Score (20)", **zscore_results},
        {"signal": "NVI", **nvi_results},
        {"signal": "MACD", **macd_results},
    ]

    df = pd.DataFrame(rows)
    # 🔴 تغییر: ID ستون اصلی را به 'signal' (با s کوچک) تغییر می‌دهیم.
    # این برای Filter Query در style_data_conditional ضروری است.
    df = df.rename(columns={'Signal': 'signal'}) 
    
    # ساختار Columns برای DataTable
    columns = [{"name": "Signal", "id": "signal"}]
    # اضافه کردن ID برای ستون‌های داده
    columns.extend([{"name": f"{key} ({timeframes.get(key, key)})", "id": key} for key in timeframes.keys()])


    return df.to_dict("records"), columns
# -------------------- Callbacks --------------------

# @callback(
#     Output("candlestick-graph", "figure"),
#     Input("signal-symbol-dropdown", "value"),
#     Input("trade-update-interval", "n_intervals"),  # اگر نمی‌خوای اتومات آپدیت بشه، این ورودی رو حذف کن
# )


# کال‌بک چهار نمودار برای 4 سیمبل
@callback(
    Output("candlestick-graph_1", "figure"),
    Output("candlestick-graph_2", "figure"),
    Output("candlestick-graph_3", "figure"),
    Output("candlestick-graph_4", "figure"),
    # Input("trade-symbol-dropdown", "value"),  # فرض می‌کنیم اینجا لیست 4 سیمبل میده
    Input("signal-symbol-dropdown", "value"), 
    Input("trade-update-interval", "n_intervals")
)
def update_all_candlesticks(symbols, n):
    # اگر کاربر کمتر از 4 سیمبل انتخاب کرده باشه، بقیه رو None قرار بده
    if not isinstance(symbols, list):
        symbols = [symbols]
    while len(symbols) < 4:
        symbols.append(None)
    
    # Multi Symbol
    # fig1 = update_candlestick_figure(symbols[0], '1m', n) if symbols[0] else go.Figure()
    # fig2 = update_candlestick_figure(symbols[1], '1m', n) if symbols[1] else go.Figure()
    # fig3 = update_candlestick_figure(symbols[2], '1m', n) if symbols[2] else go.Figure()
    # fig4 = update_candlestick_figure(symbols[3], '1m', n) if symbols[3] else go.Figure()
    
    # Multi TF
    fig1 = update_candlestick_figure(symbols[0], '1m', n) if symbols[0] else go.Figure()
    fig2 = update_candlestick_figure(symbols[0], '5m', n) if symbols[0] else go.Figure()
    fig3 = update_candlestick_figure(symbols[0], '15m', n) if symbols[0] else go.Figure()
    fig4 = update_candlestick_figure(symbols[0], '1h', n) if symbols[0] else go.Figure()

    return fig1, fig2, fig3, fig4



def update_candlestick_figure(symbol, timeframe, n_intervals):

    lookback_candles=100 
    #timeframe = "1m"
    # --- دریافت دیتا ---
    try:
        df = fetch_data_binance_candles(symbol, timeframe = timeframe, lookback_days = 5, lookback_candles = lookback_candles)
    except Exception as e:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark")
        fig.add_annotation(text=f"Error fetching data: {e}", xref="paper", yref="paper", showarrow=False)
        return fig

    if df is None or df.empty:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark")
        fig.add_annotation(text="No data available", xref="paper", yref="paper", showarrow=False)
        return fig

    # --- تضمین DatetimeIndex ---
    try:
        if not isinstance(df.index, pd.DatetimeIndex):
            # اگر timestamp ستون هست، از اون استفاده کن، وگرنه سعی کن ایندکس رو به datetime تبدیل کنی
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
                df.set_index("timestamp", inplace=True)
            elif "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"], utc=True)
                df.set_index("time", inplace=True)
            else:
                # آخرین تلاش: تبدیل ایندکس فعلی به datetime (ممکنه string باشه)
                df.index = pd.to_datetime(df.index, utc=True)
    except Exception as e:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark")
        fig.add_annotation(text=f"Datetime parse error: {e}", xref="paper", yref="paper", showarrow=False)
        return fig

    # --- تضمین ستون‌های OHLC هستند و عددی ---
    for col in ["open", "high", "low", "close"]:
        if col not in df.columns:
            alt = col.capitalize()
            if alt in df.columns:
                df[col] = pd.to_numeric(df[alt], errors="coerce")
            else:
                fig = go.Figure()
                fig.update_layout(template="plotly_dark")
                fig.add_annotation(text=f"Missing column: {col}", xref="paper", yref="paper", showarrow=False)
                return fig
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # حذف ردیف‌های ناقص
    df = df.dropna(subset=["open", "high", "low", "close"])
    if df.empty:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark")
        fig.add_annotation(text="No valid OHLC rows after cleaning", xref="paper", yref="paper", showarrow=False)
        return fig

    # --- ساخت کندل استیک ساده ---
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name=symbol,
                increasing_line_color="#00B894",
                decreasing_line_color="#FF6B6B",
                showlegend=False
            )
        ]
    )

    # --- تنظیمات ظاهری (بدون range slider) ---
    fig.update_layout(
        #title_text=f"{symbol} ({timeframe})" if symbol else "No Symbol",
        title_text=f"{timeframe}" if symbol else "No Symbol",
        template="plotly_dark",
        plot_bgcolor='#1e1e2f',  # مثلاً "white" یا "#000000"
        paper_bgcolor='#1e1e2f',  # مثلاً "white" یا "#000000"
        xaxis_rangeslider_visible=False,  # اسلایدر حذف شد
        margin=dict(l=10, r=10, t=40, b=20),
        yaxis_title="Price",
        # height=450
    )
    fig.update_xaxes(type="date", showspikes=True)
    fig.update_yaxes(showgrid=True)

    return fig

# Large Transactions Monitoring Globals


# Function to fetch the current Bitcoin price in USD
def get_btc_price():
    """Fetch the current Bitcoin price from CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'bitcoin' in data and 'usd' in data['bitcoin']:
                return data['bitcoin']['usd']
            else:
                #print("Error: 'bitcoin' or 'usd' not found in the response.")
                return None
        elif response.status_code == 429:
            #print("Error: Rate limit exceeded (429).")
            return None
        else:
            #print(f"Error: Failed to fetch data (Status code: {response.status_code})")
            return None
    except requests.RequestException as e:
        #print(f"Error fetching BTC price: {e}")
        return None

# Function to analyze transactions and generate trading signals
def analyze_transaction(input_addresses, output_addresses, btc_value, num_inputs, num_outputs):
    """Analyze transaction characteristics and return a trading signal."""
    signal = "Neutral"
    if btc_value > 1000 and num_inputs <= 2 and num_outputs <= 2:
        signal = "Whale Move - Potential HODL or Dump"
    elif num_inputs > 5 and len(output_addresses) == 1:
        signal = "Possible Exchange Deposit - Selling Pressure?"
    elif num_inputs < 3 and num_outputs > 10:
        signal = "Distribution - Potential Sell-Off"
    return signal

# WebSocket message handler
def on_message(ws, message, threshold=50):
    """Process incoming WebSocket messages and handle large transactions."""
    #print("Received WebSocket message:", message)  # Debug print to check if messages are received
    if not global_monitoring_active[0]:  # Check global monitoring state
        return  # Skip processing if monitoring is not active

    try:
        data = json.loads(message)
    except json.JSONDecodeError as e:
        #print(f"Error decoding JSON: {e}")
        return

    if "x" not in data:  # Check if the message contains transaction data
        #print("No 'x' key in message:", data)
        return

    tx = data["x"]
    tx_hash = tx.get("hash", "N/A")
    tx_value = sum(out.get("value", 0) for out in tx.get("out", []))  # Total value in satoshis
    btc_value = tx_value / 10**8  # Convert to BTC
    #print(f"Transaction value: {btc_value} BTC")  # Debug print
    if btc_value < threshold:
        #print(f"Transaction value {btc_value} BTC is below threshold {threshold} BTC")
        return  # Skip transactions below the threshold

    # Check for special transactions (>1000 BTC) and create notification
    if btc_value > 1000:
        notification = {
            "time": datetime.now(pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "message": f"⚠️ Special Transaction Detected: {btc_value:.2f} BTC",
            "timestamp": datetime.now().timestamp()  # For expiration tracking
        }
        with tx_data_lock:
            notification_list.append(notification)
            #print(f"Added notification: {notification}")  # Debug print
            # Keep only the last 3 notifications
            if len(notification_list) > 3:
                notification_list[:] = notification_list[-3:]

    # Extract transaction details
    inputs = tx.get("inputs", [])
    outputs = tx.get("out", [])
    input_addresses = [inp.get("prev_out", {}).get("addr", "N/A") for inp in inputs 
                       if "prev_out" in inp and "addr" in inp.get("prev_out", {}) and inp["prev_out"]["addr"] is not None]
    output_addresses = [out.get("addr", "N/A") for out in outputs if "addr" in out and out["addr"] is not None]
    num_inputs = len(inputs)
    num_outputs = len(outputs)
    tx_size = tx.get("size", 0)
    tx_fee = tx.get("fee", 0)
    fee_per_byte = tx_fee / tx_size if tx_size > 0 else 0

    # Fetch current BTC price and calculate USD value
    btc_price = get_btc_price()
    usd_value = btc_value * btc_price if btc_price is not None else "N/A"

    # Convert transaction time to Germany timezone
    tx_time_unix = tx.get("time")
    if tx_time_unix:
        try:
            utc_time = datetime.utcfromtimestamp(tx_time_unix).replace(tzinfo=pytz.UTC)
            germany_tz = pytz.timezone("Europe/Berlin")
            tx_time = utc_time.astimezone(germany_tz)
            tx_time_str = tx_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        except Exception as e:
            #print(f"Error converting time: {e}")
            # Use current time as fallback
            tx_time = datetime.now(pytz.timezone("Europe/Berlin"))
            tx_time_str = tx_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    else:
        #print("No time provided in transaction, using current time.")
        tx_time = datetime.now(pytz.timezone("Europe/Berlin"))
        tx_time_str = tx_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    # Prepare display strings for inputs and outputs (limit to first 3 addresses)
    input_display = ', '.join(input_addresses[:3]) if input_addresses else "No addresses"
    output_display = ', '.join(output_addresses[:3]) if output_addresses else "No addresses"
    
    # Generate trading signal
    signal = analyze_transaction(input_addresses, output_addresses, btc_value, num_inputs, num_outputs)

    # Create transaction data dictionary
    tx_data = {
        "Time (Germany)": tx_time,  # Store as datetime object for chart
        "Time (Germany) Str": tx_time_str,  # Store string version for table
        "Value": btc_value,
        "Trading Signal": signal,
        "Num Inputs": num_inputs,
        "Num Outputs": num_outputs,
        #"Fee (satoshis)": tx_fee,
        #"Fee per Byte": round(fee_per_byte, 2),
        #"TX Hash": tx_hash,
    }

    # Append data to shared list with thread safety
    with tx_data_lock:
        tx_data_list.append(tx_data)
        #print(f"Added transaction to list: {tx_data}")  # Debug print
        # Limit the size of tx_data_list to prevent memory issues
        if len(tx_data_list) > 100:
            tx_data_list[:] = tx_data_list[-100:]

# WebSocket error handler
def on_error(ws, error):
    """Handle WebSocket errors."""
    #print(f"WebSocket Error: {error}")

# WebSocket open handler
def on_open(ws):
    """Subscribe to unconfirmed transactions when the WebSocket connection opens."""
    #print("WebSocket connection opened")
    ws.send(json.dumps({"op": "unconfirmed_sub"}))

# Start the WebSocket monitoring in a background thread
def start_monitoring():
    """Start monitoring unconfirmed Bitcoin transactions in a background thread."""
    def run_websocket():
        ws = websocket.WebSocketApp(
            "wss://ws.blockchain.info/inv",  # Try the original API
            on_message=lambda ws, message: on_message(ws, message, threshold=50),
            on_error=on_error,
            on_open=on_open
        )
        ws.run_forever()

    thread = Thread(target=run_websocket)
    thread.daemon = True  # Thread will terminate when the main program exits
    thread.start()

# Start monitoring when the module is loaded
start_monitoring()



# Callback to update the global monitoring state
@callback(
    Output("monitoring-toggle", "id"),  # Dummy output to avoid circular dependency
    Input("monitoring-toggle", "value"),
    prevent_initial_call=True,
    allow_duplicate=True
)
def update_monitoring_state(is_active):
    global_monitoring_active[0] = is_active if is_active is not None else False
    return "monitoring-toggle"  # Return the ID as a dummy output

# Callback to update notifications
@callback(
    Output("notifications-container", "children"),
    Input("notification-interval", "n_intervals"),
    Input("update-interval", "n_intervals"),  # Trigger on both intervals to catch new notifications
    allow_duplicate=True
)
def update_notifications(n_intervals_notification, n_intervals_update):
    #print("Updating notifications...")  # Debug print
    current_time = datetime.now().timestamp()
    
    # Remove expired notifications (older than 10 seconds)
    with tx_data_lock:
        notification_list[:] = [notif for notif in notification_list if (current_time - notif["timestamp"]) < 10]
        notifications = notification_list.copy()
    
    if not notifications:
        return html.Div()  # Return empty div if no notifications

    # Create alert components for each notification
    notification_components = [
        dbc.Alert(
            f"{notif['time']}: {notif['message']}",
            color="warning",
            dismissable=True,
            style={'marginBottom': '10px'}
        )
        for notif in notifications
    ]
    return notification_components

# Callback to display large transactions in a table and chart
@callback(
    Output("large-transactions-table", "children"),
    Output("large-transactions-chart", "figure"),
    Output("error-message", "children"),
    Input("large-transactions-store", "data"),
    Input("signal-symbol-dropdown", "value"),
    Input("threshold-input", "value"),
    allow_duplicate=True
)

def display_large_transactions_and_chart(store_data, selected_symbol_full, threshold):
    #print("Updating table and chart...")  # Debug print
    if not store_data:
        return html.Div("No data available in store."), {}, "Error: Store data is empty."

    base_symbol = get_base_symbol(selected_symbol_full)

    if base_symbol != 'BTC':  # Placeholder for future expansion
        return html.Div(f"Large transactions monitoring not yet supported for {base_symbol}.", style={'color': '#888888'}), {}, ""

    transactions = store_data.get("transactions", [])
    #print(f"Transactions in store: {transactions}")  # Debug print
    if not transactions:
        return html.Div("No large transactions detected yet.", style={'color': '#888888'}), {}, "No transactions detected."

    # Filter transactions based on the user-defined threshold
    if threshold is None or threshold < 1:
        threshold = 50  # Default threshold if invalid input
    filtered_transactions = [tx for tx in transactions if tx["Value"] >= threshold]
    #print(f"Filtered transactions: {filtered_transactions}")  # Debug print

    if not filtered_transactions:
        return html.Div(f"No transactions above {threshold} BTC detected.", style={'color': '#888888'}), {}, f"No transactions above {threshold} BTC."

    # Create table (use string version of time for display)
    df_table = pd.DataFrame(filtered_transactions)
    df_table['Time (Germany)'] = df_table['Time (Germany) Str']  # Use string version for table
    df_table = df_table.drop(columns=['Time (Germany) Str'])  # Drop the string column after use
    df_table = df_table.drop_duplicates(subset=['Time (Germany)', 'Value'])


    table = dash_table.DataTable(
        data=df_table.to_dict('records'),
        columns=[
            {"name": col, "id": col} for col in df_table.columns
        ],
        style_table={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'height': '420px', # TABLE_HEIGHT,
            'minWidth': '100%',
            'backgroundColor': '#1e1e2f'
        },
        # style_header={
        #     'backgroundColor': '#252540',
        #     'color': '#ffffff',
        #     'fontWeight': 'bold',
        #     'border': 'none'
        # },
        style_header={"fontWeight": "bold", "backgroundColor": "#333", "color": "white"},
        style_cell={
            'backgroundColor': '#1e1e2f',
            'color': '#ffffff',
            'border': 'none',
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Roboto, sans-serif'
        },
        style_data={
            'borderBottom': '1px solid #2a2a3d'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{Trading Signal} contains "Whale Move"'},
                'backgroundColor': '#dc3545',  # Red for whale moves
                'color': '#ffffff'
            },
            {
                'if': {'filter_query': '{Trading Signal} contains "Exchange Deposit"'},
                'backgroundColor': '#ffcc00',  # Yellow for exchange deposits
                'color': '#000000'
            },
            {
                'if': {'filter_query': '{Trading Signal} contains "Distribution"'},
                'backgroundColor': '#ff5722',  # Orange for distribution
                'color': '#ffffff'
            }
        ]
    )

    # Create scatter line chart
    try:
        df_chart = pd.DataFrame(filtered_transactions)
        # Ensure time is in datetime format
        df_chart['Time (Germany)'] = pd.to_datetime(df_chart['Time (Germany)'], errors='coerce')
        #print(f"Chart times: {df_chart['Time (Germany)'].tolist()}")  # Debug print
        # Drop rows with invalid dates
        df_valid = df_chart.dropna(subset=['Time (Germany)'])
        #print(f"Valid transactions for chart: {len(df_valid)}")  # Debug print

        if not df_valid.empty:
            # Sort by time to ensure points are added from left to right
            df_valid = df_valid.sort_values('Time (Germany)')
            fig = px.scatter(
                df_valid,
                x='Time (Germany)',
                y='Value',
                title="Large Transactions Over Time",
                labels={'Time (Germany)': 'Time', 'Value': 'Value'},
                template="plotly_dark"
            )
            # Update to show lines and markers
            fig.update_traces(mode='lines+markers')
            fig.update_layout(
                plot_bgcolor='#1e1e2f',
                paper_bgcolor='#1e1e2f',
                font_color='#ffffff',
                title_font_color='#ffffff',
                margin=dict(l=40, r=40, t=40, b=40),
                yaxis=dict(range=[0, max(df_valid['Value'].max(), threshold) + 10])  # Ensure y-axis starts at 0
            )
        else:
            #print("No valid time data for chart.")
            fig = {
                "layout": {
                    "title": "Large Transactions Over Time",
                    "plot_bgcolor": "#1e1e2f",
                    "paper_bgcolor": "#1e1e2f",
                    "font": {"color": "#ffffff"},
                    "margin": {"l": 40, "r": 40, "t": 40, "b": 40},
                    "annotations": [{
                        "text": "No valid time data available for chart.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 14, "color": "#ffffff"}
                    }]
                }
            }
    except Exception as e:
        #print(f"Error creating chart: {e}")
        fig = {
            "layout": {
                "title": "Large Transactions Over Time",
                "plot_bgcolor": "#1e1e2f",
                "paper_bgcolor": "#1e1e2f",
                "font": {"color": "#ffffff"},
                "margin": {"l": 40, "r": 40, "t": 40, "b": 40},
                "annotations": [{
                    "text": f"Error creating chart: {str(e)}",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 14, "color": "#ffffff"}
                }]
            }
        }

    return table, fig, ""

# Callback to update the store with new transactions
@callback(
    Output("large-transactions-store", "data"),
    Input("update-interval", "n_intervals"),
    Input("threshold-input", "value"),
    State("large-transactions-store", "data"),
    allow_duplicate=True
)
def update_store(n_intervals, threshold, store_data):
    #print("Updating store...")  # Debug print
    if threshold is None or threshold < 1:
        threshold = 50  # Default threshold if invalid input

    # Fetch new transactions
    new_data = []
    with tx_data_lock:
        new_data = tx_data_list.copy()
        #tx_data_list.clear()  # Not clearing to retain transactions across tab switches
        #print(f"New data fetched: {new_data}")  # Debug print

    # Filter new transactions based on the threshold
    new_data = [tx for tx in new_data if tx["Value"] >= threshold]

    current_transactions = store_data.get("transactions", [])
    all_transactions = current_transactions + new_data
    updated_transactions = all_transactions[-10:]  # Keep only the last 10 transactions for the table

    # Return full all_transactions so chart can use complete history (mirrors standalone page behavior)
    return {
        "transactions": all_transactions,
        "threshold": threshold
    }


# ----------------------------- END OF FILE ----------------------------- #