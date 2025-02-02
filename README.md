# EngraveDetect

## Description
EngraveDetect est une application complète qui combine plusieurs fonctionnalités pour la gestion et la détection des gravures de verres optiques :

- **API REST** : Gestion des données des verres et gravures
- **Scraping** : Collecte automatisée des données techniques
- **Interface de dessin** : Outil de création et reconnaissance des gravures
- **Base de données** : Stockage structuré des informations
- **Reconnaissance IA** : Détection automatique des symboles gravés

## État Actuel du Projet

### API REST (Opérationnel)
- Authentification JWT implémentée
- Routes CRUD pour :
  - Fournisseurs
  - Gammes
  - Matériaux
  - Séries
  - Traitements
  - Verres
- Documentation Swagger disponible sur `/docs`

### Base de Données (Opérationnel)
- SQLite avec SQLAlchemy
- Modèles :
  - Verre
  - Fournisseur
  - Gamme
  - Matériau
  - Série
  - Traitement
- Scripts d'import/export des données

### Scraping (Opérationnel)
- Collecte automatisée depuis plusieurs fournisseurs :
  - BBGR OPTIQUE
  - HOYA
  - SEIKO
  - SHAMIR
  - RODENSTOCK
  - Autres...
- Pipeline de nettoyage des données
- Export au format CSV standardisé

### Système de Reconnaissance (Opérationnel)
- Réseau de neurones siamois pour la détection
- Interface de dessin interactive
- Performances :
  - Précision : 92.3%
  - Rappel : 88.7%
  - F1-score : 90.4%
- Fonctionnalités :
  - Détection en temps réel
  - Prétraitement automatique
  - Débogage visuel
  - Gestion des cas incertains

### Interface de Dessin (Opérationnel)
- Interface Tkinter intuitive
- Fonctionnalités :
  - Dessin libre avec épaisseur ajustable
  - Détection automatique des symboles
  - Sauvegarde des dessins
  - Visualisation du processus de détection
  - Feedback en temps réel

## Structure du Projet
```
engravedetect/
├── api/                    # API REST FastAPI
│   ├── routes/            # Points d'entrée de l'API
│   ├── auth/              # Authentification JWT
│   ├── dependencies/      # Dépendances FastAPI
│   └── models/            # Modèles Pydantic
├── database/              # Gestion base de données
│   ├── config/           # Configuration SQLAlchemy
│   ├── models/           # Modèles SQLAlchemy
│   ├── scripts/          # Scripts d'import/export
│   └── utils/            # Utilitaires
├── model/                 # Système de reconnaissance
│   ├── dataset/          # Données d'entraînement
│   ├── models/           # Modèles entraînés
│   ├── templates/        # Templates de référence
│   ├── draw_interface.py # Interface de dessin
│   ├── siamese_model.py  # Architecture du modèle
│   └── [autres modules]  # Modules auxiliaires
├── scrapers/              # Scrapers Scrapy
│   ├── spiders/          # Spiders par fournisseur
│   ├── pipelines/        # Nettoyage des données
│   └── utils/            # Utilitaires
└── scripts/              # Scripts principaux
    ├── runall.sh        # Lancement des scrapers
    └── server.py        # Démarrage du serveur
```

## Installation

### Prérequis
- Python 3.8+
- pip
- virtualenv (recommandé)
- CUDA (optionnel, pour accélération GPU)

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Configuration
1. Copier `.env.example` en `.env`
2. Configurer les variables d'environnement :
```env
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
```

### Initialisation
1. Base de données :
```bash
cd database
./setup_db.sh
```

2. Système de reconnaissance :
```bash
cd model
python create_dataset.py
python create_templates.py
python train_siamese.py
```

## Utilisation

### Démarrage des Services

1. Serveur API :
```bash
python server.py
```
L'API sera disponible sur `http://localhost:8000`

2. Interface de reconnaissance :
```bash
python -m model.draw_interface
```

3. Collecte des données :
```bash
./scripts/runall.sh
```

### Utilisation de l'Interface de Dessin

1. Lancer l'interface :
```bash
python -m model.draw_interface
```

2. Fonctionnalités :
   - Dessiner avec la souris
   - Ajuster l'épaisseur du trait (2-6 pixels)
   - Détecter le symbole (bouton "Détecter")
   - Consulter les résultats et le débogage

## API Endpoints

### Authentification
- POST `/token` : Obtention du token JWT

### Fournisseurs
- GET `/fournisseurs` : Liste des fournisseurs
- GET `/fournisseurs/{id}` : Détails d'un fournisseur
- POST `/fournisseurs` : Création (auth requise)
- PUT `/fournisseurs/{id}` : Modification (auth requise)
- DELETE `/fournisseurs/{id}` : Suppression (auth requise)

[Documentation complète disponible sur `/docs`]

## Maintenance

### Base de données
- Sauvegarde régulière recommandée
- Scripts de migration fournis
- Validation des données importées

### Système de Reconnaissance
- Vérification régulière des templates
- Monitoring des performances
- Réentraînement périodique recommandé

### Scraping
- Mise à jour des spiders si nécessaire
- Validation des données collectées
- Nettoyage régulier du cache

## Support

Pour plus d'informations :
- Documentation technique détaillée dans `/model/README.md`
- Guide de dépannage dans `/docs/troubleshooting.md`
- Issues et bugs sur le repository GitHub

