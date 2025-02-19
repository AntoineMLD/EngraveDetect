import sqlite3
import pyodbc
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "..", "data", "verres.db")


# Configuration de la connexion Azure SQL
SERVER = "adventureworks-server-hdf.database.windows.net"
DATABASE = "engravedetect-db"
USERNAME = "jvcb"
PASSWORD = "cbjv592023!"

AZURE_CONN_STRING = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)


def connect_sqlite():
    """Connexion à la base SQLite"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion SQLite : {e}")
        return None


def connect_azure():
    """Connexion à la base Azure SQL"""
    try:
        conn = pyodbc.connect(AZURE_CONN_STRING)
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion Azure SQL : {e}")
        return None


def migrate_table(table_name, sqlite_conn, azure_conn):
    """Transfert des données d'une table SQLite vers Azure SQL"""
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", sqlite_conn)

        if df.empty:
            print(f"⚠️ Table {table_name} vide, pas d'import.")
            return

        cursor = azure_conn.cursor()

        # Générer les colonnes et placeholders
        cols = ", ".join(df.columns)
        placeholders = ", ".join(["?"] * len(df.columns))

        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

        # Vérifier si les données existent déjà (évite les doublons)
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count_before = cursor.fetchone()[0]

        # Insertion en masse des données
        for row in df.itertuples(index=False, name=None):
            try:
                cursor.execute(sql, row)
            except pyodbc.IntegrityError:
                print(f"⚠️ Donnée déjà existante ignorée pour {table_name} : {row}")
        
        azure_conn.commit()

        # Vérifier combien de lignes ont été ajoutées
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count_after = cursor.fetchone()[0]
        inserted = count_after - count_before

        print(f"✅ {inserted} lignes insérées dans {table_name}")

    except Exception as e:
        print(f"❌ Erreur lors de l'import de {table_name} : {e}")


def main():
    """Fonction principale d'exécution"""
    sqlite_conn = connect_sqlite()
    azure_conn = connect_azure()

    if not sqlite_conn or not azure_conn:
        print("❌ Impossible de migrer les données, connexion échouée.")
        return

    tables = ["verres", "symboles", "verres_symboles"]

    for table in tables:
        migrate_table(table, sqlite_conn, azure_conn)

    # Fermeture des connexions
    sqlite_conn.close()
    azure_conn.close()
    print("✅ Migration terminée avec succès !")


if __name__ == "__main__":
    main()
