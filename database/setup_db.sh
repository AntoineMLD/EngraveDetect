#!/bin/bash

# Couleurs pour le formatage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages de succès
success_message() {
    echo -e "${GREEN}✔ $1${NC}"
}

# Fonction pour afficher les messages d'erreur
error_message() {
    echo -e "${RED}✘ $1${NC}"
    exit 1
}

# Fonction pour afficher les messages d'information
info_message() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Charger les variables d'environnement
info_message "Chargement des variables d'environnement..."
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '#' | xargs)
    success_message "Variables d'environnement chargées"
else
    error_message "Fichier .env non trouvé dans le répertoire parent"
fi

# Vérifier si PostgreSQL est installé
if ! command -v psql &> /dev/null; then
    error_message "PostgreSQL n'est pas installé. Veuillez l'installer avant de continuer."
fi

# Vérifier si la base de données existe déjà
info_message "Vérification de l'existence de la base de données..."
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    info_message "La base de données $DB_NAME existe déjà"
else
    info_message "Création de la base de données $DB_NAME..."
    if PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME; then
        success_message "Base de données créée avec succès"
    else
        error_message "Erreur lors de la création de la base de données"
    fi
fi

# Créer le dossier logs s'il n'existe pas
mkdir -p logs

# Initialiser la base de données avec SQLAlchemy
info_message "Initialisation des tables dans la base de données..."

# Remonter d'un niveau, exécuter Python, puis revenir
cd ..
python -c "from database.models.base import init_models; init_models()"
PYTHON_RESULT=$?
cd database

if [ $PYTHON_RESULT -eq 0 ]; then
    success_message "Tables créées avec succès"
else
    error_message "Erreur lors de la création des tables"
fi

# Vérification finale de la connexion
info_message "Vérification de la structure de la base de données..."
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\dt'; then
    success_message "Base de données initialisée avec succès"
    echo -e "\n${GREEN}✔ Installation terminée avec succès !${NC}"
else
    error_message "Erreur lors de la vérification finale"
fi

# Afficher les instructions finales
echo -e "\n${YELLOW}Pour utiliser la base de données :${NC}"
echo "1. Importez les modèles : from database.models.base import Verres, Tags, Fournisseurs"
echo "2. Utilisez le gestionnaire de contexte : from database.config.database import get_db"
echo -e "\n${YELLOW}Les logs seront disponibles dans :${NC} logs/db_YYYYMMDD.log"