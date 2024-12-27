import json
from django.core.management.base import BaseCommand
from engraving.models import Glass, Supplier, Material
from django.db import transaction
import os

class Command(BaseCommand):
    """
    Commande pour importer des données scrappées depuis un fichier JSON dans la base de données.
    """
    help = 'Import scrapped data from a JSON file into the database'

    def add_arguments(self, parser):
        """
        Ajouter un argument pour spécifier le chemin du fichier JSON.
        """
        parser.add_argument(
            '--file_path',
            type=str,
            default='data/cleaned_output.json',
            help='The path to the JSON file containing the scrapped data (default: data/cleaned_output.json)'
        )

    def handle(self, *args, **kwargs):
        """
        Gestion principale de la commande.
        """
        file_path = kwargs['file_path']

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        try:
            self.stdout.write(self.style.WARNING(f'Loading data from {file_path}...'))

            # Charger le fichier JSON
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if not isinstance(data, list):
                self.stderr.write(self.style.ERROR("The JSON file should contain a list of items."))
                return

            with transaction.atomic():
                imported_count = 0
                updated_count = 0

                for entry in data:
                    glass_name = entry.get('glass_name')
                    glass_index = entry.get('glass_index')
                    supplier_name = entry.get('glass_supplier_name')
                    material_name = entry.get('material')

                    if not (glass_name and glass_index and supplier_name and material_name):
                        self.stderr.write(
                            self.style.ERROR(f"Missing required fields in entry: {entry}")
                        )
                        continue

                    supplier, _ = Supplier.objects.get_or_create(
                        supplier_name=supplier_name
                    )

                    material, _ = Material.objects.get_or_create(
                        material_name=material_name
                    )

                    glass, created = Glass.objects.update_or_create(
                        glass_name=glass_name,
                        glass_index=glass_index,
                        supplier=supplier,
                        material=material,
                        defaults={
                            'category': entry.get('category', 'Other'),
                            'image_engraving': entry.get('image_engraving', None),
                            'text_engraving': entry.get('text_engraving', None),
                        }
                    )
                    if created:
                        imported_count += 1
                    else:
                        updated_count += 1

                self.stdout.write(self.style.SUCCESS(
                    f"Data import complete! {imported_count} new glasses imported, {updated_count} glasses updated."
                ))

        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR("Invalid JSON format. Please check the file content."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {str(e)}"))