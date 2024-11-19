# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class directions(models.Model):
    _name = "directions"
    _description = "Podiatry Directions"
    _rec_name = "directions_pathology_id"

    directions_pathology_id = fields.Many2one("pathology", "Procedure")
    patient_evaluation_id = fields.Many2one("patient.evaluation", "Patient Evaluation")
    comments = fields.Char("Comments")
