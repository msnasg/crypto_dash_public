
# src/layout.py

from dash import html, dcc
import dash_bootstrap_components as dbc
from src.sidebar import create_sidebar
from dash import page_container

# version hover sidebar & body
def create_layout():
    return html.Div(
        [
            # Sidebar (Hover-expandable)
            html.Div(
                create_sidebar(collapsed=True),  
                className="sidebar"
            ),

            # Main content that resizes dynamically
            html.Div(
                page_container,
                className="main-content"
            ),
        ]
    )


# Custom table generation function
def generate_custom_table(df):
    return html.Table(
        children=[
            html.Thead(
                html.Tr([
                    html.Th(col, style={
                        'color': '#ffffff',
                        'border': '1px solid #444',
                        'padding': '6px'
                    }) for col in df.columns
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(df.iloc[i][col], style={
                        'color': '#ffffff',
                        'border': '1px solid #444',
                        'padding': '6px'
                    }) for col in df.columns
                ]) for i in range(len(df))
            ])
        ],
        style={
            'backgroundColor': '#1e1e2f',
            'width': '100%',
            'border': '1px solid #444',
            'borderCollapse': 'collapse',
            'borderSpacing': '0',
        }
    )



