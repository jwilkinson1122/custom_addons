

from odoo import fields, models


class PodRole(models.Model):

    _name = "pod.role"
    _description = "Practitioner Roles"

    name = fields.Char(string='Role', help='Clinic role type', required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
    # _sql_constraints = [
    #     ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    # ]
