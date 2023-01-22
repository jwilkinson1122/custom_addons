# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .reporting_template import ALIGNMENT_VALS


class ReportingCustomTemplateLinessField(models.Model):
    _name = 'report.custom.template.lines.field'

    report_line_id = fields.Many2one('report.custom.template.line', ondelete='cascade')
    model_id = fields.Many2one('ir.model', related='report_line_id.model_id', readonly=True)
    sequence = fields.Integer('Sequence', default=10)
    field_id = fields.Many2one('ir.model.fields', domain="[('model_id', '=', model_id)]")
    field_type = fields.Selection('Field Type', related='field_id.ttype', readonly=True)
    field_relation = fields.Char(related='field_id.relation', readonly=True)
    field_display_field_id = fields.Many2one('ir.model.fields', string="Display Field",
                                             domain="[('model_id.model', '=', field_relation)]")
    currency_field_name = fields.Char(string='Currency Field')
    label = fields.Char(string='Label')
    width = fields.Char(string='Width')
    alignment = fields.Selection(ALIGNMENT_VALS, string='Alignment')
    null_hide_column = fields.Boolean(string='Hide Column if Null')
    thousands_separator = fields.Selection([('not_applicable', 'Not Applicable'), ('applicable', 'Applicable')], default='not_applicable')
    remove_decimal_zeros = fields.Boolean(string="Remove Decimal Zeros", default=False)


