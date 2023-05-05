from odoo import api, fields, models


class PrescriptionImportProducts(models.TransientModel):
    _name = "prescription.import.products"
    _description = "Prescription Import Products"

    products = fields.Many2many(comodel_name="product.product")
    items = fields.One2many(comodel_name="prescription.import.products.items", inverse_name="wizard_id")
 
    def create_items(self):
        for wizard in self:
            for product in wizard.products:
                self.env["prescription.import.products.items"].create(
                    {"wizard_id": wizard.id, "product_id": product.id}
                )
        view = self.env.ref("podiatry.view_import_product_to_prescription2")
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_type": "form",
            "view_mode": "form",
            "views": [(view.id, "form")],
            "target": "new",
            "res_id": self.id,
            "context": self.env.context,
        }

    @api.model
    def _get_line_values(self, prescription, item):
        prescription_line = self.env["podiatry.prescription.line"].new(
            {
                "prescription_id": prescription.id,
                "name": item.product_id.name,
                "product_id": item.product_id.id,
                "product_uom_qty": item.quantity,
                "product_uom": item.product_id.uom_id.id,
                "price_unit": item.product_id.list_price,
            }
        )
        prescription_line._onchange_product_id()
        line_values = prescription_line._convert_to_write(prescription_line._cache)
        return line_values

    def select_products(self):
        prescription_obj = self.env["podiatry.prescription"]
        for wizard in self:
            prescription = prescription_obj.browse(self.env.context.get("active_id", False))

            if prescription:
                for item in wizard.items:
                    vals = self._get_line_values(prescription, item)
                    if vals:
                        self.env["podiatry.prescription.line"].create(vals)

        return {"type": "ir.actions.act_window_close"}


class prescriptionImportProductsItem(models.TransientModel):
    _name = "prescription.import.products.items"
    _description = "prescription Import Products Items"

    prescription_id = fields.Many2one("podiatry.prescription", "Prescription Number", ondelete="cascade")
    wizard_id = fields.Many2one(string="Wizard", comodel_name="prescription.import.products")
    product_id = fields.Many2one(
        string="Product", comodel_name="product.product", required=True
    )
    quantity = fields.Float(
        digits="Product Unit of Measure", default=1.0, required=True
    )
   
    
 
    
    # type = fields.Selection(string='Type', selection=[('lt', 'LT'), ('rt', 'RT')])
