# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.addons.device.models.device_custom_model import SHELL_TYPES


#Some fields don't have the exact same name
MODEL_FIELDS_TO_VEHICLE = {
    'transmission': 'transmission', 'model_year': 'model_year', 'electric_assistance': 'electric_assistance',
    'color': 'color', 'seats': 'seats', 'doors': 'doors', 'trailer_hook': 'trailer_hook',
    'default_co2': 'co2', 'co2_standard': 'co2_standard', 'default_shell_type': 'shell_type',
    'power': 'power', 'horsepower': 'horsepower', 'horsepower_tax': 'horsepower_tax', 'category_id': 'category_id',
}

class DeviceCustom(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'avatar.mixin']
    _name = 'device.custom'
    _description = 'Custom'
    _order = 'device_id asc, acquisition_date asc'
    _rec_names_search = ['name', 'driver_id.name']

    def _get_default_state(self):
        state = self.env.ref('device.device_custom_state_new_request', raise_if_not_found=False)
        return state if state and state.id else False

    name = fields.Char(compute="_compute_custom_name", store=True)
    description = fields.Html("Custom Description")
    active = fields.Boolean('Active', default=True, tracking=True)
    manager_id = fields.Many2one(
        'res.users', 'Device Manager',
        domain=lambda self: [('groups_id', 'in', self.env.ref('device.device_group_manager').id), ('company_id', 'in', self.env.companies.ids)],
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    country_id = fields.Many2one('res.country', related='company_id.country_id')
    country_code = fields.Char(related='country_id.code', depends=['country_id'])
    device_id = fields.Char(tracking=True,
        help='ID number of the custom (i = plate number for a orthotic)')
    vin_sn = fields.Char('Chassis Number', help='Unique number written on the custom motor (VIN/SN number)', copy=False)
    trailer_hook = fields.Boolean(default=False, string='Trailer Hitch', compute='_compute_model_fields', store=True, readonly=False)
    driver_id = fields.Many2one('res.partner', 'Driver', tracking=True, help='Driver address of the custom', copy=False)
    future_driver_id = fields.Many2one('res.partner', 'Future Driver', tracking=True, help='Next Driver Address of the custom', copy=False, check_company=True)
    model_id = fields.Many2one('device.custom.model', 'Model',
        tracking=True, required=True)

    brand_id = fields.Many2one('device.custom.model.brand', 'Brand', related="model_id.brand_id", store=True, readonly=False)
    log_drivers = fields.One2many('device.custom.assignation.log', 'custom_id', string='Assignment Logs')
    log_services = fields.One2many('device.custom.log.services', 'custom_id', 'Services Logs')
    log_contracts = fields.One2many('device.custom.log.contract', 'custom_id', 'Contracts')
    contract_count = fields.Integer(compute="_compute_count_all", string='Contract Count')
    service_count = fields.Integer(compute="_compute_count_all", string='Services')
    odometer_count = fields.Integer(compute="_compute_count_all", string='Odometer')
    history_count = fields.Integer(compute="_compute_count_all", string="Drivers History Count")
    next_assignation_date = fields.Date('Assignment Date', help='This is the date at which the orthotic will be available, if not set it means available instantly')
    order_date = fields.Date('Order Date')
    acquisition_date = fields.Date('Registration Date', required=False,
        default=fields.Date.today, help='Date of custom registration')
    write_off_date = fields.Date('Cancellation Date', tracking=True, help="Date when the custom device id has been cancelled/removed.")
    first_contract_date = fields.Date(string="First Contract Date", default=fields.Date.today)
    color = fields.Char(help='Color of the custom', compute='_compute_model_fields', store=True, readonly=False)
    state_id = fields.Many2one('device.custom.state', 'State',
        default=_get_default_state, group_expand='_read_group_stage_ids',
        tracking=True,
        help='Current state of the custom', ondelete="set null")
    location = fields.Char(help='Location of the custom (garage, ...)')
    seats = fields.Integer('Seats Number', help='Number of seats of the custom', compute='_compute_model_fields', store=True, readonly=False)
    model_year = fields.Char('Model Year', help='Year of the model', compute='_compute_model_fields', store=True, readonly=False)
    doors = fields.Integer('Doors Number', help='Number of doors of the custom', compute='_compute_model_fields', store=True, readonly=False)
    tag_ids = fields.Many2many('device.custom.tag', 'device_custom_custom_tag_rel', 'custom_tag_id', 'tag_id', 'Tags', copy=False)
    odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer', string='Last Odometer',
        help='Odometer measure of the custom at the moment of this log')
    odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'mi')
        ], 'Odometer Unit', default='kilometers', required=True)
    transmission = fields.Selection(
        [('manual', 'Manual'), ('automatic', 'Automatic')], 'Transmission',
        compute='_compute_model_fields', store=True, readonly=False)
    shell_type = fields.Selection(SHELL_TYPES, 'Shell Type', compute='_compute_model_fields', store=True, readonly=False)
    horsepower = fields.Integer(compute='_compute_model_fields', store=True, readonly=False)
    horsepower_tax = fields.Float('Horsepower Taxation', compute='_compute_model_fields', store=True, readonly=False)
    power = fields.Integer('Power', help='Power in kW of the custom', compute='_compute_model_fields', store=True, readonly=False)
    co2 = fields.Float('CO2 Emissions', help='CO2 emissions of the custom', compute='_compute_model_fields', store=True, readonly=False, tracking=True, group_operator=None)
    co2_standard = fields.Char('CO2 Standard', compute='_compute_model_fields', store=True, readonly=False)
    category_id = fields.Many2one('device.custom.model.category', 'Category', compute='_compute_model_fields', store=True, readonly=False)
    image_128 = fields.Image(related='model_id.image_128', readonly=True)
    contract_renewal_due_soon = fields.Boolean(compute='_compute_contract_reminder', search='_search_contract_renewal_due_soon',
        string='Has Contracts to renew')
    contract_renewal_overdue = fields.Boolean(compute='_compute_contract_reminder', search='_search_get_overdue_contract_reminder',
        string='Has Contracts Overdue')
    contract_renewal_name = fields.Text(compute='_compute_contract_reminder', string='Name of contract to renew soon')
    contract_renewal_total = fields.Text(compute='_compute_contract_reminder', string='Total of contracts due or overdue minus one')
    contract_state = fields.Selection(
        [('futur', 'Incoming'),
         ('open', 'In Progress'),
         ('expired', 'Expired'),
         ('closed', 'Closed')
        ], string='Last Contract State', compute='_compute_contract_reminder', required=False)
    car_value = fields.Float(string="Catalog Value (VAT Incl.)")
    net_orthotic_value = fields.Float(string="Purchase Value")
    residual_value = fields.Float()
    plan_to_change_orthotic = fields.Boolean(related='driver_id.plan_to_change_orthotic', store=True, readonly=False)
    plan_to_change_bike = fields.Boolean(related='driver_id.plan_to_change_bike', store=True, readonly=False)
    custom_type = fields.Selection(related='model_id.custom_type')
    frame_type = fields.Selection([('diamant', 'Diamant'), ('trapez', 'Trapez'), ('wave', 'Wave')], string="Bike Frame Type")
    electric_assistance = fields.Boolean(compute='_compute_model_fields', store=True, readonly=False)
    frame_size = fields.Float()
    service_activity = fields.Selection([
        ('none', 'None'),
        ('overdue', 'Overdue'),
        ('today', 'Today'),
    ], compute='_compute_service_activity')
    custom_properties = fields.Properties('Properties', definition='model_id.custom_properties_definition', copy=True)

    @api.depends('log_services')
    def _compute_service_activity(self):
        for custom in self:
            activities_state = set(state for state in custom.log_services.mapped('activity_state') if state and state != 'planned')
            custom.service_activity = sorted(activities_state)[0] if activities_state else 'none'

    @api.depends('model_id')
    def _compute_model_fields(self):
        '''
        Copies all the related fields from the model to the custom
        '''
        model_values = dict()
        for custom in self.filtered('model_id'):
            if custom.model_id.id in model_values:
                write_vals = model_values[custom.model_id.id]
            else:
                # copy if value is truthy
                write_vals = {MODEL_FIELDS_TO_VEHICLE[key]: custom.model_id[key] for key in MODEL_FIELDS_TO_VEHICLE\
                    if custom.model_id[key]}
                model_values[custom.model_id.id] = write_vals
            custom.update(write_vals)

    @api.depends('model_id.brand_id.name', 'model_id.name', 'device_id')
    def _compute_custom_name(self):
        for record in self:
            record.name = (record.model_id.brand_id.name or '') + '/' + (record.model_id.name or '') + '/' + (record.device_id or _('No Plate'))

    def _get_odometer(self):
        DeviceVehicalOdometer = self.env['device.custom.odometer']
        for record in self:
            custom_odometer = DeviceVehicalOdometer.search([('custom_id', '=', record.id)], limit=1, order='value desc')
            if custom_odometer:
                record.odometer = custom_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        for record in self:
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date, 'custom_id': record.id}
                self.env['device.custom.odometer'].create(data)

    def _compute_count_all(self):
        Odometer = self.env['device.custom.odometer']
        LogService = self.env['device.custom.log.services'].with_context(active_test=False)
        LogContract = self.env['device.custom.log.contract'].with_context(active_test=False)
        History = self.env['device.custom.assignation.log']
        odometers_data = Odometer._read_group([('custom_id', 'in', self.ids)], ['custom_id'], ['__count'])
        services_data = LogService._read_group([('custom_id', 'in', self.ids)], ['custom_id', 'active'], ['__count'])
        logs_data = LogContract._read_group([('custom_id', 'in', self.ids), ('state', '!=', 'closed')], ['custom_id', 'active'], ['__count'])
        histories_data = History._read_group([('custom_id', 'in', self.ids)], ['custom_id'], ['__count'])

        mapped_odometer_data = defaultdict(lambda: 0)
        mapped_service_data = defaultdict(lambda: defaultdict(lambda: 0))
        mapped_log_data = defaultdict(lambda: defaultdict(lambda: 0))
        mapped_history_data = defaultdict(lambda: 0)

        for custom, count in odometers_data:
            mapped_odometer_data[custom.id] = count
        for custom, active, count in services_data:
            mapped_service_data[custom.id][active] = count
        for custom, active, count in logs_data:
            mapped_log_data[custom.id][active] = count
        for custom, count in histories_data:
            mapped_history_data[custom.id] = count

        for custom in self:
            custom.odometer_count = mapped_odometer_data[custom.id]
            custom.service_count = mapped_service_data[custom.id][custom.active]
            custom.contract_count = mapped_log_data[custom.id][custom.active]
            custom.history_count = mapped_history_data[custom.id]

    @api.depends('log_contracts')
    def _compute_contract_reminder(self):
        params = self.env['ir.config_parameter'].sudo()
        delay_alert_contract = int(params.get_param('hr_device.delay_alert_contract', default=30))
        for record in self:
            overdue = False
            due_soon = False
            total = 0
            name = ''
            state = ''
            for element in record.log_contracts:
                if element.state in ('open', 'expired') and element.expiration_date:
                    current_date_str = fields.Date.context_today(record)
                    due_time_str = element.expiration_date
                    current_date = fields.Date.from_string(current_date_str)
                    due_time = fields.Date.from_string(due_time_str)
                    diff_time = (due_time - current_date).days
                    if diff_time < 0:
                        overdue = True
                        total += 1
                    if diff_time < delay_alert_contract:
                        due_soon = True
                        total += 1
                    if overdue or due_soon:
                        log_contract = self.env['device.custom.log.contract'].search([
                            ('custom_id', '=', record.id),
                            ('state', 'in', ('open', 'expired'))
                            ], limit=1, order='expiration_date asc')
                        if log_contract:
                            # we display only the name of the oldest overdue/due soon contract
                            name = log_contract.name
                            state = log_contract.state

            record.contract_renewal_overdue = overdue
            record.contract_renewal_due_soon = due_soon
            record.contract_renewal_total = total - 1  # we remove 1 from the real total for display purposes
            record.contract_renewal_name = name
            record.contract_state = state

    def _get_analytic_name(self):
        # This function is used in device_account and is overrided in l10n_be_hr_payroll_device
        return self.device_id or _('No plate')

    def _search_contract_renewal_due_soon(self, operator, value):
        params = self.env['ir.config_parameter'].sudo()
        delay_alert_contract = int(params.get_param('hr_device.delay_alert_contract', default=30))
        res = []
        assert operator in ('=', '!=', '<>') and value in (True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = 'in'
        else:
            search_operator = 'not in'
        today = fields.Date.context_today(self)
        datetime_today = fields.Datetime.from_string(today)
        limit_date = fields.Datetime.to_string(datetime_today + relativedelta(days=+delay_alert_contract))
        res_ids = self.env['device.custom.log.contract'].search([
            ('expiration_date', '>', today),
            ('expiration_date', '<', limit_date),
            ('state', 'in', ['open', 'expired'])
        ]).mapped('custom_id').ids
        res.append(('id', search_operator, res_ids))
        return res

    def _search_get_overdue_contract_reminder(self, operator, value):
        res = []
        assert operator in ('=', '!=', '<>') and value in (True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = 'in'
        else:
            search_operator = 'not in'
        today = fields.Date.context_today(self)
        res_ids = self.env['device.custom.log.contract'].search([
            ('expiration_date', '!=', False),
            ('expiration_date', '<', today),
            ('state', 'in', ['open', 'expired'])
        ]).mapped('custom_id').ids
        res.append(('id', search_operator, res_ids))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # Device administrator may not have rights to create the plan_to_change_orthotic
        # value when the driver_id is a res.user.
        # This trick is used to prevent access right error.
        ptc_values = [
            'plan_to_change_orthotic' in vals.keys() and {'plan_to_change_orthotic': vals.pop('plan_to_change_orthotic')} for vals in vals_list
        ]
        custom = super().create(vals_list)
        for custom, vals, ptc_value in zip(custom, vals_list, ptc_values):
            if ptc_value:
                custom.sudo().write(ptc_value)
            if 'driver_id' in vals and vals['driver_id']:
                custom.create_driver_history(vals)
            if 'future_driver_id' in vals and vals['future_driver_id']:
                state_waiting_list = self.env.ref('device.device_custom_state_waiting_list', raise_if_not_found=False)
                states = custom.mapped('state_id').ids
                if not state_waiting_list or state_waiting_list.id not in states:
                    future_driver = self.env['res.partner'].browse(vals['future_driver_id'])
                    if self.custom_type == 'bike':
                        future_driver.sudo().write({'plan_to_change_bike': True})
                    if self.custom_type == 'car':
                        future_driver.sudo().write({'plan_to_change_orthotic': True})
        return custom

    def write(self, vals):
        if 'driver_id' in vals and vals['driver_id']:
            driver_id = vals['driver_id']
            for custom in self.filtered(lambda v: v.driver_id.id != driver_id):
                custom.create_driver_history(vals)
                if custom.driver_id:
                    custom.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=custom.manager_id.id or self.env.user.id,
                        note=_('Specify the End date of %s', custom.driver_id.name))

        if 'future_driver_id' in vals and vals['future_driver_id']:
            state_waiting_list = self.env.ref('device.device_custom_state_waiting_list', raise_if_not_found=False)
            states = self.mapped('state_id').ids if 'state_id' not in vals else [vals['state_id']]
            if not state_waiting_list or state_waiting_list.id not in states:
                future_driver = self.env['res.partner'].browse(vals['future_driver_id'])
                if self.custom_type == 'bike':
                    future_driver.sudo().write({'plan_to_change_bike': True})
                if self.custom_type == 'car':
                    future_driver.sudo().write({'plan_to_change_orthotic': True})

        if 'active' in vals and not vals['active']:
            self.env['device.custom.log.contract'].search([('custom_id', 'in', self.ids)]).active = False
            self.env['device.custom.log.services'].search([('custom_id', 'in', self.ids)]).active = False

        res = super(DeviceCustom, self).write(vals)
        return res

    def _get_driver_history_data(self, vals):
        self.ensure_one()
        return {
            'custom_id': self.id,
            'driver_id': vals['driver_id'],
            'date_start': fields.Date.today(),
        }

    def create_driver_history(self, vals):
        for custom in self:
            self.env['device.custom.assignation.log'].create(
                custom._get_driver_history_data(vals),
            )

    def action_accept_driver_change(self):
        # Find all the custom of the same type for which the driver is the future_driver_id
        # remove their driver_id and close their history using current date
        custom = self.search([('driver_id', 'in', self.mapped('future_driver_id').ids), ('custom_type', '=', self.custom_type)])
        custom.write({'driver_id': False})

        for custom in self:
            if custom.custom_type == 'bike':
                custom.future_driver_id.sudo().write({'plan_to_change_bike': False})
            if custom.custom_type == 'car':
                custom.future_driver_id.sudo().write({'plan_to_change_orthotic': False})
            custom.driver_id = custom.future_driver_id
            custom.future_driver_id = False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['device.custom.state'].search([], order=order)

    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current custom """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('device.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_custom_id=self.id, group_by=False),
                domain=[('custom_id', '=', self.id)]
            )
            return res
        return False

    def act_show_log_cost(self):
        """ This opens log view to view and add new log for this custom, groupby default to only show effective costs
            @return: the costs log view
        """
        self.ensure_one()
        copy_context = dict(self.env.context)
        copy_context.pop('group_by', None)
        res = self.env['ir.actions.act_window']._for_xml_id('device.device_custom_costs_action')
        res.update(
            context=dict(copy_context, default_custom_id=self.id, search_default_parent_false=True),
            domain=[('custom_id', '=', self.id)]
        )
        return res

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'driver_id' in init_values or 'future_driver_id' in init_values:
            return self.env.ref('device.mt_device_driver_updated')
        return super(DeviceCustom, self)._track_subtype(init_values)

    def open_assignation_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignment Logs',
            'view_mode': 'tree',
            'res_model': 'device.custom.assignation.log',
            'domain': [('custom_id', '=', self.id)],
            'context': {'default_driver_id': self.driver_id.id, 'default_custom_id': self.id}
        }
