# src/dashboard/callbacks.py
from dash import Output, Input, State, html, dcc, callback_context, no_update
import dash_bootstrap_components as dbc
import base64
from src.services.media_processor import MediaProcessorService

# Instanciamos el servicio
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

    # 3. CALLBACK DE PROCESAMIENTO: Solo se encarga de la IA y mostrar la UI de éxito
    @app.callback(
        [
            Output("output-status", "children"),
            Output("store-md", "data"),
            Output("store-img", "data")
        ],
        Input("btn-run", "n_clicks"),
        [
            State("source-type", "value"),
            State("url-input", "value"),
            State("upload-data", "contents"),
            State("upload-data", "filename"),
            State("name-input", "value")
        ],
        prevent_initial_call=True
    )
    def procesar_con_ia(n_run, stype, url, contents, upload_filename, proj_name):
        if not proj_name:
            return dbc.Alert("⚠️ El nombre del proyecto es obligatorio.", color="warning"), None, None
        
        source_val = url if stype == 'youtube' else upload_filename
        if not source_val:
            return dbc.Alert("⚠️ Falta el archivo o la URL de YouTube.", color="warning"), None, None

        try:
            # Ejecución del servicio de IA
            texto_md, img_bytes = processor.procesar_todo(stype, source_val, proj_name, contents)
            
            # Convertimos los bytes de la imagen a base64 para guardarlos en dcc.Store
            img_base64 = base64.b64encode(img_bytes).decode('utf-8') if img_bytes else None

            # UI de éxito que se mantiene visible
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

            return success_ui, texto_md, img_base64

        except Exception as e:
            print(f"DEBUG Error: {str(e)}")
            return dbc.Alert(f"❌ Error crítico: {str(e)}", color="danger"), None, None

    # 4. CALLBACK DE DESCARGA TXT (Markdown)
    @app.callback(
        Output("download-text", "data"),
        Input("btn-download-txt", "n_clicks"),
        [State("store-md", "data"), State("name-input", "value")],
        prevent_initial_call=True
    )
    def descargar_markdown(n_clicks, data_md, proj_name):
        if n_clicks and data_md:
            return dcc.send_string(data_md, filename=f"{proj_name}.md")
        return no_update

    # 5. CALLBACK DE DESCARGA IMG (PNG)
    @app.callback(
        Output("download-image", "data"),
        Input("btn-download-img", "n_clicks"),
        [State("store-img", "data"), State("name-input", "value")],
        prevent_initial_call=True
    )
    def descargar_png(n_clicks, data_img_b64, proj_name):
        if n_clicks and data_img_b64:
            # Re-convertimos de base64 a bytes para la descarga
            img_bytes = base64.b64decode(data_img_b64)
            return dcc.send_bytes(img_bytes, filename=f"{proj_name}.png")
        return no_update