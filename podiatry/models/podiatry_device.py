# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.addons.podiatry.models.podiatry_device_model import DEVICE_TYPES


#Some fields don't have the exact same name
MODEL_FIELDS_TO_DEVICE = {
    'arch_height': 'arch_height', 'color': 'color', 'pairs': 'pairs', 'default_device_type': 'device_type',
    'patient_weight': 'patient_weight', 'patient_weight_tax': 'patient_weight_tax',
}

class PodiatryDevice(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'podiatry.device'
    _description = 'Device'
    _order = 'device_registration asc, acquisition_date asc'

    def _get_default_state(self):
        state = self.env.ref('podiatry.podiatry_device_state_registered', raise_if_not_found=False)
        return state if state and state.id else False

    name = fields.Char(compute="_compute_device_name", store=True)
    description = fields.Html("Device Description", help="Add a note about this device")
    active = fields.Boolean('Active', default=True, tracking=True)
    manager_id = fields.Many2one(
        'res.users', 'Podiatry Manager',
        domain=lambda self: [('groups_id', 'in', self.env.ref('podiatry.podiatry_group_manager').id)],
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    country_id = fields.Many2one('res.country', related='company_id.country_id')
    country_code = fields.Char(related='country_id.code')
    device_registration = fields.Char(tracking=True,
        help='Registration number of the device (i = number for a device)')
    din_sn = fields.Char('Shell Number', help='Unique number written on the device shell (DIN/SN number)', copy=False)
    patient_id = fields.Many2one('res.partner', 'Patient', tracking=True, help='Patient', copy=False)
    hold_patient_id = fields.Many2one('res.partner', 'Pending Patient', tracking=True, help='Planned Patient', copy=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    model_id = fields.Many2one('podiatry.device.model', 'Model',
        tracking=True, required=True, help='Model of the device')

    line_id = fields.Many2one('podiatry.device.model.line', 'Line', related="model_id.line_id", store=True, readonly=False)
    log_patients = fields.One2many('podiatry.device.assignation.log', 'device_id', string='Assignment Logs')
    log_services = fields.One2many('podiatry.device.log.services', 'device_id', 'Services Logs')
    service_count = fields.Integer(compute="_compute_count_all", string='Services')
    laterality_count = fields.Integer(compute="_compute_count_all", string='Laterality')
    history_count = fields.Integer(compute="_compute_count_all", string="Patients History Count")
    next_assignation_date = fields.Date('Assignment Date', help='This is the date at which the device will be available, if not set it means available instantly')
    acquisition_date = fields.Date('Acquired Date', required=False,
        default=fields.Date.today, help='Date when the device has been acquired')
    color = fields.Char(help='Color of the device top cover', compute='_compute_model_fields', store=True, readonly=False)
    state_id = fields.Many2one('podiatry.device.state', 'State',
        default=_get_default_state, group_expand='_read_group_stage_ids',
        tracking=True,
        help='Current state of the device', ondelete="set null")
    location = fields.Char(help='Location (hospital, ...)')
    pairs = fields.Integer('Make Number', help='Number of pairs of the device', compute='_compute_model_fields', store=True, readonly=False)
    tag_ids = fields.Many2many('podiatry.device.tag', 'podiatry_device_device_tag_rel', 'device_tag_id', 'tag_id', 'Tags', copy=False)
    device_type = fields.Selection(DEVICE_TYPES, 'Device Type', help='Type of device', compute='_compute_model_fields', store=True, readonly=False)
    laterality = fields.Float(compute='_get_laterality', inverse='_set_laterality', string='Last Laterality',
        help='Laterality measure of the device at the moment of this log')
    laterality_unit = fields.Selection(
        [('lt', 'Left Only'), ('rt', 'Right Only'), ('bl', 'Bilateral'),], 'Laterality Unit', default='bl', help='Foot side unit ', required=True)
    arch_height = fields.Selection(
        [('very_high', 'Very High'), 
         ('high', 'High'),
         ('standard', 'Standard'),
         ('low', 'Low'),
         ], 'Arch Height', default='standard', help='Arch Height of the device',
        compute='_compute_model_fields', store=True, readonly=False)
    patient_weight = fields.Integer(compute='_compute_model_fields', store=True, readonly=False)
    patient_height = fields.Integer(compute='_compute_model_fields', store=True, readonly=False)
    image_128 = fields.Image(related='model_id.image_128', readonly=True)
    prescription_renewal = fields.Boolean(compute='_compute_prescription_reminder', search='_search_prescription_renewal',
        string='Renew Prior Prescription')
    prescription_renewal_name = fields.Text(compute='_compute_prescription_reminder', string='Name of prescription to renew soon')
    prescription_renewal_total = fields.Text(compute='_compute_prescription_reminder', string='Total of prescriptions due or overdue minus one')
    prescription_state = fields.Selection(
        [('futur', 'Incoming'),
         ('open', 'In Progress'),
         ('expired', 'Expired'),
         ('closed', 'Closed')
        ], string='Last Prescription State', compute='_compute_prescription_reminder', required=False)
    device_price = fields.Float(string="Price of Device(s)", help='Price of the device')
    net_device_price = fields.Float(string="Purchase Price", help="Purchase price of the device")
    residual_value = fields.Float()
    plan_to_change_device = fields.Boolean(related='patient_id.plan_to_change_device', store=True, readonly=False)
    device_type = fields.Selection(related='model_id.device_type')
    shell_type = fields.Selection(
        [('sg_flex', 'Superglass Flex'), 
         ('sg_everyday', 'Superglass Everyday'), 
         ('sg_proformance', 'Superglass Proformance'),
         ('ncv_gentle', 'NCV Gentle'),
         ('ncv_firm', 'NCV Firm'),
         ('pc_multi_density', 'Prescription Comfort Multi-Density'),
         ('pc_composite', 'Prescription Comfort Composite'),
         ], help="Shell/Foundation type of the device")
 
    shoe_size = fields.Float()

    @api.depends('model_id')
    def _compute_model_fields(self):
        '''
        Copies all the related fields from the model to the device
        '''
        model_values = dict()
        for device in self.filtered('model_id'):
            if device.model_id.id in model_values:
                write_vals = model_values[device.model_id.id]
            else:
                # copy if value is truthy
                write_vals = {MODEL_FIELDS_TO_DEVICE[key]: device.model_id[key] for key in MODEL_FIELDS_TO_DEVICE\
                    if device.model_id[key]}
                model_values[device.model_id.id] = write_vals
            device.write(write_vals)

    @api.depends('model_id.line_id.name', 'model_id.name', 'device_registration')
    def _compute_device_name(self):
        for record in self:
            record.name = (record.model_id.line_id.name or '') + '/' + (record.model_id.name or '') + '/' + (record.device_registration or _('No Plate'))

    def _get_laterality(self):
        PodiatryDeviceLaterality = self.env['podiatry.device.laterality']
        for record in self:
            device_laterality = PodiatryDeviceLaterality.search([('device_id', '=', record.id)], limit=1, order='value desc')
            if device_laterality:
                record.laterality = device_laterality.value
            else:
                record.laterality = 0

    def _set_laterality(self):
        for record in self:
            if record.laterality:
                date = fields.Date.context_today(record)
                data = {'value': record.laterality, 'date': date, 'device_id': record.id}
                self.env['podiatry.device.laterality'].create(data)

    def _compute_count_all(self):
        Laterality = self.env['podiatry.device.laterality']
        LogService = self.env['podiatry.device.log.services']
        LogPrescription = self.env['podiatry.device.log.prescription']
        for record in self:
            record.laterality_count = Laterality.search_count([('device_id', '=', record.id)])
            record.service_count = LogService.search_count([('device_id', '=', record.id), ('active', '=', record.active)])
            record.prescription_count = LogPrescription.search_count([('device_id', '=', record.id), ('state', '!=', 'closed'), ('active', '=', record.active)])
            record.history_count = self.env['podiatry.device.assignation.log'].search_count([('device_id', '=', record.id)])

    @api.depends('log_prescriptions')
    def _compute_prescription_reminder(self):
        params = self.env['ir.config_parameter'].sudo()
        delay_alert_prescription = int(params.get_param('hr_podiatry.delay_alert_prescription', default=30))
        for record in self:
            overdue = False
            due_soon = False
            total = 0
            name = ''
            state = ''
            for element in record.log_prescriptions:
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
                        log_prescription = self.env['podiatry.device.log.prescription'].search([
                            ('device_id', '=', record.id),
                            ('state', 'in', ('open', 'expired'))
                            ], limit=1, order='expiration_date asc')
                        if log_prescription:
                            # we display only the name of the oldest overdue/due soon prescription
                            name = log_prescription.name
                            state = log_prescription.state

            record.prescription_renewal_overdue = overdue
            record.prescription_renewal = due_soon
            record.prescription_renewal_total = total - 1  # we remove 1 from the real total for display purposes
            record.prescription_renewal_name = name
            record.prescription_state = state

    def _get_analytic_name(self):
        # This function is used in podiatry_account and is overrided in l10n_be_hr_payroll_podiatry
        return self.device_registration or _('No id')

    def _search_prescription_renewal(self, operator, value):
        params = self.env['ir.config_parameter'].sudo()
        delay_alert_prescription = int(params.get_param('hr_podiatry.delay_alert_prescription', default=30))
        res = []
        assert operator in ('=', '!=', '<>') and value in (True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = 'in'
        else:
            search_operator = 'not in'
        today = fields.Date.context_today(self)
        datetime_today = fields.Datetime.from_string(today)
        limit_date = fields.Datetime.to_string(datetime_today + relativedelta(days=+delay_alert_prescription))
        res_ids = self.env['podiatry.device.log.prescription'].search([
            ('expiration_date', '>', today),
            ('expiration_date', '<', limit_date),
            ('state', 'in', ['open', 'expired'])
        ]).mapped('device_id').ids
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
        res_ids = self.env['podiatry.device.log.prescription'].search([
            ('expiration_date', '!=', False),
            ('expiration_date', '<', today),
            ('state', 'in', ['open', 'expired'])
        ]).mapped('device_id').ids
        res.append(('id', search_operator, res_ids))
        return res

    @api.model
    def create(self, vals):
        # Podiatry administrator may not have rights to create the plan_to_change_device value when the patient_id is a res.user
        # This trick is used to prevent access right error.
        ptc_value = 'plan_to_change_device' in vals.keys() and {'plan_to_change_device': vals.pop('plan_to_change_device')}
        res = super(PodiatryDevice, self).create(vals)
        if ptc_value:
            res.sudo().write(ptc_value)
        if 'patient_id' in vals and vals['patient_id']:
            res.create_patient_history(vals)
        if 'hold_patient_id' in vals and vals['hold_patient_id']:
            state_waiting_list = self.env.ref('podiatry.podiatry_device_state_waiting_list', raise_if_not_found=False)
            states = res.mapped('state_id').ids
            if not state_waiting_list or state_waiting_list.id not in states:
                future_patient = self.env['res.partner'].browse(vals['hold_patient_id'])
                if self.device_type == 'device':
                    future_patient.sudo().write({'plan_to_change_device': True})
        return res

    def write(self, vals):
        if 'patient_id' in vals and vals['patient_id']:
            patient_id = vals['patient_id']
            for device in self.filtered(lambda v: v.patient_id.id != patient_id):
                device.create_patient_history(vals)
                if device.patient_id:
                    device.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=device.manager_id.id or self.env.user.id,
                        note=_('Specify the End date of %s') % device.patient_id.name)

        if 'hold_patient_id' in vals and vals['hold_patient_id']:
            state_waiting_list = self.env.ref('podiatry.podiatry_device_state_waiting_list', raise_if_not_found=False)
            states = self.mapped('state_id').ids if 'state_id' not in vals else [vals['state_id']]
            if not state_waiting_list or state_waiting_list.id not in states:
                future_patient = self.env['res.partner'].browse(vals['hold_patient_id'])
                if self.device_type == 'device':
                    future_patient.sudo().write({'plan_to_change_device': True})

        if 'active' in vals and not vals['active']:
            self.env['podiatry.device.log.prescription'].search([('device_id', 'in', self.ids)]).active = False
            self.env['podiatry.device.log.services'].search([('device_id', 'in', self.ids)]).active = False

        res = super(PodiatryDevice, self).write(vals)
        return res

    def _get_patient_history_data(self, vals):
        self.ensure_one()
        return {
            'device_id': self.id,
            'patient_id': vals['patient_id'],
            'date_start': fields.Date.today(),
        }

    def create_patient_history(self, vals):
        for device in self:
            self.env['podiatry.device.assignation.log'].create(
                device._get_patient_history_data(vals),
            )

    def action_accept_patient_change(self):
        # Find all the devices for which the patient is the hold_patient_id
        # remove their patient_id and close their history using current date
        devices = self.search([('patient_id', 'in', self.mapped('hold_patient_id').ids)])
        devices.write({'patient_id': False})

        for device in self:
            if device.device_type == 'device':
                device.hold_patient_id.sudo().write({'plan_to_change_device': False})
            device.patient_id = device.hold_patient_id
            device.hold_patient_id = False

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['podiatry.device.state'].search([], order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        return super(PodiatryDevice, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('patient_id.name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current device """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('podiatry.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_device_id=self.id, group_by=False),
                domain=[('device_id', '=', self.id)]
            )
            return res
        return False

    def act_show_log_cost(self):
        """ This opens log view to view and add new log for this device, groupby default to only show effective costs
            @return: the costs log view
        """
        self.ensure_one()
        copy_context = dict(self.env.context)
        copy_context.pop('group_by', None)
        res = self.env['ir.actions.act_window']._for_xml_id('podiatry.podiatry_device_costs_action')
        res.update(
            context=dict(copy_context, default_device_id=self.id, search_default_parent_false=True),
            domain=[('device_id', '=', self.id)]
        )
        return res

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'patient_id' in init_values or 'hold_patient_id' in init_values:
            return self.env.ref('podiatry.mt_podiatry_patient_updated')
        return super(PodiatryDevice, self)._track_subtype(init_values)

    def open_assignation_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignment Logs',
            'view_mode': 'tree',
            'res_model': 'podiatry.device.assignation.log',
            'domain': [('device_id', '=', self.id)],
            'context': {'default_patient_id': self.patient_id.id, 'default_device_id': self.id}
        }
