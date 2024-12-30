from odoo import fields, models, api


class VersionWizard(models.TransientModel):
    _name = "version.wizard"

    order_id = fields.Many2one('sale.order', string="Order")
    version = fields.Float(string="Version")
    orders_ids = fields.One2many('sale.order.line.wizard', 'wizard_id', string="Version Orders")

    @api.model
    def default_get(self, fields_list):
        res = super(VersionWizard, self).default_get(fields_list)
        order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))

        line_data = []
        for line in order_id.order_line:
            line_data.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
            }))

        res.update({
            'order_id': order_id.id,
            'version': order_id.version,
            'orders_ids': line_data
        })
        return res

    def create_version(self):
        self.ensure_one()
        order = self.order_id

        # Store current version before replacing lines
        new_version = self.env['sale.order.version'].create({
            'origin_order_id': order.id,
            'version_number': order.version,
            'version_date': order.version_date,
            'partner_id': order.partner_id.id,
            'user_id': order.user_id.id,
            'date_order': order.date_order,
            'expiration': order.validity_date,
            'state': 'revision',  # Set the state to 'revision'
            'amount_total': order.amount_total,
            'currency_id': order.currency_id.id,
            'note': order.note,
            'pricelist_id': order.pricelist_id.id,
            'payment_term_id': order.payment_term_id.id,
            'order_line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
            }) for line in order.order_line],
        })

        # Update the name to include the version number
        new_version.name = f"{order.name} - {new_version.version_number}"

        # Delete existing order lines
        order.order_line.unlink()

        # Replace with wizard sale order lines
        for wizard_line in self.orders_ids:
            order.write({
                'order_line': [(0, 0, {
                    'product_id': wizard_line.product_id.id,
                    'name': wizard_line.name,
                    'product_uom_qty': wizard_line.product_uom_qty,
                    'price_unit': wizard_line.price_unit,
                })]
            })

        # Update the version and version_date
        order.write({
            'version': self.version,
            'version_date': fields.Datetime.now(),
        })

        return {'type': 'ir.actions.act_window_close'}