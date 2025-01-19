import os
import requests
import time
import csv
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from urllib.parse import urlparse
import re

class ScrapersPipeline:
   def __init__(self):
       load_dotenv()
       self.azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")

       if not self.azure_connection_string:
           raise RuntimeError("Vérifier .env pour la connection Azure.")

       try:
           self.blob_service_client = BlobServiceClient.from_connection_string(self.azure_connection_string)
           self.container_name = "raw-data"
       except Exception as e:
           raise RuntimeError(f"Échec de l'initialisation du client Azure Blob : {e}")

       # Dictionnaires et sets pour le suivi
       self.items_by_url = {}
       self.processed_urls = set()
       self.local_image_path = "datalake/staging/media"
       
       # Création des dossiers
       os.makedirs("datalake/staging/data", exist_ok=True)
       os.makedirs(self.local_image_path, exist_ok=True)

   def get_filename_from_url(self, url):
       """Génère un nom de fichier basé sur l'URL."""
       try:
           # Pour les URLs avec fournisseur=XXX
           if 'fournisseur=' in url:
               fournisseur_id = url.split('fournisseur=')[-1]
               return f"datalake/staging/data/fournisseur_{fournisseur_id}.csv"
           
           # Pour les URLs avec fournisseur/XXXX-nom
           match = re.search(r'fournisseur/(\d+)', url)
           if match:
               fournisseur_id = match.group(1)
               return f"datalake/staging/data/fournisseur_{fournisseur_id}.csv"
           
           # Si aucun pattern ne correspond, utiliser l'URL complète
           safe_filename = re.sub(r'[^a-zA-Z0-9]', '_', url)
           return f"datalake/staging/data/url_{safe_filename[-30:]}.csv"
           
       except Exception as e:
           # Fallback sécurisé
           timestamp = int(time.time())
           return f"datalake/staging/data/backup_{timestamp}.csv"

   def upload_to_azure(self, local_file_path, spider):
       """Upload un fichier vers Azure Blob Storage."""
       try:
           blob_name = f"staging/{os.path.basename(local_file_path)}"
           blob_client = self.blob_service_client.get_blob_client(
               container=self.container_name,
               blob=blob_name
           )
           with open(local_file_path, "rb") as data:
               blob_client.upload_blob(data, overwrite=True)
           spider.logger.info(f"Fichier uploadé vers Azure: {blob_name}")
           return True
       except Exception as e:
           spider.logger.error(f"Erreur upload Azure: {e}")
           return False

   def save_empty_file(self, url, spider):
       """Crée un fichier vide avec en-tête pour une URL."""
       try:
           local_output_file = self.get_filename_from_url(url)
           with open(local_output_file, "w", newline='', encoding="utf-8") as f:
               writer = csv.writer(f)
               writer.writerow(['source_url'])
           spider.logger.info(f"Fichier vide créé pour: {url}")
           return local_output_file
       except Exception as e:
           spider.logger.error(f"Erreur création fichier vide pour {url}: {e}")
           return None

   def open_spider(self, spider):
       """Initialise les ressources à l'ouverture du spider."""
       spider.logger.info(f"Démarrage du spider: {spider.name}")
       spider.logger.info(f"URLs à traiter: {spider.start_urls}")
       
       # Initialise un dictionnaire vide pour chaque URL de départ
       for url in spider.start_urls:
           self.items_by_url[url] = []

   def process_item(self, item, spider):
       """Traite chaque élément collecté par le spider."""
       source_url = item['source_url']
       self.processed_urls.add(source_url)
       spider.logger.info(f"Traitement item pour URL: {source_url}")

       # Vérifie si l'URL est attendue
       if source_url not in spider.start_urls:
           spider.logger.warning(f"URL non prévue trouvée: {source_url}")
       
       # Initialise la liste si nécessaire
       if source_url not in self.items_by_url:
           spider.logger.warning(f"Initialisation tardive pour URL: {source_url}")
           self.items_by_url[source_url] = []

       # Traitement de l'image
       image_url = item.get("nasal_engraving")
       if image_url and image_url.startswith(("http", "https")):
           try:
               image_name = os.path.basename(image_url)
               local_image_path = os.path.join(self.local_image_path, image_name)

               response = requests.get(image_url, stream=True)
               if response.status_code == 200:
                   with open(local_image_path, 'wb') as out_file:
                       for chunk in response.iter_content(chunk_size=8192):
                           out_file.write(chunk)
                   item["image_engraving"] = local_image_path
                   
                   # Upload image vers Azure
                   self.upload_to_azure(local_image_path, spider)
               else:
                   item["image_engraving"] = None
                   spider.logger.warning(f"Image non téléchargée (status {response.status_code}): {image_url}")
           except Exception as e:
               spider.logger.error(f"Erreur traitement image: {e}")
               item["image_engraving"] = None
       else:
           item["image_engraving"] = None

       # Ajoute l'item au dictionnaire
       self.items_by_url[source_url].append(dict(item))
       return item

   def close_spider(self, spider):
       """Gère le traitement final lors de la fermeture du spider."""
       spider.logger.info(f"Fermeture du spider: {spider.name}")
       
       # Vérifie les URLs non traitées
       missing_urls = set(spider.start_urls) - self.processed_urls
       if missing_urls:
           spider.logger.warning(f"URLs non traitées: {missing_urls}")
           # Crée des fichiers vides pour les URLs manquantes
           for url in missing_urls:
               self.save_empty_file(url, spider)

       # Traite toutes les URLs configurées
       for url in spider.start_urls:
           items = self.items_by_url.get(url, [])
           local_output_file = self.get_filename_from_url(url)

           try:
               # Écriture du fichier CSV
               with open(local_output_file, "w", newline='', encoding="utf-8") as f:
                   if not items:
                       spider.logger.warning(f"Aucun item pour l'URL: {url}")
                       writer = csv.writer(f)
                       writer.writerow(['source_url'])
                   else:
                       writer = csv.DictWriter(f, fieldnames=items[0].keys())
                       writer.writeheader()
                       writer.writerows(items)
               
               spider.logger.info(f"Fichier créé: {local_output_file}")
               
               # Upload vers Azure
               self.upload_to_azure(local_output_file, spider)
               
           except Exception as e:
               spider.logger.error(f"Erreur traitement fichier pour {url}: {e}")

       # Résumé final
       spider.logger.info("\nRésumé de l'exécution:")
       spider.logger.info(f"URLs totales: {len(spider.start_urls)}")
       spider.logger.info(f"URLs traitées: {len(self.processed_urls)}")
       spider.logger.info(f"URLs manquantes: {len(missing_urls)}")