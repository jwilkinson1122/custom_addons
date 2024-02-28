# -*- coding: utf-8 -*-


from odoo.tests.common import new_test_user
from odoo.addons.spreadsheet_edition.tests.spreadsheet_test_case import SpreadsheetTestCase

from uuid import uuid4

TEST_CONTENT = "{}"
GIF = b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs="


class SpreadsheetTestCommon(SpreadsheetTestCase):
    @classmethod
    def setUpClass(cls):
        super(SpreadsheetTestCommon, cls).setUpClass()
        cls.folder = cls.env["prescriptions.folder"].create({"name": "Test folder"})
        cls.spreadsheet_user = new_test_user(
            cls.env, login="spreadsheetDude", groups="prescriptions.group_prescriptions_user"
        )

    def create_spreadsheet(self, values=None, *, user=None, name="Untitled Spreadsheet"):
        if values is None:
            values = {}
        return (
            self.env["prescriptions.prescription"]
            .with_user(user or self.env.user)
            .create({
                "spreadsheet_data": r"{}",
                "folder_id": self.folder.id,
                "handler": "spreadsheet",
                "mimetype": "application/o-spreadsheet",
                "name": name,
                **values,
            })
        )

    def share_spreadsheet(self, prescription):
        share = self.env["prescriptions.share"].create(
            {
                "folder_id": prescription.folder_id.id,
                "prescription_ids": [(6, 0, [prescription.id])],
                "type": "ids",
            }
        )
        self.env["prescriptions.shared.spreadsheet"].create(
            {
                "share_id": share.id,
                "prescription_id": prescription.id,
                "spreadsheet_data": prescription.spreadsheet_data,
            }
        )
        return share
