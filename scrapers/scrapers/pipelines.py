import os
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import csv

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

        # Utilisation d'un dictionnaire pour stocker les items par URL
        self.items_by_url = {}
        self.local_image_path = "datalake/staging/media"
        
        # Créer les dossiers nécessaires
        os.makedirs("datalake/staging/data", exist_ok=True)
        os.makedirs(self.local_image_path, exist_ok=True)

    def get_filename_from_url(self, url, spider_name):
        """Génère un nom de fichier basé sur le dernier paramètre de l'URL."""
        # Extraire le dernier paramètre après le =
        fournisseur = url.split('=')[-1]
        return f"datalake/staging/data/fournisseur_{fournisseur}.csv"

    def open_spider(self, spider):
        """Initialise les ressources à l'ouverture du spider."""
        spider.logger.info("Pipeline initialisé et prêt.")
        # Initialise un dictionnaire pour chaque start_url
        for url in spider.start_urls:
            self.items_by_url[url] = []

    def process_item(self, item, spider):
        """Traite chaque élément collecté par le spider."""
        # Récupére l'URL source de l'item
        source_url = item.get('source_url', spider.start_urls[0])
        
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
                    
                    # Upload to Azure Blob Storage
                    try:
                        blob_client = self.blob_service_client.get_blob_client(
                            container=self.container_name,
                            blob=f"staging/media/{image_name}"
                        )
                        with open(local_image_path, "rb") as data:
                            blob_client.upload_blob(data, overwrite=True)
                    except Exception as e:
                        spider.logger.error(f"Impossible de télécharger l'image vers Azure Blob Storage: {e}")
                else:
                    item["image_engraving"] = None
            except Exception as e:
                spider.logger.error(f"Erreur lors du téléchargement de l'image: {e}")
                item["image_engraving"] = None
        else:
            item["image_engraving"] = None

        # Ajoute l'item au dictionnaire correspondant à son URL source
        self.items_by_url[source_url].append(dict(item))
        return item

    def close_spider(self, spider):
        """Gère le traitement final lors de la fermeture du spider."""
        for url, items in self.items_by_url.items():
            if not items:
                spider.logger.warning(f"Aucun item à sauvegarder pour l'URL: {url}")
                continue

            # Génére le nom de fichier pour cette URL
            local_output_file = self.get_filename_from_url(url, spider.name)

            # Sauvegarde dans un fichier CSV local
            try:
                import csv
                with open(local_output_file, "w", newline='', encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=items[0].keys())
                    writer.writeheader()
                    writer.writerows(items)
                spider.logger.info(f"Données sauvegardées dans : {local_output_file}")

                # Upload vers Azure Blob Storage
                try:
                    blob_name = f"staging/{os.path.basename(local_output_file)}"
                    blob_client = self.blob_service_client.get_blob_client(
                        container=self.container_name,
                        blob=blob_name
                    )
                    with open(local_output_file, "rb") as data:
                        blob_client.upload_blob(data, overwrite=True)
                    spider.logger.info(f"Données téléchargées vers Azure Blob Storage: {blob_name}")
                except Exception as e:
                    spider.logger.error(f"Échec du téléchargement vers Azure Blob Storage : {e}")
            except Exception as e:
                spider.logger.error(f"Échec de la sauvegarde du fichier CSV {local_output_file}: {e}")