# EngraveDetect

## Description

EngraveDetect est un projet conçu pour gérer et analyser les données liées aux verres optiques, y compris les fournisseurs, matériaux, gammes, séries, traitements, et verres eux-mêmes. Il utilise FastAPI pour fournir une API RESTful permettant d'interagir avec une base de données SQLite.

## Fonctionnalités

- **Gestion des fournisseurs** : Créer, lire, mettre à jour et supprimer des fournisseurs.
- **Gestion des matériaux** : Créer, lire, mettre à jour et supprimer des matériaux.
- **Gestion des gammes** : Créer, lire, mettre à jour et supprimer des gammes.
- **Gestion des séries** : Créer, lire, mettre à jour et supprimer des séries.
- **Gestion des traitements** : Créer, lire, mettre à jour et supprimer des traitements.
- **Gestion des verres** : Lire les informations détaillées sur les verres, y compris leurs traitements associés.

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/engravedetect.git
   cd engravedetect
   ```

2. Créez un environnement virtuel et activez-le :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Initialisez la base de données :
   ```bash
   bash database/setup_db.sh
   ```

5. Importez les données initiales :
   ```bash
   python database/scripts/import_data.py
   ```

## Utilisation

1. Lancez le serveur FastAPI :
   ```bash
   uvicorn api.main:app --reload
   ```

2. Accédez à la documentation interactive de l'API à l'adresse [http://localhost:8000/docs](http://localhost:8000/docs).

## Structure du Projet

- `api/`: Contient les routes de l'API et les dépendances.
- `database/`: Contient la configuration de la base de données, les modèles et les scripts d'initialisation.
- `requirements.txt`: Liste des dépendances Python nécessaires au projet.

## Schéma de la Base de Données

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


## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Contact

Pour toute question ou suggestion concernant ce projet, veuillez contacter l'équipe de développement.




