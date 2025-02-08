# Stage de build
FROM python:3.10-slim as builder

WORKDIR /app

# Installation des dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY scrapers/requirements.txt .

# Installation des dépendances dans un environnement virtuel
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Stage final
FROM python:3.10-slim

WORKDIR /app

# Copie de l'environnement virtuel du stage de build
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copie du code source des scrapers
COPY scrapers/ ./scrapers/

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création des répertoires nécessaires
RUN mkdir -p scrapers/data scrapers/logs

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV SCRAPY_SETTINGS_MODULE=scrapers.settings

# Volume pour les données scrapées
VOLUME /app/scrapers/data

# Commande de démarrage (par défaut, peut être surchargée)
CMD ["scrapy", "crawl", "all"] 