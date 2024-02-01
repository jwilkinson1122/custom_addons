# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PodiatryLocation(models.Model):
    _name = "pod.location"
    _description = "Location"
    _inherit = ['mail.thread']
    _order = "name"
    _rec_name = 'complete_name'
    _parent_store = True


    active = fields.Boolean(default=True)
    name = fields.Char(string="Location", required=True)
    partner_id = fields.Many2one('res.partner')
    # partner_id = fields.Many2one('res.partner', index=True, domain=[('is_company', '=', True)], string="Account")

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    location_type_id = fields.Many2one(string='Type', comodel_name='pod.location.type')
    location_type = fields.Selection(
        [('clinic', 'Clinic'),
         ('hospital', 'Hospital'),
         ('military_va', 'Military/VA'),
         ('other', 'Other'),
        ], string='Type', default='clinic', required=True)
    address_id = fields.Many2one('res.partner', required=True, string="Address")
    location_number = fields.Char()


    name = fields.Char('Location Name', required=True, translate=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    parent_id = fields.Many2one('pod.location', string='Parent Location', index=True, check_company=True)
    child_ids = fields.One2many('pod.location', 'parent_id', string='Child Locations')
    manager_id = fields.Many2one('res.partner', string='Manager', tracking=True, check_company=True)
    location_ids = fields.One2many('res.partner', 'location_id', string='Partners', readonly=True)
    # location_ids = fields.One2many("res.partner", compute="_compute_locations", string="Locations", readonly=True)
    total_practitioner = fields.Integer(compute='_compute_total_practitioner', string='Practitioners Count')
    role_ids = fields.One2many('pod.role', 'location_id', string='Roles')
    plan_ids = fields.One2many('mail.activity.plan', 'location_id')
    plans_count = fields.Integer(compute='_compute_plan_count')
    note = fields.Text('Note')
    color = fields.Integer('Color Index')
    parent_path = fields.Char(index=True, unaccent=False)
    primary_location_id = fields.Many2one(
        'pod.location', 'Primary Location', compute='_compute_primary_location_id', store=True)

    @api.depends_context('hierarchical_naming')
    def _compute_display_name(self):
        if self.env.context.get('hierarchical_naming', True):
            return super()._compute_display_name()
        for record in self:
            record.display_name = record.name

    @api.model
    def name_create(self, name):
        record = self.create({'name': name})
        return record.id, record.display_name

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id:
                location.complete_name = '%s / %s' % (location.parent_id.complete_name, location.name)
            else:
                location.complete_name = location.name

    @api.depends('parent_path')
    def _compute_primary_location_id(self):
        for location in self:
            location.primary_location_id = int(location.parent_path.split('/')[0])

    def _compute_total_practitioner(self):
        emp_data = self.env['res.partner']._read_group([('location_id', 'in', self.ids)], ['location_id'], ['__count'])
        result = {location.id: count for location, count in emp_data}
        for location in self:
            location.total_practitioner = result.get(location.id, 0)

    def _compute_plan_count(self):
        plans_data = self.env['mail.activity.plan']._read_group([('location_id', 'in', self.ids)], ['location_id'], ['__count'])
        plans_count = {location.id: count for location, count in plans_data}
        for location in self:
            location.plans_count = plans_count.get(location.id, 0)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive locations.'))

    @api.model_create_multi
    def create(self, vals_list):
        # TDE note: auto-subscription of manager done by hand, because currently
        # the tracking allows to track+subscribe fields linked to a res.user record
        # An update of the limited behavior should come, but not currently done.
        locations = super(Location, self.with_context(mail_create_nosubscribe=True)).create(vals_list)
        for location, vals in zip(locations, vals_list):
            manager = self.env['res.partner'].browse(vals.get("manager_id"))
            if manager.user_id:
                location.message_subscribe(location_ids=manager.user_id.partner_id.ids)
        return locations

    def write(self, vals):
        """ If updating manager of a location, we need to update all the practitioners
            of location hierarchy, and subscribe the new manager.
        """
        # TDE note: auto-subscription of manager done by hand, because currently
        # the tracking allows to track+subscribe fields linked to a res.user record
        # An update of the limited behavior should come, but not currently done.
        if 'manager_id' in vals:
            manager_id = vals.get("manager_id")
            if manager_id:
                manager = self.env['res.partner'].browse(manager_id)
                # subscribe the manager user
                if manager.user_id:
                    self.message_subscribe(location_ids=manager.user_id.partner_id.ids)
            # set the practitioners's parent to the new manager
            self._update_practitioner_manager(manager_id)
        return super(Location, self).write(vals)

    def _update_practitioner_manager(self, manager_id):
        practitioners = self.env['res.partner']
        for location in self:
            practitioners = practitioners | self.env['res.partner'].search([
                ('id', '!=', manager_id),
                ('location_id', '=', location.id),
                ('parent_id', '=', location.manager_id.id)
            ])
        practitioners.write({'parent_id': manager_id})

    def get_formview_action(self, access_uid=None):
        res = super().get_formview_action(access_uid=access_uid)
        if (not self.user_has_groups('hr.group_hr_user') and
           self.env.context.get('open_practitioners_kanban', False)):
            res.update({
                'name': self.name,
                'res_model': 'res.partner.public',
                'view_mode': 'kanban',
                'views': [(False, 'kanban'), (False, 'form')],
                'context': {'searchpanel_default_location_id': self.id},
                'res_id': False,
            })
        return res

    def action_plan_from_location(self):
        action = self.env['ir.actions.actions']._for_xml_id('hr.mail_activity_plan_action')
        action['context'] = {'default_location_id': self.id, 'search_default_location_id': self.id}
        return action

    def get_children_location_ids(self):
        return self.env['pod.location'].search([('id', 'child_of', self.ids)])

    def get_location_hierarchy(self):
        if not self:
            return {}

        hierarchy = {
            'parent': {
                'id': self.parent_id.id,
                'name': self.parent_id.name,
                'practitioners': self.parent_id.total_practitioner,
            } if self.parent_id else False,
            'self': {
                'id': self.id,
                'name': self.name,
                'practitioners': self.total_practitioner,
            },
            'children': [
                {
                    'id': child.id,
                    'name': child.name,
                    'practitioners': child.total_practitioner
                } for child in self.child_ids
            ]
        }

        return hierarchy