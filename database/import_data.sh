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

# Vérifier la présence du fichier CSV
CSV_FILE="C:/Users/antoi/Documents/Projets/Projet Certif/EngraveDetect/scrapers/datalake/enhanced/enhanced_scrapping.csv"
info_message "Vérification du fichier de données..."
if [ ! -f "$CSV_FILE" ]; then
    error_message "Fichier $CSV_FILE non trouvé"
fi
success_message "Fichier de données trouvé"

# Vérifier si PostgreSQL est installé
if ! command -v psql &> /dev/null; then
    error_message "PostgreSQL n'est pas installé. Veuillez l'installer avant de continuer."
fi

# Vérifier la connexion à la base de données
info_message "Vérification de la connexion à la base de données..."
if ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q' > /dev/null 2>&1; then
    error_message "Impossible de se connecter à la base de données $DB_NAME"
fi
success_message "Connexion à la base de données établie"

# Créer le dossier logs s'il n'existe pas
mkdir -p logs

# Import des données
info_message "Début de l'import des données..."

# Remonter d'un niveau et exécuter l'import Python
cd ..
PYTHONPATH=$PYTHONPATH:. python -c "from database.scripts.import_data import import_data; import_data('$CSV_FILE')"
PYTHON_RESULT=$?
cd - > /dev/null

if [ $PYTHON_RESULT -eq 0 ]; then
    success_message "Import des données terminé avec succès"
else
    error_message "Erreur lors de l'import des données"
fi

# Afficher les statistiques
info_message "Statistiques des données importées :"
echo "Nombre de fournisseurs :"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM fournisseurs;" -qt
echo "Nombre de verres :"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM verres;" -qt

success_message "Import terminé avec succès!"

# Afficher les instructions finales
echo -e "\n${YELLOW}Pour utiliser la base de données :${NC}"
echo "1. Importez les modèles : from database.models.base import Verres, Tags, Fournisseurs"
echo "2. Utilisez le gestionnaire de contexte : from database.config.database import get_db"
echo -e "\n${YELLOW}Les logs sont disponibles dans :${NC} logs/db_YYYYMMDD.log"