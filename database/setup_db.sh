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

# Obtenir le chemin absolu du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Se placer dans le répertoire du script
cd "$SCRIPT_DIR"

# Créer la structure des dossiers avec les bons droits
info_message "Création de la structure des dossiers..."
mkdir -p data
chmod 777 data
mkdir -p logs
chmod 777 logs
success_message "Structure des dossiers créée"

# Initialiser la base de données SQLite
info_message "Initialisation de la base de données SQLite..."
cd ..
PYTHONPATH=$PWD python -c "from database.models.base import init_models; init_models()"
PYTHON_RESULT=$?
cd database

if [ $PYTHON_RESULT -eq 0 ]; then
    success_message "Base de données initialisée avec succès"
else
    error_message "Erreur lors de l'initialisation de la base de données"
fi

# Vérification finale
info_message "Vérification de la structure de la base de données..."
if [ -f "data/verres.db" ]; then
    success_message "Base de données créée avec succès"
    echo -e "\n${GREEN}✔ Installation terminée avec succès !${NC}"
else
    error_message "La base de données n'a pas été créée correctement"
fi

# Afficher les instructions finales
echo -e "\n${YELLOW}Pour utiliser la base de données :${NC}"
echo "1. Importez les modèles : from database.models.base import Verre, Fournisseur, Materiau, Gamme, Serie, Traitement"
echo "2. Utilisez le gestionnaire de contexte : from database.config.database import get_db"
echo -e "\n${YELLOW}Les logs seront disponibles dans :${NC} logs/db_YYYYMMDD.log"