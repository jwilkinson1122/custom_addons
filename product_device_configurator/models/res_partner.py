from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_device_pricelist_id = fields.Many2one(
        'device.pricelist',
        company_dependent=True,
        string="Device Pricelist",
    )

    def _commercial_fields(self):
        return super()._commercial_fields() + ['property_device_pricelist_id']
