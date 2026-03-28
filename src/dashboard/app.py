# src/dashboard/app.py
from dash import Dash
import dash_bootstrap_components as dbc
from .layout import layout
from .callbacks import register_callbacks

def init_dashboard(server):
    dash_app = Dash(
        __name__,
        server=server, # Aquí se vincula al server de FastAPI
        requests_pathname_prefix="/dashboard/",
        external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    
    dash_app.title = "Flowchart Resume AI"
    dash_app.layout = layout
    register_callbacks(dash_app)
    
    return dash_app