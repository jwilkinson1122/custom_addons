# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ForefootValue(models.Model):
    _name = 'pod.forefoot.value'
    _rec_name = 'name'
    _description = 'Podiatry Forefoot Value'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class ForefootCorrection(models.Model):
    _name = 'pod.forefoot.correction'
    _rec_name = 'name'
    _description = 'Podiatry Forefoot Correction'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class RearfootCorrection(models.Model):
    _name = 'pod.rearfoot.correction'
    _rec_name = 'name'
    _description = 'Podiatry Rearfoot Correction'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class OrthoticMeasure(models.Model):
    _name = 'pod.orthotic.measure'
    _rec_name = 'name'
    _description = 'Podiatry Orthotic Measure'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")
