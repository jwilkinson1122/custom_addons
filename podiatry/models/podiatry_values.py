# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ForefootValue(models.Model):
    _name = 'podiatry.forefoot.value'
    _rec_name = 'name'
    _description = 'Podiatry Forefoot Value'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class ForefootCorrection(models.Model):
    _name = 'podiatry.forefoot.correction'
    _rec_name = 'name'
    _description = 'Podiatry Forefoot Correction'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class RearfootCorrection(models.Model):
    _name = 'podiatry.rearfoot.correction'
    _rec_name = 'name'
    _description = 'Podiatry Rearfoot Correction'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class OrthoticMeasure(models.Model):
    _name = 'podiatry.orthotic.measure'
    _rec_name = 'name'
    _description = 'Podiatry Orthotic Measure'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")
