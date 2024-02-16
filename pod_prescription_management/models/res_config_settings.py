# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_prescription_order_template = fields.Boolean(
        "Draft RX Templates", implied_group='pod_prescription_management.group_prescription_order_template')
    company_rx_template_id = fields.Many2one(
        related="company_id.prescription_order_template_id", string="Default Template", readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    def set_values(self):
        if not self.group_prescription_order_template:
            if self.company_rx_template_id:
                self.company_rx_template_id = False
            companies = self.env['res.company'].sudo().search([
                ('prescription_order_template_id', '!=', False)
            ])
            if companies:
                companies.prescription_order_template_id = False
        super().set_values()
