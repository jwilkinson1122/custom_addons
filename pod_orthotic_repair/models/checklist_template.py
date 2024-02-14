# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CheckListTemplateItems(models.Model):
    """Check List Template Items"""
    _name = 'checklist.template.item'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Title", required=True)
    checklist_template_id = fields.Many2one('checklist.template')


class ChecklistTemplate(models.Model):
    """Check List Template"""
    _name = 'checklist.template'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    checklist_template_item_ids = fields.One2many('checklist.template.item', 'checklist_template_id',
                                                  string="Checklist Items")


class RepairChecklist(models.Model):
    """Repair Check List"""
    _name = 'repair.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Char(string="Description", translate=True)
    is_check = fields.Boolean(string="Check")
    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order')

    @api.onchange('is_check')
    def repair_checklist_check(self):
        for rec in self:
            if rec.is_check:
                rec.name = rec.name
            else:
                rec.name = False
