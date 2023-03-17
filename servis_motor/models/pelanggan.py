from email.policy import default
from odoo import api, fields, models

# Customers
class Pelanggan(models.Model):
    _inherit = 'res.partner'

    is_pegawainya = fields.Boolean(string='Pelanggan Baru',
    default=False
    )
    is_customernya = fields.Boolean(string='Member', default=False)
    

