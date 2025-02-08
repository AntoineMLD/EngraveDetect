# Stage de build
FROM python:3.10-slim as builder

WORKDIR /app

# Installation des dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY model/requirements.txt .

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

# Copie du code source du modèle
COPY model/ ./model/

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    python3-tk \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Création des répertoires nécessaires
RUN mkdir -p model/models model/templates model/debug

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# CPU only
ENV CUDA_VISIBLE_DEVICES=""

# Exposition du port pour l'API du modèle
EXPOSE 5000

# Commande de démarrage
CMD ["python", "-m", "model.serve"] 