#!/usr/bin/env python3
import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SqlIntegratedChangeTrackingPolicy,
)
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration Azure Cognitive Search
SEARCH_ENDPOINT = os.getenv(
    "AZURE_SEARCH_ENDPOINT", "https://engravedetect-search.search.windows.net"
)
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY", "YOUR_SEARCH_KEY")
INDEX_NAME = "verres-index"
DATA_SOURCE_NAME = "azure-sql-verres"
INDEXER_NAME = "verres-indexer"

# Configuration Azure SQL
SQL_CONNECTION_STRING = os.getenv(
    "AZURE_SQL_CONNECTION_STRING",
    "Server=adventureworks-server-hdf.database.windows.net;Database=engravedetect-db;User Id=jvcb;Password=cbjv592023!",
)


def create_data_source(client):
    """Crée la source de données pour Azure SQL"""
    data_source = SearchIndexerDataSourceConnection(
        name=DATA_SOURCE_NAME,
        type="azuresql",
        connection_string=SQL_CONNECTION_STRING,
        container=SearchIndexerDataContainer(
            name="verres",
            query="""
            SELECT 
                CAST(v.id as NVARCHAR(50)) as id,
                v.nom,
                v.variante,
                v.hauteur_min,
                v.hauteur_max,
                v.indice,
                v.url_gravure,
                v.url_source,
                v.created_at,
                v.updated_at,
                
                -- Fournisseur
                JSON_OBJECT(
                    'id': f.id,
                    'nom': f.nom
                ) as fournisseur,
                
                -- Materiau
                JSON_OBJECT(
                    'id': m.id,
                    'nom': m.nom
                ) as materiau,
                
                -- Gamme
                JSON_OBJECT(
                    'id': g.id,
                    'nom': g.nom
                ) as gamme,
                
                -- Serie
                JSON_OBJECT(
                    'id': s.id,
                    'nom': s.nom
                ) as serie,
                
                -- Symboles (collection)
                (
                    SELECT JSON_QUERY('[' + STRING_AGG(
                        JSON_OBJECT(
                            'id': sym.id,
                            'nom': sym.nom,
                            'description': sym.description,
                            'score_confiance': vs.score_confiance
                        ), ','
                    ) + ']')
                    FROM verres_symboles vs
                    JOIN symboles sym ON vs.symbole_id = sym.id
                    WHERE vs.verre_id = v.id
                ) as symboles,
                
                -- Traitements (collection)
                (
                    SELECT JSON_QUERY('[' + STRING_AGG(
                        JSON_OBJECT(
                            'id': t.id,
                            'nom': t.nom,
                            'type': t.type
                        ), ','
                    ) + ']')
                    FROM verres_traitements vt
                    JOIN traitements t ON vt.traitement_id = t.id
                    WHERE vt.verre_id = v.id
                ) as traitements
                
            FROM verres v
            LEFT JOIN fournisseurs f ON v.fournisseur_id = f.id
            LEFT JOIN materiaux m ON v.materiau_id = m.id
            LEFT JOIN gammes g ON v.gamme_id = g.id
            LEFT JOIN series s ON v.serie_id = s.id
            """,
        ),
    )

    try:
        result = client.create_or_update_data_source_connection(data_source)
        print(
            f"Source de données '{DATA_SOURCE_NAME}' créée ou mise à jour avec succès"
        )
        return result
    except Exception as e:
        print(f"Erreur lors de la création de la source de données: {str(e)}")
        raise


def create_indexer(client):
    """Crée l'indexeur pour synchroniser les données"""
    indexer = SearchIndexer(
        name=INDEXER_NAME,
        data_source_name=DATA_SOURCE_NAME,
        target_index_name=INDEX_NAME,
        schedule=None,  # Pas de planification automatique
        parameters={
            "batchSize": 1000,
            "maxFailedItems": 0,
            "maxFailedItemsPerBatch": 0,
        },
    )

    try:
        result = client.create_or_update_indexer(indexer)
        print(f"Indexeur '{INDEXER_NAME}' créé ou mis à jour avec succès")
        return result
    except Exception as e:
        print(f"Erreur lors de la création de l'indexeur: {str(e)}")
        raise


def run_indexer(client):
    """Lance l'indexation"""
    try:
        client.run_indexer(INDEXER_NAME)
        print("Indexation démarrée avec succès")
    except Exception as e:
        print(f"Erreur lors du lancement de l'indexation: {str(e)}")
        raise


def main():
    """Fonction principale"""
    try:
        print("Création du client Azure Cognitive Search...")
        client = SearchIndexerClient(
            endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_KEY)
        )

        print("\nCréation de la source de données...")
        create_data_source(client)

        print("\nCréation de l'indexeur...")
        create_indexer(client)

        print("\nLancement de l'indexation...")
        run_indexer(client)

        print("\nConfiguration de l'indexation terminée avec succès!")

    except Exception as e:
        print(f"\nErreur lors de la configuration: {str(e)}")
        raise


if __name__ == "__main__":
    main()
