
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit = "product.template"

    is_medical_device = fields.Boolean(default=False)

    sct_code_id = fields.Many2one(
        string="Clinical Terms code",
        comodel_name="pod.sct.concept",
        domain=[("is_medical_device_code", "=", True)],
        help="Clinical Terms Prescription Codes",
    )

    over_the_counter = fields.Boolean(
        default=False,
        help="True if device does not require a prescription",
    )

    form_id = fields.Many2one(
        string="Form code",
        comodel_name="pod.sct.concept",
        domain=[("is_prescription_form", "=", True)],
        help="Clinical Terms Form Codes",
    )

    @api.constrains("type", "is_medical_device")
    def _check_prescription(self):
        if self.is_medical_device:
            if self.type not in ["product", "consu"]:
                raise ValidationError(
                    _("Device must be a stockable product")
                )
