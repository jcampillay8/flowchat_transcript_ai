import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from dash import Dash
import dash_bootstrap_components as dbc

from src.core.config import settings
from src.dashboard.layout import layout
from src.dashboard.callbacks import register_callbacks

# ==============================
# 🪵 Logging Configuration
# ==============================
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ==============================
# 🚀 FastAPI App Init
# ==============================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

# 🧱 Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# 📊 Dash App Configuration
# ==============================
dash_app = Dash(
    __name__,
    # CLAVE 1: Para que Dash sepa dónde está parado dentro de FastAPI
    requests_pathname_prefix="/dashboard/",
    # CLAVE 2: Forzar el servicio local de todos los scripts de Dash
    serve_locally=True, 
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True 
)

# CLAVE 3: Configuración explícita para evitar el error de dependencias
dash_app.scripts.config.serve_locally = True
dash_app.css.config.serve_locally = True

dash_app.title = settings.PROJECT_NAME
dash_app.layout = layout

# Registro de Callbacks
register_callbacks(dash_app)

# ==============================
# 🧭 FastAPI Routes
# ==============================
@app.get("/")
async def root():
    return {"ui_path": "/dashboard/"}

# Montaje de Dash en FastAPI (Usando el servidor Flask interno de Dash)
app.mount("/dashboard", WSGIMiddleware(dash_app.server))

if __name__ == "__main__":
    import uvicorn
    # IMPORTANTE: En Docker/Producción reload debe ser False para evitar conflictos con Gunicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=False)