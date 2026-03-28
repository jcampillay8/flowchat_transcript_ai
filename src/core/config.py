# src/core/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Definimos la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- RUTAS DE PROYECTO ---
    # Directorio para transcripciones y diagramas
    OUTPUT_PATH: Path = BASE_DIR / "outputs"
    TRANSCRIPTION_PATH: Path = OUTPUT_PATH / "transcripciones"
    DIAGRAM_PATH: Path = OUTPUT_PATH / "diagramas"

    # --- CONFIGURACIÓN GLOBAL ---
    ENVIRONMENT: str 
    PROJECT_NAME: str
    ALLOWED_ORIGINS: str
    WEBSITE_URL: str

    # --- IA CONFIG ---
    GEMINI_API_KEY: str
    MODEL_ID: str = "gemini-2.0-flash"

    def create_directories(self):
        """Asegura que existan las carpetas necesarias al iniciar"""
        for path in [self.OUTPUT_PATH, self.TRANSCRIPTION_PATH, self.DIAGRAM_PATH]:
            path.mkdir(parents=True, exist_ok=True)

settings = Settings()
# Ejecutamos la creación de carpetas al importar
settings.create_directories()