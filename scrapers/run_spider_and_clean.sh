#!/bin/bash


PROJECT_NAME="scrapers"
SPIDER_NAME="glass_spider"
DATA_CLEANER_SCRIPT="scrapers/utils/data_cleaner.py"  

# Lance le spider Scrapy
echo "Lancement du spider Scrapy..."
scrapy crawl $SPIDER_NAME

# Vérifie si le spider a réussi
if [ $? -eq 0 ]; then
    echo "Le spider a réussi. Lancement du script de nettoyage..."
    
    # Lance le script de nettoyage
    python $DATA_CLEANER_SCRIPT  
else
    echo "Le spider a rencontré une erreur. Le script de nettoyage ne sera pas exécuté."
fi
