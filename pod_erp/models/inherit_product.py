from odoo import api, models, fields,_

class InheritedProduct(models.Model):
    _inherit = "product.product"

    is_helpdesk = fields.Boolean("Helpdesk Ticket?")
    helpdesk_team = fields.Many2one('helpdesk.team', string='Helpdesk Team')
    helpdesk_assigned_to = fields.Many2one('res.users', string='Assigned to')
