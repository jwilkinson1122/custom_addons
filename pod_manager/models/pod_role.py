# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.web_editor.controllers.main import handle_history_divergence


class Role(models.Model):

    _name = "pod.role"
    _description = "Role Position"
    _inherit = ['mail.thread']
    _order = 'sequence'

    name = fields.Char(string='Role Position', required=True, index=True, translate=True)
    sequence = fields.Integer(default=10)
    no_of_practitioner = fields.Integer(compute='_compute_practitioners', string="Current Number of Practitioners", store=True,
        help='Number of practitioners currently occupying this role position.')
    practitioner_ids = fields.One2many('pod.practitioner', 'role_id', string='Practitioners', groups='base.group_user')
    description = fields.Html(string='Role Description')
    practice_id = fields.Many2one('pod.practice', string='Practice', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, practice_id)', 'The name of the role position must be unique per practice in company!'),
    ]

    @api.depends('practitioner_ids.role_id', 'practitioner_ids.active')
    def _compute_practitioners(self):
        practitioner_data = self.env['pod.practitioner'].read_group([('role_id', 'in', self.ids)], ['role_id'], ['role_id'])
        result = dict((data['role_id'][0], data['role_id_count']) for data in practitioner_data)
        for role in self:
            role.no_of_practitioner = result.get(role.id, 0)
          

    @api.model
    def create(self, values):
        """ We don't want the current user to be follower of all created role """
        return super(Role, self.with_context(mail_create_nosubscribe=True)).create(values)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)") % (self.name)
        return super(Role, self).copy(default=default)

    def write(self, vals):
        if len(self) == 1:
            handle_history_divergence(self, 'description', vals)
        return super(Role, self).write(vals)
