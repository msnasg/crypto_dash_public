# Trade Summary (pages/trade_summary.py)

from dash import html, dcc
import plotly.express as px
import pandas as pd

def get_layout():
    # Sample data for demonstration (replace with real trade data)
    df = pd.DataFrame({
        "Trade_ID": [1, 2, 3],
        "Profit_Loss": [500, -200, 300],
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"]
    })
    fig = px.bar(df, x="Date", y="Profit_Loss", title="Trade Profit/Loss Summary")
    fig.update_layout(template="plotly_dark")

    return html.Div([
        html.H1("Trade Summary"),
        html.P("This page shows a summary of completed trades."),
        dcc.Graph(figure=fig)
    ])