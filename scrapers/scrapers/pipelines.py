import csv
import os
import re
import time
from urllib.parse import urlparse

import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


class ScrapersPipeline:
    def __init__(self):
        load_dotenv()
        self.azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")

        if not self.azure_connection_string:
            raise RuntimeError("Vérifier .env pour la connection Azure.")

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.azure_connection_string
            )
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
            if "fournisseur=" in url:
                fournisseur_id = url.split("fournisseur=")[-1]
                return f"datalake/staging/data/fournisseur_{fournisseur_id}.csv"

            # Pour les URLs avec fournisseur/XXXX-nom
            match = re.search(r"fournisseur/(\d+)", url)
            if match:
                fournisseur_id = match.group(1)
                return f"datalake/staging/data/fournisseur_{fournisseur_id}.csv"

            # Si aucun pattern ne correspond, utiliser l'URL complète
            safe_filename = re.sub(r"[^a-zA-Z0-9]", "_", url)
            return f"datalake/staging/data/url_{safe_filename[-30:]}.csv"

        except Exception as e:
            self.logger.error(f"Erreur génération nom fichier: {e}")
            timestamp = int(time.time())
            return f"datalake/staging/data/backup_{timestamp}.csv"

    def upload_to_azure(self, local_file_path, spider):
        """Upload un fichier vers Azure Blob Storage."""
        try:
            blob_name = f"staging/{os.path.basename(local_file_path)}"
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
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
            with open(local_output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["source_url"])
            spider.logger.info(f"Fichier vide créé pour: {url}")
            return local_output_file
        except Exception as e:
            spider.logger.error(f"Erreur création fichier vide pour {url}: {e}")
            return None

    def open_spider(self, spider):
        """Initialise les ressources à l'ouverture du spider."""
        spider.logger.info(f"Démarrage du pipeline pour: {spider.name}")
        spider.logger.info(f"URLs à traiter: {spider.start_urls}")

        # Initialise un dictionnaire vide pour chaque URL de départ
        for url in spider.start_urls:
            spider.logger.info(f"Initialisation pour URL: {url}")
            self.items_by_url[url] = []

        spider.logger.info(f"État initial items_by_url: {self.items_by_url.keys()}")

    def process_item(self, item, spider):
        """Traite chaque élément collecté par le spider."""
        try:
            source_url = item["source_url"]
            spider.logger.info(
                f"Pipeline - Début traitement item pour URL: {source_url}"
            )

            # Vérification et initialisation pour l'URL 644
            if "fournisseur=644" in source_url and source_url not in self.items_by_url:
                spider.logger.warning(
                    f"Forçage initialisation pour URL 644: {source_url}"
                )
                self.items_by_url[source_url] = []

            # Ajoute l'URL aux URLs traitées
            spider.logger.info(
                f"État processed_urls avant ajout: {self.processed_urls}"
            )
            self.processed_urls.add(source_url)
            spider.logger.info(
                f"État processed_urls après ajout: {self.processed_urls}"
            )

            # Vérifie si l'URL est attendue
            if source_url not in spider.start_urls:
                spider.logger.warning(f"URL non prévue trouvée: {source_url}")

            # Traitement de l'image avec retry
            max_retries = 3
            retry_count = 0
            image_url = item.get("nasal_engraving")

            if image_url:
                # Si c'est une liste (cas du texte), on la joint en string
                if isinstance(image_url, list):
                    item["nasal_engraving"] = " ".join(image_url)
                    item["image_engraving"] = None  # Pas d'image dans ce cas
                # Si c'est une string et que c'est une URL
                elif isinstance(image_url, str) and image_url.startswith(
                    ("http", "https")
                ):
                    retry_count = 0
                    while retry_count < max_retries:
                        try:
                            image_name = os.path.basename(image_url)
                            local_image_path = os.path.join(
                                self.local_image_path, image_name
                            )

                            response = requests.get(image_url, stream=True, timeout=30)
                            if response.status_code == 200:
                                with open(local_image_path, "wb") as out_file:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        out_file.write(chunk)
                                item["image_engraving"] = local_image_path
                                self.upload_to_azure(local_image_path, spider)
                                break
                            else:
                                retry_count += 1
                                spider.logger.warning(
                                    f"Tentative {retry_count}: Image non téléchargée (status {response.status_code})"
                                )
                                time.sleep(5)
                        except Exception as e:
                            retry_count += 1
                            spider.logger.error(
                                f"Erreur téléchargement image (tentative {retry_count}): {e}"
                            )
                            time.sleep(5)

                    if retry_count >= max_retries:
                        item["image_engraving"] = None
                        spider.logger.error(
                            f"Échec téléchargement image après {max_retries} tentatives"
                        )
                else:
                    item["image_engraving"] = None
            else:
                item["image_engraving"] = None

            # Ajoute l'item au dictionnaire avec vérification
            if source_url not in self.items_by_url:
                spider.logger.warning(f"Initialisation tardive pour URL: {source_url}")
                self.items_by_url[source_url] = []

            self.items_by_url[source_url].append(dict(item))
            spider.logger.info(
                f"Item ajouté pour {source_url}. Total items: {len(self.items_by_url[source_url])}"
            )

            return item

        except Exception as e:
            spider.logger.error(f"Erreur traitement item: {e}")
            return item

    def close_spider(self, spider):
        """Gère le traitement final lors de la fermeture du spider."""
        spider.logger.info(f"Fermeture pipeline - État final:")
        spider.logger.info(f"URLs traitées: {self.processed_urls}")
        spider.logger.info(
            f"Contenu items_by_url: {[f'{url}: {len(items)}' for url, items in self.items_by_url.items()]}"
        )

        # Vérifie les URLs non traitées
        missing_urls = set(spider.start_urls) - self.processed_urls
        if missing_urls:
            spider.logger.warning(f"URLs non traitées: {missing_urls}")
            # Crée des fichiers vides pour les URLs manquantes
            for url in missing_urls:
                self.save_empty_file(url, spider)

        # Traite toutes les URLs configurées avec retry
        for url in spider.start_urls:
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    items = self.items_by_url.get(url, [])
                    local_output_file = self.get_filename_from_url(url)

                    with open(
                        local_output_file, "w", newline="", encoding="utf-8"
                    ) as f:
                        if not items:
                            spider.logger.warning(f"Aucun item pour l'URL: {url}")
                            writer = csv.writer(f)
                            writer.writerow(["source_url"])
                        else:
                            writer = csv.DictWriter(f, fieldnames=items[0].keys())
                            writer.writeheader()
                            writer.writerows(items)

                    spider.logger.info(f"Fichier créé: {local_output_file}")
                    self.upload_to_azure(local_output_file, spider)
                    break

                except Exception as e:
                    retry_count += 1
                    spider.logger.error(
                        f"Erreur traitement fichier pour {url} (tentative {retry_count}): {e}"
                    )
                    time.sleep(5)

            if retry_count >= max_retries:
                spider.logger.error(
                    f"Échec définitif pour {url} après {max_retries} tentatives"
                )

        # Résumé final
        spider.logger.info("\nRésumé de l'exécution:")
        spider.logger.info(f"URLs totales: {len(spider.start_urls)}")
        spider.logger.info(f"URLs traitées: {len(self.processed_urls)}")
        spider.logger.info(f"URLs manquantes: {len(missing_urls)}")
