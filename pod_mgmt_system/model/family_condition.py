# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class family_condition(models.Model):
    _name = "family.condition"
    _description = "Family Condition"
    _rec_name = "pathology_id"

    pathology_id = fields.Many2one("pathology", "Condition", required=True)
    relative = fields.Selection(
        [
            ("m", "Mother"),
            ("f", "Father"),
            ("b", "Brother"),
            ("s", "Sister"),
            ("a", "aunt"),
            ("u", "Uncle"),
            ("ne", "Nephew"),
            ("ni", "Niece"),
            ("gf", "GrandFather"),
            ("gm", "GrandMother"),
        ],
        string="Relative",
    )
    metrnal = fields.Selection(
        [("m", "Maternal"), ("p", "Paternal")], string="Maternal"
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
