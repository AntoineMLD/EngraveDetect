#!/bin/bash

PROJECT_NAME="scrapers"
SPIDER_NAME="glass_spider"
DATA_CLEANER_SCRIPT="scrapers/utils/data_cleaner.py"

# Fonction pour afficher une barre de progression
show_progress() {
    local bar_width=50
    local fill='#'
    local empty='-'
    local percent=0

    while kill -0 $1 2>/dev/null; do
        let filled=percent*bar_width/100
        let empty_space=bar_width-filled
        
        printf "\rProgression : ["
        printf "%${filled}s" | tr ' ' "$fill"
        printf "%${empty_space}s" | tr ' ' "$empty"
        printf "] %3d%%" $percent
        
        ((percent+=1))
        if ((percent > 99)); then
            percent=0
        fi
        sleep 0.2
    done
    
    # Complète la barre à 100% à la fin
    printf "\rProgression : ["
    printf "%${bar_width}s" | tr ' ' "$fill"
    printf "] 100%%\n"
}

# Lance le spider Scrapy
echo "Lancement du spider Scrapy..."
scrapy crawl $SPIDER_NAME &
spider_pid=$!

# Affiche la barre pendant que le spider tourne
show_progress $spider_pid &
progress_pid=$!

# Attend que le spider finisse
wait $spider_pid
spider_status=$?

if [ $spider_status -eq 0 ]; then
    echo "Le spider a réussi. Lancement du script de nettoyage..."
    
    # Lance le script de nettoyage
    python $DATA_CLEANER_SCRIPT &
    cleaner_pid=$!
    
    # Affiche la barre pour le nettoyage
    show_progress $cleaner_pid &
    progress_pid=$!
    
    wait $cleaner_pid
    cleaner_status=$?
    
    if [ $cleaner_status -eq 0 ]; then
        echo "Nettoyage terminé avec succès."
    else
        echo "Erreur lors du nettoyage des données."
    fi
else
    echo "Le spider a rencontré une erreur. Le script de nettoyage ne sera pas exécuté."
fi