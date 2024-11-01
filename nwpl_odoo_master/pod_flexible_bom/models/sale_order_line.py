from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    allowed_bom_ids = fields.Many2many("mrp.bom", compute="_compute_allowed_bom_ids")
    bom_id = fields.Many2one("mrp.bom", string="BOM", domain="[('id', 'in', allowed_bom_ids)]")
    flexible_bom = fields.Boolean(string="Flexible bom", related="product_id.product_tmpl_id.flexible_bom")

    @api.depends("product_id")
    def _compute_allowed_bom_ids(self):
        for record_id in self:
            allowed_bom_ids = self.env["mrp.bom"].search([])
            if record_id.product_id:
                allowed_bom_ids = allowed_bom_ids.filtered(lambda m: m.product_tmpl_id == record_id.product_id.product_tmpl_id)
            record_id.allowed_bom_ids = allowed_bom_ids

    @api.onchange("product_id")
    def onchange_product_id(self):
        for record_id in self:
            if record_id.product_id:
                record_id.allowed_bom_ids = self.env["mrp.bom"].search([]).filtered(lambda m: m.product_tmpl_id == record_id.product_id.product_tmpl_id)

    @api.onchange("bom_id")
    def onchange_bom_id(self):
        if self.bom_id:
            product_id = self.product_id
            product_tmpl_id = product_id.product_tmpl_id
            purchase_price = self.product_id.standard_price
            total_cost = product_id._compute_bom_price(self.bom_id)
            if total_cost:
                purchase_price = total_cost
            self.purchase_price = purchase_price
            if product_tmpl_id.margin:
                self.price_unit = purchase_price / (1 - product_tmpl_id.margin)
        else:
            self.price_unit = self.product_id.list_price
            self.purchase_price = self.product_id.standard_price

    def action_set_bom(self):
        # This method opens the wizard for creating a new MRP BOM
        if self.bom_id:
            return
        bom_ids = self.env["mrp.bom"].search([("product_tmpl_id", "=", self.product_id.product_tmpl_id.id)]).sorted("sequence")
        bom_id = None
        if not bom_ids:
            bom_ids = self.env["mrp.bom"].search([("product_tmpl_id", "=", self.product_id.product_tmpl_id.id)]).sorted("id")
        if bom_ids:
            bom_id = bom_ids[0]
        action = {
            'name': 'Create MRP BOM',
            'view_mode': 'form',
            'res_model': 'create.mrp.bom.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
                'default_product_id': self.product_id.id,
                'active_id': self.id,
                'default_code': self.order_id.name,
                # Add other default values if needed
            },
        }
        if bom_id:
            action['context']['default_bom_template_id'] = bom_id.id
        return action

    def action_edit_bom(self):
        # This method opens the existing BOM in form view for editing
        if not self.bom_id:
            raise UserError('No BOM selected to edit.')
        action = {
            'name': 'Edit MRP BOM',
            'view_mode': 'form',
            'res_model': 'mrp.bom',
            'res_id': self.bom_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
                'default_product_id': self.product_id.id,
            },
        }
        return action
