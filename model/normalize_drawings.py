#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import cv2
import numpy as np


def apply_random_rotation(image, max_angle=15):
    """Applique une rotation aléatoire à l'image"""
    angle = np.random.uniform(-max_angle, max_angle)
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image,
        rotation_matrix,
        (width, height),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=255,
    )
    return rotated


def add_gaussian_noise(image, mean=0, sigma=15):
    """Ajoute du bruit gaussien à l'image"""
    noise = np.random.normal(mean, sigma, image.shape).astype(np.uint8)
    noisy_image = cv2.add(image, noise)
    return noisy_image


def adjust_contrast(image, factor=None):
    """Ajuste le contraste de l'image"""
    if factor is None:
        factor = np.random.uniform(0.8, 1.2)
    adjusted = cv2.convertScaleAbs(image, alpha=factor, beta=0)
    return adjusted


def apply_elastic_deformation(image, alpha=500, sigma=20, random_state=None):
    """Applique une déformation élastique à l'image"""
    if random_state is None:
        random_state = np.random.RandomState(None)

    shape = image.shape
    dx = random_state.rand(*shape) * 2 - 1
    dy = random_state.rand(*shape) * 2 - 1

    dx = cv2.GaussianBlur(dx, (0, 0), sigma)
    dy = cv2.GaussianBlur(dy, (0, 0), sigma)

    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    mapx = np.float32(x + alpha * dx)
    mapy = np.float32(y + alpha * dy)

    return cv2.remap(
        image,
        mapx,
        mapy,
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=255,
    )


def create_augmented_image(image, output_size=64):
    """Crée une version augmentée de l'image avec des transformations aléatoires"""
    # Appliquer les transformations dans un ordre aléatoire
    transforms = [
        lambda img: apply_random_rotation(img),
        lambda img: add_gaussian_noise(img),
        lambda img: adjust_contrast(img),
        lambda img: apply_elastic_deformation(img),
    ]

    # Mélanger l'ordre des transformations
    np.random.shuffle(transforms)

    # Appliquer les transformations
    augmented = image.copy()
    for transform in transforms:
        if np.random.random() > 0.5:  # 50% de chance d'appliquer chaque transformation
            augmented = transform(augmented)

    return augmented


def center_and_resize(img, output_size=64, threshold=True):
    """
    Convertit l'image en niveaux de gris,
    binarise (option threshold=True),
    trouve le bounding box du tracé,
    redimensionne et centre le tracé dans un canevas (output_size x output_size).

    Retourne l'image 2D traitée (np.array).
    """

    # 1) Convertir en niveaux de gris si ce n'est pas déjà fait
    if len(img.shape) == 3:  # si l'image est en couleur BGR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # 2) Optionnel : binariser (pour forcer un tracé noir sur fond blanc)
    #    Seuil = 127 (ou 128) comme point de coupure
    if threshold:
        _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    else:
        bw = gray

    # 3) Trouver le bounding box (x_min, x_max, y_min, y_max) du tracé
    coords = cv2.findNonZero(
        255 - bw
    )  # on inverse si le tracé est noir (0) sur fond blanc (255)
    # coords est un tableau de points (x, y). On veut minX, maxX, minY, maxY
    if coords is not None:
        x_min = np.min(coords[:, :, 0])
        x_max = np.max(coords[:, :, 0])
        y_min = np.min(coords[:, :, 1])
        y_max = np.max(coords[:, :, 1])
    else:
        # cas extrême : image blanche ou noire complète
        # On renvoie juste une image vide
        return np.zeros((output_size, output_size), dtype=np.uint8)

    # Extraire la zone d'intérêt (ROI)
    cropped = bw[y_min : y_max + 1, x_min : x_max + 1]

    # 4) Déterminer l'échelle pour que le ROI tienne dans output_size x output_size
    roi_height, roi_width = cropped.shape
    # Calculer le ratio d'échelle
    scale = float(output_size) / max(roi_height, roi_width)

    # 5) Redimensionner (scale) pour que le plus grand côté soit = output_size
    new_w = int(roi_width * scale)
    new_h = int(roi_height * scale)
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # 6) Créer un canevas (fond blanc) de size=output_size x output_size
    canvas = np.ones((output_size, output_size), dtype=np.uint8) * 255  # fond blanc

    # 7) Calculer la position pour centrer le tracé
    y_offset = (output_size - new_h) // 2
    x_offset = (output_size - new_w) // 2

    # 8) Placer l'image redimensionnée dans le canevas
    canvas[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized

    return canvas


def process_images_in_folder(
    input_folder, output_folder, output_size=64, num_augmentations=5
):
    """
    Parcourt récursivement input_folder et ses sous-dossiers, lit chaque fichier image,
    applique center_and_resize, et crée plusieurs versions augmentées.
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Parcourir tous les sous-dossiers
    for subdir, _, files in os.walk(input_folder):
        if not files:  # Ignorer les dossiers vides
            continue

        # Obtenir le nom du dossier parent (catégorie)
        category = os.path.basename(subdir)

        # Créer le dossier de sortie correspondant
        category_output = os.path.join(output_folder, category)
        if not os.path.exists(category_output):
            os.makedirs(category_output)

        # Traiter chaque image dans le dossier
        idx = 1
        for filename in sorted(files):
            input_path = os.path.join(subdir, filename)

            # Vérifier si c'est un fichier image
            if not os.path.isfile(input_path):
                continue

            # Lire l'image
            img = cv2.imread(input_path)
            if img is None:
                print(f"[WARN] Impossible de lire : {input_path}")
                continue

            # Traiter l'image originale
            processed = center_and_resize(img, output_size=output_size, threshold=True)

            # Sauvegarder l'image originale normalisée
            new_filename = f"{category}_{idx:02d}.png"
            output_path = os.path.join(category_output, new_filename)
            cv2.imwrite(output_path, processed)
            print(f"[INFO] Image originale traitée : {output_path}")

            # Créer et sauvegarder les versions augmentées
            for aug_idx in range(num_augmentations):
                augmented = create_augmented_image(processed, output_size)
                aug_filename = f"{category}_{idx:02d}_aug{aug_idx+1}.png"
                aug_output_path = os.path.join(category_output, aug_filename)
                cv2.imwrite(aug_output_path, augmented)
                print(f"[INFO] Image augmentée créée : {aug_output_path}")

            idx += 1


if __name__ == "__main__":
    """
    Usage :
        python normalize_drawings.py /chemin/vers/images /chemin/vers/output [64] [5]

    - 1er argument : dossier d'entrée contenant les sous-dossiers d'images
    - 2ème argument : dossier de sortie
    - 3ème argument (optionnel) : taille de sortie (défaut=64)
    - 4ème argument (optionnel) : nombre d'augmentations par image (défaut=5)
    """
    if len(sys.argv) < 3:
        print(
            "Usage: python normalize_drawings.py <input_folder> <output_folder> [output_size] [num_augmentations]"
        )
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    output_size = 64
    num_augmentations = 5

    if len(sys.argv) > 3:
        output_size = int(sys.argv[3])
    if len(sys.argv) > 4:
        num_augmentations = int(sys.argv[4])

    process_images_in_folder(
        input_folder,
        output_folder,
        output_size=output_size,
        num_augmentations=num_augmentations,
    )
