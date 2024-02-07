

from odoo import _, api, fields, models


class PrescriptionReSplitWizard(models.TransientModel):
    _name = "prescription.split.wizard"
    _description = "Prescription Split Wizard"

    prescription_id = fields.Many2one(
        comodel_name="prescription",
        string="Prescription",
    )
    product_uom_qty = fields.Float(
        string="Quantity to extract",
        digits="Product Unit of Measure",
        required=True,
        help="Quantity to extract to a new Prescription.",
    )
    product_uom = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of measure",
        required=True,
    )

    _sql_constraints = [
        (
            "check_product_uom_qty_positive",
            "CHECK(product_uom_qty > 0)",
            "Quantity must be greater than 0.",
        ),
    ]

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes=attributes)
        prescription_id = self.env.context.get("active_id")
        prescription = self.env["prescription"].browse(prescription_id)
        res["product_uom"]["domain"] = [
            ("category_id", "=", prescription.product_uom.category_id.id)
        ]
        return res

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        prescription_id = self.env.context.get("active_id")
        prescription = self.env["prescription"].browse(prescription_id)
        res.update(
            prescription_id=prescription.id,
            product_uom_qty=prescription.remaining_qty,
            product_uom=prescription.product_uom.id,
        )
        return res

    def action_split(self):
        self.ensure_one()
        extracted_prescription = self.prescription_id.extract_quantity(
            self.product_uom_qty, self.product_uom
        )
        return {
            "name": _("Extracted Prescription"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "prescription",
            "views": [(self.env.ref("prescription.view_prescription_form").id, "form")],
            "res_id": extracted_prescription.id,
        }
