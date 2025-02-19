#!/usr/bin/env python3
import os
from typing import Dict, List

import pandas as pd
import pyodbc
from dotenv import load_dotenv
from tabulate import tabulate

# Configuration de la connexion
SERVER = "adventureworks-server-hdf.database.windows.net"
DATABASE = "engravedetect-db"
USERNAME = "jvcb"
PASSWORD = "cbjv592023!"
DRIVER = "{ODBC Driver 18 for SQL Server}"


def get_connection_string() -> str:
    """
    Construit la chaîne de connexion pour Azure SQL
    """
    return f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Encrypt=yes;TrustServerCertificate=no;"


def get_table_info() -> List[Dict]:
    """
    Récupère les informations sur toutes les tables de la base de données
    """
    tables_info = []
    try:
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()

        # Requête pour obtenir toutes les tables
        table_query = """
        SELECT 
            t.TABLE_SCHEMA as schema_name,
            t.TABLE_NAME as table_name,
            t.TABLE_TYPE as table_type,
            (
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS c 
                WHERE c.TABLE_SCHEMA = t.TABLE_SCHEMA 
                AND c.TABLE_NAME = t.TABLE_NAME
            ) as column_count
        FROM INFORMATION_SCHEMA.TABLES t
        ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME;
        """

        cursor.execute(table_query)
        tables = cursor.fetchall()

        for table in tables:
            # Requête pour obtenir les colonnes de chaque table
            column_query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION;
            """

            cursor.execute(column_query, (table.schema_name, table.table_name))
            columns = cursor.fetchall()

            tables_info.append(
                {
                    "schema": table.schema_name,
                    "name": table.table_name,
                    "type": table.table_type,
                    "column_count": table.column_count,
                    "columns": [
                        {
                            "name": col.COLUMN_NAME,
                            "type": col.DATA_TYPE,
                            "max_length": col.CHARACTER_MAXIMUM_LENGTH,
                            "nullable": col.IS_NULLABLE,
                            "default": col.COLUMN_DEFAULT,
                        }
                        for col in columns
                    ],
                }
            )

        return tables_info

    except pyodbc.Error as e:
        print(f"Erreur lors de la connexion à la base de données: {str(e)}")
        raise
    finally:
        if "conn" in locals():
            conn.close()


def display_table_info(tables_info: List[Dict]) -> None:
    """
    Affiche les informations des tables de manière formatée
    """
    if not tables_info:
        print("Aucune table trouvée dans la base de données.")
        return

    print("\n=== Structure de la base de données Azure SQL ===\n")

    for table in tables_info:
        print(f"\nTable: {table['schema']}.{table['name']}")
        print(f"Type: {table['type']}")
        print(f"Nombre de colonnes: {table['column_count']}")

        # Création d'un DataFrame pour afficher les colonnes
        columns_df = pd.DataFrame(table["columns"])
        print("\nColonnes:")
        print(tabulate(columns_df, headers="keys", tablefmt="grid", showindex=False))
        print("\n" + "=" * 50)


def main():
    """
    Fonction principale
    """
    try:
        print("Connexion à la base de données Azure SQL...")
        tables_info = get_table_info()
        display_table_info(tables_info)

        # Sauvegarde des informations dans un fichier
        output_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(output_dir, exist_ok=True)

        report_path = os.path.join(output_dir, "azure_db_structure.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Structure de la base de données Azure SQL\n\n")
            for table in tables_info:
                f.write(f"## Table: {table['schema']}.{table['name']}\n")
                f.write(f"Type: {table['type']}\n")
                f.write(f"Nombre de colonnes: {table['column_count']}\n\n")

                columns_df = pd.DataFrame(table["columns"])
                f.write("### Colonnes:\n\n")
                f.write(
                    tabulate(
                        columns_df, headers="keys", tablefmt="pipe", showindex=False
                    )
                )
                f.write("\n\n---\n\n")

        print(f"\nRapport sauvegardé dans: {report_path}")

    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}")
        raise


if __name__ == "__main__":
    main()
