# src/services/media_processor.py
import os
import json
import whisper
import textwrap
import base64
import torch
import yt_dlp
from diagrams import Diagram, Edge
from diagrams.custom import Custom
from google import genai
from src.core.config import settings

class MediaProcessorService:
    def __init__(self):
        # Configuración de Gemini 2.0
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-2.0-flash"
        
        # --- AJUSTES DE ESPACIADO PARA EVITAR COLISIONES ---
        self.graph_attr = {
            "fontsize": "14",
            "bgcolor": "white",
            "rankdir": "TB",
            "splines": "ortho",      # Cambiado a 'ortho' para líneas más limpias en flujos industriales
            "nodesep": "1.5",        # Aumentamos espacio horizontal entre nodos (antes 0.5)
            "ranksep": "1.2",        # Aumentamos espacio vertical entre niveles (antes 0.75)
            "pad": "0.5",            # Margen interno del diagrama
            "compound": "true"
        }
        
        self.node_attr = {
            "fontsize": "12",
            "fontname": "Sans-serif",
            "style": "filled",
            "color": "#123456",
            "fillcolor": "white",
            "shape": "box",          # Cambiado a 'box' si el texto es muy largo, o mantener circle
            "fixedsize": "false",    # IMPORTANTE: false permite que el nodo crezca según el texto
            "width": "1.5",
            "height": "1.0"
        }

    def limpiar_nombre(self, nombre):
        """Limpia el nombre del proyecto para evitar errores de sistema de archivos."""
        return "".join([c for c in nombre if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')

    def procesar_todo(self, source_type, source_value, nombre_base, contents=None):
        """
        Flujo completo: Extracción -> Transcripción -> IA Analysis -> Diagram Render.
        Retorna: (texto_markdown: str, imagen_png_bytes: bytes)
        """
        nombre_clean = self.limpiar_nombre(nombre_base)
        # Usamos nombres únicos para evitar colisiones entre workers
        temp_audio_final = os.path.abspath(f"temp_{nombre_clean}.wav")
        
        try:
            # --- 1. OBTENCIÓN DE AUDIO ---
            if source_type == 'youtube':
                print(f"📥 Descargando audio desde YouTube: {source_value}")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': '192',
                    }],
                    'outtmpl': temp_audio_final.replace('.wav', ''),
                    'quiet': True,
                    'no_warnings': True,
                    # --- AJUSTE PARA EVITAR BLOQUEO DE BOT ---
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['ios', 'android'],
                            'skip': ['dash', 'hls']
                        }
                    },
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1'
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([source_value])
                
                # A veces yt-dlp genera nombre.wav.wav dependiendo de la versión
                if not os.path.exists(temp_audio_final) and os.path.exists(f"{temp_audio_final}.wav"):
                    os.rename(f"{temp_audio_final}.wav", temp_audio_final)
            
            else:
                # Caso Upload: Decodificar base64 enviado por Dash
                print(f"📁 Procesando archivo subido: {nombre_base}")
                if not contents:
                    raise ValueError("No se recibió contenido del archivo.")
                
                _, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                with open(temp_audio_final, "wb") as f:
                    f.write(decoded)

            # --- 2. VERIFICACIÓN ---
            if not os.path.exists(temp_audio_final):
                raise FileNotFoundError(f"Error crítico: No se encontró el archivo {temp_audio_final}")

            # --- 3. TRANSCRIPCIÓN CON WHISPER ---
            print("🎙️ Iniciando transcripción con Whisper...")
            model = whisper.load_model("base")
            result = model.transcribe(temp_audio_final, language="es")
            texto_transcrito = result['text']
            texto_md = f"# Transcripción: {nombre_base}\n\n{texto_transcrito}"

            # --- 4. GENERACIÓN DE ESTRUCTURA CON GEMINI ---
            print("🧠 Generando lógica de diagrama con Gemini...")
            prompt = f"""
            Analiza la transcripción y crea un diagrama de flujo.
            REGLA CRÍTICA: Las 'etiquetas' deben ser concisas (máximo 6 palabras).
            Responde ÚNICAMENTE JSON:
            {{
              "titulo": "{nombre_base}",
              "nodos": [ {{"id": "n1", "etiqueta": "Inicio Proceso"}}, ... ],
              "connections": [ {{"de": "n1", "a": "n2"}}, ... ]
            }}
            Texto: {texto_transcrito}
            """
            
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            struct = json.loads(clean_json)

            # --- 5. RENDERIZADO EN MEMORIA ---
            print("🎨 Renderizando diagrama con espaciado mejorado...")
            icon_path = os.path.abspath("src/dashboard/assets/icon_step.png")
            file_name = f"diag_{nombre_clean}"
            
            with Diagram(struct["titulo"], filename=file_name, show=False, direction="TB", 
                         graph_attr=self.graph_attr, node_attr=self.node_attr, outformat="png") as diag:
                nodes = {}
                for n in struct["nodos"]:
                    # Reducimos el ancho del wrap para que el texto sea más vertical y no choque de lado
                    label = "\n".join(textwrap.wrap(n["etiqueta"], width=15))
                    nodes[n["id"]] = Custom(label, icon_path)
                
                links = struct.get("connections") or struct.get("conexiones") or []
                for c in links:
                    # Añadimos un minlen para forzar que las flechas sean más largas si hay mucho texto
                    nodes[c["de"]] >> Edge(color="royalblue", style="bold", minlen="2") >> nodes[c["a"]]

            # El archivo se crea como 'diag_nombre.png'
            generated_file = f"{file_name}.png"
            
            if os.path.exists(generated_file):
                with open(generated_file, "rb") as f:
                    img_bytes = f.read()
                os.remove(generated_file) # Limpiamos el PNG temporal
            else:
                raise FileNotFoundError("No se pudo generar el archivo del diagrama")

            print("✅ ¡Proceso finalizado con éxito!")
            return texto_md, img_bytes

        finally:
            # --- 6. LIMPIEZA ---
            if os.path.exists(temp_audio_final):
                try:
                    os.remove(temp_audio_final)
                    print(f"waste bin: {temp_audio_final} eliminado.")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar el temporal: {e}")