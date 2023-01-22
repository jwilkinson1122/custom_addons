# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .reporting_template import SEPARATORS


class ReportingCustomTemplateAddressField(models.Model):
    _name = 'report.custom.template.address.field'

    report_line_id = fields.Many2one('report.custom.template.line', ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    prefix = fields.Selection(SEPARATORS, string='Start With')
    model_id = fields.Many2one('ir.model', related='report_line_id.model_id', readonly=True)
    field_id = fields.Many2one('ir.model.fields', domain="[('model_id', '=', model_id)]")
    field_type = fields.Selection('Field Type', related='field_id.ttype', readonly=True)
    field_relation = fields.Char(related='field_id.relation', readonly=True)
    field_display_field_id = fields.Many2one('ir.model.fields', string="Display Field", domain="[('model_id.model', '=', field_relation)]")
    label = fields.Char(string='Label')
