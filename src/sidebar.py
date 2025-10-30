# src/sidebar.py
# import dash_bootstrap_components as dbc
# from dash import html
# from config.settings import tabs
# hiden sidebar
import dash_bootstrap_components as dbc
from dash import html
from config.settings import tabs

+
def generate_nav_links(collapsed):
    return [
        dbc.NavLink(
            html.Span(tab["icon"] if collapsed else f"{tab['icon']} {tab['name']}", style={"color": "white"}),
            href=tab["path"],
            active="exact",
            style={"padding": "15px", "fontWeight": "500", "fontSize": "22px"}
        ) for tab in tabs
    ]


def create_sidebar(collapsed=False):
    # sidebar
    sidebar_classes = "sidebar"
    if collapsed:
        sidebar_classes += " collapsed"

    return html.Div(
        [
            # Wrapper 
            html.Div(
                [
                    # 
                    html.H2(
                        "Crypto Analytics",
                        className="sidebar-logo",
                        style={"fontSize": "24px",
                               "textAlign": "center",
                               "color": "#38bdf8",
                                "fontWeight": "bold",
                                "marginBottom": "50px", 
                                "marginTop": "50px" }
                    ),
                    # Nav 
                    dbc.Nav(
                        [
                            dbc.NavLink(
                                [
                                    html.Span(tab["icon"], className="me-2"),
                                    html.Span(
                                        tab["name"],
                                        className="sidebar-text",
                                    ),
                                ],
                                href=tab["path"],
                                active="exact",
                                className="sidebar-link",
                            )
                            for tab in tabs
                        ],
                        vertical=True,
                        pills=True,
                    ),
                ],
                className=sidebar_classes
            )
        ],
        className="sidebar"
    )
