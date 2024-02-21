# Copyright 2016 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalMedicament(TransactionCase):
    def setUp(self):
        super(TestMedicalMedicament, self).setUp()
        self.medical_medicament_obj = self.env['medical.medicament']

    def test_create(self):
        """Test create to assure second level inherits works fine"""
        name = 'ProductMedicament'
        vals = {
            'name': name,
            'drug_form_id': self.env.ref('medical_medicament.AEM').id,
        }
        medicament_id = self.medical_medicament_obj.create(vals)
        self.assertTrue(medicament_id)
        self.assertTrue(medicament_id.product_id)
        self.assertTrue(medicament_id.product_id.is_medicament)
