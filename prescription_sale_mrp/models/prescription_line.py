
from odoo import _, fields, models
from odoo.exceptions import UserError


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

    def _get_refund_line_quantity(self):
        """Refund the kit, not the component"""
        if self.phantom_bom_product:
            uom = self.sale_line_id.product_uom or self.phantom_bom_product.uom_id
            return (self.kit_qty, uom)
        return (self.product_uom_qty, self.product_uom)

    def action_refund(self):
        """We want to process them altogether"""
        phantom_prescription = self.filtered("phantom_bom_product")
        phantom_prescription |= self.search(
            [
                ("prescription_kit_register", "in", phantom_prescription.mapped("prescription_kit_register")),
                ("id", "not in", phantom_prescription.ids),
            ]
        )
        self -= phantom_prescription
        for prescription_kit_register in phantom_prescription.mapped("prescription_kit_register"):
            # We want to avoid refunding kits that aren't completely processed
            prescription_by_register = phantom_prescription.filtered(
                lambda x: x.prescription_kit_register == prescription_kit_register
            )
            if any(prescription_by_register.filtered(lambda x: x.state != "received")):
                raise UserError(
                    _("You can't refund a kit in wich some Prescription aren't received")
                )
            self |= prescription_by_register[0]
        res = super().action_refund()
        # We can just link the line to an Prescription but we can link several Prescription
        # to one invoice line.
        for prescription_kit_register in set(phantom_prescription.mapped("prescription_kit_register")):
            grouped_prescription = phantom_prescription.filtered(
                lambda x: x.prescription_kit_register == prescription_kit_register
            )
            lead_prescription = grouped_prescription.filtered("refund_line_id")
            grouped_prescription -= lead_prescription
            grouped_prescription.write(
                {
                    "refund_line_id": lead_prescription.refund_line_id.id,
                    "refund_id": lead_prescription.refund_id.id,
                    "state": "refunded",
                }
            )
        return res

    def action_draft(self):
        if self.filtered(lambda r: r.state == "cancelled" and r.phantom_bom_product):
            raise UserError(
                _(
                    "To avoid kit quantities inconsistencies it is not possible to convert "
                    "to draft a cancelled Prescription. You should do a new one from the sales order."
                )
            )
        return super().action_draft()
