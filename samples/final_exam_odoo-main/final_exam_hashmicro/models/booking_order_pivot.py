from odoo import models, fields


class BookingOrderPivot(models.Model):
    _name = 'booking.order.pivot'
    _auto = False

    date_order = fields.Datetime('Order Date')
    partner_id = fields.Many2one('res.partner', 'Customer')
    amount_total = fields.Float('Total Amount')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status')

    def init(self):
        self._cr.execute("""
            CREATE OR REPLACE VIEW booking_order_pivot AS (
                SELECT
                    so.id,
                    so.date_order,
                    so.partner_id,
                    so.amount_total,
                    so.state
                FROM
                    sale_order so
                WHERE
                    so.is_booking = TRUE
            )
        """)
