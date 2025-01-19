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

# Vérifier si la base de données existe
info_message "Vérification de la base de données..."
if [ ! -f "data/verres.db" ]; then
    error_message "Base de données non trouvée. Veuillez exécuter setup_db.sh d'abord."
fi
success_message "Base de données trouvée"

# Vérifier la présence des fichiers CSV
ENHANCED_DIR="../scrapers/scrapers/datalake/enhanced/data"
info_message "Vérification des fichiers de données..."
if [ ! -d "$ENHANCED_DIR" ]; then
    error_message "Dossier $ENHANCED_DIR non trouvé"
fi

CSV_COUNT=$(ls -1 "$ENHANCED_DIR"/*.csv 2>/dev/null | wc -l)
if [ "$CSV_COUNT" -eq 0 ]; then
    error_message "Aucun fichier CSV trouvé dans $ENHANCED_DIR"
fi
success_message "$CSV_COUNT fichiers CSV trouvés"

# Créer le dossier logs s'il n'existe pas
mkdir -p logs

# Import des données
info_message "Début de l'import des données..."

# Remonter d'un niveau et exécuter l'import Python
cd ..
PYTHONPATH=$PYTHONPATH:. python -c "from database.scripts.import_data import import_data; import_data()"
PYTHON_RESULT=$?
cd database

if [ $PYTHON_RESULT -eq 0 ]; then
    success_message "Import des données terminé avec succès"
else
    error_message "Erreur lors de l'import des données"
fi

# Afficher les statistiques de la base de données
info_message "Statistiques de la base de données :"
cd ..
python -c "
from database.config.database import get_db
from database.models.base import Verre, Fournisseur, Materiau, Gamme, Serie, Traitement

with get_db() as db:
    print(f'Nombre de verres : {db.query(Verre).count()}')
    print(f'Nombre de fournisseurs : {db.query(Fournisseur).count()}')
    print(f'Nombre de matériaux : {db.query(Materiau).count()}')
    print(f'Nombre de gammes : {db.query(Gamme).count()}')
    print(f'Nombre de séries : {db.query(Serie).count()}')
    print(f'Nombre de traitements : {db.query(Traitement).count()}')
"
cd database

success_message "Import terminé avec succès!"

# Afficher les instructions finales
echo -e "\n${YELLOW}Pour utiliser la base de données :${NC}"
echo "1. Importez les modèles : from database.models.base import Verre, Fournisseur, Materiau, Gamme, Serie, Traitement"
echo "2. Utilisez le gestionnaire de contexte : from database.config.database import get_db"
echo -e "\n${YELLOW}Les logs sont disponibles dans :${NC} logs/db_YYYYMMDD.log"