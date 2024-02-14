# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AnalysisTemplateItems(models.Model):
    """Analysis Template Items"""
    _name = 'analysis.template.item'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Title", required=True)
    analysis_template_id = fields.Many2one('analysis.template')


class AnalysisTemplate(models.Model):
    """Analysis Template"""
    _name = 'analysis.template'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    analysis_template_item_ids = fields.One2many('analysis.template.item', 'analysis_template_id',
                                                 string="Analysis Items")


class RequiredAnalysis(models.Model):
    """Required Analysis"""
    _name = 'required.analysis'
    _description = __doc__
    _rec_name = 'description'

    description = fields.Char(string="Description", required=True)
    is_check = fields.Boolean(string="Check")
    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order')

    @api.onchange('is_check')
    def required_analysis_check(self):
        for rec in self:
            if rec.is_check:
                rec.description = rec.description
            else:
                rec.description = False
