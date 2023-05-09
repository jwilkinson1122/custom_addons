# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models
from pytz import timezone, UTC, utc
from datetime import timedelta

from odoo.tools import format_time


class PodiatryEmployeeBase(models.AbstractModel):
    _name = "podiatry.employee.base"
    _description = "Practice Employee"
    _order = 'name'

    name = fields.Char()
    active = fields.Boolean("Active")
    color = fields.Integer('Color Index', default=0)
    practice_id = fields.Many2one('podiatry.practice', 'Practice', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_id = fields.Many2one('podiatry.job', 'Job Position', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_title = fields.Char("Job Title", compute="_compute_job_title", store=True, readonly=False)
    company_id = fields.Many2one('res.company', 'Company')
    address_id = fields.Many2one('res.partner', 'Practice Address', compute="_compute_address_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    work_phone = fields.Char('Work Phone', compute="_compute_phones", store=True, readonly=False)
    mobile_phone = fields.Char('Work Mobile')
    work_email = fields.Char('Work Email')
    practice_location_id = fields.Many2one('podiatry.practice.location', 'Practice Location', compute="_compute_practice_location_id", store=True, readonly=False,
    domain="[('address_id', '=', address_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    user_id = fields.Many2one('res.users')
    resource_id = fields.Many2one('resource.resource')
    resource_calendar_id = fields.Many2one('resource.calendar', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    parent_id = fields.Many2one('podiatry.employee', 'Manager', compute="_compute_parent_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    coach_id = fields.Many2one(
        'podiatry.employee', 'Coach', compute='_compute_coach', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
             'The "Coach" has no specific rights or responsibilities by default.')
    tz = fields.Selection(
        string='Timezone', related='resource_id.tz', readonly=False,
        help="This field is used in order to define in which timezone the resources will work.")
    podiatry_presence_state = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('to_define', 'To Define')], compute='_compute_presence_state', default='to_define')
    last_activity = fields.Date(compute="_compute_last_activity")
    last_activity_time = fields.Char(compute="_compute_last_activity")
    podiatry_icon_display = fields.Selection([
        ('presence_present', 'Present'),
        ('presence_absent_active', 'Present but not active'),
        ('presence_absent', 'Absent'),
        ('presence_to_define', 'To define'),
        ('presence_undetermined', 'Undetermined')], compute='_compute_presence_icon')
    employee_type = fields.Selection([
        ('employee', 'Employee'),
        ('physician', 'Physician'),
        ('assistant', 'Assistant'),
        ('receptionist', 'Receptionist'),
        ], string='Employee Type', default='employee', required=True,
        help="The employee type.")

    @api.depends('user_id.im_status')
    def _compute_presence_state(self):
        """
        This method is overritten in several other modules which add additional
        presence criterions. e.g. podiatry_attendance, podiatry_holidays
        """
        # Check on login
        check_login = literal_eval(self.env['ir.config_parameter'].sudo().get_param('podiatry.podiatry_presence_control_login', 'False'))
        employee_to_check_working = self.filtered(lambda e: e.user_id.im_status == 'offline')
        working_now_list = employee_to_check_working._get_employee_working_now()
        for employee in self:
            state = 'to_define'
            if check_login:
                if employee.user_id.im_status == 'online':
                    state = 'present'
                elif employee.user_id.im_status == 'offline' and employee.id not in working_now_list:
                    state = 'absent'
            employee.podiatry_presence_state = state

    @api.depends('user_id')
    def _compute_last_activity(self):
        presences = self.env['bus.presence'].search_read([('user_id', 'in', self.mapped('user_id').ids)], ['user_id', 'last_presence'])
        # transform the result to a dict with this format {user.id: last_presence}
        presences = {p['user_id'][0]: p['last_presence'] for p in presences}

        for employee in self:
            tz = employee.tz
            last_presence = presences.get(employee.user_id.id, False)
            if last_presence:
                last_activity_datetime = last_presence.replace(tzinfo=UTC).astimezone(timezone(tz)).replace(tzinfo=None)
                employee.last_activity = last_activity_datetime.date()
                if employee.last_activity == fields.Date.today():
                    employee.last_activity_time = format_time(self.env, last_presence, time_format='short')
                else:
                    employee.last_activity_time = False
            else:
                employee.last_activity = False
                employee.last_activity_time = False

    @api.depends('parent_id')
    def _compute_coach(self):
        for employee in self:
            manager = employee.parent_id
            previous_manager = employee._origin.parent_id
            if manager and (employee.coach_id == previous_manager or not employee.coach_id):
                employee.coach_id = manager
            elif not employee.coach_id:
                employee.coach_id = False

    @api.depends('job_id')
    def _compute_job_title(self):
        for employee in self.filtered('job_id'):
            employee.job_title = employee.job_id.name

    @api.depends('address_id')
    def _compute_phones(self):
        for employee in self:
            if employee.address_id and employee.address_id.phone:
                employee.work_phone = employee.address_id.phone
            else:
                employee.work_phone = False

    @api.depends('company_id')
    def _compute_address_id(self):
        for employee in self:
            address = employee.company_id.partner_id.address_get(['default'])
            employee.address_id = address['default'] if address else False

    @api.depends('practice_id')
    def _compute_parent_id(self):
        for employee in self.filtered('practice_id.manager_id'):
            employee.parent_id = employee.practice_id.manager_id

    @api.depends('resource_calendar_id', 'podiatry_presence_state')
    def _compute_presence_icon(self):
        """
        This method compute the state defining the display icon in the kanban view.
        It can be overriden to add other possibilities, like time off or attendances recordings.
        """
        working_now_list = self.filtered(lambda e: e.podiatry_presence_state == 'present')._get_employee_working_now()
        for employee in self:
            if employee.podiatry_presence_state == 'present':
                if employee.id in working_now_list:
                    icon = 'presence_present'
                else:
                    icon = 'presence_absent_active'
            elif employee.podiatry_presence_state == 'absent':
                # employee is not in the working_now_list and he has a user_id
                icon = 'presence_absent'
            else:
                # without attendance, default employee state is 'to_define' without confirmed presence/absence
                # we need to check why they are not there
                if employee.user_id:
                    # Display an orange icon on internal users.
                    icon = 'presence_to_define'
                else:
                    # We don't want non-user employee to have icon.
                    icon = 'presence_undetermined'
            employee.podiatry_icon_display = icon

    @api.depends('address_id')
    def _compute_practice_location_id(self):
        to_reset = self.filtered(lambda e: e.address_id != e.practice_location_id.address_id)
        to_reset.practice_location_id = False

    @api.model
    def _get_employee_working_now(self):
        working_now = []
        # We loop over all the employee tz and the resource calendar_id to detect working hours in batch.
        all_employee_tz = set(self.mapped('tz'))
        for tz in all_employee_tz:
            employee_ids = self.filtered(lambda e: e.tz == tz)
            resource_calendar_ids = employee_ids.mapped('resource_calendar_id')
            for calendar_id in resource_calendar_ids:
                res_employee_ids = employee_ids.filtered(lambda e: e.resource_calendar_id.id == calendar_id.id)
                start_dt = fields.Datetime.now()
                stop_dt = start_dt + timedelta(hours=1)
                from_datetime = utc.localize(start_dt).astimezone(timezone(tz or 'UTC'))
                to_datetime = utc.localize(stop_dt).astimezone(timezone(tz or 'UTC'))
                # Getting work interval of the first is working. Functions called on resource_calendar_id
                # are waiting for singleton
                work_interval = res_employee_ids[0].resource_calendar_id._work_intervals_batch(from_datetime, to_datetime)[False]
                # Employee that is not supposed to work have empty items.
                if len(work_interval._items) > 0:
                    # The employees should be working now according to their work schedule
                    working_now += res_employee_ids.ids
        return working_now

