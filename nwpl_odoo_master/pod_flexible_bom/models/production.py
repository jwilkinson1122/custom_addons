from odoo import models, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def create(self, vals):
        ret = super().create(vals)
        for record_id in ret:
            if record_id.origin:
                origins = record_id.origin.split(" - ")
                for origin in origins:
                    so_id = self.env["sale.order"].search([("name", "=", origin)])
                    if not so_id:
                        continue
                    for order_line in so_id.order_line:
                        if not order_line.product_id or (order_line.product_id and order_line.product_id != record_id.product_id):
                            continue
                        if order_line.bom_id:
                            record_id.write({"bom_id": order_line.bom_id.id})
        return ret
