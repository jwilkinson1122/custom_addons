# -*- coding: utf-8 -*-


from odoo.addons.pod_prescriptions.tests.common import PrescriptionCommon

class PrescriptionManagementCommon(PrescriptionCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.empty_order_template = cls.env['prescriptions.order.template'].create({
            'name': "Test Device Template",
        })
