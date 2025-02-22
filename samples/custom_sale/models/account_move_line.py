
from odoo import fields, models, api


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    last_sold_price = fields.Float(string="Last Sold Price", compute="_compute_last_sold_price", store=True)

    @api.depends('product_id')
    def _compute_last_sold_price(self):
        for line in self:
            if line.product_id and line.order_id.partner_id:
                query = """
                    SELECT sol.price_unit
                    FROM sale_order_line sol
                    JOIN sale_order so ON sol.order_id = so.id
                    WHERE sol.product_id = %s
                      AND so.partner_id = %s
                      AND so.state IN ('sale', 'done')
                    ORDER BY so.date_order DESC
                    LIMIT 1
                """
                self.env.cr.execute(query, (line.product_id.id, line.order_id.partner_id.id))
                last_sale = self.env.cr.fetchone()

                # line.last_sold_price = last_sale.price_unit if last_sale else 0.000
                line.last_sold_price = last_sale[0] if last_sale else 0.000
            else:
                line.last_sold_price = 0.000
