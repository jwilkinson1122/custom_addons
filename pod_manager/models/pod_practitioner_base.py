# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import api, fields, models
from pytz import timezone, UTC, utc
from datetime import timedelta

from odoo.tools import format_time


class PodPractitionerBase(models.AbstractModel):
    _name = "pod.practitioner.base"
    _description = "Basic Practitioner"
    _order = 'name'

    name = fields.Char()
    active = fields.Boolean("Active")
    color = fields.Integer('Color Index', default=0)
    practice_id = fields.Many2one('pod.practice', 'Practice', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    role_id = fields.Many2one('pod.role', 'Role Position', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    role_title = fields.Char("Role Title", compute="_compute_role_title", store=True, readonly=False)
    company_id = fields.Many2one('res.company', 'Company')
    address_id = fields.Many2one('res.partner', 'Practice Address', compute="_compute_address_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    practice_phone = fields.Char('Practice Phone', compute="_compute_phones", store=True, readonly=False)
    mobile_phone = fields.Char('Practice Mobile')
    practice_email = fields.Char('Practice Email')
    practice_location_id = fields.Many2one('pod.practice.location', 'Practice Location', compute="_compute_practice_location_id", store=True, readonly=False,
    domain="[('address_id', '=', address_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    user_id = fields.Many2one('res.users')
    resource_id = fields.Many2one('resource.resource')
    resource_calendar_id = fields.Many2one('resource.calendar', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    parent_id = fields.Many2one('pod.practitioner', 'Manager', compute="_compute_parent_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    assistant_id = fields.Many2one(
        'pod.practitioner', 'Assistant', compute='_compute_assistant', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Practitioner" who is the assistant of this practitioner.\n'
             'The "Assistant" has no specific rights or responsibilities by default.')
    tz = fields.Selection(
        string='Timezone', related='resource_id.tz', readonly=False,
        help="This field is used in order to define in which timezone the resources will work.")
    pod_existence_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('to_define', 'To Define')], compute='_compute_existence_state', default='to_define')
    last_activity = fields.Date(compute="_compute_last_activity")
    last_activity_time = fields.Char(compute="_compute_last_activity")
    pod_icon_display = fields.Selection([
        ('existence_active', 'Active'),
        ('existence_inactive', 'Inactive'),
        ('existence_to_define', 'To define'),
        ('existence_undetermined', 'Undetermined')], compute='_compute_existence_icon')
    practitioner_type = fields.Selection([
        ('practitioner', 'Practitioner'),
        ('student', 'Student'),
        ('trainee', 'Trainee'),
        ('contractor', 'Contractor'),
        ('freelance', 'Freelancer'),
        ], string='Practitioner Type', default='practitioner', required=True,
        help="The practitioner type. Although the primary purpose may seem to categorize practitioners, this field has also an impact in the Contract History. Only Practitioner type is supposed to be under contract and will have a Contract History.")

    @api.depends('user_id.im_status')
    def _compute_existence_state(self):
        """
        This method is overritten in several other modules which add additional
        existence criterions. e.g. pod_attendance, pod_holidays
        """
        # Check on login
        check_login = literal_eval(self.env['ir.config_parameter'].sudo().get_param('pod_manager.pod_existence_control_login', 'False'))
        practitioner_to_check_working = self.filtered(lambda e: e.user_id.im_status == 'offline')
        active_list = practitioner_to_check_working._get_practitioner_active()
        for practitioner in self:
            state = 'to_define'
            if check_login:
                if practitioner.user_id.im_status == 'online':
                    state = 'active'
                elif practitioner.user_id.im_status == 'offline' and practitioner.id not in active_list:
                    state = 'inactive'
            practitioner.pod_existence_state = state

    @api.depends('user_id')
    def _compute_last_activity(self):
        existences = self.env['bus.presence'].search_read([('user_id', 'in', self.mapped('user_id').ids)], ['user_id', 'last_existence'])
        # transform the result to a dict with this format {user.id: last_existence}
        existences = {p['user_id'][0]: p['last_existence'] for p in existences}

        for practitioner in self:
            tz = practitioner.tz
            last_existence = existences.get(practitioner.user_id.id, False)
            if last_existence:
                last_activity_datetime = last_existence.replace(tzinfo=UTC).astimezone(timezone(tz)).replace(tzinfo=None)
                practitioner.last_activity = last_activity_datetime.date()
                if practitioner.last_activity == fields.Date.today():
                    practitioner.last_activity_time = format_time(self.env, last_existence, time_format='short')
                else:
                    practitioner.last_activity_time = False
            else:
                practitioner.last_activity = False
                practitioner.last_activity_time = False

    @api.depends('parent_id')
    def _compute_assistant(self):
        for practitioner in self:
            manager = practitioner.parent_id
            previous_manager = practitioner._origin.parent_id
            if manager and (practitioner.assistant_id == previous_manager or not practitioner.assistant_id):
                practitioner.assistant_id = manager
            elif not practitioner.assistant_id:
                practitioner.assistant_id = False

    @api.depends('role_id')
    def _compute_role_title(self):
        for practitioner in self.filtered('role_id'):
            practitioner.role_title = practitioner.role_id.name

    @api.depends('address_id')
    def _compute_phones(self):
        for practitioner in self:
            if practitioner.address_id and practitioner.address_id.phone:
                practitioner.practice_phone = practitioner.address_id.phone
            else:
                practitioner.practice_phone = False

    @api.depends('company_id')
    def _compute_address_id(self):
        for practitioner in self:
            address = practitioner.company_id.partner_id.address_get(['default'])
            practitioner.address_id = address['default'] if address else False

    @api.depends('practice_id')
    def _compute_parent_id(self):
        for practitioner in self.filtered('practice_id.manager_id'):
            practitioner.parent_id = practitioner.practice_id.manager_id

    @api.depends('resource_calendar_id', 'pod_existence_state')
    def _compute_existence_icon(self):
        active_list = self.filtered(lambda e: e.pod_existence_state == 'active')._get_practitioner_active()
        for practitioner in self:
            # Assign a default value to icon
            icon = 'default_icon'  # or whatever default you want to set

            if practitioner.pod_existence_state == 'active':
                if practitioner.id in active_list:
                    icon = 'existence_active'
            elif practitioner.pod_existence_state == 'inactive':
                icon = 'existence_inactive'
            else:
                if practitioner.user_id:
                    icon = 'existence_to_define'
                else:
                    icon = 'existence_undetermined'
            
            practitioner.pod_icon_display = icon


    @api.depends('address_id')
    def _compute_practice_location_id(self):
        to_reset = self.filtered(lambda e: e.address_id != e.practice_location_id.address_id)
        to_reset.practice_location_id = False

    @api.model
    def _get_practitioner_active(self):
        active = []
        all_practitioner_tz = set(self.mapped('tz'))
        for tz in all_practitioner_tz:
            practitioner_ids = self.filtered(lambda e: e.tz == tz)
            resource_calendar_ids = practitioner_ids.mapped('resource_calendar_id')
            for calendar_id in resource_calendar_ids:
                res_practitioner_ids = practitioner_ids.filtered(lambda e: e.resource_calendar_id.id == calendar_id.id)
                start_dt = fields.Datetime.now()
                stop_dt = start_dt + timedelta(hours=1)
                from_datetime = utc.localize(start_dt).astimezone(timezone(tz or 'UTC'))
                to_datetime = utc.localize(stop_dt).astimezone(timezone(tz or 'UTC'))
                practice_interval = res_practitioner_ids[0].resource_calendar_id._work_intervals_batch(from_datetime, to_datetime)[False]
                if len(practice_interval._items) > 0:
                    active += res_practitioner_ids.ids
        return active

