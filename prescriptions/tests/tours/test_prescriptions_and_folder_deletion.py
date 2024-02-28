# -*- coding: utf-8 -*-


from odoo.tests import tagged
from odoo.tests.common import HttpCase

GIF = b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs="

@tagged("post_install", "-at_install")
class TestPrescriptionDeletion(HttpCase):

    def test_delete_folder_and_prescriptions_tour(self):
        folder = self.env['prescriptions.folder'].create({
            "name": "Workspace1",
        })
        prescription = self.env['prescriptions.prescription'].create({
            'datas': GIF,
            "name": "Chouchou",
            "folder_id": folder.id,
            'mimetype': 'image/gif',
        })
        folder_copy = folder
        prescription_copy = prescription
        self.start_tour("/web", 'prescription_delete_tour', login='admin')
        self.assertFalse(folder_copy.exists(), "The folder should not exist anymore")
        self.assertFalse(prescription_copy.exists(), "The prescription should not exist anymore")
