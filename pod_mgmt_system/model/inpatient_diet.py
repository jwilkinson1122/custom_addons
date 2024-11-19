# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class inpatient_diet(models.Model):
    _name = "inpatient.diet"
    _description = "Inpatient Diet"

    diet_id = fields.Many2one("diet.therapeutic", string="Diet", required=True)
    remarks = fields.Text(string=" Remarks / Directions ")
    inpatient_registration_id = fields.Many2one(
        "inpatient.registration", string="Inpatient Id"
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
