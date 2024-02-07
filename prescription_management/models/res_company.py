# -*- coding: utf-8 -*-


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    _check_company_auto = True

    prescription_template_id = fields.Many2one(
        "prescription.template", string="Default Prescription Template",
        domain="['|', ('company_id', '=', False), ('company_id', '=', id)]",
        check_company=True,
    )
