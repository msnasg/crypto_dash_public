# options_analysis.py
import pandas as pd
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from utils.options_data import analyze_options_data, analyze_all_expiries, get_expiry_dates
from config.settings import default_coins
import dash

dash.register_page(__name__, path="/options", name="Options")

layout = html.Div([
    dbc.Container([
        html.H2("Binance Options Analysis", className="text-white mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.Label("Symbol:", className="text-white"),
                dcc.Dropdown(
                    id="symbol-selector",
                    options=[{"label": sym, "value": sym} for sym in default_coins],
                    value="BTC",
                    clearable=False
                ),
            ], width=3),

            dbc.Col([
                html.Label("Option Type:", className="text-white"),
                dbc.RadioItems(
                    id="option-type-selector",
                    options=[
                        {"label": "Call", "value": "C"},
                        {"label": "Put", "value": "P"}
                    ],
                    value="C",
                    inline=True,
                    className="mb-3",
                    labelClassName="text-white"
                ),
            ], width=3),

            dbc.Col([
                html.Label("Expiry Date:", className="text-white"),
                dcc.Dropdown(
                    id="expiry-date-selector",
                    options=[],
                    value=None,
                    clearable=False
                ),
            ], width=3),

        ], className="mb-4"),

        dcc.Loading(
            id="loading-options-data",
            type="default",
            children=[
                html.Div(id="signals-container"),
                html.Div(id="plots-container"),
                html.Div(id="options-table-container")
            ]
        )
    ], fluid=True)
], style={'backgroundColor': '#1e1e2f', 'padding': '20px'})

@callback(
    Output("expiry-date-selector", "options"),
    Output("expiry-date-selector", "value"),
    Input("symbol-selector", "value")
)
def update_expiry_dropdown(symbol):
    if not symbol:
        return [], None
    dates = get_expiry_dates(symbol)
    if not dates:
        return [], None
    options = [{"label": date, "value": date} for date in dates]
    default_value = dates[0] if dates else None
    return options, default_value

