# -*- coding: utf-8 -*-
from odoo import api, fields, models


class OpticalSphType(models.Model):
    _name = 'optical.sph.type'
    _rec_name = 'name'
    _description = 'Optical SPH Types'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class OpticalCylType(models.Model):
    _name = 'optical.cyl.type'
    _rec_name = 'name'
    _description = 'Optical CYL Types'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class OpticalAxisType(models.Model):
    _name = 'optical.axis.type'
    _rec_name = 'name'
    _description = 'Optical Axis Types'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class OpticalAddType(models.Model):
    _name = 'optical.add.type'
    _rec_name = 'name'
    _description = 'Optical Add Types'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")


class OpticalPrismType(models.Model):
    _name = 'optical.prism.type'
    _rec_name = 'name'
    _description = 'Optical Prism Types'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    note = fields.Text(string="Remarks")

