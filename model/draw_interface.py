import datetime
import os
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, messagebox, ttk

import numpy as np
import torch
import torch.nn as nn
from PIL import Image, ImageDraw, ImageOps
from torchvision import transforms

from model.infer_siamese import (SiamesePredictor, load_templates,
                                 predict_symbol)
from model.siamese_model import SiameseNetwork


class DrawingInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface de Dessin de Gravures")
        
        # Configuration de la taille du canvas
        self.canvas_width = 400
        self.canvas_height = 400
        
        # Variables pour le dessin
        self.drawing = False
        self.last_x = None
        self.last_y = None
        self.current_color = 'black'
        self.line_width = 4  # Augmentation de l'épaisseur par défaut
        
        # Création des dossiers
        self.save_dir = Path("model/engraving_draw")
        self.debug_dir = Path("model/debug")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Chargement du modèle et des templates
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.templates = load_templates()
        
        # Vérification des templates disponibles
        self.available_templates = []
        templates_dir = Path("model/templates")
        for template_dir in templates_dir.iterdir():
            if template_dir.is_dir() and (template_dir / "template.png").exists():
                self.available_templates.append(template_dir.name)
        print("Templates disponibles:", sorted(self.available_templates))
        
        self.setup_ui()
        self.setup_canvas()
        self.create_pil_image()
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame pour les contrôles
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, pady=5)
        
        # Boutons et contrôles
        ttk.Button(control_frame, text="Effacer", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Sauvegarder", command=self.save_drawing).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Détecter", command=self.detect_drawing).pack(side=tk.LEFT, padx=5)
        
        # Contrôle de l'épaisseur du trait (réduit la plage)
        ttk.Label(control_frame, text="Épaisseur:").pack(side=tk.LEFT, padx=5)
        self.width_scale = ttk.Scale(control_frame, from_=2, to=6, orient=tk.HORIZONTAL,
                                   command=self.change_width)
        self.width_scale.set(3)  # Valeur par défaut plus petite
        self.width_scale.pack(side=tk.LEFT, padx=5)
    def setup_canvas(self):
        """Configure le canvas de dessin."""
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height,
                              bg='white', cursor="crosshair")
        self.canvas.grid(row=1, column=0, padx=5, pady=5)
        
        # Événements de la souris
        self.canvas.bind('<Button-1>', self.start_drawing)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.stop_drawing)
    def create_pil_image(self):
        """Crée une nouvelle image PIL."""
        self.image = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
        self.draw = ImageDraw.Draw(self.image)
    def start_drawing(self, event):
        """Commence le dessin."""
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
    def draw(self, event):
        """Dessine sur le canvas et l'image PIL."""
        if self.drawing and self.last_x and self.last_y:
            # Dessiner sur le canvas
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                  width=self.line_width, fill=self.current_color,
                                  capstyle=tk.ROUND, smooth=True)
            
            # Dessiner sur l'image PIL
            self.draw.line([self.last_x, self.last_y, event.x, event.y],
                         fill=self.current_color, width=self.line_width)
            
            self.last_x = event.x
            self.last_y = event.y
    def stop_drawing(self, event):
        """Arrête le dessin."""
        self.drawing = False
        self.last_x = None
        self.last_y = None
    def clear_canvas(self):
        """Efface le canvas et l'image PIL."""
        self.canvas.delete("all")
        self.create_pil_image()
    def change_width(self, value):
        """Change l'épaisseur du trait."""
        self.line_width = int(float(value))
    def save_drawing(self):
        """Sauvegarde le dessin."""
        # Créer un nom de fichier unique avec la date et l'heure
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gravure_{timestamp}.png"
        filepath = self.save_dir / filename
        
        # Convertir en noir et blanc
        bw_image = self.image.convert('L')
        # Binariser l'image
        threshold = 127
        binary = bw_image.point(lambda x: 255 if x > threshold else 0, 'L')
        # Sauvegarder l'image
        binary.save(filepath)
        print(f"Dessin sauvegardé: {filepath}")
    def preprocess_drawing(self, image):
        """Prétraite le dessin pour la détection."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 1. Convertir en noir et blanc et réduire la taille initiale
            # Réduire d'abord l'image pour avoir une taille plus proche des templates
            initial_size = 100  # Taille initiale plus petite
            bw_image = image.convert('L')
            aspect_ratio = bw_image.width / bw_image.height
            if aspect_ratio > 1:
                new_w = initial_size
                new_h = int(initial_size / aspect_ratio)
            else:
                new_h = initial_size
                new_w = int(initial_size * aspect_ratio)
            bw_image = bw_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            bw_image.save(self.debug_dir / f"1_grayscale_{timestamp}.png")
            
            # 2. Convertir en numpy array pour un meilleur contrôle
            img_array = np.array(bw_image)
            
            # 3. Binariser avec un seuil adaptatif
            threshold = np.mean(img_array)  # Utiliser la moyenne comme dans create_templates.py
            binary = (img_array > threshold).astype(np.uint8) * 255
            binary_image = Image.fromarray(binary)
            binary_image.save(self.debug_dir / f"2_binary_{timestamp}.png")
            
            # 4. Inverser pour avoir le dessin en noir
            inverted = ImageOps.invert(binary_image)
            inverted.save(self.debug_dir / f"3_inverted_{timestamp}.png")
            
            # 5. Trouver la boîte englobante
            bbox = inverted.getbbox()
            if not bbox:
                return None, None
            
            # 6. Recadrer
            cropped = inverted.crop(bbox)
            
            # Vérifier la taille minimale
            min_size = 10
            if cropped.size[0] < min_size or cropped.size[1] < min_size:
                return None, None
            
            # 7. Ajouter une marge fixe de 4 pixels
            margin = 4  # Comme dans create_templates.py
            padded_size = (cropped.size[0] + 2*margin, cropped.size[1] + 2*margin)
            padded = Image.new('L', padded_size, 255)
            padded.paste(cropped, (margin, margin))
            padded.save(self.debug_dir / f"4_padded_{timestamp}.png")
            
            # 8. Redimensionner en préservant le ratio
            target_size = 64
            w, h = padded.size
            if w > h:
                new_w = target_size
                new_h = int((h * target_size) / w)
            else:
                new_h = target_size
                new_w = int((w * target_size) / h)
            
            # S'assurer que les dimensions ne sont pas nulles
            new_w = max(new_w, 1)
            new_h = max(new_h, 1)
            
            resized = padded.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # 9. Centrer dans une image carrée
            final = Image.new('L', (target_size, target_size), 255)
            paste_x = (target_size - new_w) // 2
            paste_y = (target_size - new_h) // 2
            final.paste(resized, (paste_x, paste_y))
            final.save(self.debug_dir / f"5_final_{timestamp}.png")
            
            return final, timestamp
            
        except Exception as e:
            print(f"Erreur lors du prétraitement: {str(e)}")
            return None, None
    def detect_drawing(self):
        """Détecte le symbole dessiné."""
        if not hasattr(self, 'image'):
            messagebox.showwarning("Attention", "Veuillez d'abord dessiner quelque chose!")
            return
            
        # Prétraiter l'image
        processed_image, timestamp = self.preprocess_drawing(self.image)
        if processed_image is None:
            messagebox.showwarning("Attention", "Aucun dessin détecté!")
            return
            
        # Sauvegarder temporairement l'image
        temp_path = self.save_dir / "temp_drawing.png"
        processed_image.save(temp_path)
        
        try:
            # Prédire le symbole
            predicted_symbol, similarity = predict_symbol(str(temp_path), None, self.templates, self.device)
            
            # Vérifier si la prédiction est suffisamment confiante
            confidence_threshold = 0.65  # Seuil plus strict
            
            if similarity < confidence_threshold:
                message = (
                    f"Aucun symbole n'a été détecté avec une confiance suffisante.\n"
                    f"Meilleure correspondance : {predicted_symbol} ({similarity:.2%})\n"
                    f"Veuillez réessayer en dessinant plus clairement."
                )
                messagebox.showwarning("Détection incertaine", message)
                return
            
            # Sauvegarder les templates pour comparaison
            template_path = Path(f"model/templates/{predicted_symbol}/template.png")
            if template_path.exists():
                # Sauvegarder le template de référence et le template détecté
                template = Image.open(template_path)
                template.save(self.debug_dir / f"6_template_reference_{timestamp}.png")
                template.save(self.debug_dir / f"7_template_detected_{timestamp}.png")
            
            # Afficher le résultat avec plus de détails
            message = (
                f"Symbole détecté : {predicted_symbol}\n"
                f"Confiance : {similarity:.2%}\n\n"
                f"Les images de débogage ont été sauvegardées dans le dossier 'debug'.\n"
                f"Vérifiez les images pour voir les étapes de traitement."
            )
            messagebox.showinfo("Résultat de la détection", message)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la détection : {str(e)}")
        finally:
            # Supprimer le fichier temporaire
            if temp_path.exists():
                temp_path.unlink()
def main():
    root = tk.Tk()
    app = DrawingInterface(root)
    root.mainloop()
if __name__ == "__main__":
    main()