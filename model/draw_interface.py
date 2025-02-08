import datetime
import json
import os
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, messagebox, ttk

import requests
from PIL import Image, ImageDraw, ImageOps


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
        self.current_color = "black"
        self.line_width = 4

        # Création des dossiers
        self.save_dir = Path("model/engraving_draw")
        self.debug_dir = Path("model/debug")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        # URL de l'API
        self.api_url = "http://localhost:8000/api/detect"

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
        ttk.Button(control_frame, text="Effacer", command=self.clear_canvas).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(control_frame, text="Sauvegarder", command=self.save_drawing).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(control_frame, text="Détecter", command=self.detect_drawing).pack(
            side=tk.LEFT, padx=5
        )

        # Contrôle de l'épaisseur du trait
        ttk.Label(control_frame, text="Épaisseur:").pack(side=tk.LEFT, padx=5)
        self.width_scale = ttk.Scale(
            control_frame,
            from_=2,
            to=6,
            orient=tk.HORIZONTAL,
            command=self.change_width,
        )
        self.width_scale.set(3)
        self.width_scale.pack(side=tk.LEFT, padx=5)

    def setup_canvas(self):
        """Configure le canvas de dessin."""
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
            cursor="crosshair",
        )
        self.canvas.grid(row=1, column=0, padx=5, pady=5)

        # Événements de la souris
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def create_pil_image(self):
        """Crée une nouvelle image PIL."""
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
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
            self.canvas.create_line(
                self.last_x,
                self.last_y,
                event.x,
                event.y,
                width=self.line_width,
                fill=self.current_color,
                capstyle=tk.ROUND,
                smooth=True,
            )

            # Dessiner sur l'image PIL
            self.draw.line(
                [self.last_x, self.last_y, event.x, event.y],
                fill=self.current_color,
                width=self.line_width,
            )

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
        bw_image = self.image.convert("L")
        # Binariser l'image
        threshold = 127
        binary = bw_image.point(lambda x: 255 if x > threshold else 0, "L")
        # Sauvegarder l'image
        binary.save(filepath)
        print(f"Dessin sauvegardé: {filepath}")

    def detect_drawing(self):
        """Détecte le symbole dessiné en utilisant l'API."""
        if not hasattr(self, "image"):
            messagebox.showwarning(
                "Attention", "Veuillez d'abord dessiner quelque chose!"
            )
            return

        try:
            # Sauvegarder temporairement l'image
            temp_path = self.save_dir / "temp_drawing.png"
            self.image.save(temp_path)

            # Préparer le fichier pour l'envoi
            with open(temp_path, "rb") as f:
                files = {"file": ("drawing.png", f, "image/png")}

                # Envoyer la requête à l'API
                print(f"Envoi de la requête à {self.api_url}...")
                response = requests.post(self.api_url, files=files)

                if response.status_code == 200:
                    result = response.json()

                    # Afficher le résultat
                    message = (
                        f"Symbole détecté : {result['predicted_symbol']}\n"
                        f"Confiance : {result['similarity_score']:.2%}\n"
                        f"Statut : {result['message']}"
                    )
                    messagebox.showinfo("Résultat de la détection", message)
                else:
                    messagebox.showerror(
                        "Erreur",
                        f"Erreur lors de la détection (code {response.status_code}):\n{response.text}",
                    )

        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Une erreur est survenue lors de la détection : {str(e)}"
            )

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
