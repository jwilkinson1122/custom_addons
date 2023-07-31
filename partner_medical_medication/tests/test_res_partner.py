# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalPatient(TransactionCase):

    def setUp(self):
        super(TestMedicalPatient, self).setUp()
        self.partner_patient_1 = self.env.ref(
            'medical_medication.res_partner_patient_6',
        )

    def test_medication_ids(self):
        """ It should have the proper amount of medications set. """
        self.assertEqual(
            len(self.partner_patient_1.medication_ids), 1,
        )
