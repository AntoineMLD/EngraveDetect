# Stage de build
FROM python:3.10-slim as builder

WORKDIR /app

# Installation des dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances dans un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.10-slim

WORKDIR /app

# Copie de l'environnement virtuel du stage de build
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copie du code source
COPY . .

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Création des répertoires nécessaires
RUN mkdir -p model/models model/templates model/debug database/data

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"] 