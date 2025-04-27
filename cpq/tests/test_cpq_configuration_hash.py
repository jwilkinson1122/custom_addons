# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
import json
import hashlib
from datetime import datetime, date

class TestCPQConfigurationHash(TransactionCase):

    def setUp(self):
        super().setUp()
        self.line = self.env['sale.order.line'].new({})

    def _expected_hash(self, config):
        """Helper to calculate the expected hash using sorted keys and safe serialization."""
        def default_serializer(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()  # Match production logic
            return str(obj)  # Fallback like your main logic

        if isinstance(config, dict):
            config_json = json.dumps(config, sort_keys=True, default=default_serializer)
        elif isinstance(config, str):
            config_json = config
        else:
            try:
                config_json = json.dumps(config, default=default_serializer)
            except Exception:
                config_json = str(config)

        return hashlib.sha256(config_json.encode("utf-8")).hexdigest()[:16]

    def test_configuration_hash_generation(self):
        """Test basic configuration hash generation with dict input."""
        config_data = {
            "laterality": "bilateral",
            "quantity_to_make": 2,
            "selected": {
                "101": "High Arch",
                "202": "Soft Topcover"
            }
        }
        expected_hash = self._expected_hash(config_data)  # ✅ Uses helper!
        generated_hash = self.line._get_configuration_hash(config_data)
        self.assertEqual(generated_hash, expected_hash, "Generated hash does not match expected hash.")

    def test_empty_configuration_hash(self):
        """Test hash generation with an empty configuration."""
        config_data = {}
        expected_hash = self._expected_hash(config_data)
        generated_hash = self.line._get_configuration_hash(config_data)
        self.assertEqual(generated_hash, expected_hash, "Hash for empty config does not match expected.")

    def test_configuration_hash_with_string_input(self):
        """Test hash generation when config is already a JSON string."""
        config_data = {
            "laterality": "right",
            "quantity_to_make": 1,
            "selected": {"303": "Cushioned Heel"}
        }
        config_str = json.dumps(config_data, sort_keys=True)
        expected_hash = self._expected_hash(config_str)
        generated_hash = self.line._get_configuration_hash(config_str)
        self.assertEqual(generated_hash, expected_hash, "Hash for stringified JSON config does not match expected.")

    def test_configuration_hash_with_unsorted_keys(self):
        """Test that key ordering does not affect hash generation."""
        config_sorted = {
            "laterality": "bilateral",
            "quantity_to_make": 2,
            "selected": {"101": "High Arch", "202": "Soft Topcover"}
        }
        config_unsorted = {
            "selected": {"202": "Soft Topcover", "101": "High Arch"},
            "quantity_to_make": 2,
            "laterality": "bilateral"
        }
        expected_hash = self._expected_hash(config_sorted)
        generated_hash = self.line._get_configuration_hash(config_unsorted)
        self.assertEqual(generated_hash, expected_hash, "Hash should be consistent regardless of dict key order.")

    def test_configuration_hash_with_datetime_input(self):
        """Test hash generation with datetime objects (fallback str conversion)."""
        config_data = {"laterality": "left", "timestamp": datetime(2025, 4, 23, 15, 30)}
        config_str = json.dumps(
            {"laterality": "left", "timestamp": config_data["timestamp"].isoformat()},
            sort_keys=True
        )
        expected_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()[:16]
        generated_hash = self.line._get_configuration_hash(config_data)
        self.assertEqual(generated_hash, expected_hash, "Hash for config with datetime did not match expected value.")

    def test_configuration_hash_with_date_input(self):
        """Test hash generation with date objects (fallback str conversion)."""
        config_data = {"laterality": "left", "date": date(2025, 4, 23)}
        config_str = json.dumps(
            {"laterality": "left", "date": config_data["date"].isoformat()},
            sort_keys=True
        )
        expected_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()[:16]
        generated_hash = self.line._get_configuration_hash(config_data)
        self.assertEqual(generated_hash, expected_hash, "Hash for config with date did not match expected value.")

    def test_configuration_hash_with_invalid_input(self):
        """Test hash generation with unsupported input type (like int)."""
        config_data = 12345  # More stable than object()!
        expected_hash = self._expected_hash(config_data)
        generated_hash = self.line._get_configuration_hash(config_data)
        self.assertEqual(generated_hash, expected_hash, "Hash for invalid config type did not match expected value.")

    def test_configuration_hash_with_list_input(self):
        """Test hash generation with list input."""
        config_data = ["item1", "item2", "item3"]
        expected_hash = self._expected_hash(config_data)
        generated_hash = self.line._get_configuration_hash(config_data)
        self.assertEqual(generated_hash, expected_hash, "Hash for list input did not match expected value.")
    
 