# -*- coding: utf-8 -*-


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    plan_to_change_prescription = fields.Boolean('Plan To Change Prescription', default=False, tracking=True)
    plan_to_change_otc = fields.Boolean('Plan To Change OTC', default=False)
