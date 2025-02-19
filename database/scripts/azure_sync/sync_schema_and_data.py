#!/usr/bin/env python3
import os
import sqlite3
import pyodbc
from typing import List, Dict, Tuple
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import numpy as np

# Configuration Azure SQL
SERVER = 'adventureworks-server-hdf.database.windows.net'
DATABASE = 'engravedetect-db'
USERNAME = 'jvcb'
PASSWORD = 'cbjv592023!'
DRIVER = '{ODBC Driver 18 for SQL Server}'

# Configuration SQLite
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'verres.db')

def get_azure_connection():
    """Établit une connexion à Azure SQL"""
    conn_str = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Encrypt=yes;TrustServerCertificate=no;'
    return pyodbc.connect(conn_str)

def get_sqlite_connection():
    """Établit une connexion à SQLite"""
    return sqlite3.connect(SQLITE_DB_PATH)

def get_sqlite_tables(conn) -> List[str]:
    """Récupère la liste des tables existantes dans SQLite"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] for row in cursor.fetchall()]

def create_azure_schema():
    """Crée le schéma dans Azure SQL"""
    azure_conn = get_azure_connection()
    cursor = azure_conn.cursor()

    try:
        # Suppression des tables existantes dans l'ordre inverse des dépendances
        print("Suppression des tables existantes...")
        tables_to_drop = [
            'verres_symboles', 'verres_traitements', 'gravures', 'verres', 
            'series', 'gammes', 'materiaux', 'fournisseurs', 'symboles', 
            'traitements'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                azure_conn.commit()
            except Exception as e:
                print(f"Erreur lors de la suppression de la table {table}: {str(e)}")

        # Création des tables dans l'ordre des dépendances
        print("Création des nouvelles tables...")
        
        # Table fournisseurs
        cursor.execute("""
        CREATE TABLE fournisseurs (
            id INT PRIMARY KEY IDENTITY(1,1),
            nom VARCHAR(100) NOT NULL UNIQUE,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table materiaux
        cursor.execute("""
        CREATE TABLE materiaux (
            id INT PRIMARY KEY IDENTITY(1,1),
            nom VARCHAR(100) NOT NULL UNIQUE,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table gammes
        cursor.execute("""
        CREATE TABLE gammes (
            id INT PRIMARY KEY IDENTITY(1,1),
            nom VARCHAR(100) NOT NULL UNIQUE,
            fournisseur_id INT REFERENCES fournisseurs(id),
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table series
        cursor.execute("""
        CREATE TABLE series (
            id INT PRIMARY KEY IDENTITY(1,1),
            nom VARCHAR(100) NOT NULL,
            gamme_id INT REFERENCES gammes(id),
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table traitements
        cursor.execute("""
        CREATE TABLE traitements (
            id INT PRIMARY KEY IDENTITY(1,1),
            nom VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table verres
        cursor.execute("""
        CREATE TABLE verres (
            id INT PRIMARY KEY IDENTITY(1,1),
            nom VARCHAR(100),
            variante VARCHAR(50),
            hauteur_min INT,
            hauteur_max INT,
            indice FLOAT NOT NULL,
            url_gravure VARCHAR(255),
            url_source VARCHAR(255),
            fournisseur_id INT REFERENCES fournisseurs(id),
            materiau_id INT REFERENCES materiaux(id),
            gamme_id INT REFERENCES gammes(id),
            serie_id INT REFERENCES series(id),
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table symboles (correspond à symboles_tags dans SQLite)
        cursor.execute("""
        CREATE TABLE symboles (
            id INT PRIMARY KEY IDENTITY(1,1),
            nom VARCHAR(100) NOT NULL,
            description VARCHAR(1000),
            type VARCHAR(50),
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table verres_symboles
        cursor.execute("""
        CREATE TABLE verres_symboles (
            id INT PRIMARY KEY IDENTITY(1,1),
            verre_id INT REFERENCES verres(id),
            symbole_id INT REFERENCES symboles(id),
            score_confiance FLOAT,
            est_valide BIT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table verres_traitements
        cursor.execute("""
        CREATE TABLE verres_traitements (
            id INT PRIMARY KEY IDENTITY(1,1),
            verre_id INT REFERENCES verres(id),
            traitement_id INT REFERENCES traitements(id),
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
        """)

        # Table gravures
        cursor.execute("""
        CREATE TABLE gravures (
            id INT PRIMARY KEY IDENTITY(1,1),
            verre_id INT REFERENCES verres(id),
            type_gravure VARCHAR(10),
            contenu_textuel VARCHAR(255),
            image_url VARCHAR(500),
            date_ajout DATETIME DEFAULT GETDATE()
        )
        """)

        # Création des index
        print("Création des index...")
        cursor.execute("CREATE INDEX idx_verres_nom ON verres(nom)")
        cursor.execute("CREATE INDEX idx_verres_indice ON verres(indice)")
        cursor.execute("CREATE INDEX idx_fournisseurs_nom ON fournisseurs(nom)")
        cursor.execute("CREATE INDEX idx_materiaux_nom ON materiaux(nom)")
        cursor.execute("CREATE INDEX idx_gammes_nom ON gammes(nom)")
        cursor.execute("CREATE INDEX idx_series_nom ON series(nom)")
        cursor.execute("CREATE INDEX idx_symboles_nom ON symboles(nom)")

        # Création des triggers pour updated_at
        print("Création des triggers...")
        for table in ['verres', 'fournisseurs', 'materiaux', 'gammes', 'series', 
                     'traitements', 'symboles', 'verres_symboles', 'verres_traitements']:
            cursor.execute(f"""
            CREATE TRIGGER tr_{table}_update_timestamp
            ON {table}
            AFTER UPDATE
            AS
            BEGIN
                UPDATE {table}
                SET updated_at = GETDATE()
                FROM {table}
                INNER JOIN inserted
                ON {table}.id = inserted.id
            END
            """)

        azure_conn.commit()
        print("Schéma créé avec succès dans Azure SQL")

    except Exception as e:
        azure_conn.rollback()
        print(f"Erreur lors de la création du schéma: {str(e)}")
        raise
    finally:
        azure_conn.close()

def convert_numpy_types(value):
    """Convertit les types numpy en types Python natifs"""
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.bool_):
        return bool(value)
    return value

def migrate_data():
    """Migre les données de SQLite vers Azure SQL"""
    sqlite_conn = get_sqlite_connection()
    azure_conn = get_azure_connection()
    
    try:
        # Récupération des tables existantes dans SQLite
        existing_tables = get_sqlite_tables(sqlite_conn)
        print(f"\nTables trouvées dans SQLite: {', '.join(existing_tables)}")

        # Mapping des tables SQLite vers Azure
        table_mapping = {
            'fournisseurs': 'fournisseurs',
            'materiaux': 'materiaux',
            'gammes': 'gammes',
            'series': 'series',
            'traitements': 'traitements',
            'verres': 'verres',
            'symboles_tags': 'symboles',  # Mapping de symboles_tags vers symboles
            'verres_symboles': 'verres_symboles',
            'verres_traitements': 'verres_traitements'
        }

        # Liste des tables dans l'ordre de migration
        tables_to_migrate = [
            'fournisseurs',
            'materiaux',
            'gammes',
            'series',
            'traitements',
            'verres',
            'symboles_tags',  # On migre symboles_tags au lieu de symboles
            'verres_symboles',
            'verres_traitements'
        ]

        for sqlite_table in tables_to_migrate:
            if sqlite_table not in existing_tables:
                print(f"\nTable {sqlite_table} non trouvée dans SQLite, ignorée.")
                continue

            azure_table = table_mapping[sqlite_table]
            print(f"\nMigration de {sqlite_table} vers {azure_table}...")
            
            try:
                # Lecture des données SQLite
                df = pd.read_sql_query(f"SELECT * FROM {sqlite_table}", sqlite_conn)
                if df.empty:
                    print(f"Aucune donnée à migrer pour la table {sqlite_table}")
                    continue

                # Suppression des colonnes created_at et updated_at
                if 'created_at' in df.columns:
                    df = df.drop('created_at', axis=1)
                if 'updated_at' in df.columns:
                    df = df.drop('updated_at', axis=1)

                # Obtention des colonnes de la table Azure
                cursor = azure_conn.cursor()
                cursor.execute(f"""
                    SELECT c.name AS COLUMN_NAME,
                           COLUMNPROPERTY(OBJECT_ID('{azure_table}'), c.name, 'IsIdentity') as IS_IDENTITY
                    FROM sys.columns c
                    WHERE object_id = OBJECT_ID('{azure_table}')
                    ORDER BY column_id
                """)
                azure_columns_info = cursor.fetchall()
                azure_columns = [row.COLUMN_NAME for row in azure_columns_info]
                has_identity = any(row.IS_IDENTITY == 1 for row in azure_columns_info)
                identity_column = next((row.COLUMN_NAME for row in azure_columns_info if row.IS_IDENTITY == 1), None)

                # Si la table a une colonne identity mais qu'elle n'est pas dans les données SQLite,
                # on génère des IDs séquentiels
                if has_identity and identity_column and identity_column not in df.columns:
                    df[identity_column] = range(1, len(df) + 1)

                # Filtrage des colonnes pour ne garder que celles qui existent dans Azure
                df_columns = [col for col in df.columns if col in azure_columns]
                df = df[df_columns]

                # Préparation de la requête d'insertion
                placeholders = ','.join(['?' for _ in df_columns])
                insert_query = f"INSERT INTO {azure_table} ({','.join(df_columns)}) VALUES ({placeholders})"

                # Activation de IDENTITY_INSERT si nécessaire
                if has_identity and identity_column in df_columns:
                    cursor.execute(f"SET IDENTITY_INSERT {azure_table} ON")
                
                try:
                    # Insertion des données avec conversion des types
                    for _, row in df.iterrows():
                        try:
                            # Conversion des types numpy en types Python natifs
                            values = tuple(convert_numpy_types(row[col]) for col in df_columns)
                            cursor.execute(insert_query, values)
                        except Exception as e:
                            print(f"Erreur lors de l'insertion dans {azure_table}: {str(e)}")
                            print(f"Requête: {insert_query}")
                            print(f"Colonnes: {df_columns}")
                            print(f"Données: {values}")
                            raise
                    
                    azure_conn.commit()
                    print(f"Migration terminée pour la table {azure_table}: {len(df)} enregistrements")
                
                finally:
                    # Désactivation de IDENTITY_INSERT si nécessaire
                    if has_identity and identity_column in df_columns:
                        cursor.execute(f"SET IDENTITY_INSERT {azure_table} OFF")
                        azure_conn.commit()

            except Exception as e:
                print(f"Erreur lors de la migration de {sqlite_table} vers {azure_table}: {str(e)}")
                raise

        print("\nMigration des données terminée avec succès")

    except Exception as e:
        print(f"Erreur lors de la migration des données: {str(e)}")
        raise
    finally:
        sqlite_conn.close()
        azure_conn.close()

def main():
    """Fonction principale"""
    try:
        print("Début de la synchronisation...")
        
        # Création du schéma dans Azure
        print("\n1. Création du schéma dans Azure SQL...")
        create_azure_schema()
        
        # Migration des données
        print("\n2. Migration des données de SQLite vers Azure SQL...")
        migrate_data()
        
        print("\nSynchronisation terminée avec succès!")
        
    except Exception as e:
        print(f"\nErreur lors de la synchronisation: {str(e)}")
        raise

if __name__ == "__main__":
    main() 