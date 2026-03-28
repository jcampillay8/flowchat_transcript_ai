# src/dashboard/callbacks.py
from dash import Output, Input, State, html, dcc, callback_context
import dash_bootstrap_components as dbc
from src.services.media_processor import MediaProcessorService

# Instanciamos el servicio. 
# Nota: Si el error persiste, asegúrate de que exista un archivo src/services/__init__.py
processor = MediaProcessorService()

def register_callbacks(app):
    # 1. Feedback visual al seleccionar un archivo local
    @app.callback(
        Output('upload-text', 'children'),
        Input('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def actualizar_nombre_archivo(filename):
        if filename:
            return html.B(f"✅ Listo: {filename}", style={'color': '#2c3e50'})
        return "Arrastra o Selecciona Archivo"

    # 2. Alternar entre Input de URL y Upload de archivo
    @app.callback(
        [Output("url-container", "style"), Output("upload-container", "style")],
        Input("source-type", "value")
    )
    def toggle_inputs(source):
        if source == "youtube":
            return {"display": "block"}, {"display": "none"}
        return {"display": "none"}, {"display": "block"}

    # 3. CALLBACK PRINCIPAL: Procesa y genera la UI de descarga
    @app.callback(
        [
            Output("output-status", "children"),
            Output("download-text", "data"),
            Output("download-image", "data")
        ],
        [
            Input("btn-run", "n_clicks"),
            Input("btn-download-txt", "n_clicks"),
            Input("btn-download-img", "n_clicks")
        ],
        [
            State("source-type", "value"),
            State("url-input", "value"),
            State("upload-data", "contents"),
            State("upload-data", "filename"),
            State("name-input", "value")
        ],
        prevent_initial_call=True
    )
    def handle_all_actions(n_run, n_txt, n_img, stype, url, contents, upload_filename, proj_name):
        ctx = callback_context
        if not ctx.triggered:
            return "", None, None

        # Identificamos qué botón disparó el callback
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # LÓGICA DE PROCESAMIENTO (Botón principal "Procesar con IA")
        if trigger_id == "btn-run":
            if not proj_name:
                return dbc.Alert("⚠️ El nombre del proyecto es obligatorio.", color="warning"), None, None
            
            source_val = url if stype == 'youtube' else upload_filename
            if not source_val:
                return dbc.Alert("⚠️ Falta el archivo o la URL de YouTube.", color="warning"), None, None

            try:
                # El procesamiento ocurre aquí con la lógica de espaciado y fondo blanco que ya configuramos
                texto_md, img_bytes = processor.procesar_todo(stype, source_val, proj_name, contents)
                
                # Creamos la UI de éxito que contiene los botones con IDs específicos
                success_ui = dbc.Card([
                    dbc.CardBody([
                        html.H4("🚀 ¡Procesamiento Exitoso!", className="text-success fw-bold"),
                        html.P("El diagrama se ha generado con fondo blanco y espaciado mejorado."),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col(dbc.Button("📥 Descargar Markdown", id="btn-download-txt", color="primary", className="w-100"), width=6),
                            dbc.Col(dbc.Button("🖼️ Descargar PNG", id="btn-download-img", color="info", className="w-100"), width=6),
                        ]),
                    ])
                ], className="mt-3 shadow-sm border-success")

                # Intentamos disparar las descargas de inmediato (si el navegador lo permite)
                file_txt = dcc.send_string(texto_md, filename=f"{proj_name}.md")
                file_img = dcc.send_bytes(img_bytes, filename=f"{proj_name}.png")

                return success_ui, file_txt, file_img

            except Exception as e:
                print(f"DEBUG Error: {str(e)}")
                return dbc.Alert(f"❌ Error crítico: {str(e)}", color="danger"), None, None

        # LÓGICA DE DESCARGA MANUAL (Si el usuario hace clic en los botones de la Card)
        # Dash volverá a ejecutar la lógica o simplemente puedes dejar que el estado 
        # previo maneje la persistencia si usaras dcc.Store. 
        # Para este flujo simple, el btn-run ya devuelve los datos.
        
        return "", None, None