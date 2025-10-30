# pair_analysis.py

# Relative Opportunity Ratio (ROR)
# ROR = Excess Positive Returns / Excess Negative Returns (abs)
# به بیان ساده:
# اگر ROR > 1 → نسبت بازده مثبت به ریسک نزولی بالاست → یعنی نماد دوم بهتر از اولی.
# اگر ROR < 1 → ریسک نزولی بیشتر از سودهای نسبی → یعنی نماد دوم پرریسک‌تر از اولی.

import numpy as np
import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import sys, os
from config.settings import default_symbols
from utils.binance_data import fetch_data_binance, fetch_data_binance_candles

# مسیر utils برای ایمپورت
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------- ثبت صفحه ----------
dash.register_page(__name__, path="/pairanalysis", name="Pair Analysis")




# ---------- Layout ----------
layout = html.Div([
    dbc.Container([
    html.H2("Crypto Pair Analysis (Relative Opportunity Ratio)", style={"color": "white", "marginBottom": "20px"}),

    dbc.Row([
        dbc.Col([
            html.Label("Symbol 1", style={"color": "white"}),
            dcc.Dropdown(
                options=[{"label": s, "value": s} for s in default_symbols],
                value="BTCUSDC",
                id="pair1-dropdown",
                style={
                    'border': '1px solid white',
                    'borderRadius': '8px',
                    'backgroundColor': '#1e1e2f',
                    'color': 'white'
                }
            ),
        ], width=1),
        dbc.Col([
            html.Label("Symbol 2 (Risky)", style={"color": "white"}),
            dcc.Dropdown(
                options=[{"label": s, "value": s} for s in default_symbols],
                value="ETHUSDC",
                id="pair2-dropdown",
                style={
                    'border': '1px solid white',
                    'borderRadius': '8px',
                    'backgroundColor': '#1e1e2f',
                    'color': 'white'
                }
            ),
        ], width=1),
    ], justify="start", className="mb-4"),

        # ✅ Spinner برای نمودار
    dcc.Loading(
        id="loading-spinner",
        type="circle",  # یا "default" یا "cube" بسته به سلیقه‌ت
        color="#00cc96",
        children=html.Div(id='comparison-chart-container')
    )

], fluid=True)
], style={'backgroundColor': '#1e1e2f', 'padding': '20px',  "minHeight": "100vh"})

# ---------- Callback ----------
from dash import callback

@callback(
    Output('comparison-chart-container', 'children'),
    Input('pair1-dropdown', 'value'),
    Input('pair2-dropdown', 'value')
)


