import os
import unittest
from unittest.mock import MagicMock, patch
from scrapers.pipelines import ScrapersPipeline

class TestScrapersPipeline(unittest.TestCase):

    @patch('scrapers.pipelines.BlobServiceClient')
    @patch('scrapers.pipelines.load_dotenv')
    @patch.dict(os.environ, {"AZURE_CONNECTION_STRING": "fake_connection_string"}, clear=True)
    def setUp(self, mock_load_dotenv, mock_blob_service_client):
        self.pipeline = ScrapersPipeline()
        self.spider = MagicMock()
        self.item = {
            "glass_supplier_id": 70,
            "glass_name": "Test Glass",
            "nasal_engraving": "http://example.com/image.jpg",
            "category": "Test Category"
        }

    def test_process_item_valid_supplier(self):
        result = self.pipeline.process_item(self.item, self.spider)
        self.assertEqual(result["glass_supplier_name"], "DIVEL FRANCE")

    def test_process_item_invalid_supplier(self):
        self.item["glass_supplier_id"] = "invalid"
        result = self.pipeline.process_item(self.item, self.spider)
        self.assertEqual(result["glass_supplier_name"], "Unknown Supplier")

    def test_process_item_missing_category(self):
        del self.item['category']
        result = self.pipeline.process_item(self.item, self.spider)
        self.assertEqual(result['category'], "Non spécifié")

    @patch('requests.get')
    def test_process_item_image_download(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = MagicMock(return_value=[b'test_image_data'])
        mock_requests_get.return_value = mock_response

        result = self.pipeline.process_item(self.item, self.spider)
        self.assertIn("image_engraving", result)
        self.assertIsNotNone(result["image_engraving"])

    def test_close_spider_with_items(self):
        self.pipeline.items.append(self.item)
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            self.pipeline.close_spider(self.spider)
            self.assertEqual(mock_file.call_count, 2)
            mock_file.assert_any_call(self.pipeline.local_output_file, "w", newline='', encoding="utf-8")
            mock_file.assert_any_call(self.pipeline.local_output_file, "rb")

    def test_close_spider_no_items(self):
        self.pipeline.close_spider(self.spider)
        self.spider.logger.warning.assert_called_once_with("Aucun items à sauvegarder.")

if __name__ == '__main__':
    unittest.main()
