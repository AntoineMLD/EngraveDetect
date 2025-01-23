# EngraveDetect

## Description

EngraveDetect est une application complète de gestion et d'analyse des verres optiques. Ce système permet de gérer l'ensemble du cycle de vie des verres optiques, depuis leur référencement jusqu'à leur traitement, en passant par la gestion des fournisseurs et des caractéristiques techniques.

## Table des matières
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Architecture du Projet](#architecture-du-projet)
- [API Reference](#api-reference)
- [Base de données](#base-de-données)
- [Tests](#tests)
- [Sécurité](#sécurité)
- [Déploiement](#déploiement)
- [Contribution](#contribution)
- [Licence](#licence)
- [Support](#support)

## Fonctionnalités

### Gestion des Données
- **Fournisseurs** : 
  - Création et gestion des profils fournisseurs
  - Suivi des informations de contact
  - Historique des interactions

- **Matériaux** :
  - Catalogue complet des matériaux disponibles
  - Caractéristiques techniques détaillées
  - Compatibilité avec les traitements

- **Gammes et Séries** :
  - Organisation hiérarchique des produits
  - Gestion des gammes par fournisseur
  - Classification des séries spéciales

- **Traitements** :
  - Catalogue des traitements disponibles
  - Compatibilité avec les matériaux
  - Processus d'application

- **Verres** :
  - Fiches techniques détaillées
  - Association avec les traitements
  - Traçabilité complète

### Fonctionnalités Techniques
- API RESTful complète
- Authentication JWT
- Documentation interactive (Swagger/OpenAPI)
- Gestion des erreurs robuste
- Logging détaillé
- Validation des données

## Prérequis

- Python 3.8 ou supérieur
- SQLite 3
- Git
- Environnement virtuel Python (recommandé)

## Installation

1. **Clonage du dépôt**
   ```bash
   git clone https://github.com/votre-utilisateur/engravedetect.git
   cd engravedetect
   ```

2. **Création de l'environnement virtuel**
   ```bash
   python -m venv venv
   # Sur Windows
   .\venv\Scripts\activate
   # Sur Linux/MacOS
   source venv/bin/activate
   ```

3. **Installation des dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration de l'environnement**
   ```bash
   cp .env.example .env
   # Éditez le fichier .env avec vos paramètres
   ```

5. **Initialisation de la base de données**
   ```bash
   bash database/setup_db.sh
   ```

6. **Import des données initiales**
   ```bash
   bash database/import_data.sh
   ```

## Configuration

Le fichier `.env` doit contenir les variables suivantes :
```env
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=votre_clé_secrète
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Utilisation

1. **Démarrage du serveur**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Accès aux interfaces**
   - Documentation API : http://localhost:8000/docs
   - Documentation alternative : http://localhost:8000/redoc
   - API Base URL : http://localhost:8000/api/v1

## Architecture du Projet

```
engravedetect/
├── api/
│   ├── dependencies/      # Dépendances de l'API (auth, etc.)
│   ├── routes/           # Routes de l'API par ressource
│   └── main.py          # Point d'entrée de l'API
├── database/
│   ├── config/          # Configuration de la base de données
│   ├── models/          # Modèles SQLAlchemy
│   └── scripts/         # Scripts d'initialisation et import
├── tests/               # Tests unitaires et d'intégration
├── .env                 # Variables d'environnement
├── requirements.txt     # Dépendances Python
└── README.md           # Documentation
```

## API Reference

### Endpoints Principaux

#### Fournisseurs
- `GET /api/v1/fournisseurs/` - Liste tous les fournisseurs
- `POST /api/v1/fournisseurs/` - Crée un nouveau fournisseur
- `GET /api/v1/fournisseurs/{id}` - Détails d'un fournisseur
- `PUT /api/v1/fournisseurs/{id}` - Met à jour un fournisseur
- `DELETE /api/v1/fournisseurs/{id}` - Supprime un fournisseur

[Documentation complète similaire pour les autres endpoints]

## Base de données

### Schéma Relationnel

![Schéma de la base de données](image.png)

### Tables Principales

- **verres**: Table centrale contenant les informations des verres optiques
  - `id`: Identifiant unique
  - `reference`: Référence du verre
  - `fournisseur_id`: Lien vers le fournisseur
  - [autres champs...]

[Description détaillée des autres tables]

## Tests

```bash
# Exécution de tous les tests
pytest

# Tests avec couverture
pytest --cov=app tests/
```

## Sécurité

- Authentication JWT
- Hachage des mots de passe avec Bcrypt
- Validation des données entrantes
- Protection CORS
- Rate limiting

## Déploiement

### Production
1. Configurez les variables d'environnement de production
2. Utilisez un serveur WSGI (Gunicorn recommandé)
3. Configurez un reverse proxy (Nginx recommandé)

```bash
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Support

Pour toute question ou assistance :
- Ouvrez une issue sur GitHub
- Contactez l'équipe de développement à [email]
- Consultez la documentation en ligne




