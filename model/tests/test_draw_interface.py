import pytest
import torch
from PIL import Image
import os
from pathlib import Path
from model.draw_interface import DrawingInterface

class TestDrawingInterface:
    @pytest.fixture
    def interface(self, test_data_dir):
        """Fixture pour l'interface de dessin sans Tkinter"""
        # Sauvegarder les chemins originaux
        original_save_dir = Path("model/engraving_draw")
        original_debug_dir = Path("model/debug")
        
        # Créer des répertoires temporaires
        temp_save_dir = test_data_dir / "engraving_draw"
        temp_debug_dir = test_data_dir / "debug"
        temp_save_dir.mkdir(exist_ok=True)
        temp_debug_dir.mkdir(exist_ok=True)
        
        # Créer une instance sans Tkinter
        interface = DrawingInterface.__new__(DrawingInterface)
        interface.save_dir = temp_save_dir
        interface.debug_dir = temp_debug_dir
        interface.canvas_width = 400
        interface.canvas_height = 400
        interface.current_color = 'black'
        interface.line_width = 4
        interface.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        yield interface
        
        # Nettoyage
        for file in temp_save_dir.glob("*"):
            file.unlink()
        for file in temp_debug_dir.glob("*"):
            file.unlink()
            
    def test_preprocess_drawing(self, interface, debug_dir):
        """Test le prétraitement du dessin"""
        # Créer une image simple
        img = Image.new('L', (100, 100), color=255)
        pixels = img.load()
        for i in range(30, 70):
            for j in range(30, 70):
                pixels[i, j] = 0
                
        # Prétraiter l'image
        processed, timestamp = interface.preprocess_drawing(img)
        
        assert processed is not None
        assert isinstance(processed, Image.Image)
        assert processed.size == (64, 64)  # Taille cible
        assert processed.mode == 'L'
        
        # Vérifier les fichiers de debug
        debug_files = list(interface.debug_dir.glob(f"*_{timestamp}.png"))
        assert len(debug_files) > 0
        
    def test_detect_drawing(self, interface, model_dir, templates_dir):
        """Test la détection du dessin"""
        # Créer un modèle factice
        model_path = model_dir / "best_model.pth"
        if not model_path.parent.exists():
            model_path.parent.mkdir(parents=True)
            
        # Sauvegarder un modèle factice
        from model.siamese_model import SiameseNetwork
        model = SiameseNetwork()
        torch.save({
            'epoch': 1,
            'model_state_dict': model.state_dict(),
        }, model_path)
        
        # Créer un template
        template_dir = templates_dir / "test_symbol"
        template_dir.mkdir(exist_ok=True)
        img = Image.new('L', (64, 64), color=255)
        pixels = img.load()
        for i in range(20, 40):
            for j in range(20, 40):
                pixels[i, j] = 0
        img.save(template_dir / "template.png")
        
        # Créer une image test
        test_img = Image.new('L', (400, 400), color=255)
        pixels = test_img.load()
        for i in range(150, 250):
            for j in range(150, 250):
                pixels[i, j] = 0
        interface.image = test_img
        
        # Détecter le dessin
        interface.detect_drawing()
        
        # Vérifier les fichiers de debug
        debug_files = list(interface.debug_dir.glob("*.png"))
        assert len(debug_files) > 0 