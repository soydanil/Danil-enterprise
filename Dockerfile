FROM python:3.12.4-slim
LABEL authors="abrahamperz"

# Set up the working directory
WORKDIR /app

# Copiar requirements y dependencias
COPY backend/requirements.txt .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear y activar entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn uvicorn

# Copiar solo el directorio backend
COPY backend/ ./backend/

# Cambiar al directorio de backend
WORKDIR /app/backend

EXPOSE 8080

# Comando de inicio
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080", "--worker-class", "uvicorn.workers.UvicornWorker"]