from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    version = fields.Float(string="Version", default=1.0)
    version_date = fields.Datetime(string="Version Date", default=lambda self: fields.Datetime.now())
    version_count = fields.Integer(string="Version Count", compute="_compute_version_count")

    def _compute_version_count(self):
        for order in self:
            order.version_count = self.env['sale.order.version'].search_count([('origin_order_id', '=', order.id)])

    def action_view_sale_order_versions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order Versions',
            'view_mode': 'tree,form',
            'res_model': 'sale.order.version',
            'domain': [('origin_order_id', '=', self.id)],
            'context': {'default_origin_order_id': self.id},
        }

    @api.model
    def create(self, vals):
        if 'version' not in vals:
            vals['version'] = 1.0
        if 'version_date' not in vals:
            vals['version_date'] = fields.Datetime.now()
        return super(SaleOrder, self).create(vals)

    def create_new_version(self):
        return {
            'name': 'Create New Version',
            'type': 'ir.actions.act_window',
            'res_model': 'version.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
            },
        }
