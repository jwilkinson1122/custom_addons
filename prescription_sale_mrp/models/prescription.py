
from odoo import _, fields, models
from odoo.exceptions import UserError


class Prescription(models.Model):
    _inherit = "prescription"

        # Add a related field to fetch 'phantom_bom_product' from the associated prescription_line
    phantom_bom_product = fields.Many2one(
        comodel_name="product.product",
        string="Related kit product",
        readonly=True,
        related="prescription_line_ids.phantom_bom_product", 
    )

    prescription_line_ids = fields.One2many(
        comodel_name="prescription.line",
        inverse_name="prescription_id",
        string="Prescription Lines",
        copy=True,
    )

    def _get_refund_line_quantity(self, prescription_line):
        """Refund the kit, not the component"""
        if prescription_line.phantom_bom_product:
            uom = prescription_line.sale_line_id.product_uom or prescription_line.phantom_bom_product.uom_id
            return (prescription_line.kit_qty, uom)
        return (prescription_line.product_uom_qty, prescription_line.product_uom)

    def action_refund(self):
        """Refund prescription lines"""
        self.ensure_one()
        if self.state == "received":
            raise UserError(_("You can't refund a received prescription"))

        prescription_lines = self.env["prescription.line"].search([
            ("prescription_id", "=", self.id),
            ("state", "!=", "received")
        ])

        phantom_prescription = prescription_lines.filtered("phantom_bom_product")
        phantom_prescription |= prescription_lines.search([
            ("prescription_kit_register", "in", phantom_prescription.mapped("prescription_kit_register")),
            ("id", "not in", phantom_prescription.ids),
        ])
        prescription_lines -= phantom_prescription

        for prescription_kit_register in phantom_prescription.mapped("prescription_kit_register"):
            # We want to avoid refunding kits that aren't completely processed
            prescription_by_register = phantom_prescription.filtered(
                lambda x: x.prescription_kit_register == prescription_kit_register
            )
            if any(prescription_by_register.filtered(lambda x: x.state != "received")):
                raise UserError(_("You can't refund a kit in which some prescriptions aren't received"))

        # Call the action_refund method for each prescription line
        refund_lines = self.env["sale.order.line"]
        for prescription_line in prescription_lines:
            refund_line = prescription_line.action_refund()
            refund_lines |= refund_line

        # Link the refund lines to this prescription
        refund_lines.write({"prescription_id": self.id, "state": "refunded"})

        return True

    def action_draft(self):
        if self.filtered(lambda r: r.state == "cancelled" and r.prescription_line.filtered(lambda line: line.phantom_bom_product)):
            raise UserError(_("To avoid kit quantities inconsistencies, it is not possible to convert to draft a cancelled Prescription with kit products. You should create a new one from the sales order."))
        return super().action_draft()

    
class PrescriptionLine(models.Model):
    _inherit = "prescription.line"

    phantom_bom_product = fields.Many2one(
        comodel_name="product.product",
        string="Related kit product",
        readonly=True,
    )
   
    kit_qty = fields.Float(
        string="Kit quantity",
        digits="Product Unit of Measure",
        readonly=True,
        help="To how many kits this components corresponds to. Used mainly "
        "for refunding the right quantity",
    )

    prescription_kit_register = fields.Char(readonly=True)
 