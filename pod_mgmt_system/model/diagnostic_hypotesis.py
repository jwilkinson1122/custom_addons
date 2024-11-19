# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class diagnostic_hypotesis(models.Model):
    _name = "diagnostic_hypotesis"
    _description = "pod diagnostic hypotesis"
    _rec_name = "diagnostic_pathology_id"

    diagnostic_pathology_id = fields.Many2one("pathology", "Procedure")
    patient_evaluation_id = fields.Many2one("patient.evaluation", "Patient Evaluation")
    comments = fields.Char("Comments")
