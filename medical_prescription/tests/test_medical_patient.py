# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalPatient(TransactionCase):

    def setUp(self):
        super(TestMedicalPatient, self).setUp()

        self.RxLine = self.env['medical.prescription.order.line']
        self.Patient = self.env['medical.patient']

        self.patient_1 = self.env.ref(
            'medical.medical_patient_patient_1'
        )
        self.rx_line_1 = self.env.ref(
            'medical_prescription.'
            'medical_prescription_order_order_line_1'
        )
        self.dispense_uom_id = \
            self.rx_line_1.medical_medication_id.medicament_id.uom_id.id

    def test_compute_prescription_order_line_ids(self):
        """ It should properly calculate order lines """
        lines = self.RxLine.search([
            ('patient_id', '=', self.patient_1.id),
        ]).sorted()
        self.assertEquals(
            self.patient_1.prescription_order_line_ids,
            lines,
        )

    def test_compute_prescription_order_line_count(self):
        """ It should properly calculate order lines count """
        lines = self.RxLine.search([
            ('patient_id', '=', self.patient_1.id),
        ])
        self.assertEquals(
            len(self.patient_1.prescription_order_line_ids),
            len(lines),
        )
