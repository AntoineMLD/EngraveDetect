# Documentation du Projet de Scraping de Verres Optiques

## 1. Vue d'ensemble du projet

### Objectif
Le projet vise à collecter et structurer les données des verres optiques de différents fournisseurs via le site france-optique.com. Ces données sont essentielles pour maintenir une base de données à jour des produits optiques disponibles sur le marché français.

### Architecture technique
- **Language**: Python
- **Framework principal**: Scrapy
- **Structure des données**: Format CSV
- **Organisation**: Architecture en couches (spiders, pipelines, data cleaning)

## 2. Structure des données

### Données collectées
- Nom du verre
- Gamme
- Série
- Variante
- Hauteur minimale/maximale
- Traitements (protection, photochromique)
- Matériau
- Indice
- Fournisseur
- URLs (gravure, source)

### Format des fichiers

```
scrapers/
├── datalake/
│ ├── staging/
│ │ └── data/
│ └── enhanced/
│ └── data/
```

## 3. Composants principaux

### Spiders
- **GlassSpider**: Spider générique pour la majorité des fournisseurs
- **GlassSpiderHoya**: Spécialisé pour Hoya
- **GlassSpiderIndoOptical**: Spécialisé pour Indo Optical
- **GlassSpiderOptovision**: Spécialisé pour Optovision
- **GlassSpiderParticular**: Pour les cas particuliers
- **GlassSpiderFullXPath**: Utilisant des XPath complets

### Pipeline de données
1. Collecte des données brutes
2. Nettoyage et standardisation
3. Enrichissement
4. Export en format structuré

## 4. Fournisseurs couverts
- SHAMIR FRANCE
- ZEISS VISION CARE FRANCE
- LEICA EYECARE
- VERRES KODAK
- BBGR OPTIQUE
- ESSILOR
- HOYA
- Et autres...

## 5. Processus de maintenance

### Mise à jour des données
- Exécution périodique des spiders
- Validation des données collectées
- Mise à jour de la base de données

### Gestion des erreurs
- Logging détaillé
- Système de retry pour les requêtes échouées
- Alertes en cas d'échec critique

## 6. Points d'attention

### Performances
- Gestion des temps d'attente entre requêtes
- Optimisation des parsers
- Parallélisation des spiders

### Qualité des données
- Validation des formats
- Détection des anomalies
- Standardisation des valeurs

## 7. Évolutions futures possibles
- Ajout de nouveaux fournisseurs
- Amélioration de la détection des changements
- Automatisation complète du pipeline
- Interface de visualisation des données
- API pour accès aux données

## 8. Installation et démarrage

### Prérequis
- Python 3.8+
- pip
- virtualenv (recommandé)

### Installation
```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Exécution
```bash
# Lancer un spider spécifique
scrapy crawl glass_spider

# Lancer tous les spiders
python scrapers/run_all_spiders.py
```
```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## 9. Contribution
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 10. Licence
Ce projet est sous licence privée. Tous droits réservés.

## 11. Contact
Pour toute question ou suggestion concernant ce projet, veuillez contacter l'équipe de développement.


