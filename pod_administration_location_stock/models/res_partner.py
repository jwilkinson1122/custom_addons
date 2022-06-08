
from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    stock_location_id = fields.Many2one(comodel_name="stock.location")

    stock_picking_type_id = fields.Many2one(comodel_name="stock.picking.type")
