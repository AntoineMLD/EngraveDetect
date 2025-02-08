import io
import logging
from typing import Optional, Set

import torch
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel

from model.infer_siamese import load_templates, predict_symbol

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Extensions d'images autorisées
ALLOWED_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

# Variable globale pour les templates
templates = None


# Modèle de réponse
class DetectionResponse(BaseModel):
    image_path: str
    predicted_symbol: Optional[str]
    similarity_score: float
    is_confident: bool
    message: str


def init_model():
    """Initialise le modèle et les templates"""
    global templates

    logger.info("Initialisation du modèle de détection...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Utilisation du device: {device}")

    try:
        templates = load_templates()
        logger.info("Modèle et templates chargés avec succès")
        logger.info(f"Seuil de confiance: {templates.similarity_threshold}")
        # Liste les templates disponibles
        template_names = list(templates.templates.keys())
        logger.info(f"Templates disponibles: {template_names}")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle: {str(e)}")
        raise


def is_valid_image_extension(filename: str) -> bool:
    """Vérifie si l'extension du fichier est autorisée"""
    import os

    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS


@router.post("/detect", response_model=DetectionResponse)
async def detect_image(file: UploadFile = File(...)):
    """
    Endpoint pour détecter un symbole dans une image

    Args:
        file: Image à analyser (formats supportés: JPG, JPEG, PNG, GIF, BMP, TIFF)

    Returns:
        DetectionResponse: Résultat de la détection avec le symbole et le score de confiance
    """
    global templates
    if templates is None:
        init_model()

    logger.info(f"Nouvelle demande de détection pour le fichier: {file.filename}")

    # Vérification de l'extension du fichier
    if not is_valid_image_extension(file.filename):
        logger.warning(f"Extension non supportée: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format de fichier non supporté. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        # Lecture de l'image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        logger.info(
            f"Image chargée avec succès. Dimensions: {image.size}, Mode: {image.mode}"
        )

        # Vérification supplémentaire que le fichier est bien une image
        image.verify()
        image = Image.open(io.BytesIO(contents))  # Réouverture après verify()

        # Sauvegarde temporaire de l'image
        temp_path = "temp_detection.png"
        image.save(temp_path)
        logger.info(f"Image temporaire sauvegardée: {temp_path}")

        try:
            # Prédiction
            logger.info("Lancement de la détection...")
            predicted_symbol, similarity_score = predict_symbol(
                temp_path,
                None,
                templates,
                torch.device("cuda" if torch.cuda.is_available() else "cpu"),
            )
            logger.info(
                f"Détection terminée. Symbole: {predicted_symbol}, Score: {similarity_score:.2%}"
            )

            # Vérification du seuil de confiance (utilise le même seuil que le modèle)
            is_confident = similarity_score >= templates.similarity_threshold
            logger.info(
                f"Confiance suffisante: {is_confident} (seuil: {templates.similarity_threshold})"
            )

            message = (
                "Détection réussie"
                if is_confident
                else "Confiance insuffisante dans la détection"
            )

            response = DetectionResponse(
                image_path=temp_path,
                predicted_symbol=predicted_symbol,
                similarity_score=similarity_score,
                is_confident=is_confident,
                message=message,
            )
            logger.info(f"Réponse préparée: {response.dict()}")
            return response

        finally:
            # Nettoyage du fichier temporaire
            import os

            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info("Fichier temporaire supprimé")

    except (IOError, SyntaxError) as e:
        logger.error(f"Erreur lors du traitement de l'image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier semble corrompu ou n'est pas une image valide",
        )
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la détection: {str(e)}",
        )
