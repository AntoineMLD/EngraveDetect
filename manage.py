import os
import sys

def setup_directories():
    """
    Crée les répertoires nécessaires pour les fichiers statiques et médias si absents.
    """
    media_path = os.path.join(os.getcwd(), 'media/engraving_images/')
    static_path = os.path.join(os.getcwd(), 'static/')
    os.makedirs(media_path, exist_ok=True)
    os.makedirs(static_path, exist_ok=True)
    print(f"Répertoire médias initialisé : {media_path}")
    print(f"Répertoire statique initialisé : {static_path}")

def main():
    """Exécute les tâches administratives."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engrave_detect.settings')

    # Initialisation des répertoires
    setup_directories()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Assurez-vous qu'il est installé et "
            "disponible sur votre variable d'environnement PYTHONPATH. Avez-vous "
            "oublié d'activer un environnement virtuel ?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
