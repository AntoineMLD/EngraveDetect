#!/usr/bin/env python3
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration Azure Cognitive Search
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "verres-index"

def create_search_client():
    """Crée un client de recherche"""
    return SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

def search_verres(client, query, **kwargs):
    """Effectue une recherche dans l'index"""
    try:
        response = client.search(
            search_text=query,
            include_total_count=True,
            **kwargs
        )
        
        # Si on attend des facettes, retourner la réponse complète
        if kwargs.get('facets'):
            return response
            
        # Sinon, retourner la liste des résultats
        return list(response)
    except Exception as e:
        print(f"Erreur lors de la recherche: {str(e)}")
        raise

def test_basic_search():
    """Test de recherche basique"""
    client = create_search_client()
    
    print("\n=== Test de recherche basique ===")
    query = "essilor"
    print(f"\nRecherche de '{query}':")
    
    # Utiliser select pour limiter les champs retournés
    results = search_verres(
        client, 
        query,
        select=["nom", "variante", "fournisseur"]
    )
    
    # Utiliser un set pour éviter les doublons
    seen = set()
    for result in results:
        # Créer une clé unique pour chaque verre
        key = f"{result['nom']}_{result.get('variante', '')}"
        if key not in seen:
            seen.add(key)
            print(f"\nVerre: {result['nom']}")
            if result.get('variante'):
                print(f"Variante: {result['variante']}")
            if result.get('fournisseur'):
                print(f"Fournisseur: {result['fournisseur']['nom']}")
            if hasattr(result, '@search.score'):
                print(f"Score: {result['@search.score']}")
            
            # Limiter à 5 résultats uniques
            if len(seen) >= 5:
                break

def test_filtered_search():
    """Test de recherche avec filtres"""
    client = create_search_client()
    
    print("\n=== Test de recherche avec filtres ===")
    
    # Recherche avec filtre sur l'indice
    filter_expr = "indice ge 1.5"
    print(f"\nRecherche des verres avec indice >= 1.5:")
    
    results = search_verres(
        client,
        query="*",
        filter=filter_expr,
        order_by=["indice desc"],
        select=["nom", "indice", "fournisseur"]
    )
    
    # Utiliser un set pour éviter les doublons
    seen = set()
    for result in results:
        # Créer une clé unique pour chaque verre
        key = f"{result['nom']}_{result.get('indice')}"
        if key not in seen:
            seen.add(key)
            print(f"\nVerre: {result['nom']}")
            print(f"Indice: {result['indice']}")
            if result.get('fournisseur'):
                print(f"Fournisseur: {result['fournisseur']['nom']}")
            
            # Limiter à 5 résultats uniques
            if len(seen) >= 5:
                break

def test_faceted_search():
    """Test de recherche avec facettes"""
    client = create_search_client()
    
    print("\n=== Test de recherche avec facettes ===")
    
    # Recherche avec facettes sur les fournisseurs
    results = search_verres(
        client,
        query="*",
        facets=["fournisseur/nom"],
        top=0  # On ne s'intéresse qu'aux facettes
    )
    
    print("\nDistribution par fournisseur:")
    if hasattr(results, 'get_facets'):
        facets = results.get_facets()
        if facets and "fournisseur/nom" in facets:
            for facet in facets["fournisseur/nom"]:
                if facet['value']:  # Ignorer les valeurs nulles
                    print(f"{facet['value']}: {facet['count']} verres")
        else:
            print("Aucune facette trouvée pour les fournisseurs")
    else:
        print("Les facettes ne sont pas disponibles dans les résultats")

def main():
    """Fonction principale"""
    try:
        print("Démarrage des tests de recherche...")
        
        # Test de recherche basique
        test_basic_search()
        
        # Test de recherche avec filtres
        test_filtered_search()
        
        # Test de recherche avec facettes
        test_faceted_search()
        
        print("\nTests terminés avec succès!")
        
    except Exception as e:
        print(f"\nErreur lors des tests: {str(e)}")
        raise

if __name__ == "__main__":
    main() 