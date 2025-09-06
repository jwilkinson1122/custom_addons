# -*- coding: utf-8 -*-
from odoo import fields, models

class MrpWorkorder(models.Model):
    _inherit = "mrp.workorder"
    
    ptav_ids = fields.Many2many(
        "product.template.attribute.value",
        "mrp_workorder_ptav_rel",
        "workorder_id", "ptav_id",
        string="CPQ Attribute Values"
    )
    
    sale_primary_id = fields.Many2one(related='production_id.sale_primary_id', store=True)
    cpq_configuration_json = fields.Text(related='production_id.cpq_configuration_json', store=True)
    cpq_configuration_summary = fields.Html(related='production_id.cpq_configuration_summary', store=True, sanitize=False)
    cpq_qr_code_image = fields.Binary("CPQ QR", related="production_id.cpq_qr_code_image", readonly=True)
