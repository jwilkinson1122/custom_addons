# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .reporting_template import ALIGNMENT_VALS

colors = ['#bfb781', '#81bcbf', '#dcaf95', '#acafd0', '#daa6a6', '#93c193']


class ReportingTemplateTemplateLine(models.Model):
    _name = 'report.custom.template.line'

    report_id = fields.Many2one('report.custom.template', ondelete='cascade')
    model_id = fields.Many2one('ir.model', readonly=True)
    name_technical = fields.Char()
    name = fields.Char(string="Name")
    type = fields.Selection([
        ('fields', 'fields'),
        ('address', 'Address'),
        ('lines', 'Lines'),
        ('options', 'Options'),
        ('header_footer_images', 'Header Footer Images'),  # DEPRECATED
        ('signature_boxes', 'Signature Boxes'),
    ])
    color = fields.Char()
    field_ids = fields.One2many('report.custom.template.fields.field', 'report_line_id')
    address_field_ids = fields.One2many('report.custom.template.address.field', 'report_line_id')
    option_field_ids = fields.One2many('report.custom.template.options.field', 'report_line_id')
    line_field_ids = fields.One2many('report.custom.template.lines.field', 'report_line_id')
    header_footer_img_ids = fields.One2many('report.custom.template.header.footer.img', 'report_line_id')  # DEPRECATED (Using options for images)
    signature_box_ids = fields.One2many('report.custom.template.signature.box', 'report_line_id')
    preview_img = fields.Char()
    data_field_names = fields.Char()

    @api.model
    def create(self, vals):
        res = super(ReportingTemplateTemplateLine, self).create(vals)
        for each in res:
            each.color = colors[each.id % len(colors)]
        return res

