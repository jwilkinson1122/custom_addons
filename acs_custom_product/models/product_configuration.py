
from odoo import api, fields, models, tools, _


class ProductLaboratory(models.Model):
    _name = 'product.laboratory'
    _description = 'Laboratorios'

    name = fields.Char('Nombre', required=True)


class ProductTherapeuticAction(models.Model):
    _name = 'product.therapeutic.action'
    _description = 'Terapeutica'

    name = fields.Char('Nombre', required=True)


class ProductPathology(models.Model):
    _name = 'product.pathology'
    _description = 'Patologia'

    name = fields.Char('Nombre', required=True)


class ProductActivePrinciple(models.Model):
    _name = 'product.active.principle'
    _description = 'Principio activo'

    name = fields.Char('Nombre', required=True)


