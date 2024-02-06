# -*- coding: utf-8 -*-


from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    def test_01_prescription_tour(self):
        self.start_tour("/web", 'prescription_tour', login="admin", step_delay=100)

    def test_02_prescription_tour_company_onboarding_done(self):
        self.env["onboarding.onboarding.step"].action_validate_step("account.onboarding_onboarding_step_company_data")
        self.start_tour("/web", "prescription_tour", login="admin", step_delay=100)

    def test_03_prescription_quote_tour(self):
        self.env['res.partner'].create({'name': 'Agrolait', 'email': 'agro@lait.be'})
        self.start_tour("/web", 'prescription_quote_tour', login="admin", step_delay=100)
