#!/bin/bash

# Exécute le script pour lancer tous les spiders
echo "Lancement de tous les spiders..."
python3 scrapers/scrapers/run_all_spiders.py

# Vérifie si l'exécution des spiders a réussi
if [ $? -eq 0 ]; then
    echo "Tous les spiders ont été exécutés avec succès."
    # Exécute le script de nettoyage des données
    echo "Lancement du nettoyeur de données..."
    python3 scrapers/scrapers/utils/data_cleaner.py
else
    echo "Échec de l'exécution des spiders. Le nettoyeur de données ne sera pas lancé."
fi