# -*- coding: utf-8 -*-


from odoo.addons.prescription.tests.common import PrescriptionCommon

class PrescriptionManagementCommon(PrescriptionCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.empty_order_template = cls.env['prescription.order.template'].create({
            'name': "Test Draft Rx Template",
        })
