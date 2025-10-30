
# on_chain_analysis.py



import dash
from dash import html, Input, Output, ctx, ALL
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

from analytics.market_liquidity.exchange_netflow import render_exchange_netflow_layout


dash.register_page(__name__, path="/onchain", name="On-Chain Analysis")

# ---------- دسته‌ها و زیرمجموعه‌ها ----------
categories = {
    #"Structural Analysis": ["Feature Interaction", "Market Regime Dynamics", "Joint Behavior Analysis","Econometric Prediction", "Causal Inference"],
    "Market Liquidity": ["Exchange Netflow", "Whale Transactions", "Stablecoin Inflow"],
    "Profitability": ["MVRV Ratio", "NUPL", "SOPR"],
    "Holders Behavior": ["LTH Supply", "Short-Term Holder SOPR", "Dormancy"],
    "Network Activity": ["Active Addresses", "Tx Count/Volume", "Gas Used"],
    "Market Valuation": ["Realized Cap", "Thermo Cap", "Delta Cap"],
    "Miner / Supply Pressure": ["Miner Balance", "Miner to Exchange Flow"]
}

# ---------- Sidebar ----------
def generate_sidebar(categories):
    category_icons = {
        "Structural Analysis": "mdi:chart-box-outline",
        "Market Liquidity": "mdi:water",
        "Profitability": "mdi:cash-multiple",
        "Holders Behavior": "mdi:account-group",
        "Network Activity": "mdi:network",
        "Market Valuation": "mdi:chart-line",
        "Miner / Supply Pressure": "mdi:pickaxe"
    }

    accordion_items = []
    for cat, metrics in categories.items():
        metric_links = []
        for m in metrics:
            item_index = f"{cat}|{m}"
            metric_links.append(
                dbc.NavLink(
                    [
                        DashIconify(
                            icon="mdi:circle",
                            width=18,
                            id={"type": "metric-icon", "index": item_index},
                            style={"marginRight": "6px"}
                        ),
                        html.Span(m, style={"color": "#ffffff"})
                    ],
                    id={"type": "metric-link", "index": item_index},
                    style={
                        "backgroundColor": "#1e1e2f",
                        "color": "#ffffff",
                        "fontSize": "20px",
                        "padding": "6px 10px",
                        "marginBottom": "4px",
                        "display": "flex",
                        "alignItems": "center"
                    }
                )
            )

        accordion_items.append(
            dbc.AccordionItem(
                metric_links,
                title=html.Span([
                    DashIconify(icon=category_icons.get(cat, "mdi:folder"), width=20, style={"marginRight": "8px", "fontSize": "20px"}),
                    html.Span(cat)
                ], style={"display": "flex", "alignItems": "center", "fontSize": "20px"}),
                item_id=cat.lower().replace(" ", "-")
            )
        )

    return dbc.Accordion(
        accordion_items,
        start_collapsed=True,
        always_open=False,
        style={"marginTop": "20px"}
    )

# ---------- Layout ----------
layout = html.Div([
    html.Div(
        [
            # ---- Sidebar ----
            html.Div(
                [
                    html.Br(),
                    html.H3(
                        "On-Chain Metrics",
                        style={
                            "fontSize": "30px",
                            "color": "#38bdf8",
                            "fontWeight": "bold",
                            "marginBottom": "10px",
                            "marginLeft": "40px",
                            "marginTop": "30px",
                            "maginbottom": "30px"
                        }
                    ),
                    generate_sidebar(categories)
                ],
                id="sidebar-container",
                style={
                    "backgroundColor": "#1e1e2f",
                    "border": "1px solid white",
                    "borderRadius": "8px",
                    "height": "95vh",
                    "overflowY": "auto",
                    "padding": "5px 5px",
                    "borderRight": "1px solid #ffffff",
                    "flex": "0 0 350px"  # 👈 اینجا عدد دقیق بده (px یا %)
                }
            ),

            # ---- Body ----
            html.Div(
                id="onchain-body",
                style={
                    "backgroundColor": "#1e1e2f",
                    "border": "1px solid white",
                    "borderRadius": "8px",
                    "padding": "20px",
                    "height": "95vh",
                    "overflowY": "auto",
                    "flex": "1",  # 👈 بقیه فضا رو می‌گیره
                    "marginLeft": "10px"
                }
            )
        ],
        style={
            "display": "flex",
            "flexDirection": "row",
            "height": "100vh",
            "gap": "10px",
            "padding": "10px"
        }
    )
], style={'backgroundColor': '#1e1e2f', 'padding': '10px'})