def update_pair_analysis(pair1, pair2):
    if not pair1 or not pair2:
        return html.Div("Please select both pairs.", style={"color": "gray"})

    charts = []

    # ---------- تنظیمات ----------
    timeframes = {
        "1M": "Monthly",
        "1w": "Weekly",
        "1d": "Daily",
        "4h": "4-Hour",
        #"1h": "1-Hour"
    }

    # 🔹 تعداد روزهای متفاوت برای هر تایم‌فریم
    lookback_by_tf = {
        "1M": 365,
        "1w": 365,
        "1d": 90,
        "4h": 14,
        #"1h": 7
    }

    for tf, label in timeframes.items():
        try:
            lookback_days = lookback_by_tf.get(tf, 90)

            df1 = fetch_data_binance(pair1, tf, lookback_days)
            df2 = fetch_data_binance(pair2, tf, lookback_days)

            if df1 is None or df2 is None or df1.empty or df2.empty:
                continue

            # --- محاسبه جهت کندل: +1 اگر close >= open و -1 اگر close < open
            dir1 = np.where(df1["close"] >= df1["open"], 1, -1)
            dir2 = np.where(df2["close"] >= df2["open"], 1, -1)

            # --- محاسبه درصد Range بین high و low و ضرب در جهت کندل
            df1["range_%"] = ((df1["high"] - df1["low"]) / df1["low"]) * 100 * dir1
            df2["range_%"] = ((df2["high"] - df2["low"]) / df2["low"]) * 100 * dir2

            # ✅ محاسبه میانگین بازده برای نمایش در عنوان
            avg1 = df1["range_%"].mean()
            avg2 = df2["range_%"].mean()

            # --- جدا کردن بازده‌های مثبت و منفی
            pos1 = df1[df1["range_%"] > 0]["range_%"]
            pos2 = df2[df2["range_%"] > 0]["range_%"]
            neg1 = df1[df1["range_%"] < 0]["range_%"]
            neg2 = df2[df2["range_%"] < 0]["range_%"]

            # --- میانگین‌ها
            mean_pos1, mean_pos2 = pos1.mean(), pos2.mean()
            mean_neg1, mean_neg2 = neg1.mean(), neg2.mean()

            # --- محاسبه شاخص‌ها
            growth_potential = mean_pos2 - mean_pos1
            risk_diff = abs(mean_neg2) - abs(mean_neg1)
            ror = (growth_potential / risk_diff) if risk_diff != 0 else None

            # --- رنگ و متن برای نمایش
            gp_color = "#00cc96" if growth_potential > 0 else "#ef553b"
            risk_color = "#ef553b" if risk_diff > 0 else "#00cc96"
            ror_color = "#00cc96" if (ror and ror > 1) else "#ef553b"

            stats_card = html.Div([
                html.Div([
                    html.Span("📈 Growth Potential: ", style={"color": "white"}),
                    html.Span(f"{growth_potential:.2f}%", style={"color": gp_color, "fontWeight": "bold"}),
                ]),
                html.Div([
                    html.Span("⚠️ Risk Difference: ", style={"color": "white"}),
                    html.Span(f"{risk_diff:.2f}%", style={"color": risk_color, "fontWeight": "bold"}),
                ]),
                html.Div([
                    html.Span("⚖️ ROR: ", style={"color": "white"}),
                    html.Span(f"{ror:.2f}" if ror is not None else "N/A", style={"color": ror_color, "fontWeight": "bold"}),
                ])
            ], style={
                "marginTop": "10px",
                "padding": "10px",
                "backgroundColor": "#1e1e2f",
                "borderRadius": "8px"
            })

            # ✅ ساخت نمودار میله‌ای گروهی
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df1.index,
                y=df1["range_%"],
                name=f"{pair1} % Range",
                opacity=0.6
            ))
            fig.add_trace(go.Bar(
                x=df2.index,
                y=df2["range_%"],
                name=f"{pair2} % Range",
                opacity=0.6
            ))



            fig.update_layout(
                title=f"{label} Comparison: {pair1} vs {pair2} "
                      f"— Avg Range: {avg1:.2f}% vs {avg2:.2f}%",
                xaxis_title="Date",
                yaxis_title="% Range (Volatility per Candle)",
                template="plotly_dark",
                plot_bgcolor='#1e1e2f',
                paper_bgcolor='#1e1e2f',
                barmode="group",
                height=400,
                margin=dict(l=40, r=20, t=40, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            charts.append(
                dbc.Card(
                    dbc.CardBody([
                        dcc.Graph(figure=fig),
                        stats_card
                    ]),
                    style={
                        "margin": "10px",
                        "backgroundColor": "#1e1e2f", # main background
                        "borderRadius": "10px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.3)"
                    }
                )
            )

        except Exception as e:
            print(f"Error processing {tf}: {e}")

    # ✅ گروه‌بندی کارت‌ها به صورت دو در دو (mosaic)
    rows = []
    for i in range(0, len(charts), 2):
        row = dbc.Row(
            [
                dbc.Col(charts[i], width=6),
                dbc.Col(charts[i + 1], width=6) if i + 1 < len(charts) else dbc.Col(width=6)
            ],
            className="mb-3"
        )
        rows.append(row)

    return rows


