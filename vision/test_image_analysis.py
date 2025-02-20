import sys
import os
import json

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision.services.azure_vision import AzureVisionService

def test_image(image_path: str):
    """
    Teste l'analyse d'une image avec Azure Vision.
    
    Args:
        image_path: Chemin vers l'image à analyser
    """
    try:
        # Initialiser le service
        vision_service = AzureVisionService()
        
        print(f"\nAnalyse de l'image: {image_path}")
        print("-" * 50)
        
        # Prétraitement de l'image
        print("\nPrétraitement de l'image...")
        preprocessed_path = vision_service.preprocess_image(image_path)
        print(f"Image prétraitée: {preprocessed_path}")
        
        # Analyse de l'image
        print("\nAnalyse de l'image avec Azure Vision...")
        results = vision_service.analyze_image(preprocessed_path)
        
        # Affichage des résultats
        if results['status'] == 'success':
            print("\n✅ Analyse réussie!")
            
            # Description de l'image
            print("\n📷 Description de l'image:")
            if results['description_results']:
                for i, desc in enumerate(results['description_results'], 1):
                    print(f"{i}. {desc['description']}")
                    print(f"   Confiance: {desc['confidence']:.2%}")
            else:
                print("Aucune description générée")
            
            # Tags détectés
            print("\n🏷️ Tags détectés:")
            if results['tags_results']:
                for i, tag in enumerate(results['tags_results'], 1):
                    print(f"{i}. {tag['tag']}")
                    print(f"   Confiance: {tag['confidence']:.2%}")
            else:
                print("Aucun tag détecté")
            
            # Texte détecté
            print("\n📝 Texte détecté:")
            if results['text_results']:
                for i, text in enumerate(results['text_results'], 1):
                    print(f"{i}. Texte: {text['text']}")
                    print(f"   Confiance: {text['confidence']:.2%}")
                    print(f"   Position: {text['bounding_box']}")
            else:
                print("Aucun texte détecté")
            
            # Objets/symboles détectés
            print("\n🔍 Objets/symboles détectés:")
            if results['objects_results']:
                for i, obj in enumerate(results['objects_results'], 1):
                    print(f"{i}. Objet: {obj['object']}")
                    print(f"   Confiance: {obj['confidence']:.2%}")
                    print(f"   Position: {obj['bounding_box']}")
            else:
                print("Aucun objet/symbole détecté")
            
            # Sauvegarde des résultats
            output_file = image_path.replace('.', '_results.')
            with open(f"{output_file}.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\nRésultats sauvegardés dans: {output_file}.json")
            
        else:
            print(f"\n❌ Erreur lors de l'analyse: {results['error']}")
    
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_image_analysis.py <chemin_image>")
        sys.exit(1)
    
    test_image(sys.argv[1]) 