# -*- coding: utf-8 -*-

from odoo import models, fields


class Blood(models.Model):
    _name = 'hospital.blood'
    _description = 'Blood Group'
    _rec_name = 'blood_grp'

    blood_grp = fields.Char(string="Blood Group", required="True")
    _sql_constraints = [('unique_blood', 'unique (blood_grp)',
                         'Blood group already present!')]


class GeneticRisks(models.Model):
    _name = 'genetic.risks'
    _description = ' Genetic Risks'
    _rec_name = 'risks'

    risks = fields.Char(string="Genetic Risks", required="True")

