# Scripts de Synchronisation Azure SQL

Ce dossier contient les scripts nécessaires pour l'inspection et la synchronisation entre la base de données SQLite locale et Azure SQL.

## Prérequis

1. Installer le driver ODBC pour SQL Server :
   - Windows : [SQL Server ODBC Driver](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - Linux : 
     ```bash
     curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
     curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
     sudo apt-get update
     sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
     ```

2. Installer les dépendances Python :
   ```bash
   pip install pyodbc pandas tabulate python-dotenv
   ```

## Scripts disponibles

### 1. inspect_azure_tables.py

Ce script permet d'analyser la structure de la base de données Azure SQL.

**Fonctionnalités :**
- Liste toutes les tables de la base de données
- Affiche les détails de chaque colonne (type, nullable, etc.)
- Génère un rapport au format Markdown dans le dossier `reports`

**Utilisation :**
```bash
python inspect_azure_tables.py
```

Le rapport généré sera disponible dans `reports/azure_db_structure.md`

### 2. sync_schema_and_data.py

Ce script synchronise le schéma de la base de données SQLite avec Azure SQL et migre les données.

**Fonctionnalités :**
- Supprime les tables existantes dans Azure
- Recrée le schéma complet avec les contraintes et index
- Migre toutes les données de SQLite vers Azure
- Préserve les relations et les contraintes d'intégrité
- Gère les timestamps automatiquement

**Utilisation :**
```bash
python sync_schema_and_data.py
```

**Ordre de migration des tables :**
1. fournisseurs
2. materiaux
3. gammes
4. series
5. traitements
6. verres
7. symboles
8. verres_symboles

**⚠️ Attention :**
- Ce script supprime toutes les tables existantes dans Azure
- Assurez-vous d'avoir une sauvegarde si nécessaire
- La migration peut prendre du temps selon le volume de données

## Sécurité

⚠️ **Important** : Les informations de connexion sont actuellement en dur dans les scripts. 
Pour la production, il est recommandé de :
1. Utiliser un fichier .env
2. Utiliser Azure Key Vault
3. Utiliser des variables d'environnement

## Prochaines étapes

1. Ajout de la gestion des erreurs détaillée
2. Support de la migration incrémentielle
3. Ajout de la validation des données migrées
4. Support de la synchronisation bidirectionnelle 