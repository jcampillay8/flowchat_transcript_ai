# src/dashboard/layout.py
from dash import dcc, html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    # 1. COMPONENTES DE ESTADO (Invisibles)
    # Almacenan los datos en el navegador para permitir descargas sin re-procesar
    dcc.Store(id='store-md'),
    dcc.Store(id='store-img'),

    # 2. COMPONENTES DE TRANSFERENCIA (Invisibles)
    dcc.Download(id="download-text"),
    dcc.Download(id="download-image"),

    # 3. ENCABEZADO PRINCIPAL
    dbc.Row([
        dbc.Col([
            html.H1([
                html.Span("📊 Flowchart", className="text-primary"), 
                html.Span(" AI", className="text-dark")
            ], className="text-center my-4 fw-bold display-4"),
            html.P("Transforma audios y videos en diagramas lógicos con IA", 
                   className="text-center text-muted mb-5")
        ], width=12)
    ]),
    
    # 4. FORMULARIO DE CONFIGURACIÓN
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H5("Configuración del Proyecto", className="mb-0 text-white"), 
                    className="bg-primary"
                ),
                dbc.CardBody([
                    # Selección de Origen
                    dbc.Label("1. Selecciona el origen del contenido:", className="fw-bold"),
                    dbc.RadioItems(
                        id="source-type",
                        options=[
                            {"label": "🔗 Enlace YouTube", "value": "youtube"},
                            {"label": "📁 Archivo Local (MP3/WAV)", "value": "upload"},
                        ],
                        value="youtube", 
                        inline=True, 
                        className="mb-3 p-2 bg-light rounded border"
                    ),
                    
                    # Contenedor para Input de YouTube
                    html.Div([
                        dbc.InputGroup([
                            dbc.InputGroupText(html.I(className="bi bi-youtube text-danger")),
                            dbc.Input(
                                id="url-input", 
                                placeholder="https://www.youtube.com/watch?v=...", 
                                type="text"
                            ),
                        ])
                    ], id="url-container", style={'display': 'block'}),
                    
                    # Contenedor para Carga de Archivo
                    html.Div([
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="bi bi-cloud-arrow-up fs-3"),
                                html.Br(),
                                html.Span('Arrastra o Selecciona Archivo', id='upload-text', className="small")
                            ]),
                            style={
                                'width': '100%', 'height': '100px', 'lineHeight': '30px',
                                'borderWidth': '2px', 'borderStyle': 'dashed',
                                'borderRadius': '10px', 'textAlign': 'center', 'backgroundColor': '#f8f9fa'
                            },
                            multiple=False
                        ),
                    ], id="upload-container", style={'display': 'none'}),
                    
                    html.Hr(),
                    
                    # Nombre del Proyecto
                    dbc.Label("2. Nombre del Proyecto:", className="fw-bold"),
                    dbc.InputGroup([
                        dbc.InputGroupText(html.I(className="bi bi-folder2-open")),
                        dbc.Input(
                            id="name-input", 
                            placeholder="Ej: Analisis_Mercado_2026", 
                            type="text"
                        ),
                    ]),
                    html.Small(
                        "Este nombre se usará para nombrar tus archivos .md y .png", 
                        className="text-muted"
                    ),
                    
                    html.Br(),
                    
                    # Botón de Acción Principal
                    dbc.Button(
                        [html.I(className="bi bi-cpu-fill me-2"), "Procesar con IA"], 
                        id="btn-run", 
                        color="primary", 
                        size="lg",
                        className="w-100 shadow fw-bold mt-2",
                        n_clicks=0
                    ),
                ])
            ], className="shadow-lg border-0 rounded-3")
        ], lg=5, md=8, xs=12)
    ], justify="center"),
    
    html.Br(),
    
    # 5. ÁREA DE RESULTADOS Y FEEDBACK (Donde ocurre la magia)
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-output", 
                type="circle", # Spinner circular clásico, más confiable que 'graph'
                color="#007bff",
                children=html.Div(
                    id="output-status", 
                    style={"minHeight": "120px"} # Espacio mínimo para que el spinner sea visible
                )
            ),
            
            # Botones de descarga invisibles que actúan como placeholders
            # Esto ayuda a Dash a registrar los IDs antes de que la tarjeta de éxito aparezca
            html.Div([
                dbc.Button(id="btn-download-txt", n_clicks=0, style={"display": "none"}),
                dbc.Button(id="btn-download-img", n_clicks=0, style={"display": "none"}),
            ])
        ], width=10, lg=6)
    ], justify="center", className="mb-5")

], fluid=True, className="p-0 bg-light", style={
    "minHeight": "100vh", 
    "fontFamily": "'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
})