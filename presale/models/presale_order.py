from odoo import api, fields, models


class PresaleOrder(models.Model):
    _name = "presale.order"
    _description = "Presale order model"

    active = fields.Boolean(default=True)
    name = fields.Char(default="Draft", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    state = fields.Selection(
        default="new",
        required=True,
        selection=[("new", "Draft"), ("validated", "Validated"), ("cancelled", "Cancelled")],
    )
    order_line_ids = fields.One2many("presale.order.line", "presale_order_id")

    @api.model
    def create(self, vals):
        if vals.get("name") == "Draft":
            vals["name"] = self.env["ir.sequence"].next_by_code("presale.order.name")
        res = super(PresaleOrder, self).create(vals)
        return res

    def send_validation_email(self):
        mail_template = self.env.ref("presale.presale_order_validation_email")
        mail_template.send_mail(self.id, force_send=True)

    def action_validate_preorder(self):
        for record in self:
            if record.state == "new":
                sale_order = self.env["sale.order"].create(
                    {
                        "name": record.name,
                        "partner_id": record.partner_id.id,
                    }
                )
                presale_order_lines = list()
                for line in record.order_line_ids:
                    presale_order_lines.append(
                        {
                            "order_id": sale_order.id,
                            "product_id": line.product_id.id,
                            "product_uom_qty": line.quantity,
                            "price_unit": line.price,
                        }
                    )
                self.env["sale.order.line"].create(presale_order_lines)
                sale_order.presale_order = record.id
                record.state = "validated"
                record.send_validation_email()

    def action_cancel_preorder(self):
        self.filtered(lambda rec: rec.state == "new").state = "cancelled"

    def archive_confirmed_orders(self):
        self.filtered(lambda rec: rec.state == "validated").action_archive()
