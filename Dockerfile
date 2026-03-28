FROM python:3.11-slim

# Instalamos uv directamente desde el binario oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app
ENV PORT=8080

WORKDIR /app

# Dependencias de sistema (FFmpeg y Graphviz siguen siendo obligatorios)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    graphviz \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# En vez de requirements.txt, copiamos los archivos de uv
COPY pyproject.toml uv.lock ./

# Instalamos las dependencias sin instalar el proyecto todavía (para cachear capas)
# --frozen evita que uv intente actualizar el lockfile
RUN uv sync --no-install-project

# Copiamos el resto
COPY . .

# Exponemos puerto
EXPOSE 8080

# Ejecutamos usando 'uv run' para asegurar que use el venv gestionado por uv
CMD ["uv", "run", "gunicorn", "-w", "2", "--threads", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "src.main:app"]