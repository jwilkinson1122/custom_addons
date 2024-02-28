# -*- coding: utf-8 -*-


import odoo
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestSpreadsheetTemplate(HttpCase):

    def test_insert_pivot_in_spreadsheet(self):
        self.start_tour('/web', 'insert_crm_pivot_in_spreadsheet', login='admin')
