# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    production_from_primary_ids = fields.One2many('mrp.production', 'sale_primary_id')
    picking_from_primary_ids = fields.One2many('stock.picking', 'sale_primary_id')
    
    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            order._cpq_generate_manufacturing_orders()
        return res

    def _cpq_generate_manufacturing_orders(self):
        for line in self.order_line:
            line._cpq_create_mo_if_needed()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    cpq_configuration_summary = fields.Html("CPQ Summary")  # Already exists in your system?
    cpq_dynamic_bom_id = fields.Many2one('cpq.dynamic.bom', help="Template-level Dynamic BoM chosen for this configuration")
    # cpq_selected_ptav_ids = fields.Many2many('product.template.attribute.value', string="Selected PTAVs")
    cpq_selected_ptav_ids = fields.Many2many(
        'product.template.attribute.value',
        relation='sol_cpq_selected_ptav_rel',    
        column1='sale_line_id',                
        column2='ptav_id',                     
        string="Selected PTAVs",
        help="PTAVs selected via the CPQ configurator."
    )
    cpq_custom_map = fields.Json(string="Custom values (by PTAV id)")
    cpq_laterality = fields.Selection([('left','Left'),('right','Right'),('bilateral','Bilateral')], string="Laterality")

    def _cpq_create_mo_if_needed(self):
        for line in self:
            product = line.product_id

            if not product or not product.product_tmpl_id.cpq_ok:
                continue

            if not product.bom_ids:
                raise UserError(_(
                    "Product %s has no Bill of Materials. Cannot generate Manufacturing Order."
                ) % product.display_name)

            bom = product.bom_ids[0]

            mo_vals = {
                'product_id': product.id,
                'product_qty': line.product_uom_qty,
                'product_uom_id': line.product_uom.id,
                'bom_id': bom.id,
                'origin': line.order_id.name,
                'sale_line_id': line.id,
                'cpq_configuration_summary': line.cpq_configuration_summary,
                'ptav_ids': [(6, 0, line.cpq_selected_ptav_ids.ids)],
            }

            mo = self.env['mrp.production'].create(mo_vals)
            mo.action_confirm()

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id)
        # push CPQ data downstream
        vals.update({
            'cpq_configuration_json': self.cpq_configuration_json or '',
            'cpq_configuration_summary': self.cpq_configuration_summary or '',
        })
        return vals