from odoo import models, fields

class InfrastructureRequest(models.Model):
    _name = 'infrastructure.request'
    _description = 'Infrastructure Request'

    name = fields.Char("Request Name", required=True)
    request_type = fields.Selection([
        ('server', 'Server'),
        ('network', 'Network'),
        ('storage', 'Storage'),
    ], string="Request Type", required=True)
    quantity = fields.Integer("Quantity", default=1)
    description = fields.Text("Description")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft')
