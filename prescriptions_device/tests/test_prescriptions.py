# -*- coding: utf-8 -*-


import base64
from odoo.tests import new_test_user
from odoo.tests.common import tagged, TransactionCase

TEXT = base64.b64encode(bytes("prescriptions_device", 'utf-8'))


@tagged('post_install', '-at_install', 'test_prescription_bridge')
class TestCasePrescriptionsBridgeDevice(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.device_folder = cls.env.ref('prescriptions_device.prescriptions_device_folder')
        company = cls.env.user.company_id
        company.prescriptions_device_settings = True
        company.prescriptions_device_folder = cls.device_folder
        cls.prescriptions_user = new_test_user(cls.env, "test device manager",
            groups="prescriptions.group_prescriptions_user, device.device_group_manager"
        )
        # Create the Audi custom
        brand = cls.env["device.custom.model.brand"].create({
            "name": "Audi",
        })
        model = cls.env["device.custom.model"].create({
            "brand_id": brand.id,
            "name": "A3",
        })
        cls.device_custom = cls.env["device.custom"].create({
            "model_id": model.id,
            "driver_id": cls.prescriptions_user.partner_id.id,
            "plan_to_change_orthotic": False
        })

    def test_device_attachment(self):
        """
        Make sure the custom attachment is linked to the prescriptions application

        Test Case:
        =========
            - Attach attachment to Audi custom
            - Check if the prescription is created
            - Check the res_id of the prescription
            - Check the res_model of the prescription
        """
        attachment_txt_test = self.env['ir.attachment'].with_user(self.env.user).create({
            'datas': TEXT,
            'name': 'fileText_test.txt',
            'mimetype': 'text/plain',
            'res_model': 'device.custom',
            'res_id': self.device_custom.id,
        })
        prescription = self.env['prescriptions.prescription'].search([('attachment_id', '=', attachment_txt_test.id)])
        self.assertTrue(prescription.exists(), "It should have created a prescription")
        self.assertEqual(prescription.res_id, self.device_custom.id, "device record linked to the prescription ")
        self.assertEqual(prescription.owner_id, self.env.user, "default prescription owner is the current user")
        self.assertEqual(prescription.res_model, self.device_custom._name, "device model linked to the prescription")

    def test_disable_device_centralize_option(self):
        """
        Make sure that the prescription is not created when your Device Centralize is disabled.

        Test Case:
        =========
            - Disable the option Centralize your Device' prescriptions option
            - Add an attachment to a device custom
            - Check whether the prescription is created or not
        """
        company = self.env.user.company_id
        company.prescriptions_device_settings = False

        attachment_txt_test = self.env['ir.attachment'].create({
            'datas': TEXT,
            'name': 'fileText_test.txt',
            'mimetype': 'text/plain',
            'res_model': 'device.custom',
            'res_id': self.device_custom.id,
        })
        prescription = self.env['prescriptions.prescription'].search([('attachment_id', '=', attachment_txt_test.id)])
        self.assertFalse(prescription.exists(), 'the prescription should not exist')
