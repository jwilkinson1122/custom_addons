from odoo import models, fields, api, _ 
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_cash_control = fields.Boolean(string="Enable Cash Control", related="pos_config_id.pos_cash_control", readonly=False)
    
    # pos_cash_control = fields.Boolean(related='pos_config_id.cash_control')
 