# ---------- Callback 1: فقط برای آیکون‌ها ----------
@dash.callback(
    Output({"type": "metric-icon", "index": ALL}, "icon"),
    Input({"type": "metric-link", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_sidebar_icons(n_clicks_list):
    icons = ["mdi:circle"] * len(n_clicks_list)

    if not ctx.triggered:
        return icons

    triggered_id = ctx.triggered_id
    selected_idx = None

    for i, input_dict in enumerate(ctx.inputs_list[0]):
        if input_dict["id"] == triggered_id:
            selected_idx = i
            break

    if selected_idx is not None:
        # ✅ انتخاب تیک و رنگ آبی
        icons[selected_idx] = "mdi:check-circle"

    return icons


# ---------- Callback 2: فقط برای محتوا ----------
@dash.callback(
    Output("onchain-body", "children"),
    Input({"type": "metric-link", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_onchain_body(n_clicks_list):
    if not ctx.triggered:
        return html.Div(
            "Select a metric from the left panel to view its analysis.",
            style={"fontSize": "20px", "color": "#ffffff", "marginTop": "20px"}
        )

    triggered_id = ctx.triggered_id
    category, metric = triggered_id["index"].split("|")

    # 🔹 حالت پیش‌فرض محتوا
    body = html.Div([
        html.Br(),
        html.H3(f"{metric}",
                style={
                    "fontSize": "30px",
                    "color": "#38bdf8",
                    "fontWeight": "bold",
                    "marginBottom": "10px",
                    "marginLeft": "10px"
                }),
        html.P(f"Category: {category}",
               style={"color": "#9ca3af", "fontSize": "20px"}),
        html.Div(
            f"📊 This is where charts, tables, and analysis for {metric} will appear.",
            style={
                "backgroundColor": "#1e1e2f",
                "padding": "20px",
                "fontSize": "20px",
                "borderRadius": "10px",
                "color": "#e2e8f0",
                "marginTop": "15px"
            }
        )
    ])

    # 🔸 محتوای خاص برای هر شاخص
    # if metric == "Exchange Netflow":
    #     from analytics.market_liquidity.exchange_netflow import render_exchange_netflow_layout
    #     body = render_exchange_netflow_layout()

    # در callback
    if metric == "Exchange Netflow":
        body = render_exchange_netflow_layout()


    return body





# ---------- Callback ----------
# @dash.callback(
#     Output("onchain-body", "children"),
#     Output({"type": "metric-icon", "index": ALL}, "icon"),
#     Input({"type": "metric-link", "index": ALL}, "n_clicks"),
#     prevent_initial_call=True
# )

# def update_body_and_icons(n_clicks_list):
#     icons = ["mdi:circle"] * len(n_clicks_list)

#     if not ctx.triggered:
#         return html.Div(
#             "Select a metric from the left panel to view its analysis.",
#             style={"fontSize": "20px", "color": "#ffffff", "marginTop": "20px"}
#         ), icons

#     triggered_id = ctx.triggered_id
#     selected_idx = None

#     for i, input_dict in enumerate(ctx.inputs_list[0]):
#         if input_dict["id"] == triggered_id:
#             selected_idx = i
#             break

#     if selected_idx is not None:
#         icons[selected_idx] = "mdi:check-circle" # "mdi:check-circle-outline"

#     category, metric = triggered_id["index"].split("|")
#     body = html.Div([
#         html.Br(),
#         html.H3(f"{metric}",
#                 style={
#                     "fontSize": "30px",
#                     "color": "#38bdf8",
#                     "fontWeight": "bold",
#                     "marginBottom": "10px",
#                     "marginLeft": "10px"
#                 }),
#         html.P(f"Category: {category}",
#                style={"color": "#9ca3af", "fontSize": "20px"}),
#         html.Div(
#             f"📊 This is where charts, tables, and analysis for {metric} will appear.",
#             style={
#                 "backgroundColor": "#1e1e2f",
#                 "padding": "20px",
#                 "fontSize": "20px",
#                 "borderRadius": "10px",
#                 "color": "#e2e8f0",
#                 "marginTop": "15px"
#             }
#         )
#     ])

#     return body, icons

# pages/onchain.py
# version 6 - Accordion sidebar with dynamic body icon
# import dash
# from dash import html, dcc, Input, Output, State, ctx, MATCH, ALL
# import dash_bootstrap_components as dbc
# from dash_iconify import DashIconify 

# dash.register_page(__name__, path="/onchain", name="On-Chain Analysis")

# # ---------- دسته‌ها و زیرمجموعه‌ها ----------
# categories = {
#     "Market Liquidity": ["Exchange Netflow", "Whale Transactions", "Stablecoin Inflow"],
#     "Profitability": ["MVRV Ratio", "NUPL", "SOPR"],
#     "Holders Behavior": ["LTH Supply", "Short-Term Holder SOPR", "Dormancy"],
#     "Network Activity": ["Active Addresses", "Tx Count/Volume", "Gas Used"],
#     "Market Valuation": ["Realized Cap", "Thermo Cap", "Delta Cap"],
#     "Miner / Supply Pressure": ["Miner Balance", "Miner to Exchange Flow"]
# }


# # ---------- Sidebar ----------
# # def generate_sidebar(categories):
# #     accordion_items = []
# #     for cat, metrics in categories.items():
# #         metric_links = []
# #         for m in metrics:
# #             item_index = f"{cat}|{m}"
# #             metric_links.append(
# #                 dbc.NavLink(
# #                     # children: آیکون (قابل آپدیت) + متن
# #                     [
# #                         html.Span("○", id={"type": "metric-icon", "index": item_index},
# #                                   style={"display": "inline-block", "width": "22px", "textAlign": "center", "color": "#94a3b8"}),
# #                         html.Span(m, style={"color": "#ffffff", "marginLeft": "6px"})
# #                     ],
# #                     id={"type": "metric-link", "index": item_index},
# #                     style={
# #                         "backgroundColor": "#1e1e2f",
# #                         "color": "#ffffff",
# #                         "fontSize": "18px",
# #                         "padding": "5px 10px",
# #                         "marginBottom": "5px",
# #                         "display": "flex",
# #                         "alignItems": "center"
# #                     }
# #                 )
# #             )

# #         # عنوان آکاردئون شامل آیکون کتگوری
# #         title_div = html.Div([
# #             html.Span("🔁", style={"marginRight": "8px"}) if cat == "Market Liquidity" else None,
# #             # میتونی این بخش رو ببری به یک مپ آیکونی برای هر دسته
# #             # برای مثال ساده: از emoji استفاده کردم؛ اگر خواستی DashIconify بذاریم.
# #             html.Span(cat, style={"fontWeight": "700", "color": "#e2e8f0"})
# #         ])

# #         accordion_items.append(
# #             dbc.AccordionItem(
# #                 metric_links,
# #                 title=cat,  # آکاردئون title باید رشته باشه برای رفتار داخلی، پس اینجا همون cat میمونه
# #                 item_id=cat.lower().replace(" ", "-")
# #             )
# #         )

# #     return dbc.Accordion(
# #         accordion_items,
# #         start_collapsed=True,
# #         always_open=False,
# #         style={"marginTop": "20px", "backgroundColor": "#1e1e2f"}
# #     )


# def generate_sidebar(categories):
#     category_icons = {
#         "Market Liquidity": "mdi:water",
#         "Profitability": "mdi:cash-multiple",
#         "Holders Behavior": "mdi:account-group",
#         "Network Activity": "mdi:network",
#         "Market Valuation": "mdi:chart-line",
#         "Miner / Supply Pressure": "mdi:pickaxe"
#     }

#     accordion_items = []
#     for cat, metrics in categories.items():
#         metric_links = []
#         for m in metrics:
#             metric_links.append(
#                 dbc.NavLink(
#                     [
#                         DashIconify(
#                             icon="mdi:circle",
#                             width=18,
#                             id={"type": "metric-icon", "index": f"{cat}|{m}"},
#                             style={"marginRight": "6px"}
#                         ),
#                         html.Span(m)
#                     ],
#                     id={"type": "metric-link", "index": f"{cat}|{m}"},
#                     style={
#                         "backgroundColor": "#1e1e2f",
#                         "color": "#ffffff",
#                         "fontSize": "17px",
#                         "padding": "6px 10px",
#                         "marginBottom": "4px",
#                         "display": "flex",
#                         "alignItems": "center"
#                     }
#                 )
#             )

#         accordion_items.append(
#             dbc.AccordionItem(
#                 metric_links,
#                 title=html.Span([
#                     DashIconify(icon=category_icons.get(cat, "mdi:folder"), width=20, style={"marginRight": "8px"}),
#                     html.Span(cat)
#                 ], style={"display": "flex", "alignItems": "center"}),
#                 item_id=cat.lower().replace(" ", "-")
#             )
#         )

#     return dbc.Accordion(
#         accordion_items,
#         start_collapsed=True,
#         always_open=False,
#         style={"marginTop": "20px"}
#     )


# # ---------- Layout ----------
# layout = html.Div([
#     dbc.Container(
#         fluid=True,
#         style={"color": "white", "height": "100vh", "padding": "0"},  # "backgroundColor": "#0f172a",
#         children=[
#             dbc.Row([
#                 # Sidebar
#                 dbc.Col(
#                     html.Div(
#                         [
#                             html.Br(),
#                             html.H3(
#                                 "On-Chain Metrics",
#                                 style={
#                                     "fontSize": "30px",
#                                     "color": "#ffffff",
#                                     "marginBottom": "10px",
#                                     "marginLeft": "10px",
#                                     "marginTop": "10px"
#                                 }
#                             ),
#                             generate_sidebar(categories)
#                         ],
#                         style={
#                             "backgroundColor": "#1e1e2f",
#                             "border": "1px solid white",
#                             "borderRadius": "8px",
#                             "height": "95vh",
#                             "overflowY": "auto",
#                             "padding": "5px 5px",
#                             "borderRight": "1px solid #ffffff"
#                         }
#                     ),
#                     width=1,  # افزایش عرض sidebar برای جای دادن بهتر زیرشاخه‌ها
#                     style={"padding": "5px"}
#                 ),

#                 # Body
#                 dbc.Col(
#                     html.Div(
#                         id="onchain-body",
#                         style={
#                             "backgroundColor": "#1e1e2f",
#                             'border': '1px solid white',
#                             "borderRadius": "8px",
#                             "padding": "20px",
#                             "height": "95vh",
#                             "overflowY": "auto"
#                         }
#                     ),
#                     width=11  # تنظیم عرض body متناسب با sidebar جدید
#                 )
#             ])
#         ]
#     ),
# ], style={'backgroundColor': '#1e1e2f', 'padding': '20px'})

# # ---------- Callbacks ----------

# # نمایش بدنه بر اساس کلیک روی لینک
# @dash.callback(
#     Output("onchain-body", "children"),
#     Input({"type": "metric-link", "index": ALL}, "n_clicks"),
#     prevent_initial_call=True
# )
# def update_body(n_clicks_list):
#     if not ctx.triggered:
#         return html.Div(
#             "Select a metric from the left panel to view its analysis.",
#             style={"fontSize": "16px", "color": "#94a3b8", "marginTop": "20px"}
#         )
    
#     triggered_id = ctx.triggered_id
#     if triggered_id and "index" in triggered_id:
#         selected = triggered_id["index"]
#         category, metric = selected.split("|")
#         return html.Div(
#             [
#                 html.Br(),
#                 html.H3(f"{metric}",
#                         style={
#                             "fontSize": "30px",
#                             "color": "#38bdf8",
#                             "fontWeight": "bold",
#                             "marginBottom": "10px",
#                             "marginLeft": "10px"
#                         }),
#                 html.P(f"Category: {category}",
#                        style={
#                            "color": "#9ca3af"
#                        }),
#                 html.Div(
#                     f"📊 This is where charts, tables, and analysis for {metric} will appear.",
#                     style={
#                         "backgroundColor": "#1e1e2f",
#                         "padding": "20px",
#                         "borderRadius": "10px",
#                         "color": "#e2e8f0",
#                         "marginTop": "15px"
#                     }
#                 )
#             ],
#             style={}
#         )
    
#     return dash.no_update


# # وقتی یک metric-link کلیک شد، آیکون همه آیتم‌ها آپدیت شود:
# @dash.callback(
#     Output("onchain-body", "children"),
#     Output({"type": "metric-icon", "index": ALL}, "icon"),
#     Input({"type": "metric-link", "index": ALL}, "n_clicks"),
#     prevent_initial_call=True
# )
# def update_body_and_icons(n_clicks_list):
#     icons = ["mdi:circle-small"] * len(n_clicks_list)

#     if not ctx.triggered:
#         return dash.no_update, icons

#     triggered_id = ctx.triggered_id
#     if triggered_id and "index" in triggered_id:
#         selected = triggered_id["index"]
#         category, metric = selected.split("|")

#         # آیکون انتخابی را تیک‌دار کن
#         selected_idx = list(ctx.inputs_list[0].keys())[0]
#         for i, link in enumerate(ctx.inputs_list[0].keys()):
#             if link["id"] == triggered_id:
#                 icons[i] = "mdi:check-circle-outline"

#         return (
#             html.Div([
#                 html.Br(),
#                 html.H3(f"{metric}",
#                         style={
#                             "fontSize": "30px",
#                             "color": "#38bdf8",
#                             "fontWeight": "bold",
#                             "marginBottom": "10px",
#                             "marginLeft": "10px"
#                         }),
#                 html.P(f"Category: {category}",
#                        style={"color": "#9ca3af"}),
#                 html.Div(
#                     f"📊 This is where charts, tables, and analysis for {metric} will appear.",
#                     style={
#                         "backgroundColor": "#1e1e2f",
#                         "padding": "20px",
#                         "borderRadius": "10px",
#                         "color": "#e2e8f0",
#                         "marginTop": "15px"
#                     }
#                 )
#             ]),
#             icons
#         )

#     return dash.no_update, icons



# version 5 - Accordion format
# import dash
# from dash import html, dcc, Input, Output, State, ctx, MATCH, ALL
# import dash_bootstrap_components as dbc
# from dash_iconify import DashIconify 

# dash.register_page(__name__, path="/onchain", name="On-Chain Analysis")

# # ---------- دسته‌ها و زیرمجموعه‌ها ----------
# categories = {
#     "Market Liquidity": ["Exchange Netflow", "Whale Transactions", "Stablecoin Inflow"],
#     "Profitability": ["MVRV Ratio", "NUPL", "SOPR"],
#     "Holders Behavior": ["LTH Supply", "Short-Term Holder SOPR", "Dormancy"],
#     "Network Activity": ["Active Addresses", "Tx Count/Volume", "Gas Used"],
#     "Market Valuation": ["Realized Cap", "Thermo Cap", "Delta Cap"],
#     "Miner / Supply Pressure": ["Miner Balance", "Miner to Exchange Flow"]
# }


# # ---------- Sidebar ----------
# def generate_sidebar(categories):
#     accordion_items = []
#     for cat, metrics in categories.items():
#         metric_links = []
#         for m in metrics:
#             metric_links.append(
#                 dbc.NavLink(
#                     m,
#                     id={"type": "metric-link", "index": f"{cat}|{m}"},
#                     style={
#                         "backgroundColor": "#1e1e2f",
#                         "color": "#ffffff",
#                         "fontSize": "18px",
#                         "padding": "5px 10px",
#                         "marginBottom": "5px",
#                         "display": "block"
#                     }
#                 )
#             )
        
#         accordion_items.append(
#             dbc.AccordionItem(
#                 metric_links,
#                 title=cat,
#                 item_id=cat.lower().replace(" ", "-")  # برای شناسایی منحصر به فرد
#             )
#         )
    
#     return dbc.Accordion(
#         accordion_items,
#         start_collapsed=True,
#         always_open=False,
#         style={"marginTop": "20px"}
#     )

# # ---------- Layout ----------
# layout = html.Div([
#     dbc.Container(
#         fluid=True,
#         style={"color": "white", "height": "100vh", "padding": "0"},  # "backgroundColor": "#0f172a",
#         children=[
#             dbc.Row([
#                 # Sidebar
#                 dbc.Col(
#                     html.Div(
#                         [
#                             html.Br(),
#                             html.H3(
#                                 "On-Chain Metrics",
#                                 style={
#                                     "fontSize": "30px",
#                                     "color": "#ffffff",
#                                     "marginBottom": "10px",
#                                     "marginLeft": "10px",
#                                     "marginTop": "10px"
#                                 }
#                             ),
#                             generate_sidebar(categories)
#                         ],
#                         style={
#                             "backgroundColor": "#1e1e2f",
#                             "border": "1px solid white",
#                             "borderRadius": "8px",
#                             "height": "95vh",
#                             "overflowY": "auto",
#                             "padding": "5px 5px",
#                             "borderRight": "1px solid #ffffff"
#                         }
#                     ),
#                     width=1,  # افزایش عرض sidebar برای جای دادن بهتر زیرشاخه‌ها
#                     style={"padding": "5px"}
#                 ),

#                 # Body
#                 dbc.Col(
#                     html.Div(
#                         id="onchain-body",
#                         style={
#                             "backgroundColor": "#1e1e2f",
#                             'border': '1px solid white',
#                             "borderRadius": "8px",
#                             "padding": "20px",
#                             "height": "95vh",
#                             "overflowY": "auto"
#                         }
#                     ),
#                     width=11  # تنظیم عرض body متناسب با sidebar جدید
#                 )
#             ])
#         ]
#     ),
# ], style={'backgroundColor': '#1e1e2f', 'padding': '20px'})

# # ---------- Callbacks ----------

# # نمایش بدنه بر اساس کلیک روی لینک
# @dash.callback(
#     Output("onchain-body", "children"),
#     Input({"type": "metric-link", "index": ALL}, "n_clicks"),
#     prevent_initial_call=True
# )
# def update_body(n_clicks_list):
#     if not ctx.triggered:
#         return html.Div(
#             "Select a metric from the left panel to view its analysis.",
#             style={"fontSize": "16px", "color": "#94a3b8", "marginTop": "20px"}
#         )
    
#     triggered_id = ctx.triggered_id
#     if triggered_id and "index" in triggered_id:
#         selected = triggered_id["index"]
#         category, metric = selected.split("|")
#         return html.Div(
#             [
#                 html.Br(),
#                 html.H3(f"{metric}",
#                         style={
#                             "fontSize": "30px",
#                             "color": "#38bdf8",
#                             "fontWeight": "bold",
#                             "marginBottom": "10px",
#                             "marginLeft": "10px"
#                         }),
#                 html.P(f"Category: {category}",
#                        style={
#                            "color": "#9ca3af"
#                        }),
#                 html.Div(
#                     f"📊 This is where charts, tables, and analysis for {metric} will appear.",
#                     style={
#                         "backgroundColor": "#1e1e2f",
#                         "padding": "20px",
#                         "borderRadius": "10px",
#                         "color": "#e2e8f0",
#                         "marginTop": "15px"
#                     }
#                 )
#             ],
#             style={}
#         )
    
#     return dash.no_update







# version 4 - Radio items for metrics
# import dash
# from dash import html, dcc, Input, Output, State, ctx, MATCH, ALL
# import dash_bootstrap_components as dbc

# dash.register_page(__name__, path="/onchain", name="On-Chain Analysis")

# # ---------- دسته‌ها و زیرمجموعه‌ها ----------
# categories = {
#     "Market Liquidity": ["Exchange Netflow", "Whale Transactions", "Stablecoin Inflow"],
#     "Profitability": ["MVRV Ratio", "NUPL", "SOPR"],
#     "Holders Behavior": ["LTH Supply", "Short-Term Holder SOPR", "Dormancy"],
#     "Network Activity": ["Active Addresses", "Tx Count/Volume", "Gas Used"],
#     "Market Valuation": ["Realized Cap", "Thermo Cap", "Delta Cap"],
#     "Miner / Supply Pressure": ["Miner Balance", "Miner to Exchange Flow"]
# }


# # ---------- Sidebar ----------
# def generate_sidebar(categories):
#     tree_items = []
#     for cat, metrics in categories.items():
#         tree_items.append(
            

#             html.Div(
#                 [                    
#                     html.Br(),
#                     html.Div(cat, className="category-title", style={
#                         # "color": "#ffffff",
#                         "color": "#38bdf8",
#                         "fontWeight": "bold",
#                         "marginBottom": "4px",
#                         "marginTop": "20px",
#                         "fontSize": "22px",
#                         "marginLeft": "5px"
#                     }),
#                     html.Br(),
#                     dcc.RadioItems(
#                         id={"type": "metric-radio", "category": cat},
#                         options=[{"label": m, "value": f"{cat}|{m}"} for m in metrics],
#                         value=None,
#                         labelStyle={"display": "block", "marginLeft": "15px", "color": "#ffffff", "fontSize": "22px"},
#                         inputStyle={"marginRight": "6px"},
#                         style={"marginBottom": "10px"}
#                     )
#                 ]
#             )
#         )
#     return tree_items


# # ---------- Layout ----------
# layout = html.Div([
#     dbc.Container(
#     fluid=True,
#     style={ "color": "white", "height": "100vh", "padding": "0"}, # "backgroundColor": "#0f172a",
    
#     children=[
       
#         dbc.Row([
#             # Sidebar
#             dbc.Col(
#                 html.Div(
#                     [
#                         html.Br(),
#                         html.H3(
#                             "On-Chain Metrics",
#                             style={
#                                 "fontSize": "30px",
#                                 "color": "#ffffff",
#                                 # "fontWeight": "bold",
#                                 "marginBottom": "10px",
#                                 "marginLeft": "10px",
#                                 "marginTop": "10px"
#                             }
#                         ),
#                         html.Div(  # 👈 اینجا اضافه شد
#                             generate_sidebar(categories)
#                         )
#                     ],
#                     style={
#                         "backgroundColor": "#1e1e2f",
#                         "border": "1px solid white",
#                         "borderRadius": "8px",
#                         "height": "95vh",
#                         "overflowY": "auto",
#                         "padding": "5px 5px",
#                         "borderRight": "1px solid #ffffff"
#                     }
#                 ),
#                 width=1,
#                 style={"padding": "5px"}  # 👈 px اضافه شد
#             ),

#             # Body
#             dbc.Col(
#                 html.Div(
#                     id="onchain-body",
#                     style={
#                         "backgroundColor": "#1e1e2f",
#                         'border': '1px solid white', 
#                         "borderRadius": "8px",
#                         "padding": "20px", 
#                         "height": "95vh", 
#                         "overflowY": "auto"}
#                 ),
#                 width=11
#             )
#         ])
#     ]
# ), 
# ], style={'backgroundColor': '#1e1e2f', 'padding': '20px'})


# # ---------- Callbacks ----------

# # کنترل اینکه فقط یکی از رادیوباتن‌ها انتخاب بشه
# @dash.callback(
#     [Output({"type": "metric-radio", "category": cat}, "value") for cat in categories.keys()],
#     [Input({"type": "metric-radio", "category": cat}, "value") for cat in categories.keys()],
#     prevent_initial_call=True
# )
# def single_select_radio(*values):
#     """Ensure only one radio item is selected across all categories."""
#     triggered_id = ctx.triggered_id
#     new_values = [None] * len(values)

#     if triggered_id is None:
#         return new_values

#     # فقط رادیوی انتخاب‌شده مقدارش بمونه
#     for i, cat in enumerate(categories.keys()):
#         if triggered_id["category"] == cat:
#             new_values[i] = values[i]
#         else:
#             new_values[i] = None
#     return new_values


# # نمایش بدنه بر اساس انتخاب فعلی
# @dash.callback(
#     Output("onchain-body", "children"),
#     [Input({"type": "metric-radio", "category": cat}, "value") for cat in categories.keys()]
# )
# def update_body(*selected_values):
#     selected = next((val for val in selected_values if val is not None), None)
#     if not selected:
#         return html.Div(
#             "Select a metric from the left panel to view its analysis.",
#             style={"fontSize": "16px", "color": "#94a3b8", "marginTop": "20px"}
#         )

#     category, metric = selected.split("|")
#     return html.Div(
#         [
#             html.Br(),
#             html.H3(f"{metric}", 
#                     style={
#                         "fontSize": "30px",
#                         "color": "#38bdf8",
#                         "fontWeight": "bold",
#                         "marginBottom": "10px",
#                         "marginLeft": "10px"                                
#                     }),
#             html.P(f"Category: {category}", 
#                    style={
#                        "color": "#9ca3af"
#                     }),
#             html.Div(
#                 f"📊 This is where charts, tables, and analysis for {metric} will appear.",
#                 style={
#                     "backgroundColor": "#1e293b",
#                     "padding": "20px",
#                     "borderRadius": "10px",
#                     "color": "#e2e8f0",
#                     "marginTop": "15px"
#                 }
#             )
#         ],
#         style={}
#     )





# # version 3 Tab format
# import ast
# import dash
# from dash import html, dcc, Output, Input, State, ctx
# import dash_bootstrap_components as dbc
# from config.settings import dune_api_key

# dash.register_page(__name__, path="/onchain")

# # ---------- Define Categories and Metrics ----------
# categories = {
#     "Market Liquidity": ["Exchange Netflow", "Whale Transactions", "Stablecoin Inflow"],
#     "Profitability": ["MVRV Ratio", "NUPL", "SOPR"],
#     "Holders Behavior": ["LTH Supply", "Short-Term Holder SOPR", "Dormancy"],
#     "Network Activity": ["Active Addresses", "Tx Count/Volume", "Gas Used"],
#     "Market Valuation": ["Realized Cap", "Thermo Cap", "Delta Cap"],
#     "Miner / Supply Pressure": ["Miner Balance", "Miner to Exchange Flow"]
# }

# currencies = ["BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "LTC", "DOT", "MATIC", "AVAX"]

# # ---------- Layout ----------
# layout = dbc.Container(
#     [
#         html.Div(
#             [
#                 html.H4("On-Chain Metrics", style={"color": "#fff", "marginBottom": "15px"}),

#                 # Currency selector
#                 dbc.Row([
#                     dbc.Col(
#                         html.Div([
#                             html.Label("Select Currency:", style={"color": "#ccc"}),
#                             dcc.Dropdown(
#                                 id="onchain-currency-selector",
#                                 options=[{"label": c, "value": c} for c in currencies],
#                                 value=currencies[0],
#                                 clearable=False,
#                                 style={
#                                     'border': '1px solid #444',
#                                     'borderRadius': '8px',
#                                     'backgroundColor': '#1e1e2f',
#                                     'color': 'white'
#                                 }
#                             )
#                         ], style={"marginBottom": "20px"}),
#                         width=3
#                     )
#                 ]),

#                 html.Br(),
#                 # Top-level category tabs
#                 dbc.Row([
#                     dcc.Tabs(
#                         id="category-tabs",
#                         value=list(categories.keys())[0],
#                         children=[
#                             dcc.Tab(label=cat, value=cat, style={
#                                 "backgroundColor": "#1e1e2f", "color": "white", "padding": "8px", "fontSize": "24px"
#                             }, selected_style={
#                                 "backgroundColor": "#ffffff", "color": "#000000", "borderBottom": "3px solid #ffffff", "fontSize": "24px"
#                             })
#                             for cat in categories.keys()
#                         ],
#                         style={"marginBottom": "10px"}
#                     )
#                 ]),

#                 # Second-level sub-metric tabs (updated dynamically)
#                 html.Div(id="metric-tabs-container"),

#                 html.Hr(style={"borderColor": "#444"}),

#                 html.Div(
#                     "Select a metric to see data for the selected currency.",
#                     id="onchain-main-body",
#                     style={"color": "#aaa", "marginTop": "20px"}
#                 )
#             ],
#             style={"padding": "25px", "backgroundColor": "#1e1e2f", "minHeight": "100vh"}
#         )
#     ],
#     fluid=True
# )

# # ---------- Callback to create sub-tabs ----------
# @dash.callback(
#     Output("metric-tabs-container", "children"),
#     Input("category-tabs", "value")
# )
# def update_metric_tabs(selected_category):
#     metrics = categories[selected_category]
#     return dcc.Tabs(
#         id="metric-tabs",
#         value=metrics[0],
#         children=[
#             dcc.Tab(label=m, value=m, style={
#                 "backgroundColor": "#1e1e2f", "color": "white", "padding": "6px", "fontSize": "24px"
#             }, selected_style={
#                 "backgroundColor": "#ffffff", "color": "#000000", "borderBottom": "3px solid #ffffff", "fontSize": "24px"
#             })
#             for m in metrics
#         ],
#         style={"marginBottom": "10px"}
#     )

# # ---------- Callback to display metric data ----------
# @dash.callback(
#     Output("onchain-main-body", "children"),
#     Input("onchain-currency-selector", "value"),
#     Input("metric-tabs", "value")
# )
# def display_metric_data(selected_currency, selected_metric):
#     if not selected_metric:
#         return "Select a metric to see data for the selected currency."
#     return html.Div([
#         html.H5(f"{selected_metric} for {selected_currency}", style={"color": "#0f0"}),
#         html.Div("Data / chart would appear here...", style={"color": "#aaa", "marginTop": "10px"})
#     ])



# version 2
# import ast
# import dash
# from dash import html, dcc, Output, Input, State, ctx
# import dash_bootstrap_components as dbc
# import plotly.express as px
# import pandas as pd
# from dune_client.client import DuneClient
# from config.settings import dune_api_key

# dash.register_page(__name__, path="/onchain")

# # ---------- Dune connection ----------
# try:
#     client = DuneClient(dune_api_key)
# except Exception as e:
#     print(f"Error connecting to Dune Analytics: {e}")
#     client = None

# # ---------- Define Categories and Metrics ----------
# categories = {
#     "Market Liquidity": ["Exchange Netflow", "Whale Transactions", "Stablecoin Inflow"],
#     "Profitability": ["MVRV Ratio", "NUPL", "SOPR"],
#     "Holders Behavior": ["LTH Supply", "Short-Term Holder SOPR", "Dormancy"],
#     "Network Activity": ["Active Addresses", "Tx Count/Volume", "Gas Used"],
#     "Market Valuation": ["Realized Cap", "Thermo Cap", "Delta Cap"],
#     "Miner / Supply Pressure": ["Miner Balance", "Miner to Exchange Flow"]
# }

# # List of currencies to track
# currencies = ["BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "LTC", "DOT", "MATIC", "AVAX"]

# # ---------- Build Sidebar Tree ----------
# def generate_sidebar_tree():
#     items = []
#     for cat, metrics in categories.items():
#         metric_items = []
#         for metric in metrics:
#             metric_div = html.Div(
#                 metric,
#                 id={"type": "metric-item", "index": metric},
#                 className="ps-3 metric-item",
#                 style={
#                     'border': '1px solid white',     # Match dropdown border
#                     'borderRadius': '8px',           # Match dropdown border radius
#                     'backgroundColor': '#1e1e2f',    # Match dropdown background (not pure black)
#                     'color': 'white',                # Match dropdown text color
#                     "cursor": "pointer",
#                     "padding": "8px",                # Add some padding for better appearance
#                     "marginBottom": "8px"            # Spacing between items
#                 }
#             )
#             metric_items.append(metric_div)
#         items.append(
#             dbc.AccordionItem(
#                 children=metric_items,
#                 title=cat,
#                 item_id=cat
#             )
#         )
#     return dbc.Accordion(
#         items,
#         start_collapsed=True,
#         flush=True,
#         id="onchain-sidebar-accordion",
#         style={
#             'backgroundColor': '#1e1e2f',  # Consistent dark background
#             'color': 'white'              # Consistent text color
#         }
#     )

# # ---------- Layout ----------
# layout = dbc.Container(
#     [
#         dbc.Row(
#             [
#                 # Sidebar
#                 dbc.Col(
#                     [
#                         html.Div(
#                             [
#                                 html.H4("On-Chain Metrics", style={"color": "#fff", "marginBottom": "15px"}),
#                                 # Single currency selector
#                                 html.Div([
#                                     html.Label("Select Currency:", style={"color": "#ccc"}),
#                                     dcc.Dropdown(
#                                         id="onchain-currency-selector",
#                                         options=[{"label": c, "value": c} for c in currencies],
#                                         value=currencies[0],
#                                         clearable=False,
#                                         style={
#                                             'border': '1px solid white',     # White border
#                                             'borderRadius': '8px',           # Rounded corners
#                                             'backgroundColor': '#1e1e2f',    # Dark background
#                                             'color': 'white'                 # White text
#                                         },
#                                         className="onchain-dropdown"
#                                     )
#                                 ], style={"marginBottom": "20px"}),
#                                 generate_sidebar_tree()
#                             ],
#                             style={
#                                 "backgroundColor": "#1e1e2f",  # Changed to match overall dark theme and dropdown
#                                 "color": "#ffffff",
#                                 "height": "70vh",
#                                 "overflowY": "auto",
#                                 "padding": "45px",
#                                 "marginTop": "20px"  # Fixed capitalization from "MarginTop"
#                             }
#                         )
#                     ],
#                     width=3,
#                     style={"backgroundColor": "#1e1e2f"}  # Consistent dark background
#                 ),
#                 # Main panel
#                 dbc.Col(
#                     [
#                         html.Div(
#                             [
#                                 html.H4("Metric Data / Chart", style={"color": "#fff"}),
#                                 html.Div(
#                                     "Select a metric to see data for the selected currency.",
#                                     id="onchain-main-body",
#                                     style={"color": "#aaa", "marginTop": "20px"}
#                                 )
#                             ],
#                             style={"padding": "20px"}
#                         )
#                     ],
#                     width=9,
#                     style={"backgroundColor": "#1e1e2f"}  # Changed to match sidebar for consistency
#                 )
#             ],
#             style={"margin": 0, "height": "100vh"}
#         )
#     ],
#     fluid=True
# )

# # ---------- Callback to update main panel ----------
# @dash.callback(
#     Output("onchain-main-body", "children"),
#     Input("onchain-currency-selector", "value"),
#     Input({"type": "metric-item", "index": dash.ALL}, "n_clicks")
# )
# def display_metric_data(selected_currency, n_clicks):
#     if not ctx.triggered:
#         return "Select a metric to see data for the selected currency."
    
#     # Determine which metric was clicked
#     triggered_prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
#     if triggered_prop_id:
#         clicked_id = ast.literal_eval(triggered_prop_id)
#         metric_name = clicked_id["index"]
#         return html.Div([
#             html.H5(f"{metric_name} for {selected_currency}", style={"color": "#fff"}),
#             html.Div("Data / chart would appear here...", style={"color": "#aaa", "marginTop": "10px"})
#         ])
#     return "Select a metric to see data for the selected currency."


# version 1
# # on_chain_analysis.py
# import ast
# import dash
# from dash import html, dcc, Output, Input, State, ctx
# import dash_bootstrap_components as dbc
# import plotly.express as px
# import pandas as pd
# from dune_client.client import DuneClient
# from config.settings import dune_api_key

# dash.register_page(__name__, path="/onchain")

# # ---------- Dune connection ----------
# try:
#     client = DuneClient(dune_api_key)
# except Exception as e:
#     print(f"Error connecting to Dune Analytics: {e}")
#     client = None

# # on_chain_analysis.py
# import dash
# from dash import html, dcc, Input, Output
# import dash_bootstrap_components as dbc

# dash.register_page(__name__, path="/onchain")

# # ---------- Define Categories and Metrics ----------
# categories = {
#     "Market Liquidity": ["Exchange Netflow", "Whale Transactions", "Stablecoin Inflow"],
#     "Profitability": ["MVRV Ratio", "NUPL", "SOPR"],
#     "Holders Behavior": ["LTH Supply", "Short-Term Holder SOPR", "Dormancy"],
#     "Network Activity": ["Active Addresses", "Tx Count/Volume", "Gas Used"],
#     "Market Valuation": ["Realized Cap", "Thermo Cap", "Delta Cap"],
#     "Miner / Supply Pressure": ["Miner Balance", "Miner to Exchange Flow"]
# }

# # List of currencies to track
# currencies = ["BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "LTC", "DOT", "MATIC", "AVAX"]

# # ---------- Build Sidebar Tree ----------
# def generate_sidebar_tree():
#     items = []
#     for cat, metrics in categories.items():
#         metric_items = [html.Div(metric, className="ps-3 metric-item", 
#                                  style={
#                                      'borderRadius': '8px',
#                                      'backgroundColor': '#1e1e2f',   
#                                      'color': 'white' ,             
#                                      "cursor": "pointer"}) 
#                         for metric in metrics]
#         items.append(
#             dbc.AccordionItem(
#                 children=metric_items,
#                 title=cat,
#                 item_id=cat
#             )
#         )
#     return dbc.Accordion(items, start_collapsed=True, flush=True, id="onchain-sidebar-accordion")
# # ---------- Layout ----------
# layout = dbc.Container(
#     [
#         dbc.Row(
#             [
#                 # Sidebar
#                 dbc.Col(
#                     [
#                         html.Div(
#                             [
#                                 html.H4("On-Chain Metrics", style={"color": "#fff", "marginBottom": "15px"}),
#                                 # Single currency selector
#                                 html.Div([
#                                     html.Label("Select Currency:", style={"color": "#ccc"}),
#                                     dcc.Dropdown(
#                                         id="onchain-currency-selector",
#                                         options=[{"label": c, "value": c} for c in currencies],
#                                         value=currencies[0],
#                                         clearable=False,
#                                         style={
#                                             'border': '1px solid white',     # ✅ رنگ سفید دور کادر
#                                             'borderRadius': '8px',           # گوشه‌های گرد (اختیاری)
#                                             'backgroundColor': '#1e1e2f',    # رنگ پس‌زمینه تیره برای کنتراست (اختیاری)
#                                             'color': 'white'                 # رنگ نوشته‌ها
#                                         },
#                                         className="onchain-dropdown"
#                                     )

#                                 ], style={"marginBottom": "20px"}),
#                                 generate_sidebar_tree()
#                             ],
#                             style={"backgroundColor": "#2a2a40", "color": "#ffffff","height": "70vh", "overflowY": "auto", "padding": "45px","MarginTop":"20px"}
#                         )
#                     ],
#                     width=3,
#                     style={"backgroundColor": "#1e1e2f"}
#                 ),
#                 # Main panel
#                 dbc.Col(
#                     [
#                         html.Div(
#                             [
#                                 html.H4("Metric Data / Chart", style={"color": "#fff"}),
#                                 html.Div(
#                                     "Select a metric to see data for the selected currency.",
#                                     id="onchain-main-body",
#                                     style={"color": "#aaa", "marginTop": "20px"}
#                                 )
#                             ],
#                             style={"padding": "20px"}
#                         )
#                     ],
#                     width=9,
#                     style={"backgroundColor": "#1b1b2a"}
#                 )
#             ],
#             style={"margin": 0, "height": "100vh"}
#         )
#     ],
#     fluid=True
# )

# # ---------- Callback to update main panel ----------
# @dash.callback(
#     Output("onchain-main-body", "children"),
#     Input("onchain-currency-selector", "value"),
#     Input({"type": "metric-item", "index": dash.ALL}, "n_clicks")
# )
# def display_metric_data(selected_currency, n_clicks):
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         return "Select a metric to see data for the selected currency."
    
#     # Determine which metric was clicked
#     clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
#     if clicked_id:
#         metric_name = clicked_id  # can map to metric if needed
#         return html.Div([
#             html.H5(f"{metric_name} for {selected_currency}", style={"color": "#fff"}),
#             html.Div("Data / chart would appear here...", style={"color": "#aaa", "marginTop": "10px"})
#         ])
#     return "Select a metric to see data for the selected currency."




# # ---------- Placeholder chart ----------
# def placeholder_chart(title):
#     df = pd.DataFrame({"x": range(10), "y": [i ** 2 for i in range(10)]})
#     fig = px.line(df, x="x", y="y", title=title)
#     return dcc.Graph(figure=fig, style={"height": "350px"})


# # ---------- On-chain category tree ----------
# ONCHAIN_TREE = {
#     "Overview": [],
#     "Supply & Holders": [
#         "Supply Dynamics",
#         "Holder Cohorts",
#         "Dormancy & Activity",
#     ],
#     "Exchange Flow": [
#         "Inflow / Outflow",
#         "Exchange Balances",
#         "Net Position Change",
#     ],
#     "Network Activity": [
#         "Active Addresses",
#         "Transactions",
#         "Fees & Gas Usage",
#     ],
#     "Stablecoins & DeFi": [
#         "Stablecoin Supply",
#         "DeFi TVL Trends",
#         "Lending / Borrowing",
#     ],
#     "Mining & Security": [
#         "Hashrate & Difficulty",
#         "Miner Revenue",
#         "Security Costs",
#     ],
#     "Derivatives & Sentiment": [
#         "Open Interest",
#         "Funding Rates",
#         "Sentiment Indices",
#     ],
# }


# # ---------- Build internal sidebar ----------
# def build_inner_sidebar():
#     """Creates the internal sidebar (tree structure) for on-chain categories."""
#     nav_elements = []

#     for cat, subs in ONCHAIN_TREE.items():
#         if not subs:
#             nav_elements.append(
#                 dbc.Button(
#                     cat,
#                     id={"type": "onchain-cat", "index": cat},
#                     color="dark",
#                     outline=True,
#                     className="w-100 text-start mb-1",
#                     size="sm",
#                     style={"color": "white", "background": "transparent", "borderColor": "#444"},
#                 )
#             )
#         else:
#             sub_buttons = [
#                 dbc.Button(
#                     f"• {sub}",
#                     id={"type": "onchain-sub", "index": f"{cat}|{sub}"},
#                     color="dark",
#                     outline=True,
#                     className="w-100 text-start mb-1 ms-2",
#                     size="sm",
#                     style={"color": "white", "background": "transparent", "borderColor": "#333"},
#                 )
#                 for sub in subs
#             ]
#             nav_elements.append(
#                 html.Div(
#                     [
#                         dbc.Button(
#                             cat,
#                             id={"type": "onchain-cat-toggle", "index": cat},
#                             color="dark",
#                             outline=True,
#                             className="w-100 text-start mb-1",
#                             size="sm",
#                             style={"color": "white", "background": "transparent", "borderColor": "#444"},
#                         ),
#                         dbc.Collapse(
#                             html.Div(sub_buttons, className="ms-1 mt-1"),
#                             id={"type": "onchain-collapse", "index": cat},
#                             is_open=False,
#                         ),
#                     ]
#                 )
#             )

#     sidebar = html.Div(
#         [
#             html.H5("On-Chain Categories", className="text-white text-center mt-2 mb-3"),
#             html.Div(nav_elements),
#         ],
#         style={
#             "backgroundColor": "#1e1e2f",  # your dashboard bg
#             "color": "white",
#             "padding": "15px",
#             "borderRadius": "12px",
#             "height": "85vh",
#             "overflowY": "auto",
#         },
#     )
#     return sidebar


# # ---------- Layout ----------
# layout = dbc.Container(
#     [
#         dbc.Row(
#             [
#                 # Left inner sidebar
#                 dbc.Col(
#                     build_inner_sidebar(),
#                     width=2,
#                 ),

#                 # Right main content
#                 dbc.Col(
#                     [
#                         html.H2("On-Chain Analysis", className="mb-3"),
#                         html.Div(
#                             id="onchain-content",
#                             children=placeholder_chart("Select a category or subcategory"),
#                         ),
#                     ],
#                     width=10,
#                 ),
#             ],
#             className="mt-3",
#         )
#     ],
#     fluid=True,
# )


# # ---------- Callbacks ----------
# # Collapse toggling for tree categories
# @dash.callback(
#     Output({"type": "onchain-collapse", "index": dash.ALL}, "is_open"),
#     Input({"type": "onchain-cat-toggle", "index": dash.ALL}, "n_clicks"),
#     State({"type": "onchain-collapse", "index": dash.ALL}, "is_open"),
# )
# def toggle_onchain_collapses(n_clicks, is_open_list):
#     """
#     Only iterate over categories that actually have collapses (i.e., have subcategories).
#     This keeps the State/index mapping consistent and avoids index mismatches.
#     """
#     # Build ordered list of categories that have subcategories (this matches created Collapse components)
#     cats_with_subs = [cat for cat, subs in ONCHAIN_TREE.items() if subs]

#     if not ctx.triggered:
#         return is_open_list

#     # ctx.triggered_id may be a dict (pattern-matching) or a string — handle both safely
#     triggered = ctx.triggered_id
#     if isinstance(triggered, dict):
#         triggered_index = triggered.get("index")
#     else:
#         try:
#             triggered_index = ast.literal_eval(triggered)["index"]
#         except Exception:
#             triggered_index = str(triggered)

#     # Build result by toggling only the corresponding collapse entry
#     result = []
#     for i, cat in enumerate(cats_with_subs):
#         if cat == triggered_index:
#             result.append(not is_open_list[i])
#         else:
#             result.append(is_open_list[i])
#     return result


# # Render content dynamically
# @dash.callback(
#     Output("onchain-content", "children"),
#     Input({"type": "onchain-cat", "index": dash.ALL}, "n_clicks"),
#     Input({"type": "onchain-sub", "index": dash.ALL}, "n_clicks"),
# )
# def render_onchain_content(cat_clicks, sub_clicks):
#     if not ctx.triggered:
#         return placeholder_chart("Select a category")

#     triggered = ctx.triggered_id
#     if isinstance(triggered, dict):
#         triggered_index = triggered.get("index")
#     else:
#         try:
#             triggered_index = ast.literal_eval(triggered)["index"]
#         except Exception:
#             triggered_index = str(triggered)

#     # Subcategory selected
#     if "|" in triggered_index:
#         cat, sub = triggered_index.split("|", 1)
#         return html.Div(
#             [
#                 html.H4(f"{cat} → {sub}", className="mb-3"),
#                 placeholder_chart(f"{sub} ({cat})"),
#             ]
#         )

#     # Category selected (no subs)
#     return html.Div(
#         [
#             html.H4(triggered_index, className="mb-3"),
#             placeholder_chart(f"Overview of {triggered_index}"),
#         ]
#     )
