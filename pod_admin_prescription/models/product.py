

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Product(models.Model):

    _inherit = "product.template"

    is_device = fields.Boolean(default=False)
    sct_code_id = fields.Many2one(
        string="SNOMED CT code",
        comodel_name="podiatry.sct.concept",
        domain=[("is_device_code", "=", True)],
        help="SNOMED CT Device Codes",
    )  # Field: code

    over_the_counter = fields.Boolean(
        default=False,
        help="True if device does not require a prescription",
    )  # Field: isOverTheCounter
    form_id = fields.Many2one(
        string="Form code",
        comodel_name="podiatry.sct.concept",
        domain=[("is_device_form", "=", True)],
        help="SNOMED CT Form Codes",
    )  # Field: form

    @api.constrains("type", "is_device")
    def _check_device(self):
        if self.is_device:
            if self.type not in ["product", "consu"]:
                raise ValidationError(
                    _("Device must be a stockable product")
                )
