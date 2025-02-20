from typing import Dict, List, Optional
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image
import io
import time
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class AzureVisionService:
    def __init__(self):
        """Initialise le client Azure Vision."""
        self.endpoint = os.getenv("AZURE_VISION_ENDPOINT")
        self.key = os.getenv("AZURE_VISION_KEY")
        
        if not self.endpoint or not self.key:
            raise ValueError("Les credentials Azure Vision sont manquants dans le fichier .env")
        
        self.client = ComputerVisionClient(
            endpoint=self.endpoint,
            credentials=CognitiveServicesCredentials(self.key)
        )

    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyse une image pour en extraire le texte et les symboles.
        
        Args:
            image_path: Chemin vers l'image à analyser
            
        Returns:
            Dict contenant les résultats de l'analyse
        """
        try:
            # Lecture de l'image
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Analyse complète de l'image
            features = ["Objects", "Tags", "Description"]
            analyze_results = self.client.analyze_image_in_stream(
                image=io.BytesIO(image_data),
                visual_features=features
            )

            # Analyse du texte (OCR)
            read_response = self.client.read_in_stream(
                image=io.BytesIO(image_data),
                raw=True
            )
            
            # Récupération de l'opération ID pour le polling
            operation_location = read_response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]

            # Attente des résultats de l'OCR
            while True:
                read_result = self.client.get_read_result(operation_id)
                if read_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)

            # Extraction du texte
            text_results = []
            if read_result.status == OperationStatusCodes.succeeded:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        text_results.append({
                            'text': line.text,
                            'confidence': 1.0,
                            'bounding_box': {
                                'x': line.bounding_box[0],
                                'y': line.bounding_box[1],
                                'w': line.bounding_box[2] - line.bounding_box[0],
                                'h': line.bounding_box[3] - line.bounding_box[1]
                            }
                        })

            # Analyse des objets et symboles
            objects_results = []
            
            # Objets détectés
            if analyze_results.objects:
                for obj in analyze_results.objects:
                    objects_results.append({
                        'object': obj.object_property,
                        'confidence': obj.confidence,
                        'bounding_box': {
                            'x': obj.rectangle.x,
                            'y': obj.rectangle.y,
                            'w': obj.rectangle.w,
                            'h': obj.rectangle.h
                        }
                    })
            
            # Tags détectés
            tags_results = []
            if analyze_results.tags:
                for tag in analyze_results.tags:
                    tags_results.append({
                        'tag': tag.name,
                        'confidence': tag.confidence
                    })
            
            # Description de l'image
            description_results = []
            if analyze_results.description and analyze_results.description.captions:
                for caption in analyze_results.description.captions:
                    description_results.append({
                        'description': caption.text,
                        'confidence': caption.confidence
                    })

            return {
                'text_results': text_results,
                'objects_results': objects_results,
                'tags_results': tags_results,
                'description_results': description_results,
                'status': 'success'
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def preprocess_image(self, image_path: str) -> str:
        """
        Prétraite l'image avant l'analyse si nécessaire.
        
        Args:
            image_path: Chemin vers l'image à prétraiter
            
        Returns:
            Chemin vers l'image prétraitée
        """
        try:
            # Ouvrir l'image avec PIL
            with Image.open(image_path) as img:
                # Convertir en niveaux de gris
                img_gray = img.convert('L')
                
                # Améliorer le contraste si nécessaire
                # TODO: Implémenter l'amélioration du contraste
                
                # Sauvegarder l'image prétraitée
                preprocessed_path = image_path.replace('.', '_preprocessed.')
                img_gray.save(preprocessed_path)
                
                return preprocessed_path
        except Exception as e:
            print(f"Erreur lors du prétraitement de l'image: {str(e)}")
            return image_path  # Retourner l'image originale en cas d'erreur 