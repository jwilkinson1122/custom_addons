# -*- coding: utf-8 -*-


from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.addons.prescription.models.prescription_type_model import SHELL_TYPES, ARCH_HEIGHT


#Some fields don't have the exact same name
MODEL_FIELDS_TO_PRESCRIPTION = {
    'model_year': 'model_year', 'electric_assistance': 'electric_assistance',
    'color': 'color', 'pairs': 'pairs', 'qty': 'qty', 'trailer_hook': 'trailer_hook',
    'default_co2': 'co2', 'co2_standard': 'co2_standard', 'default_shell_type': 'shell_type', 'default_arch_height': 'arch_height',
    'power': 'power', 'horsepower': 'horsepower', 'horsepower_tax': 'horsepower_tax', 'category_id': 'category_id',
}

class PrescriptionType(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'avatar.mixin']
    _name = 'prescription.type'
    _description = 'Prescription Types'
    _order = 'prescription_id asc, order_date asc'
    _rec_names_search = ['name', 'practitioner_id.name']

    def _get_default_state(self):
        state = self.env.ref('prescription.prescription_type_state_draft', raise_if_not_found=False)
        return state if state and state.id else False

    name = fields.Char(compute="_compute_prescription_name", store=True)
    description = fields.Html("Prescription Type Description")
    active = fields.Boolean('Active', default=True, tracking=True)
    manager_id = fields.Many2one(
        'res.users', 'Prescription Type Manager',
        domain=lambda self: [('groups_id', 'in', self.env.ref('prescription.prescription_group_manager').id), ('company_id', 'in', self.env.companies.ids)],
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    country_id = fields.Many2one('res.country', related='company_id.country_id')
    country_code = fields.Char(related='country_id.code', depends=['country_id'])
    prescription_id = fields.Char(tracking=True,
        help='ID number of the prescription (i = id number for a prescription)')
    oin_sn = fields.Char('Chassis Number', help='Unique number written on the prescription motor (VIN/SN number)', copy=False)
    trailer_hook = fields.Boolean(default=False, string='Trailer Hitch', compute='_compute_model_fields', store=True, readonly=False)
    
    account_id = fields.Many2one(
        'res.partner', 
        'Account', 
        tracking=True,
        index=True, 
        domain=[('is_parent_account','=',True)], 
        help='Account of the prescription', 
        copy=False
        )
    
    location_id = fields.Many2one(
        'res.partner', 
        'Location', 
        tracking=True,
        domain=[('is_location','=',True)], 
        help='Location of the prescription', 
        copy=False
        )
    
    practitioner_id = fields.Many2one(
        'res.partner', 
        'Practitioner', 
        tracking=True, 
        domain=[('is_practitioner','=',True)], 
        copy=False, 
        check_company=True
        )
    
    model_id = fields.Many2one('prescription.type.model', 'Model', tracking=True, required=True)

    line_id = fields.Many2one('prescription.type.model.line', 'Line', related="model_id.line_id", store=True, readonly=False)
    log_practitioners = fields.One2many('prescription.type.assignation.log', 'prescription_id', string='Assignment Logs')
    log_services = fields.One2many('prescription.type.log.services', 'prescription_id', 'Adjustments Logs')
    log_prescription = fields.One2many('prescription.type.log', 'prescription_id', 'Prescription')
    prescription_count = fields.Integer(compute="_compute_count_all", string='Prescription Count')
    service_count = fields.Integer(compute="_compute_count_all", string='Adjustments')
    measure_count = fields.Integer(compute="_compute_count_all", string='Measures')
    history_count = fields.Integer(compute="_compute_count_all", string="Practitioners History Count")
    next_assignation_date = fields.Date('Assignment Date', help='This is the date at which the prescription will be available, if not set it means available instantly')
    order_date = fields.Date('Order Date')
    received_date = fields.Date('Received Date', required=False,
        default=fields.Date.today, help='Date of prescription received')
    cancelled_date = fields.Date('Cancellation Date', tracking=True, help="Date when the prescription id has been cancelled/removed.")
    first_prescription_date = fields.Date(string="First Prescription Date", default=fields.Date.today)
    color = fields.Char(help='Color', compute='_compute_model_fields', store=True, readonly=False)
    # top_cover_color = fields.Char(help='Top Cover', compute='_compute_model_fields', store=True, readonly=False)
    topcover_color = fields.Selection(SHELL_TYPES, 'Shell Type', compute='_compute_model_fields', store=True, readonly=False)

    state_id = fields.Many2one('prescription.type.state', 'State',
        default=_get_default_state, group_expand='_read_group_stage_ids',
        tracking=True,
        help='Current state of the prescription', ondelete="set null")
    location = fields.Char(help='Location of the prescription')
    pairs = fields.Integer('Pairs to Make', help='Number of pairs of the prescription to make', compute='_compute_model_fields', store=True, readonly=False)
    model_year = fields.Char('Model Year', help='Year of the model', compute='_compute_model_fields', store=True, readonly=False)
    qty = fields.Integer('QTY Number', help='Number of qty of the prescription', compute='_compute_model_fields', store=True, readonly=False)
    tag_ids = fields.Many2many('prescription.type.tag', 'prescription_type_prescription_tag_rel', 'prescription_tag_id', 'tag_id', 'Tags', copy=False)
    measure = fields.Float(compute='_get_measure', inverse='_set_measure', string='Last Measure',
        help='Measures of the prescription at the moment of this log')
    
    laterality = fields.Selection([
        ('lt', 'Left Only'),
        ('rt', 'Right Only'),
        ('bl', 'Bilateral'),
        ], 'Laterality', default='bl', required=True)
    
    shell_type = fields.Selection(SHELL_TYPES, 'Shell Type', compute='_compute_model_fields', store=True, readonly=False)
    arch_height = fields.Selection(ARCH_HEIGHT, 'Arch Height', compute='_compute_model_fields', store=True, readonly=False)

    horsepower = fields.Integer(compute='_compute_model_fields', store=True, readonly=False)
    horsepower_tax = fields.Float('Horsepower Taxation', compute='_compute_model_fields', store=True, readonly=False)
    power = fields.Integer('Power', help='Power in kW of the prescription', compute='_compute_model_fields', store=True, readonly=False)
    co2 = fields.Float('CO2 Emissions', help='CO2 emissions of the prescription', compute='_compute_model_fields', store=True, readonly=False, tracking=True, group_operator=None)
    co2_standard = fields.Char('CO2 Standard', compute='_compute_model_fields', store=True, readonly=False)
    category_id = fields.Many2one('prescription.type.model.category', 'Category', compute='_compute_model_fields', store=True, readonly=False)
    image_128 = fields.Image(related='model_id.image_128', readonly=True)
    prescription_renewal_due_soon = fields.Boolean(compute='_compute_prescription_reminder', search='_search_prescription_renewal_due_soon',
        string='Has Prescription to renew')
    prescription_renewal_overdue = fields.Boolean(compute='_compute_prescription_reminder', search='_search_get_overdue_prescription_reminder',
        string='Has Prescription Overdue')
    prescription_renewal_name = fields.Text(compute='_compute_prescription_reminder', string='Name of prescription to renew soon')
    prescription_renewal_total = fields.Text(compute='_compute_prescription_reminder', string='Total of prescription due or overdue minus one')
    prescription_state = fields.Selection(
        [('futur', 'Incoming'),
         ('open', 'In Progress'),
         ('expired', 'Expired'),
         ('closed', 'Closed')
        ], string='Last Prescription State', compute='_compute_prescription_reminder', required=False)
    prescription_price = fields.Float(string="Catalog Value (VAT Incl.)")
    net_prescription_price = fields.Float(string="Purchase Value")
    residual_value = fields.Float()
    plan_to_change_prescription = fields.Boolean(related='location_id.plan_to_change_prescription', store=True, readonly=False)
    plan_to_change_otc = fields.Boolean(related='location_id.plan_to_change_otc', store=True, readonly=False)
    prescription_type = fields.Selection(related='model_id.prescription_type')
    shoe_size = fields.Float()
    shoe_type = fields.Selection([
        ('dress', 'Dress'), 
        ('casual', 'Casual'), 
        ('athletic', 'Athletic'), 
        ('other', 'Other')
        ], string='Shoe Type')
    
    electric_assistance = fields.Boolean(compute='_compute_model_fields', store=True, readonly=False)
    
    service_activity = fields.Selection([
        ('none', 'None'),
        ('overdue', 'Overdue'),
        ('today', 'Today'),
    ], compute='_compute_service_activity')
    prescription_properties = fields.Properties('Properties', definition='model_id.prescription_properties_definition', copy=True)


    @api.onchange('account_id')
    def _onchange_account_id(self):
        if not self.account_id:
            # If no account is selected, allow all locations
            return {'domain': {'location_id': [('is_location', '=', True)]}}

        # Fetch all descendant IDs of the selected account
        # descendant_ids = self.account_id.child_ids.ids 
        descendant_ids = self.account_id.location_ids.ids 

        # Update the domain of `location_id` to include only these descendants
        return {'domain': {'location_id': [('id', 'in', descendant_ids), ('is_location', '=', True)]}}


    @api.depends('log_services')
    def _compute_service_activity(self):
        for prescription in self:
            activities_state = set(state for state in prescription.log_services.mapped('activity_state') if state and state != 'planned')
            prescription.service_activity = sorted(activities_state)[0] if activities_state else 'none'

    @api.depends('model_id')
    def _compute_model_fields(self):
        '''
        Copies all the related fields from the model to the prescription
        '''
        model_values = dict()
        for prescription in self.filtered('model_id'):
            if prescription.model_id.id in model_values:
                write_vals = model_values[prescription.model_id.id]
            else:
                # copy if value is truthy
                write_vals = {MODEL_FIELDS_TO_PRESCRIPTION[key]: prescription.model_id[key] for key in MODEL_FIELDS_TO_PRESCRIPTION\
                    if prescription.model_id[key]}
                model_values[prescription.model_id.id] = write_vals
            prescription.update(write_vals)

    @api.depends('model_id.line_id.name', 'model_id.name', 'prescription_id')
    def _compute_prescription_name(self):
        for record in self:
            record.name = (record.model_id.line_id.name or '') + (record.model_id.name or '') + (record.prescription_id or _('No ID'))

            # record.name = (record.model_id.line_id.name or '') + '/' + (record.model_id.name or '') + '/' + (record.prescription_id or _('No ID'))

    def _get_measure(self):
        PrescriptionTypeMeasure = self.env['prescription.type.measure']
        for record in self:
            prescription_measure = PrescriptionTypeMeasure.search([('prescription_id', '=', record.id)], limit=1, order='value desc')
            if prescription_measure:
                record.measure = prescription_measure.value
            else:
                record.measure = 0

    def _set_measure(self):
        for record in self:
            if record.measure:
                date = fields.Date.context_today(record)
                data = {'value': record.measure, 'date': date, 'prescription_id': record.id}
                self.env['prescription.type.measure'].create(data)

    def _compute_count_all(self):
        Measure = self.env['prescription.type.measure']
        LogService = self.env['prescription.type.log.services'].with_context(active_test=False)
        LogPrescription = self.env['prescription.type.log'].with_context(active_test=False)
        History = self.env['prescription.type.assignation.log']
        measures_data = Measure._read_group([('prescription_id', 'in', self.ids)], ['prescription_id'], ['__count'])
        services_data = LogService._read_group([('prescription_id', 'in', self.ids)], ['prescription_id', 'active'], ['__count'])
        logs_data = LogPrescription._read_group([('prescription_id', 'in', self.ids), ('state', '!=', 'closed')], ['prescription_id', 'active'], ['__count'])
        histories_data = History._read_group([('prescription_id', 'in', self.ids)], ['prescription_id'], ['__count'])

        mapped_measure_data = defaultdict(lambda: 0)
        mapped_service_data = defaultdict(lambda: defaultdict(lambda: 0))
        mapped_log_data = defaultdict(lambda: defaultdict(lambda: 0))
        mapped_history_data = defaultdict(lambda: 0)

        for prescription, count in measures_data:
            mapped_measure_data[prescription.id] = count
        for prescription, active, count in services_data:
            mapped_service_data[prescription.id][active] = count
        for prescription, active, count in logs_data:
            mapped_log_data[prescription.id][active] = count
        for prescription, count in histories_data:
            mapped_history_data[prescription.id] = count

        for prescription in self:
            prescription.measure_count = mapped_measure_data[prescription.id]
            prescription.service_count = mapped_service_data[prescription.id][prescription.active]
            prescription.prescription_count = mapped_log_data[prescription.id][prescription.active]
            prescription.history_count = mapped_history_data[prescription.id]

    @api.depends('log_prescription')
    def _compute_prescription_reminder(self):
        params = self.env['ir.config_parameter'].sudo()
        delay_alert_prescription = int(params.get_param('hr_prescription.delay_alert_prescription', default=30))
        for record in self:
            overdue = False
            due_soon = False
            total = 0
            name = ''
            state = ''
            for element in record.log_prescription:
                if element.state in ('open', 'expired') and element.expiration_date:
                    current_date_str = fields.Date.context_today(record)
                    due_time_str = element.expiration_date
                    current_date = fields.Date.from_string(current_date_str)
                    due_time = fields.Date.from_string(due_time_str)
                    diff_time = (due_time - current_date).days
                    if diff_time < 0:
                        overdue = True
                        total += 1
                    if diff_time < delay_alert_prescription:
                        due_soon = True
                        total += 1
                    if overdue or due_soon:
                        log_prescription = self.env['prescription.type.log'].search([
                            ('prescription_id', '=', record.id),
                            ('state', 'in', ('open', 'expired'))
                            ], limit=1, order='expiration_date asc')
                        if log_prescription:
                            # we display only the name of the oldest overdue/due soon prescription
                            name = log_prescription.name
                            state = log_prescription.state

            record.prescription_renewal_overdue = overdue
            record.prescription_renewal_due_soon = due_soon
            record.prescription_renewal_total = total - 1  # we remove 1 from the real total for display purposes
            record.prescription_renewal_name = name
            record.prescription_state = state

    def _get_analytic_name(self):
        # This function is used in prescription_account and is overrided in l10n_be_hr_payroll_prescription
        return self.prescription_id or _('No plate')

    def _search_prescription_renewal_due_soon(self, operator, value):
        params = self.env['ir.config_parameter'].sudo()
        delay_alert_prescription = int(params.get_param('hr_prescription.delay_alert_prescription', default=30))
        res = []
        assert operator in ('=', '!=', '<>') and value in (True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = 'in'
        else:
            search_operator = 'not in'
        today = fields.Date.context_today(self)
        datetime_today = fields.Datetime.from_string(today)
        limit_date = fields.Datetime.to_string(datetime_today + relativedelta(days=+delay_alert_prescription))
        res_ids = self.env['prescription.type.log'].search([
            ('expiration_date', '>', today),
            ('expiration_date', '<', limit_date),
            ('state', 'in', ['open', 'expired'])
        ]).mapped('prescription_id').ids
        res.append(('id', search_operator, res_ids))
        return res

    def _search_get_overdue_prescription_reminder(self, operator, value):
        res = []
        assert operator in ('=', '!=', '<>') and value in (True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = 'in'
        else:
            search_operator = 'not in'
        today = fields.Date.context_today(self)
        res_ids = self.env['prescription.type.log'].search([
            ('expiration_date', '!=', False),
            ('expiration_date', '<', today),
            ('state', 'in', ['open', 'expired'])
        ]).mapped('prescription_id').ids
        res.append(('id', search_operator, res_ids))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # Prescription administrator may not have rights to create the plan_to_change_prescription
        # value when the location_id is a res.user.
        # This trick is used to prevent access right error.
        ptc_values = [
            'plan_to_change_prescription' in vals.keys() and {'plan_to_change_prescription': vals.pop('plan_to_change_prescription')} for vals in vals_list
        ]
        prescription = super().create(vals_list)
        for prescription, vals, ptc_value in zip(prescription, vals_list, ptc_values):
            if ptc_value:
                prescription.sudo().write(ptc_value)
            if 'location_id' in vals and vals['location_id']:
                prescription.create_practitioner_history(vals)
            if 'practitioner_id' in vals and vals['practitioner_id']:
                state_on_hold = self.env.ref('prescription.prescription_type_state_on_hold', raise_if_not_found=False)
                states = prescription.mapped('state_id').ids
                if not state_on_hold or state_on_hold.id not in states:
                    future_practitioner = self.env['res.partner'].browse(vals['practitioner_id'])
                    if self.prescription_type == 'otc':
                        future_practitioner.sudo().write({'plan_to_change_otc': True})
                    if self.prescription_type == 'custom':
                        future_practitioner.sudo().write({'plan_to_change_prescription': True})
        return prescription

    def write(self, vals):
        if 'location_id' in vals and vals['location_id']:
            location_id = vals['location_id']
            for prescription in self.filtered(lambda v: v.location_id.id != location_id):
                prescription.create_practitioner_history(vals)
                if prescription.location_id:
                    prescription.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=prescription.manager_id.id or self.env.user.id,
                        note=_('Specify the End date of %s', prescription.location_id.name))

        if 'practitioner_id' in vals and vals['practitioner_id']:
            state_on_hold = self.env.ref('prescription.prescription_type_state_on_hold', raise_if_not_found=False)
            states = self.mapped('state_id').ids if 'state_id' not in vals else [vals['state_id']]
            if not state_on_hold or state_on_hold.id not in states:
                future_practitioner = self.env['res.partner'].browse(vals['practitioner_id'])
                if self.prescription_type == 'otc':
                    future_practitioner.sudo().write({'plan_to_change_otc': True})
                if self.prescription_type == 'custom':
                    future_practitioner.sudo().write({'plan_to_change_prescription': True})

        if 'active' in vals and not vals['active']:
            self.env['prescription.type.log'].search([('prescription_id', 'in', self.ids)]).active = False
            self.env['prescription.type.log.services'].search([('prescription_id', 'in', self.ids)]).active = False

        res = super(PrescriptionType, self).write(vals)
        return res

    def _get_practitioner_history_data(self, vals):
        self.ensure_one()
        return {
            'prescription_id': self.id,
            'location_id': vals['location_id'],
            'date_start': fields.Date.today(),
        }

    def create_practitioner_history(self, vals):
        for prescription in self:
            self.env['prescription.type.assignation.log'].create(
                prescription._get_practitioner_history_data(vals),
            )

    def action_accept_practitioner_change(self):
        # Find all the prescription of the same type for which the practitioner is the practitioner_id
        # remove their location_id and close their history using current date
        prescription = self.search([('location_id', 'in', self.mapped('practitioner_id').ids), ('prescription_type', '=', self.prescription_type)])
        prescription.write({'location_id': False})

        for prescription in self:
            if prescription.prescription_type == 'otc':
                prescription.practitioner_id.sudo().write({'plan_to_change_otc': False})
            if prescription.prescription_type == 'custom':
                prescription.practitioner_id.sudo().write({'plan_to_change_prescription': False})
            prescription.location_id = prescription.practitioner_id
            prescription.practitioner_id = False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['prescription.type.state'].search([], order=order)

    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current prescription """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('prescription.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_prescription_id=self.id, group_by=False),
                domain=[('prescription_id', '=', self.id)]
            )
            return res
        return False

    def act_show_log_cost(self):
        """ This opens log view to view and add new log for this prescription, groupby default to only show effective costs
            @return: the costs log view
        """
        self.ensure_one()
        copy_context = dict(self.env.context)
        copy_context.pop('group_by', None)
        res = self.env['ir.actions.act_window']._for_xml_id('prescription.prescription_type_costs_action')
        res.update(
            context=dict(copy_context, default_prescription_id=self.id, search_default_parent_false=True),
            domain=[('prescription_id', '=', self.id)]
        )
        return res

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'location_id' in init_values or 'practitioner_id' in init_values:
            return self.env.ref('prescription.mt_prescription_practitioner_updated')
        return super(PrescriptionType, self)._track_subtype(init_values)

    def open_assignation_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignment Logs',
            'view_mode': 'tree',
            'res_model': 'prescription.type.assignation.log',
            'domain': [('prescription_id', '=', self.id)],
            'context': {'default_location_id': self.location_id.id, 'default_prescription_id': self.id}
        }
