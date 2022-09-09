# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_family_condition(models.Model):
    _name = 'podiatry.family.condition'
    _description = 'Podiatry Family Condition'
    _rec_name = 'podiatry_pathology_id'

    podiatry_pathology_id = fields.Many2one(
        'podiatry.pathology', 'Condition', required=True)
    relative = fields.Selection([('m', 'Mother'), ('f', 'Father'), ('b', 'Brother'), ('s', 'Sister'), ('a', 'aunt'), (
        'u', 'Uncle'), ('ne', 'Nephew'), ('ni', 'Niece'), ('gf', 'GrandFather'), ('gm', 'GrandMother')], string="Relative")
    metrnal = fields.Selection(
        [('m', 'Maternal'), ('p', 'Paternal')], string="Maternal")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
