from odoo import fields, models, api, _, tools


class OrthoticVehicleModel(models.Model):
    _inherit = "orthotic.model"

    @tools.ormcache()
    def _set_default_uom_id(self):
        """Method for Getting the default uom id"""
        return self.env.ref("uom.product_uom_km")

    price_per_km = fields.Float(string="Price/KM", default=1.0, help="Rent for Vehicle")
    uom_id = fields.Many2one(
        "uom.uom",
        string="Referensce Uom",
        help="UOM Of the Product",
        default=_set_default_uom_id,
        required=True,
    )
