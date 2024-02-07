

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PrescriptionReDeliveryWizard(models.TransientModel):
    _name = "prescription.delivery.wizard"
    _description = "Prescription Delivery Wizard"

    prescription_count = fields.Integer()
    type = fields.Selection(
        selection=[("replace", "Replace"), ("return", "Return to customer")],
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Replace Product",
    )
    product_uom_qty = fields.Float(
        string="Product qty",
        digits="Product Unit of Measure",
    )
    product_uom = fields.Many2one(comodel_name="uom.uom", string="Unit of measure")
    scheduled_date = fields.Datetime(required=True, default=fields.Datetime.now)
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        required=True,
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    prescription_return_grouping = fields.Boolean(
        string="Group Prescription returns by customer address and warehouse",
        default=lambda self: self.env.company.prescription_return_grouping,
    )

    @api.constrains("product_uom_qty")
    def _check_product_uom_qty(self):
        self.ensure_one()
        prescription_ids = self.env.context.get("active_ids")
        if len(prescription_ids) == 1 and self.product_uom_qty <= 0:
            raise ValidationError(_("Quantity must be greater than 0."))

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        prescription_ids = self.env.context.get("active_ids")
        prescription = self.env["prescription"].browse(prescription_ids)
        warehouse_id = (
            self.env["stock.warehouse"]
            .search([("company_id", "=", prescription[0].company_id.id)], limit=1)
            .id
        )
        delivery_type = self.env.context.get("prescription_delivery_type")
        product_id = False
        if len(prescription) == 1 and delivery_type == "return":
            product_id = prescription.product_id.id
        product_uom_qty = 0.0
        if len(prescription) == 1 and prescription.remaining_qty > 0.0:
            product_uom_qty = prescription.remaining_qty
        res.update(
            prescription_count=len(prescription),
            warehouse_id=warehouse_id,
            type=delivery_type,
            product_id=product_id,
            product_uom_qty=product_uom_qty,
        )
        return res

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            if not self.product_uom or self.product_id.uom_id.id != self.product_uom.id:
                self.product_uom = self.product_id.uom_id

    def action_deliver(self):
        self.ensure_one()
        prescription_ids = self.env.context.get("active_ids")
        prescription = self.env["prescription"].browse(prescription_ids)
        if self.type == "replace":
            prescription.create_replace(
                self.scheduled_date,
                self.warehouse_id,
                self.product_id,
                self.product_uom_qty,
                self.product_uom,
            )
        elif self.type == "return":
            qty = uom = None
            if self.prescription_count == 1:
                qty, uom = self.product_uom_qty, self.product_uom
            prescription.with_context(
                prescription_return_grouping=self.prescription_return_grouping
            ).create_return(self.scheduled_date, qty, uom)
