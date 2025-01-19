# Documentation du Projet de Scraping de Verres Optiques

## 1. Vue d'ensemble du projet

### Objectif
Le projet vise à collecter et structurer les données des verres optiques de différents fournisseurs via le site france-optique.com. Ces données sont essentielles pour maintenir une base de données à jour des produits optiques disponibles sur le marché français.

### Architecture technique
- **Language**: Python
- **Framework principal**: Scrapy
- **Base de données**: SQLite
- **Structure des données**: Format CSV pour l'import, SQLite pour le stockage
- **Organisation**: Architecture en couches (spiders, pipelines, data cleaning)

## 2. Structure de la Base de Données

### Schéma de la Base de Données
![Schéma de la base de données](image.png)

### Tables principales
- **verres**: Table centrale contenant les informations des verres optiques
- **fournisseurs**: Référentiel des fournisseurs
- **materiaux**: Types de matériaux utilisés
- **gammes**: Gammes de produits
- **series**: Séries de produits
- **traitements**: Types de traitements disponibles
- **verres_traitements**: Table de liaison entre verres et traitements

### Relations
- Un verre appartient à un fournisseur (1:N)
- Un verre peut avoir un matériau (1:N)
- Un verre appartient à une gamme (1:N)
- Un verre peut appartenir à une série (1:N)
- Un verre peut avoir plusieurs traitements (N:N)

### Structure détaillée des tables

#### Table verres
- `id`: Identifiant unique (PK)
- `nom`: Nom du verre
- `variante`: Variante du verre (nullable)
- `hauteur_min`: Hauteur minimale (nullable)
- `hauteur_max`: Hauteur maximale (nullable)
- `indice`: Indice de réfraction (nullable)
- `url_gravure`: URL de la gravure (nullable)
- `url_source`: URL source (nullable)
- `fournisseur_id`: Référence au fournisseur (FK)
- `materiau_id`: Référence au matériau (FK, nullable)
- `gamme_id`: Référence à la gamme (FK)
- `serie_id`: Référence à la série (FK, nullable)

#### Table traitements
- `id`: Identifiant unique (PK)
- `nom`: Nom du traitement
- `type`: Type de traitement ('protection' ou 'photochromique')

#### Table fournisseurs
- `id`: Identifiant unique (PK)
- `nom`: Nom du fournisseur (unique)

#### Table materiaux
- `id`: Identifiant unique (PK)
- `nom`: Nom du matériau (unique)

#### Table gammes
- `id`: Identifiant unique (PK)
- `nom`: Nom de la gamme (unique)

#### Table series
- `id`: Identifiant unique (PK)
- `nom`: Nom de la série (unique)

#### Table verres_traitements
- `verre_id`: Référence au verre (PK, FK)
- `traitement_id`: Référence au traitement (PK, FK)

## 3. Structure des données

### Format des fichiers
scrapers/
├── datalake/
│ ├── staging/
│ │ └── data/
│ └── enhanced/
│ └── data/

## 4. Installation et Configuration

### Prérequis
- Python 3.8+
- pip
- virtualenv (recommandé)
- DBeaver (ou autre client SQL) pour explorer la base de données

### Installation
#Créer un environnement virtuel
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


