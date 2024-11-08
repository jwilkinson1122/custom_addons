from odoo import fields, models


class MaintenanceTeam(models.Model):
    _name = 'maintenance.team'
    _description = "Maintenance Team"

    name = fields.Char(string='Maintenance Team', help='Name of the maintenance team')
    user_id = fields.Many2one('res.users', string='Team Leader', help='Loader of Team')
    member_ids = fields.Many2many('res.users', string='Members', help='Members of the Team')