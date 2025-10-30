# Strategy (pages/strategy.py)

from dash import html, dcc

def get_layout():
    return html.Div([
        html.H1("Strategy"),
        html.P("This page allows you to manage your trading strategies."),
        dcc.Dropdown(
            id='strategy-dropdown',
            options=[
                {'label': 'Momentum Trading', 'value': 'MT'},
                {'label': 'Mean Reversion', 'value': 'MR'},
                {'label': 'Scalping', 'value': 'SC'}
            ],
            value='MT',
            style={'color': 'black'}
        ),
        html.Div(id='strategy-output')
    ])