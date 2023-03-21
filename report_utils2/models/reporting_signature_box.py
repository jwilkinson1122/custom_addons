# -*- coding: utf-8 -*-
from odoo import api, fields, models 


class ReportCustomTemplateSignatureBox(models.Model):
    _name = 'report.custom.template.signature.box'
    _description = 'Signature Box'

    report_line_id = fields.Many2one('report.custom.template.line', ondelete='cascade')
    heading = fields.Char(string="Heading")
    sequence = fields.Integer('Sequence', default=10)
