# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    # relationship = fields.Char(string='Relationship')
    # relative_partner_id = fields.Many2one('res.partner', string="Relative_id")
    is_patient = fields.Boolean(string='Patient')
    is_person = fields.Boolean(string="Person")
    is_doctor = fields.Boolean(string="Doctor")
    # is_insurance_company = fields.Boolean(string='Insurance Company')
    # is_pharmacy = fields.Boolean(string="Pharmacy")
    # patient_insurance_ids = fields.One2many('pod.insurance', 'patient_id')
    is_practice = fields.Boolean('Practice')

    is_active = fields.Boolean('Is Active')

    reference = fields.Char('ID Number')

    practitioner_role_ids = fields.Many2many(
        string="Practitioner Roles", comodel_name="pod.role"
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
