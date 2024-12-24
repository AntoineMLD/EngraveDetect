import sqlite3
import json
import logging
import shutil
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()


class EngravingPipeline:
    """
    Pipeline pour :
    - Gérer les doublons via SQLite.
    - Sauvegarder les données scrappées localement en JSON.
    - Uploader automatiquement les données sur Azure Blob Storage.
    - Déplacer le fichier local après l'upload.
    """

    def __init__(self):
        # Initialiser SQLite pour gérer les doublons
        self.conn = sqlite3.connect('seen_items.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                glass_name TEXT,
                glass_index TEXT,
                supplier_id TEXT,
                material TEXT,
                supplier_name TEXT,
                UNIQUE(glass_name, glass_index, supplier_id, material)
            )
        """)
        self.conn.commit()

        # Charger la configuration Azure depuis .env
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME")
        if not self.connection_string or not self.container_name:
            raise ValueError("Azure Storage configuration is missing in .env file.")
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Initialiser une liste pour collecter les items valides
        self.items_to_export = []

    def process_item(self, item, spider):
        glass_name = item.get('glass_name')
        glass_index = item.get('glass_index')
        supplier_id = item.get('glass_supplier_id')
        material = item.get('material')

        # Vérifier si l'item existe déjà dans la base de données
        self.cursor.execute("""
            SELECT 1 FROM items
            WHERE glass_name = ? AND glass_index = ? AND supplier_id = ? AND material = ?
        """, (glass_name, glass_index, supplier_id, material))
        if self.cursor.fetchone():
            spider.log(f"Duplicate found (skipped): {glass_name} (Index: {glass_index}, Supplier ID: {supplier_id}, Material: {material})", level=logging.DEBUG)
            return item  # Ne pas traiter les doublons

        # Ajouter l'item dans la base de données
        try:
            self.cursor.execute("""
                INSERT INTO items (glass_name, glass_index, supplier_id, material, supplier_name)
                VALUES (?, ?, ?, ?, ?)
            """, (glass_name, glass_index, supplier_id, material, item.get('supplier_name', "Unknown Supplier")))
            self.conn.commit()
            self.items_to_export.append(dict(item))
            spider.log(f"Added new item: {glass_name} (Index: {glass_index}, Supplier ID: {supplier_id}, Material: {material})", level=logging.INFO)
        except sqlite3.IntegrityError:
            spider.log(f"Error inserting item: {glass_name}", level=logging.ERROR)

        return item

    def close_spider(self, spider):
        file_path = 'output.json'
        dest_path = 'data/output.json'

        try:
            # Exporter les items valides dans un fichier JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.items_to_export, f, ensure_ascii=False, indent=4)
            spider.log(f"EngravingPipeline: {file_path} created.", level=logging.INFO)

            # Uploader le fichier JSON vers Azure Blob Storage
            blob_name = f"scrapped_data/{spider.name}.json"
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            spider.log(f"Uploaded {file_path} to Azure Blob Storage as {blob_name}.", level=logging.INFO)

            # Vérifier et créer le répertoire cible si nécessaire
            if not os.path.exists('data'):
                os.makedirs('data')
                spider.log("Created 'data/' directory.", level=logging.INFO)

            # Déplacer le fichier local après l'upload
            if os.path.exists(file_path):
                shutil.move(file_path, dest_path)
                spider.log(f"Moved {file_path} to {dest_path}.", level=logging.INFO)
            else:
                spider.log(f"File {file_path} does not exist for moving.", level=logging.ERROR)

        except Exception as e:
            spider.log(f"Error during close_spider: {e}", level=logging.ERROR)
        finally:
            # Fermer la connexion SQLite
            self.conn.close()
            spider.log("SQLite connection closed.", level=logging.INFO)
