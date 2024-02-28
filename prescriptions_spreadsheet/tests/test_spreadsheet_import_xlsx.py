# -*- coding: utf-8 -*-


import base64
from odoo import http
from odoo.tests.common import HttpCase

from .common import SpreadsheetTestCommon
from odoo.tools import file_open
from odoo.exceptions import UserError

class SpreadsheetImportXlsx(HttpCase, SpreadsheetTestCommon):
    def test_import_xlsx(self):
        """Import xlsx"""
        folder = self.env["prescriptions.folder"].create({"name": "Test folder"})
        with file_open('prescriptions_spreadsheet/tests/data/test.xlsx', 'rb') as f:
            spreadsheet_data = base64.encodebytes(f.read())
            prescription_xlsx = self.env['prescriptions.prescription'].create({
                'datas': spreadsheet_data,
                'name': 'text.xlsx',
                'mimetype': 'application/vnd.openxmlformats-officeprescription.spreadsheetml.sheet',
                'folder_id': folder.id
            })
            spreadsheet_id = prescription_xlsx.clone_xlsx_into_spreadsheet()
            spreadsheet = self.env["prescriptions.prescription"].browse(spreadsheet_id).exists()
            self.assertTrue(spreadsheet)

    def test_import_xlsx_wrong_mime_type(self):
        """Import xlsx with wrong mime type raisese an error"""
        folder = self.env["prescriptions.folder"].create({"name": "Test folder"})
        with file_open('prescriptions_spreadsheet/tests/data/test.xlsx', 'rb') as f:
            spreadsheet_data = base64.encodebytes(f.read())
            prescription_xlsx = self.env['prescriptions.prescription'].create({
                'datas': spreadsheet_data,
                'name': 'text.xlsx',
                'mimetype': 'text/plain',
                'folder_id': folder.id
            })
            with self.assertRaises(UserError) as error_catcher:
                prescription_xlsx.clone_xlsx_into_spreadsheet()

            self.assertEqual(error_catcher.exception.args[0], ("The file is not a xlsx file"))


    def test_import_xlsx_wrong_content(self):
        """Import a xlsx which isn't a zip raises error"""
        folder = self.env["prescriptions.folder"].create({"name": "Test folder"})
        prescription_xlsx = self.env['prescriptions.prescription'].create({
            'datas': base64.encodebytes(b"yolo"),
            'name': 'text.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officeprescription.spreadsheetml.sheet',
            'folder_id': folder.id
        })
        with self.assertRaises(UserError) as error_catcher:
            prescription_xlsx.clone_xlsx_into_spreadsheet()

        self.assertEqual(error_catcher.exception.args[0], ("The file is not a xlsx file"))

    def test_import_xlsx_zip_but_not_xlsx(self):
        """Import a zip which isn't a xlsx raises error"""
        folder = self.env["prescriptions.folder"].create({"name": "Test folder"})
        prescription_xlsx = self.env['prescriptions.prescription'].create({
            # Minimum zip file
            'datas': base64.encodebytes(b"\x50\x4B\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
            'name': 'text.xlsx',
            'mimetype': 'application/vnd.openxmlformats-officeprescription.spreadsheetml.sheet',
            'folder_id': folder.id
        })
        with self.assertRaises(UserError) as error_catcher:
            prescription_xlsx.clone_xlsx_into_spreadsheet()

        self.assertEqual(error_catcher.exception.args[0], ("The xlsx file is corrupted"))

    def test_import_xlsx_computes_multipage(self):
        """Import xlsx leads to accurate multipage computation"""
        folder = self.env["prescriptions.folder"].create({"name": "Test folder"})

        cases = [('test.xlsx', False), ('test2sheets.xlsx', True)]

        for filename, is_multipage in cases:
            with file_open(f'prescriptions_spreadsheet/tests/data/{filename}', 'rb') as f:
                spreadsheet_data = base64.encodebytes(f.read())
                prescription_xlsx = self.env['prescriptions.prescription'].create(
                    {
                        'datas': spreadsheet_data,
                        'name': filename,
                        'mimetype': 'application/vnd.openxmlformats-officeprescription.spreadsheetml.sheet',
                        'folder_id': folder.id,
                    }
                )
                with self.subTest(is_multipage=is_multipage, kind="xlsx"):
                    self.assertEqual(prescription_xlsx.is_multipage, is_multipage)

            spreadsheet_id = prescription_xlsx.clone_xlsx_into_spreadsheet()
            spreadsheet = self.env["prescriptions.prescription"].browse(spreadsheet_id).exists()
            with self.subTest(is_multipage=is_multipage, kind="spreadsheet"):
                self.assertEqual(spreadsheet.is_multipage, is_multipage)

    def test_request_xlsx_computes_multipage(self):
        """Successfully upload xlsx on requested prescriptions"""
        self.authenticate('admin', 'admin')
        folder = self.env["prescriptions.folder"].create({"name": "Test folder"})
        activity_type = self.env['mail.activity.type'].create({
            'name': 'request_prescription',
            'category': 'upload_file',
            'folder_id': folder.id,
        })
        prescription = self.env['prescriptions.request_wizard'].create({
            'name': 'Wizard Request',
            'requestee_id': self.spreadsheet_user.partner_id.id,
            'activity_type_id': activity_type.id,
            'folder_id': folder.id,
        }).request_prescription()

        with file_open('prescriptions_spreadsheet/tests/data/test2sheets.xlsx', 'rb') as file:
            response = self.url_open(
                url='/prescriptions/upload_attachment',
                data={
                    'folder_id':folder.id,
                    'tag_ids':'',
                    'prescription_id':prescription.id,
                    'csrf_token': http.Request.csrf_token(self),
                },
                files=[('ufile', ('test2sheets.xlsx', file.read(), 'application/vnd.openxmlformats-officeprescription.spreadsheetml.sheet'))],
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"success": "All files uploaded"}')
        self.assertEqual(prescription.is_multipage, True)
