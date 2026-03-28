FROM python:3.11-slim

# 1. Instalamos uv desde el binario oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Variables de entorno de Python y UV
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV UV_LINK_MODE=copy

WORKDIR /app

# 3. Dependencias de sistema (FFmpeg para audio y Graphviz para diagramas)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    graphviz \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiamos los archivos de configuración de dependencias primero
COPY pyproject.toml uv.lock ./

# 5. Instalamos dependencias (sin el proyecto aún para aprovechar el cache)
RUN uv sync --no-install-project --frozen

# 6. Copiamos todo el código fuente (incluyendo la carpeta src)
COPY . .

# 7. Instalamos el proyecto final
RUN uv sync --frozen

# 8. Comando de ejecución para Railway (USA EL PUERTO DINÁMICO)
# Importante: Railway inyecta la variable $PORT. Gunicorn debe escuchar ahí.
CMD ["sh", "-c", "uv run gunicorn -w 2 --threads 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT src.main:app"]