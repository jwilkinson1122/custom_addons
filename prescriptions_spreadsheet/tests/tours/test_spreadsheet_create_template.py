# -*- coding: utf-8 -*-


from ..common import SpreadsheetTestCommon

from odoo.tests import tagged
from odoo.tests.common import HttpCase

@tagged("post_install", "-at_install")
class TestSpreadsheetCreateTemplate(SpreadsheetTestCommon, HttpCase):

    def test_01_spreadsheet_create_template(self):
        self.start_tour("/web", "prescriptions_spreadsheet_create_template_tour", login="admin")
