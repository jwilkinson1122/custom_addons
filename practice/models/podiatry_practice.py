# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Practice(models.Model):
    _name = "podiatry.practice"
    _description = "Practice"
    _inherit = ['mail.thread']
    _order = "name"
    _rec_name = 'complete_name'

    name = fields.Char('Practice Name', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    parent_id = fields.Many2one('podiatry.practice', string='Parent Practice', index=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    child_ids = fields.One2many('podiatry.practice', 'parent_id', string='Child Practices')
    manager_id = fields.Many2one('podiatry.employee', string='Manager', tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    member_ids = fields.One2many('podiatry.employee', 'practice_id', string='Members', readonly=True)
    total_employee = fields.Integer(compute='_compute_total_employee', string='Total Employee')
    jobs_ids = fields.One2many('podiatry.job', 'practice_id', string='Jobs')
    note = fields.Text('Note')
    color = fields.Integer('Color Index')

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(Practice, self).name_get()

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for practice in self:
            if practice.parent_id:
                practice.complete_name = '%s / %s' % (practice.parent_id.complete_name, practice.name)
            else:
                practice.complete_name = practice.name

    def _compute_total_employee(self):
        emp_data = self.env['podiatry.employee'].read_group([('practice_id', 'in', self.ids)], ['practice_id'], ['practice_id'])
        result = dict((data['practice_id'][0], data['practice_id_count']) for data in emp_data)
        for practice in self:
            practice.total_employee = result.get(practice.id, 0)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive practices.'))

    @api.model
    def create(self, vals):
        # TDE note: auto-subscription of manager done by hand, because currently
        # the tracking allows to track+subscribe fields linked to a res.user record
        # An update of the limited behavior should come, but not currently done.
        practice = super(Practice, self.with_context(mail_create_nosubscribe=True)).create(vals)
        manager = self.env['podiatry.employee'].browse(vals.get("manager_id"))
        if manager.user_id:
            practice.message_subscribe(partner_ids=manager.user_id.partner_id.ids)
        return practice

    def write(self, vals):
        """ If updating manager of a practice, we need to update all the employees
            of practice hierarchy, and subscribe the new manager.
        """
        # TDE note: auto-subscription of manager done by hand, because currently
        # the tracking allows to track+subscribe fields linked to a res.user record
        # An update of the limited behavior should come, but not currently done.
        if 'manager_id' in vals:
            manager_id = vals.get("manager_id")
            if manager_id:
                manager = self.env['podiatry.employee'].browse(manager_id)
                # subscribe the manager user
                if manager.user_id:
                    self.message_subscribe(partner_ids=manager.user_id.partner_id.ids)
            # set the employees's parent to the new manager
            self._update_employee_manager(manager_id)
        return super(Practice, self).write(vals)

    def _update_employee_manager(self, manager_id):
        employees = self.env['podiatry.employee']
        for practice in self:
            employees = employees | self.env['podiatry.employee'].search([
                ('id', '!=', manager_id),
                ('practice_id', '=', practice.id),
                ('parent_id', '=', practice.manager_id.id)
            ])
        employees.write({'parent_id': manager_id})
