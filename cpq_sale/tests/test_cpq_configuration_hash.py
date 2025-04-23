# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
import json
import hashlib

class TestCPQConfigurationHash(TransactionCase):

    def test_configuration_hash_generation(self):
        # Example config data
        config_data = {
            "laterality": "bilateral",
            "quantity_to_make": 2,
            "selected": {
                "101": "High Arch",
                "202": "Soft Topcover"
            }
        }

        # Expected hash using the same logic as _get_configuration_hash
        config_json = json.dumps(config_data, sort_keys=True)
        expected_hash = hashlib.sha256(config_json.encode("utf-8")).hexdigest()[:16]

        # Create a sale order line record (using Odoo's environment)
        line = self.env['sale.order.line'].new({})
        generated_hash = line._get_configuration_hash(config_data)

        # Assertion: hashes should match
        self.assertEqual(
            generated_hash,
            expected_hash,
            "The generated CPQ configuration hash does not match the expected hash."
        )
