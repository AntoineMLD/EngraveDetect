import unittest
from unittest.mock import patch, MagicMock
import os
from vision.services.azure_vision import AzureVisionService

class TestAzureVisionService(unittest.TestCase):
    def setUp(self):
        """Configuration initiale pour les tests."""
        # Mock des variables d'environnement
        self.env_patcher = patch.dict('os.environ', {
            'AZURE_VISION_ENDPOINT': 'https://test-endpoint',
            'AZURE_VISION_KEY': 'test-key'
        })
        self.env_patcher.start()
        self.service = AzureVisionService()

    def tearDown(self):
        """Nettoyage après les tests."""
        self.env_patcher.stop()

    @patch('vision.services.azure_vision.ComputerVisionClient')
    def test_analyze_image_success(self, mock_client):
        """Test d'une analyse d'image réussie."""
        # Configuration des mocks
        mock_read_response = MagicMock()
        mock_read_response.headers = {"Operation-Location": "operations/123"}
        
        mock_read_result = MagicMock()
        mock_read_result.status = "succeeded"
        mock_read_result.analyze_result.read_results = [
            MagicMock(lines=[
                MagicMock(
                    text="Test Text",
                    appearance=MagicMock(confidence=0.95),
                    bounding_box=[1, 2, 3, 4]
                )
            ])
        ]
        
        mock_objects_result = MagicMock()
        mock_objects_result.objects = [
            MagicMock(
                object_property="symbol",
                confidence=0.9,
                rectangle=MagicMock(x=1, y=2, w=3, h=4)
            )
        ]
        
        # Configuration du comportement du mock
        mock_client.return_value.read_in_stream.return_value = mock_read_response
        mock_client.return_value.get_read_result.return_value = mock_read_result
        mock_client.return_value.detect_objects_in_stream.return_value = mock_objects_result
        
        # Test avec une image fictive
        test_image_path = "test_image.jpg"
        with patch("builtins.open", unittest.mock.mock_open(read_data=b"test")):
            result = self.service.analyze_image(test_image_path)
        
        # Vérifications
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['text_results']), 1)
        self.assertEqual(result['text_results'][0]['text'], "Test Text")
        self.assertEqual(len(result['objects_results']), 1)
        self.assertEqual(result['objects_results'][0]['object'], "symbol")

    def test_preprocess_image(self):
        """Test du prétraitement d'image."""
        # Création d'une image test
        from PIL import Image
        import numpy as np
        
        # Créer une image test
        test_image = Image.fromarray(np.zeros((100, 100), dtype=np.uint8))
        test_image_path = "test_image.jpg"
        test_image.save(test_image_path)
        
        try:
            # Test du prétraitement
            preprocessed_path = self.service.preprocess_image(test_image_path)
            
            # Vérifications
            self.assertTrue(os.path.exists(preprocessed_path))
            self.assertNotEqual(test_image_path, preprocessed_path)
            
            # Vérifier que l'image prétraitée est en niveaux de gris
            with Image.open(preprocessed_path) as img:
                self.assertEqual(img.mode, 'L')
        
        finally:
            # Nettoyage
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
            if os.path.exists(preprocessed_path):
                os.remove(preprocessed_path)

if __name__ == '__main__':
    unittest.main() 