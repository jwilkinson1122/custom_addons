from odoo import fields, models, api


class SaleOrderVersion(models.Model):
    _name = "sale.order.version"
    _description = "Sale Order Version"

    origin_order_id = fields.Many2one('sale.order', string="Original Order")
    version_number = fields.Float(string="Version Number")
    version_date = fields.Datetime(string="Version Date")
    user_id = fields.Many2one('res.users', string="Salesperson")

    # Additional fields from sale.order
    name = fields.Char(string="Version Name", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer")
    date_order = fields.Datetime(string="Order Date")
    expiration = fields.Date(string="Expiration")
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('revision', 'Revision'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string="Status", default='revision')

    amount_total = fields.Monetary(string="Total", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Currency")
    note = fields.Text(string="Terms and Conditions")
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms")

    # Relate to sale.order.line.version
    order_line_ids = fields.One2many('sale.order.line.version', 'order_version_id', string="Order Lines")

    def action_restore_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm Restoration',
            'res_model': 'sale.order.version.restore.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_version_id': self.id, 'active_id': self.origin_order_id.id}
        }

    def restore_order(self):
        # Get the current sale.order record from the context
        sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
        # Update sale order with version details
        name = self.name.split(' - ')[0]  # This will take only the part before " - "

        if sale_order:
            # Check if the current sale.order already exists in the sale.order.version
            existing_version = self.search([
                ('origin_order_id', '=', sale_order.id),
                ('version_number', '=', sale_order.version)
            ], limit=1)

            if not existing_version:
                # Create a new sale.order.version record to save the current sale.order state
                new_version = self.create({
                    'origin_order_id': sale_order.id,
                    'version_number': sale_order.version,
                    'version_date': sale_order.version_date,
                    'user_id': sale_order.user_id.id,
                    'partner_id': sale_order.partner_id.id,
                    'date_order': sale_order.date_order,
                    'amount_total': sale_order.amount_total,
                    'currency_id': sale_order.currency_id.id,
                    'note': sale_order.note,
                    'pricelist_id': sale_order.pricelist_id.id,
                    'payment_term_id': sale_order.payment_term_id.id,
                    'order_line_ids': [(0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'subtotal': line.price_subtotal,
                    }) for line in sale_order.order_line],
                })

                # Update the name to include the version number
                new_version.name = f"{name} - {new_version.version_number}"

            sale_order.write({
                'version': self.version_number,
                'version_date': self.version_date,
                'name': name,
                'partner_id': self.partner_id.id,
                'date_order': self.date_order,
                'amount_total': self.amount_total,
                'currency_id': self.currency_id.id,
                'note': self.note,
                'payment_term_id': self.payment_term_id.id,
            })

            # Cancel existing stock pickings associated with this sale order
            pickings = sale_order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
            pickings.action_cancel()

            # If the sale.order is confirmed, set the quantity of existing order lines to 0
            if sale_order.state in ['sale', 'done']:
                for line in sale_order.order_line:
                    line.write({'product_uom_qty': 0})
            else:
                # If the sale.order is not confirmed, unlink the existing order lines
                sale_order.order_line.unlink()

            sale_order.order_line = [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
                'price_subtotal': line.subtotal
            }) for line in self.order_line_ids]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }
