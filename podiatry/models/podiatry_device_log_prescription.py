# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class PodiatryDeviceLogPrescription(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'podiatry.device.log.prescription'
    _description = 'Device Prescription'
    _order = 'state desc,expiration_date'

    def compute_next_year_date(self, strdate):
        oneyear = relativedelta(years=1)
        start_date = fields.Date.from_string(strdate)
        return fields.Date.to_string(start_date + oneyear)

    device_id = fields.Many2one('podiatry.device', 'Device', required=True, help='Device concerned by this log', check_company=True)
    cost_subtype_id = fields.Many2one('podiatry.service.type', 'Type', help='Cost type purchased with this cost', domain=[('category', '=', 'prescription')])
    amount = fields.Monetary('Cost')
    date = fields.Date(help='Date when the cost has been executed')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    name = fields.Char(string='Name', compute='_compute_prescription_name', store=True)
    active = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, index=True)
    start_date = fields.Date(
        'Prescription Start Date', default=fields.Date.context_today,
        help='Date when the coverage of the prescription begins')
    expiration_date = fields.Date(
        'Prescription Expiration Date', default=lambda self:
        self.compute_next_year_date(fields.Date.context_today(self)),
        help='Date when the coverage of the prescription expirates (by default, one year after begin date)')
    days_left = fields.Integer(compute='_compute_days_left', string='Warning Date')
    insurer_id = fields.Many2one('res.partner', 'Vendor')
    purchaser_id = fields.Many2one(related='device_id.patient_id', string='Patient')
    ins_ref = fields.Char('Reference', size=64, copy=False)
    state = fields.Selection(
        [('futur', 'Incoming'),
         ('open', 'In Progress'),
         ('expired', 'Expired'),
         ('closed', 'Closed')
        ], 'Status', default='open', readonly=True,
        help='Choose whether the prescription is still valid or not',
        tracking=True,
        copy=False)
    notes = fields.Html('Terms and Conditions', help='Write here all supplementary information relative to this prescription', copy=False)
    cost_generated = fields.Monetary('Recurring Cost')
    cost_frequency = fields.Selection([
        ('no', 'No'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
        ], 'Recurring Cost Frequency', default='monthly', help='Frequency of the recuring cost', required=True)
    service_ids = fields.Many2many('podiatry.service.type', string="Included Services")

    @api.depends('device_id.name', 'cost_subtype_id')
    def _compute_prescription_name(self):
        for record in self:
            name = record.device_id.name
            if name and record.cost_subtype_id.name:
                name = record.cost_subtype_id.name + ' ' + name
            record.name = name

    @api.depends('expiration_date', 'state')
    def _compute_days_left(self):
        """return a dict with as value for each prescription an integer
        if prescription is in an open state and is overdue, return 0
        if prescription is in a closed state, return -1
        otherwise return the number of days before the prescription expires
        """
        for record in self:
            if record.expiration_date and record.state in ['open', 'expired']:
                today = fields.Date.from_string(fields.Date.today())
                renew_date = fields.Date.from_string(record.expiration_date)
                diff_time = (renew_date - today).days
                record.days_left = diff_time if diff_time > 0 else 0
            else:
                record.days_left = -1

    def write(self, vals):
        res = super(PodiatryDeviceLogPrescription, self).write(vals)
        if 'start_date' in vals or 'expiration_date' in vals:
            date_today = fields.Date.today()
            future_prescriptions, running_prescriptions, expired_prescriptions = self.env[self._name], self.env[self._name], self.env[self._name]
            for prescription in self.filtered(lambda c: c.start_date and c.state != 'closed'):
                if date_today < prescription.start_date:
                    future_prescriptions |= prescription
                elif not prescription.expiration_date or prescription.start_date <= date_today < prescription.expiration_date:
                    running_prescriptions |= prescription
                else:
                    expired_prescriptions |= prescription
            future_prescriptions.action_draft()
            running_prescriptions.action_open()
            expired_prescriptions.action_expire()
        if vals.get('expiration_date') or vals.get('user_id'):
            self.activity_reschedule(['podiatry.mail_act_podiatry_prescription_to_renew'], date_deadline=vals.get('expiration_date'), new_user_id=vals.get('user_id'))
        return res

    def action_close(self):
        self.write({'state': 'closed'})

    def action_draft(self):
        self.write({'state': 'futur'})

    def action_open(self):
        self.write({'state': 'open'})

    def action_expire(self):
        self.write({'state': 'expired'})

    @api.model
    def scheduler_manage_prescription_expiration(self):
        # This method is called by a cron task
        # It manages the state of a prescription, possibly by posting a message on the device concerned and updating its status
        params = self.env['ir.config_parameter'].sudo()
        delay_alert_prescription = int(params.get_param('hr_podiatry.delay_alert_prescription', default=30))
        date_today = fields.Date.from_string(fields.Date.today())
        outdated_days = fields.Date.to_string(date_today + relativedelta(days=+delay_alert_prescription))
        reminder_activity_type = self.env.ref('podiatry.mail_act_podiatry_prescription_to_renew', raise_if_not_found=False) or self.env['mail.activity.type']
        nearly_expired_prescriptions = self.search([
            ('state', '=', 'open'),
            ('expiration_date', '<', outdated_days),
            ('user_id', '!=', False)
        ]
        ).filtered(
            lambda nec: reminder_activity_type not in nec.activity_ids.activity_type_id
        )

        for prescription in nearly_expired_prescriptions:
            prescription.activity_schedule(
                'podiatry.mail_act_podiatry_prescription_to_renew', prescription.expiration_date,
                user_id=prescription.user_id.id)

        expired_prescriptions = self.search([('state', 'not in', ['expired', 'closed']), ('expiration_date', '<',fields.Date.today() )])
        expired_prescriptions.write({'state': 'expired'})

        futur_prescriptions = self.search([('state', 'not in', ['futur', 'closed']), ('start_date', '>', fields.Date.today())])
        futur_prescriptions.write({'state': 'futur'})

        now_running_prescriptions = self.search([('state', '=', 'futur'), ('start_date', '<=', fields.Date.today())])
        now_running_prescriptions.write({'state': 'open'})

    def run_scheduler(self):
        self.scheduler_manage_prescription_expiration()
