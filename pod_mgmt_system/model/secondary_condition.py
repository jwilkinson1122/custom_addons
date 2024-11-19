# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class secondary_condition(models.Model):
    _name = "secondary_condition"
    _description = "pod secondary condition"
    _rec_name = "pathology_id"

    patient_evaluation_id = fields.Many2one("patient.evaluation", "Patient Evaluation")
    pathology_id = fields.Many2one("pathology", "Pathology")
    comments = fields.Char("Comments")
