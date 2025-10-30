# pages/transactions.py

import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

from src.layout import generate_custom_table
from utils.binance_data import get_recent_trades, get_processed_trade_data

from config.settings import default_symbols
plots_height = 400
large_trade_value = 100000
dash.register_page(__name__, path="/transactions")

# Select Symbols in setting in config
# default_symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT']

layout = html.Div([
    dbc.Container([
        # html.H3("Live Binance Trade Monitor", className="my-3 text-center"),
                
    html.Div([
        html.Label("Select symbols"),
        dcc.Dropdown(
            options=[{'label': sym, 'value': sym} for sym in default_symbols],
            value=['BTCUSDC', 'BNBUSDC', 'SOLUSDC', 'DOTUSDC', 'XLMUSDC'],
            multi=True,
            id='symbol-dropdown',
            maxHeight=200,
            placeholder="Choose symbols",
            style={'width': '1200px'}  # یا '30%' یا هر مقدار دیگه
        )
    ], className="mb-4", style={'display': 'inline-block', 'verticalAlign': 'top'}),
        

        html.Div(id="tables-container"),
        # for big trades and auto update
        html.Div("Large Trades", className="fw-bold"),
        html.Div(id='large-trades-table', style={'width': '100%', 'padding': '20px'}),
        dcc.Interval(id="large-trades-interval", interval = 5 * 1000, n_intervals=0), 
        dcc.Store(id='large-trades-store', data=[]),
        
        # for trades
        dcc.Interval(id='update-interval', interval = 5 * 1000, n_intervals=0) 
        

    ], fluid=True)
], style={'backgroundColor': '#1e1e2f', 'padding': '20px'})


@dash.callback(
    Output("tables-container", "children"),
    Input("update-interval", "n_intervals"),
    State("symbol-dropdown", "value")
)



def update_tables(n, selected_symbols):
    if not selected_symbols:
        return html.Div("Please select at least one symbol.", className="text-danger")

    selected_symbols = selected_symbols[:3]  # حداکثر دو نماد
    data = get_processed_trade_data(selected_symbols)

    layout_rows = []

    for symbol in selected_symbols:
        symbol_data = data.get(symbol)
        if not symbol_data:
            continue

        top_trades = symbol_data['top']
        agg_data = symbol_data['agg']

        # جداول
#         top_table = dbc.Table.from_dataframe(top_trades,
#                                              striped=True,
#                                              bordered=True,
#                                              hover=True,
#                                              size='sm',
#                                              className="table-sm")
#         
#         agg_table = dbc.Table.from_dataframe(agg_data,
#                                              striped=True,
#                                              bordered=True,
#                                              hover=True,
#                                              size='sm')
          
        top_table = generate_custom_table(top_trades)
        agg_table = generate_custom_table(agg_data)
        
        # نمودارها
        buy_volumes, sell_volumes, df, buy_trades, sell_trades, df_ratio = prepare_plot_data(symbol)

        if buy_volumes is None or sell_volumes is None:
            continue

        chart1 = create_buy_sell_ratio_chart(df_ratio, symbol)
        chart2 = create_buy_sell_chart(buy_trades, sell_trades, symbol)
        chart3 = create_line_chart(buy_volumes, sell_volumes, symbol)
        # chart4 = create_bubble_chart(df, symbol)
        chart4 = create_heatmap(df, symbol)
        # chart5 = create_heatmap(df, symbol)

        # ...
        row = html.Div([
            html.Hr(),
            # html.H4(f"Symbol: {symbol}", className="text-center mb-3"),

            dbc.Row([
                # ستون ۱: جداول
                dbc.Col([
                    html.Div("Top Trades", className="fw-bold"),
                    top_table,
                    html.Br(),
                    html.Div("Volume Summary", className="fw-bold"),
                    agg_table
                ], xs=12, sm=12, md=6, lg=4),

                # ستون ۲: نمودار اول و دوم
                dbc.Col([
                    chart1,
                    html.Br(),
                    chart2
                ], xs=12, sm=12, md=6, lg=4),

                # ستون ۳: نمودار سوم و چهارم
                dbc.Col([
                    chart3,
                    html.Br(),
                    chart4
                ], xs=12, sm=12, md=6, lg=4),
            ], className="g-12 justify-content-center"),
        ], className="mb-5")

        layout_rows.append(row)

    return html.Div(layout_rows) # html.Div(layout_rows, className="container-fluid")



