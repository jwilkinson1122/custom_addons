# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PodiatryLocation(models.Model):
    _name = "podiatry.location"
    _description = "Practice Location"
    _inherit = ['mail.thread']
    _order = "name"
    _rec_name = 'complete_name'

    name = fields.Char('Location Name', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    parent_id = fields.Many2one('podiatry.location', string='Parent Location', index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    child_ids = fields.One2many('podiatry.location', 'parent_id', string='Child Locations')
    manager_id = fields.Many2one('podiatry.practitioner', string='Practice Manager', tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    practitioner_ids = fields.One2many('podiatry.practitioner', 'location_id', string='Practitioners', readonly=True)
    total_practitioners = fields.Integer(compute='_compute_total_practitioners', string='Total Practitioners')
    role_ids = fields.One2many('podiatry.role', 'location_id', string='Roles')
    note = fields.Text('Note')
    color = fields.Integer('Color Index')

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(PodiatryLocation, self).name_get()

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id:
                location.complete_name = '%s / %s' % (location.parent_id.complete_name, location.name)
            else:
                location.complete_name = location.name

    def _compute_total_practitioners(self):
        practitioner_data = self.env['podiatry.practitioner'].read_group([('location_id', 'in', self.ids)], ['location_id'], ['location_id'])
        result = dict((data['location_id'][0], data['location_id_count']) for data in practitioner_data)
        for location in self:
            location.total_practitioners = result.get(location.id, 0)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive locations.'))

    @api.model
    def create(self, vals):
        location = super(PodiatryLocation, self.with_context(mail_create_nosubscribe=True)).create(vals)
        manager = self.env['podiatry.practitioner'].browse(vals.get("manager_id"))
        if manager.user_id:
            location.message_subscribe(partner_ids=manager.user_id.partner_id.ids)
        return location

    def write(self, vals):
        """ If updating manager of a location, we need to update all the practitioners
            of location hierarchy, and subscribe the new manager.
        """
        if 'manager_id' in vals:
            manager_id = vals.get("manager_id")
            if manager_id:
                manager = self.env['podiatry.practitioner'].browse(manager_id)
                # subscribe the manager user
                if manager.user_id:
                    self.message_subscribe(partner_ids=manager.user_id.partner_id.ids)
            # set the practitioners's parent to the new manager
            self._update_practitioners_manager(manager_id)
        return super(PodiatryLocation, self).write(vals)

    def _update_practitioners_manager(self, manager_id):
        practitioners = self.env['podiatry.practitioner']
        for location in self:
            practitioners = practitioners | self.env['podiatry.practitioner'].search([
                ('id', '!=', manager_id),
                ('location_id', '=', location.id),
                ('parent_id', '=', location.manager_id.id)
            ])
        practitioners.write({'parent_id': manager_id})
