
# Home Page (pages/home.py)

import dash
from dash import html

dash.register_page(__name__, path='/', name='Home')

layout = html.Div(
    style={
        "backgroundColor": "#000",  # مشکی
        "color": "#fff",            # متن سفید
        "padding": "40px"
    },
    children=[
        html.H1("🤖 Crypto Trading Assistant", style={
            "textAlign": "left",
            "marginTop": "20px",
            "color": "#fff"
        }),
        html.P(
            "This dashboard serves as your intelligent assistant for navigating crypto markets with precision. "
            "Explore insights, strategies, and performance metrics—all in one place.",
            style={
                "textAlign": "left",
                "maxWidth": "100%",
                "marginTop": "10px",
                "fontSize": "18px",
                "lineHeight": "1.6"
            }
        ),
        html.H2("📢 Latest Updates & Announcements", style={
            "marginTop": "40px",
            "textAlign": "left",
            "color": "#fff"
        }),
        html.P(
            "In the following list, you’ll find the most recent updates to strategies, tools, or team announcements. "
            "This helps us stay aligned and informed as we progress.",
            style={
                "textAlign": "left",
                "maxWidth": "100%",
                "fontSize": "18px",
                "marginBottom": "30px"
            }
        ),
        html.Table([
            html.Thead(
                html.Tr([
                    html.Th("Date", style={"border": "1px solid #666", "padding": "10px"}),
                    html.Th("Update", style={"border": "1px solid #666", "padding": "10px"})
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td("June 1", style={"border": "1px solid #666", "padding": "10px"}),
                    html.Td("....", style={"border": "1px solid #666", "padding": "10px"})
                ]),
                html.Tr([
                    html.Td("June 1", style={"border": "1px solid #666", "padding": "10px"}),
                    html.Td("New team members onboarded", style={"border": "1px solid #666", "padding": "10px"})
                ]),
                html.Tr([
                    html.Td("June 1", style={"border": "1px solid #666", "padding": "10px"}),
                    html.Td("Dashboard pushed in Github.", style={"border": "1px solid #666", "padding": "10px"})
                ])
            ])
        ], style={
            "width": "100%",
            "borderCollapse": "collapse",
            "marginTop": "20px",
            "fontSize": "16px"
        })
    ]
)


# # Home Page (pages/home.py)
# 
# import dash
# from dash import html
# 
# dash.register_page(__name__, path='/', name='Home')
# 
# layout = html.Div(
#     className="home-page",
#     children=[
#         html.H1("🤖 Crypto Trading Assistant", style={
#             "textAlign": "center",
#             "marginTop": "60px",
#             "color": "#2c3e50"
#         }),
#         html.P(
#             "This dashboard serves as your intelligent assistant for navigating crypto markets with precision. "
#             "Explore insights, strategies, and performance metrics—all in one place.",
#             style={
#                 "textAlign": "center",
#                 "maxWidth": "900px",
#                 "margin": "auto",
#                 "marginTop": "20px",
#                 "fontSize": "20px",
#                 "lineHeight": "1.6",
#                 "color": "#34495e"
#             }
#         ),
# 
#         html.H2("📢 Latest Updates & Announcements", style={
#             "marginTop": "60px",
#             "textAlign": "center",
#             "color": "#2d3436"
#         }),
#         html.P(
#             "In the following list, you’ll find the most recent updates to strategies, tools, or team announcements. "
#             "This helps us stay aligned and informed as we progress.",
#             style={
#                 "textAlign": "center",
#                 "maxWidth": "800px",
#                 "margin": "auto",
#                 "fontSize": "20px",
#                 "marginBottom": "30px",
#                 "color": "#2d3436"
#             }
#         ),
#        html.Table([
#             html.Tr([html.Th("Date"), html.Th("Update")]),
#             html.Tr([html.Td("June 1"), html.Td("....")]),
#             html.Tr([html.Td("June 1"), html.Td("New team members onboarded")]),
#             html.Tr([html.Td("June 1"), html.Td("Dashboard pushed in Github.")]),
#         ], style={
#             "margin": "auto",
#             "marginTop": "20px",
#             "border": "1px solid #ccc",
#             "borderCollapse": "collapse",
#             "width": "90%",
#             "textAlign": "left",
#             "color": "#2d3436"
#         })
#     ]
# )
# 
# 
# 
#     