# تاریخچه معاملات برای ذخیره اطلاعات خرید و فروش
trade_history = []

def prepare_plot_data(symbol):
    global trade_history

    # دریافت داده‌ها
    trades = get_recent_trades(symbol)

    if not trades:
        return None, None, None, None, None

    df = pd.DataFrame(trades)
    df['timestamp'] = pd.to_datetime(df['time'], unit='ms')
    df['qty'] = pd.to_numeric(df['qty'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['direction'] = df['isBuyerMaker'].map({True: '🔴 Sell', False: '🟢 Buy '})

    # محاسبه حجم خرید و فروش
    buy_trades = df[df['isBuyerMaker'] == False]  # خریداران
    sell_trades = df[df['isBuyerMaker'] == True]  # فروشندگان

    # محاسبه حجم خرید و فروش در طول زمان
    buy_volumes = buy_trades.groupby('timestamp')['qty'].sum()
    sell_volumes = sell_trades.groupby('timestamp')['qty'].sum()
    
    
    # جمع‌آوری اطلاعات خرید و فروش به تاریخچه
    buy_volume = buy_volumes.sum()
    sell_volume = sell_volumes.sum()
    timestamp = pd.Timestamp.now()

    trade_history.append({'timestamp': timestamp, 'buy_volume': buy_volume, 'sell_volume': sell_volume})

    # ساختن DataFrame برای نسبت خرید به فروش
    df_ratio = pd.DataFrame(trade_history)
    df_ratio['buy_sell_ratio'] = df_ratio['buy_volume'] / (df_ratio['sell_volume'] + 1e-6)  # جلوگیری از تقسیم بر صفر

    return buy_volumes, sell_volumes, df, buy_trades, sell_trades, df_ratio


def create_buy_sell_ratio_chart(df_ratio, symbol):
    return dcc.Graph(
        style={'height': '400px', 'width': '800px', 'maxWidth': '100%'},
        figure={
            'data': [
                go.Scatter(
                    x=df_ratio['timestamp'], 
                    y=df_ratio['buy_sell_ratio'], 
                    mode='lines', 
                    name='Buy/Sell Ratio'
                ),
            ],
            'layout': go.Layout(
                title=f"Buy to Sell Ratio for {symbol}",
                xaxis=dict(
                    title='Time',
                    showgrid=True,
                    gridcolor='#333333',
                    color='#ffffff',       # رنگ محور x و برچسب‌ها
                ),
                yaxis=dict(
                    title='Ratio (Buy/Sell)',
                    showgrid=True,
                    gridcolor='#333333',
                    color='#ffffff',       # رنگ محور y و برچسب‌ها
                ),
                height=plots_height,
                plot_bgcolor='#1e1e2f',      # پس‌زمینه‌ی خود نمودار
                paper_bgcolor='#1e1e2f',     # پس‌زمینه‌ی کل فضای نمودار
                font=dict(color='#ffffff'),  # رنگ نوشته‌ها (اختیاری)
                # template='plotly_dark'  # Use dark theme to match Symox Dashboard
            ),
        },
        id=f"buy-sell-ratio-chart-{symbol}",
    )

def create_line_chart(buy_volumes, sell_volumes, symbol):
    return dcc.Graph(
        style={'height': '400px', 'width': '800px', 'maxWidth': '100%'},
        figure={
            'data': [
                go.Scatter(x=buy_volumes.index, y=buy_volumes.values, mode='lines', name='Buy Volume'),
                go.Scatter(x=sell_volumes.index, y=sell_volumes.values, mode='lines', name='Sell Volume'),
            ],
            'layout': go.Layout(
                title=f"Buy vs Sell Volume for {symbol}",
                xaxis=dict(
                    title='Time',
                    showgrid=True,
                    gridcolor='#333333',
                    color='#ffffff',       # رنگ محور x و برچسب‌ها
                ),
                yaxis=dict(
                    title='Volume',
                    showgrid=True,
                    gridcolor='#333333',
                    color='#ffffff',       # رنگ محور y و برچسب‌ها
                ),
                height=plots_height,
                plot_bgcolor='#1e1e2f',      # پس‌زمینه‌ی خود نمودار
                paper_bgcolor='#1e1e2f',     # پس‌زمینه‌ی کل فضای نمودار
                font=dict(color='#ffffff'),  # رنگ نوشته‌ها (اختیاری)
               # template='plotly_dark'  # Use dark theme to match Symox Dashboard
            ),
        },
        id=f"line-chart-{symbol}",
    )

def create_bubble_chart(df, symbol):
    # Creating Bubble Chart for Large Trades
    df['trade_size'] = df['qty'] * df['price']  # حجم کلی معامله
    large_trades = df.nlargest(20, 'trade_size')  # 20 معامله بزرگ

    # بررسی اینکه آیا داده‌ها بارگذاری شده‌اند یا نه
    print(f"Large Trades for {symbol}:")
    print(large_trades[['price', 'qty', 'trade_size']])  # چاپ اطلاعات بزرگترین معاملات

    if large_trades.empty:
        print(f"No large trades data for {symbol}")
        return dcc.Graph(
            figure={
                'data': [],
                'layout': go.Layout(title=f"No Data for {symbol}")
            }
        )

    # بررسی اندازه بابل‌ها
    large_trades['bubble_size'] = large_trades['trade_size'] * 10  # به طور موقت از 10 برای اندازه بابل‌ها استفاده می‌کنیم

    return dcc.Graph(
        style={'height': '400px', 'width': '800px', 'maxWidth': '100%'},
        figure={
            'data': [
                go.Scatter(
                    x=large_trades['price'],  # محور X: قیمت معاملات
                    y=large_trades['qty'],  # محور Y: حجم معاملات
                    mode='markers',  # حالت بابل
                    marker=dict(
                        size=large_trades['bubble_size'],  # اندازه بابل‌ها
                        color=large_trades['trade_size'],  # رنگ‌ها بر اساس حجم معامله
                        colorscale='Viridis',  # مقیاس رنگی برای معاملات بزرگتر
                        showscale=True,  # نمایش مقیاس رنگی
                        opacity=0.6,  # شفافیت بابل‌ها
                    ),
                    text=large_trades.apply(
                        lambda row: f"Price: {row['price']}<br>Qty: {row['qty']}<br>Trade Size: {row['trade_size']}", axis=1
                    ),  # نمایش جزئیات هر بابل هنگام هاور
                    name=f"Large Trades {symbol}"
                ),
            ],
            'layout': go.Layout(
                title=f"Bubble Chart of Large Trades for {symbol}",
                xaxis=dict(
                    title='Price',
                    showgrid=True,
                    gridcolor='#333333',
                    color='#ffffff',       # رنگ محور x و برچسب‌ها
                ),
                yaxis=dict(
                    title='Quantity',
                    showgrid=True,
                    gridcolor='#333333',
                    color='#ffffff',       # رنگ محور y و برچسب‌ها
                ),
                hovermode='closest',  # نمایش نزدیکترین بابل هنگام هاور
                height=plots_height,
                plot_bgcolor='#1e1e2f',      # پس‌زمینه‌ی خود نمودار
                paper_bgcolor='#1e1e2f',     # پس‌زمینه‌ی کل فضای نمودار
                font=dict(color='#ffffff'),  # رنگ نوشته‌ها (اختیاری)
                # template='plotly_dark'  # Use dark theme to match Symox Dashboard
            ),
        },
        id=f"bubble-chart-{symbol}",
    )


def create_heatmap(df, symbol):
    # from prepae data func
    if df is None or df.empty:
        return html.Div("No data available for heatmap.")

    df['PriceBucket'] = pd.cut(df['price'], bins=30)

    # گروه‌بندی برای خرید و فروش
    heatmap_data = df.groupby(['PriceBucket', 'direction'])['qty'].sum().unstack(fill_value=0).reset_index()

    # مقدار میانه‌ی هر سطل قیمت برای محور X
    heatmap_data['price'] = heatmap_data['PriceBucket'].apply(lambda x: x.mid)

    # استخراج داده‌ها برای Heatmap
    buy_col = '🟢 Buy ' if '🟢 Buy ' in heatmap_data.columns else heatmap_data.columns[1]
    sell_col = '🔴 Sell' if '🔴 Sell' in heatmap_data.columns else heatmap_data.columns[2]

    z_data = [
        heatmap_data[buy_col].values,
        heatmap_data[sell_col].values
    ]

    fig = go.Figure(data=[
        go.Heatmap(
            x=heatmap_data['price'],
            y=['Buy', 'Sell'],
            z=z_data,
            colorscale='Viridis'
        )
    ])

    fig.update_layout(
        title=f'Heatmap of Buy/Sell Volume for {symbol}',
        xaxis_title='Price',
        yaxis_title='Direction',
        height=plots_height,
        plot_bgcolor='#1e1e2f',      # پس‌زمینه‌ی خود نمودار
        paper_bgcolor='#1e1e2f',     # پس‌زمینه‌ی کل فضای نمودار
        font=dict(color='#ffffff'),  # رنگ نوشته‌ها (اختیاری)
       # template='plotly_dark'  # Use dark theme to match Symox Dashboard
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#333', color='#ffffff')
    fig.update_yaxes(showgrid=True, gridcolor='#333', color='#ffffff')

    return dcc.Graph(style={'height': '400px', 'width': '800px', 'maxWidth': '100%'},
                     figure=fig, 
                     id=f"heatmap-{symbol}")


def create_buy_sell_chart(buy_data, sell_data, symbol):
    # Calculate total buy and sell volumes
    buy_volume = buy_data['qty'].sum()
    sell_volume = sell_data['qty'].sum()

    # Create the pie chart with custom colors
    return dcc.Graph(
        style={'height': '400px', 'width': '800px', 'maxWidth': '100%'},
        figure={
            'data': [
                go.Pie(
                    labels=['Buy', 'Sell'],
                    values=[buy_volume, sell_volume],
                    name=f"Buy vs Sell for {symbol}",
                    marker=dict(
                        colors=['#00FF00', '#FF0000']  # Green for Buy, Red for Sell
                    )
                )
            ],
            'layout': go.Layout(
                title=f"Buy vs Sell Pie Chart for {symbol}",
                height = plots_height,
                plot_bgcolor='#1e1e2f',      # پس‌زمینه‌ی خود نمودار
                paper_bgcolor='#1e1e2f',     # پس‌زمینه‌ی کل فضای نمودار
                font=dict(color='#ffffff'),  # رنگ نوشته‌ها (اختیاری)
                # template='plotly_dark'  # Use dark theme to match Symox Dashboard
            ),
            
        },
        id=f"buy-sell-pie-chart-{symbol}",
    )

# --------------------------------------------------------------------------------------------------- #
# # Big Tranactions
from dash import Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc 

@callback(
    Output("large-trades-table", "children"),
    Input("large-trades-store", "data")
)
def display_large_trades(data):
    if not data:
        return html.Div("No large trades detected yet.", className="text-muted")

#     table = dbc.Table.from_dataframe(
#         pd.DataFrame(data),
#         striped=True,
#         bordered=True,
#         hover=True,
#         responsive=True,
#         className="table-sm table-dark"
#     )    
    table = generate_custom_table(pd.DataFrame(data))
    return table

@callback(
    Output("large-trades-store", "data"),
    Input("update-interval", "n_intervals"),
    State("symbol-dropdown", "value"),
    State("large-trades-store", "data"),
)

def detect_large_trades(n, selected_symbols, existing_data):
    new_large_trades = []

    for symbol in selected_symbols:
        trades = get_recent_trades(symbol)  

        for trade in trades:
            trade_value = float(trade['price']) * float(trade['qty'])

            # more than 50k
            if trade_value > large_trade_value:
                new_large_trades.append({
                    "Symbol": symbol,
                    "Price": trade["price"],
                    "Qty": trade["qty"],
                    "Value ($)": round(trade_value, 2),
                    "Side": "Buy" if trade["isBuyerMaker"] == False else "Sell",
                    "Time": datetime.fromtimestamp(trade["time"] / 1000).strftime("%H:%M:%S")
                })

    all_trades = existing_data + new_large_trades
    return all_trades[-10:]  # last 10






