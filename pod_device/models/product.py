from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit = "product.template"

    is_device = fields.Boolean(default=False)
    sct_code_id = fields.Many2one(
        string="SNOMED CT code",
        comodel_name="pod.sct.concept",
        domain=[("is_device_code", "=", True)],
        help="SNOMED CT Device Codes",
    )  
    
    atc_code_id = fields.Many2one(
        string="ATC code",
        comodel_name="pod.atc.concept",
        help="ATC device classification",
    )
    
    over_the_counter = fields.Boolean(
        default=False,
        help="True if device does not require a device",
    )  # FHIR Field: isOverTheCounter
    
    form_id = fields.Many2one(
        string="Form code",
        comodel_name="pod.sct.concept",
        domain=[("is_device_form", "=", True)],
        help="SNOMED CT Form Codes",
    )  # FHIR Field: form

    @api.constrains("type", "is_device")
    def _check_device(self):
        if self.is_device:
            if self.type not in ["product", "consu"]:
                raise ValidationError(
                    _("Device must be a stockable product")
                )
