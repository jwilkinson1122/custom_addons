# -*- coding: utf-8 -*-


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    prescription_count = fields.Integer(
        '# Prescriptions', compute='_compute_prescription_count', groups='prescription.group_prescription_registration_desk',
        help='Number of prescriptions the partner has participated.')

    def _compute_prescription_count(self):
        self.prescription_count = 0
        for partner in self:
            partner.prescription_count = self.env['prescription.prescription'].search_count([('registration_ids.partner_id', 'child_of', partner.ids)])

    def action_prescription_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("prescription.action_prescription_view")
        action['context'] = {}
        action['domain'] = [('registration_ids.partner_id', 'child_of', self.ids)]
        return action
