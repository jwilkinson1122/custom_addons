# -*- coding: utf-8 -*-
from odoo import api, fields, models


# DEPRECATED
class ReportCustomTemplateHeaderFooterImg(models.Model):
    _name = 'report.custom.template.header.footer.img'
    _description = 'Report Custom Template Header Footer Image'

    report_line_id = fields.Many2one('report.custom.template.line', ondelete='cascade')
    company_id = fields.Many2one("res.company", string='Company')
    header = fields.Binary(string="Header")
    footer = fields.Binary(string="Footer")
