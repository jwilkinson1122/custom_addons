from odoo import models, api, fields


class CompletePairOrder(models.TransientModel):
    _name = "complete.pair.order"

    prescription = fields.Many2one("practitioner.prescription", string="Prescription")

    shell_foundation = fields.Many2one("product.product", string="Shell / Foundation", domain="[('categ_id', '=', 'Shell / Foundation')]")
    arch_height = fields.Many2one("product.product", string="Arch Height", domain="[('categ_id', '=', 'Arch Height')]")
    topcover = fields.Many2one("product.product", string="Top Covers", domain="[('categ_id', '=', 'Top Covers')]")
    xguard = fields.Many2one("product.product", string="X-Guard", domain="[('categ_id', '=', 'X-Guard')]")
    cushion = fields.Many2one("product.product", string="Cushion", domain="[('categ_id', '=', 'Cushion')]")
    extension = fields.Many2one("product.product", string="Extension", domain="[('categ_id', '=', 'Extension')]")
    orthotic_options = fields.Many2many("product.product", string="Orthotic Options", domain="[('categ_id', '=', 'Orthotic Options')]")
    service = fields.Many2one("product.product", string="Services", domain="[('categ_id', '=', 'Service')]")
    miscellaneous = fields.Many2one(
        "product.product",
        string="Miscellaneous",
        domain="[('categ_id', '=', 'Miscellaneous')]",
    )

    def show_btn(self):
        SaleOrderLine = self.env["sale.order.line"].with_context(tracking_disable=True)
        section = (
            "Complete Pair Order" 
            if self.env.context.get("is_complete_pair", False)
            else (
                "Shell / Foundation"
                if self.env.context.get("is_shell_foundation", False)
                else (
                    "Arch Height"
                    if self.env.context.get("is_arch_height", False)
                    else (
                        "Top Covers"
                        if self.env.context.get("is_topcover", False)
                        else (
                            "X-Guard"
                            if self.env.context.get("is_xguard", False)
                            else (
                                "Cushion"
                                if self.env.context.get("is_cushion", False)
                                else(
                                    "Extension"
                                    if self.env.context.get("is_extension", False)
                                    else(
                                        "Miscellaneous"
                                        if self.env.context.get("is_miscellaneous", False)
                                        else False
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )

        if section:
            SaleOrderLine.create(
                {
                    "name": section,
                    "display_type": "line_section",
                    "order_id": self.env.context.get("active_id"),
                }
            )

        products = (
            self.topcover
            + self.lens_treatment
            + self.service
            + self.miscellaneous
            + self.lens
        )
        for product in products:
            quantity = 2 if product in (self.lens + self.contact_lens) else 1
            SaleOrderLine.create(
                {
                    "name": product.name,
                    "product_id": product.id,
                    "product_uom_qty": quantity,
                    "qty_delivered": 1,  # Set as needed
                    "product_uom": product.uom_id.id,
                    "price_unit": product.list_price,
                    "order_id": self.env.context.get("active_id"),
                }
            )
