from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def action_sale_order_line_copy(self):
        self.ensure_one()

        lines = self.order_id.order_line

        # Sort FIRST by sequence THEN by id
        sorted_lines = lines.sorted(key=lambda l: (l.sequence, l.id))

        # Big enough number is chosen because new lines have a default value of
        # 10 for their sequence.
        sequence = -1000

        # Index values start from 0. First element can have an index value of 0.
        self_index = sorted_lines.ids.index(self.id)

        for line in sorted_lines:
            line.sequence = sequence
            if sequence + 1000 == self_index:
                sequence += 1
                self.copy(
                    {
                        "order_id": self.order_id.id,
                        "sequence": sequence,
                    }
                )
            sequence += 1
