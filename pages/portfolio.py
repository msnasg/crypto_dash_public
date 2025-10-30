# Portfolio & Risk (pages/portfolio_risk.py)

from dash import html, dcc
import plotly.express as px
import pandas as pd

def get_layout():
    # Sample data for demonstration (replace with real portfolio data)
    df = pd.DataFrame({
        "Asset": ["BTC", "ETH", "XRP"],
        "Value": [10000, 5000, 2000],
        "Risk_Level": [0.3, 0.5, 0.7]
    })
    fig = px.pie(df, values="Value", names="Asset", title="Portfolio Allocation")
    fig.update_layout(template="plotly_dark")

    return html.Div([
        html.H1("Portfolio & Risk"),
        html.P("This page manages your portfolio and associated risks."),
        dcc.Graph(figure=fig)
    ])