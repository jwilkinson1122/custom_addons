# -*- coding: utf-8 -*-


from odoo.tests import HttpCase, tagged
from odoo import tools


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    # Avoid "A Chart of Accounts is not yet installed in your current company."
    # Everything is set up correctly even without installed CoA
    @tools.mute_logger('odoo.http')
    def test_01_podiatry_manager_tour(self):

        self.start_tour("/web", 'podiatry_manager_tour', login="admin")
