# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockRequestTemplate(models.Model):
    _name = "stock.request.template"
    _description = "Stock Request Template"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    template_line_ids = fields.One2many(
        "stock.request.template.line", inverse_name="template_id"
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse", "Warehouse", ondelete="restrict", required=True
    )
    location_id = fields.Many2one(
        "stock.location",
        "Location",
        domain=[("usage", "in", ["internal", "transit"])],
        ondelete="restrict",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda self: self.env.company,
    )

    @api.onchange("warehouse_id")
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            # search with sudo because the user may not have permissions
            loc_wh = self.location_id.sudo().get_warehouse()
            if self.warehouse_id != loc_wh:
                self.location_id = self.warehouse_id.sudo().lot_stock_id

            if self.warehouse_id.sudo().company_id != self.company_id:
                self.company_id = self.warehouse_id.company_id

    @api.onchange("company_id")
    def onchange_company_id(self):
        if self.company_id and (
            not self.warehouse_id
            or self.warehouse_id.sudo().company_id != self.company_id
        ):
            self.warehouse_id = self.env["stock.warehouse"].search(
                [("company_id", "=", self.company_id.id)], limit=1
            )
            self.with_context(no_change_childs=True).onchange_warehouse_id()
        return {"domain": {"warehouse_id": [("company_id", "=", self.company_id.id)]}}

    @api.onchange("location_id")
    def onchange_location_id(self):
        if self.location_id:
            loc_wh = self.location_id.sudo().get_warehouse()
            if loc_wh and self.warehouse_id != loc_wh:
                self.warehouse_id = loc_wh
                self.with_context(no_change_childs=True).onchange_warehouse_id()


class StockRequestTemplateLine(models.Model):
    _name = "stock.request.template.line"
    _description = "stock.request.template.line"

    template_id = fields.Many2one("stock.request.template", required=True)
    product_id = fields.Many2one(
        "product.product",
        "Product",
        domain=[("type", "in", ["product", "consu"])],
        ondelete="restrict",
        required=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        "Product Unit of Measure",
        required=True,
    )

    product_uom_qty = fields.Float(
        "Quantity",
        digits="Product Unit of Measure",
        required=True,
        help="Quantity, specified in the unit of measure indicated in the " "request.",
    )

    @api.constrains("product_uom_qty")
    def _check_product_uom_qty(self):
        for rec in self:
            if rec.product_uom_qty <= 0:
                raise ValidationError(
                    _("Product quantity has to be strictly positive.")
                )

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = {"domain": {}}
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            res["domain"]["product_uom_id"] = [
                ("category_id", "=", self.product_id.uom_id.category_id.id)
            ]
            return res
        res["domain"]["product_uom_id"] = []
        return res
