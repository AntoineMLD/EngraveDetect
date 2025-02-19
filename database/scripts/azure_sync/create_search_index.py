#!/usr/bin/env python3
import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    ScoringProfile,
    SearchableField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    TextWeights,
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


def create_search_client():
    """Crée un client Azure Cognitive Search"""
    return SearchIndexClient(
        endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_KEY)
    )


def create_verre_index(client):
    """Crée l'index de recherche pour les verres"""

    # Définition des champs de l'index
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(
            name="nom",
            type=SearchFieldDataType.String,
            searchable=True,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="variante",
            type=SearchFieldDataType.String,
            searchable=True,
            filterable=True,
        ),
        SimpleField(
            name="hauteur_min",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="hauteur_max",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="indice",
            type=SearchFieldDataType.Double,
            filterable=True,
            sortable=True,
        ),
        SearchableField(name="url_gravure", type=SearchFieldDataType.String),
        SearchableField(name="url_source", type=SearchFieldDataType.String),
        # Relations
        ComplexField(
            name="fournisseur",
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.Int64),
                SearchableField(
                    name="nom",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                    facetable=True,
                ),
            ],
        ),
        ComplexField(
            name="materiau",
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.Int64),
                SearchableField(
                    name="nom",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                    facetable=True,
                ),
            ],
        ),
        ComplexField(
            name="gamme",
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.Int64),
                SearchableField(
                    name="nom",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                    facetable=True,
                ),
            ],
        ),
        ComplexField(
            name="serie",
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.Int64),
                SearchableField(
                    name="nom",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                    facetable=True,
                ),
            ],
        ),
        # Champs pour les symboles et traitements
        ComplexField(
            name="symboles",
            collection=True,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.Int64),
                SearchableField(
                    name="nom",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                ),
                SearchableField(
                    name="description", type=SearchFieldDataType.String, searchable=True
                ),
                SimpleField(
                    name="score_confiance",
                    type=SearchFieldDataType.Double,
                    filterable=True,
                ),
            ],
        ),
        ComplexField(
            name="traitements",
            collection=True,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.Int64),
                SearchableField(
                    name="nom",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                ),
                SearchableField(
                    name="type",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                ),
            ],
        ),
        # Métadonnées
        SimpleField(
            name="created_at",
            type=SearchFieldDataType.DateTimeOffset,
            filterable=True,
            sortable=True,
        ),
        SimpleField(
            name="updated_at",
            type=SearchFieldDataType.DateTimeOffset,
            filterable=True,
            sortable=True,
        ),
    ]

    # Configuration CORS
    cors_options = CorsOptions(allowed_origins=["*"])

    # Profil de scoring pour prioriser certains champs
    scoring_profile = ScoringProfile(
        name="defaultScoring",
        text_weights=TextWeights(
            weights={
                "nom": 5,
                "variante": 4,
                "fournisseur/nom": 3,
                "gamme/nom": 2,
                "serie/nom": 2,
                "symboles/nom": 1,
            }
        ),
    )

    # Création de l'index
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        cors_options=cors_options,
        scoring_profiles=[scoring_profile],
    )

    try:
        result = client.create_or_update_index(index)
        print(f"Index '{INDEX_NAME}' créé ou mis à jour avec succès")
        return result
    except Exception as e:
        print(f"Erreur lors de la création de l'index: {str(e)}")
        raise


def delete_index_if_exists(client):
    """Supprime l'index s'il existe"""
    try:
        client.delete_index(INDEX_NAME)
        print(f"Index '{INDEX_NAME}' supprimé avec succès")
    except Exception as e:
        # Ignore l'erreur si l'index n'existe pas
        if "ResourceNotFound" not in str(e):
            print(f"Erreur lors de la suppression de l'index: {str(e)}")
            raise


def main():
    """Fonction principale"""
    try:
        print("Création du client Azure Cognitive Search...")
        client = create_search_client()

        print("\nSuppression de l'index existant...")
        delete_index_if_exists(client)

        print("\nCréation de l'index de recherche...")
        create_verre_index(client)

        print("\nConfiguration de l'indexation terminée avec succès!")

    except Exception as e:
        print(f"\nErreur lors de la configuration: {str(e)}")
        raise


if __name__ == "__main__":
    main()
