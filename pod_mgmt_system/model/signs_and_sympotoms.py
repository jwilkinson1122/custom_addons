# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class signs_and_sympotoms(models.Model):
    _name = "signs.and.sympotoms"
    _description = "pod signs and sympotoms"
    _rec_name = "pathology_id"

    patient_evaluation_id = fields.Many2one("patient.evaluation", "Patient Evaluation")
    pathology_id = fields.Many2one("pathology", "Sign or Symptom")
    sign_or_symptom = fields.Selection(
        [
            ("sign", "Sign"),
            ("symptom", "Symptom"),
        ],
        string="Subjective / Objective",
    )
    comments = fields.Char("Comments")