@callback(
    [
        Output("signals-container", "children"),
        Output("plots-container", "children"),
        Output("options-table-container", "children")
    ],
    [
        Input("symbol-selector", "value"),
        Input("option-type-selector", "value"),
        Input("expiry-date-selector", "value")
    ],
    prevent_initial_call=False
)
def update_options_dashboard(symbol, option_type, expiry_date):
    if not (symbol and option_type and expiry_date):
        error_message = "Initializing dashboard... Please wait."
        if not expiry_date:
            error_message = "No expiry dates available. Check API connectivity or use a VPN."
        return (
            html.Div(error_message, className="text-warning"),
            html.Div(error_message, className="text-warning"),
            html.Div(error_message, className="text-warning")
        )

    try:
        # Analyze all expiries for signals, insights, and plots
        df_all, signals, all_expiry_insights, df_indices, plot_figures = analyze_all_expiries(asset=symbol)

        # Analyze single expiry for table
        df, single_expiry_insights = analyze_options_data(asset=symbol, option_type=option_type, expiry_date=expiry_date)

        # Signals and Insights for All Expiries
        signals_block = html.Div([
            html.H4("Trading Signals (All Expiries)", className="text-white mt-4"),
            html.P("Processing signals...", className="text-info") if not signals else None,
            html.Ul([html.Li(signal, className="text-white") for signal in signals]) if signals else html.P("No signals available.", className="text-warning"),
            html.H4("Insights (All Expiries)", className="text-white mt-4"),
            html.P("Processing insights...", className="text-info") if not all_expiry_insights else None,
            html.Ul([html.Li(insight, className="text-white") for insight in all_expiry_insights]) if all_expiry_insights else html.P("No insights available for all expiries.", className="text-warning")
        ])

        # Plots
        plot_elements = []
        if plot_figures and any(fig is not None for fig in plot_figures):
            for idx, fig in enumerate(plot_figures):
                if fig is not None:
                    plot_elements.append(
                        dcc.Graph(
                            figure=fig,
                            style={"width": "48%", "height": "500px", "margin": "1%"}
                        )
                    )
            plots_block = html.Div([
                html.H4("Market Analysis Plots", className="text-white mt-4"),
                html.Div(plot_elements, style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"})
            ])
        else:
            plots_block = html.Div("No plots available. Check if data is available for analysis.", className="text-warning")

 
        # Table
        if df.empty:
            table_block = html.Div(f"No data available for expiry {expiry_date}. Try a different expiry date or symbol.", className="text-warning")
        else:
            table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
            insights_block = html.Ul([html.Li(insight, className="text-white") for insight in single_expiry_insights]) if single_expiry_insights else html.P("No insights available for this expiry.", className="text-warning")
            table_block = html.Div([
                html.H4(f"Market Data Table (Expiry: {expiry_date})", className="text-white mt-4"),
                table,
                html.H4("Insights (Selected Expiry)", className="text-white mt-4"),
                insights_block
            ])

        return signals_block, plots_block, table_block

    except Exception as e:
        error_message = f"Error processing data: {str(e)}. "
        if "429" in str(e):
            error_message += "Too many requests to the API. Try reducing the number of symbols."
        elif "403" in str(e):
            error_message += "Access denied. Check your VPN or API access."
        error_message += " Please check logs for details."
        return (
            html.Div(error_message, className="text-warning"),
            html.Div(error_message, className="text-warning"),
            html.Div(error_message, className="text-warning")
        )


# # pages/options_analysis.py
# 
# import pandas as pd
# from dash import html, dcc, callback, Input, Output
# import dash_bootstrap_components as dbc
# from utils.options_data import analyze_options_data
# from utils.options_data import get_expiry_dates
# from config.settings import default_coins
# 
# import dash
# dash.register_page(__name__, path="/options", name="Options")
# 
# # فرض: لیست دستی برای تاریخ‌های انقضا (بعداً می‌تونیم این رو داینامیک کنیم)
# # expiry_dates = ['250516', '250523', '250530']
# 
# expiry_dates = get_expiry_dates('BTC')
# 
# layout = html.Div([
#     dbc.Container([
#         html.H2("Binance Options - Symbol, Option Type, and Expiry", className="text-white mb-4"),
#         
#         dbc.Row([
#             dbc.Col([
#                 html.Label("Symbol:", className="text-white"),
#                 dcc.Dropdown(
#                     id="symbol-selector",
#                     options=[{"label": sym, "value": sym} for sym in default_coins],
#                     value = "BTC", # default_coins[0],
#                     clearable=False
#                 ),
#             ], width=3),
# 
#             dbc.Col([
#                 html.Label("Option Type:", className="text-white"),
#                 dbc.RadioItems(
#                     id="option-type-selector",
#                     options=[
#                         {"label": "Call", "value": "C"},
#                         {"label": "Put", "value": "P"}
#                     ],
#                     value="C",
#                     inline=True,
#                     className="mb-3",
#                     labelClassName="text-white"
#                 ),
#             ], width=3),
# 
#             dbc.Col([
#                 html.Label("Expiry Date:", className="text-white"),
#                 dcc.Dropdown(
#                     id="expiry-date-selector",
#                     options=[{"label": date, "value": date} for date in expiry_dates],
#                     value=expiry_dates[0],
#                     clearable=False
#                 ),
#             ], width=3),
# 
#         ], className="mb-4"),
# 
#         dcc.Loading(
#             id="loading-options-data",
#             type="default",
#             children=html.Div(id="options-table-container")
#         )
#     ], fluid=True)
# ], style={'backgroundColor': '#1e1e2f', 'padding': '20px'})
# 
# 
# # expiry date dynamic from Binnace
# @callback(
#     Output("expiry-date-selector", "options"),
#     Output("expiry-date-selector", "value"),
#     Input("symbol-selector", "value")
# )
# def update_expiry_dropdown(symbol):
#     if not symbol:
#         return [], None
#     dates = get_expiry_dates(symbol)
#     options = [{"label": date, "value": date} for date in dates]
#     default_value = dates[0] if dates else None
#     return options, default_value
# 
# 
# @callback(
#     Output("options-table-container", "children"),
#     Input("symbol-selector", "value"),
#     Input("option-type-selector", "value"),
#     Input("expiry-date-selector", "value")
# )
# 
# def update_options_table(symbol, option_type, expiry_date):
#     if not (symbol and option_type and expiry_date):
#         return html.Div("Please select all fields.", className="text-warning")
# 
#     df, insights = analyze_options_data(symbol=symbol, option_type=option_type, expiry_date=expiry_date)
# 
#     if df.empty:
#         return html.Div("No data available.", className="text-warning")
# 
#     table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True)
#     insights_block = html.Ul([html.Li(insight, className="text-white") for insight in insights])
# 
#     return html.Div([
#         html.H4("Market Data Table", className="text-white"),
#         table,
#         html.H4("Insights", className="text-white mt-4"),
#         insights_block
#     ])
# 
# 