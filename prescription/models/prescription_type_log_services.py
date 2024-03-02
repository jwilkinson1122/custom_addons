# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PrescriptionTypeLogServices(models.Model):
    _name = 'prescription.type.log.services'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'service_type_id'
    _description = 'Adjustments for prescription'

    active = fields.Boolean(default=True)
    prescription_id = fields.Many2one('prescription.type', 'Prescription', required=True)
    manager_id = fields.Many2one('res.users', 'Prescription Manager', related='prescription_id.manager_id', store=True)
    amount = fields.Monetary('Cost')
    description = fields.Char('Description')
    measure_id = fields.Many2one('prescription.type.measure', 'Measures', help='Measurements of the prescription at the moment of this log')
    measure = fields.Float(
        compute="_get_measure", inverse='_set_measure', string='Measure Value',
        help='Measurements of the prescription at the moment of this log')
    laterality = fields.Selection(related='prescription_id.laterality', string="Unit", readonly=True)
    date = fields.Date(help='Date when the cost has been executed', default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    prescriber_id = fields.Many2one('res.partner', string="Practitioner", compute='_compute_prescriber_id', readonly=False, store=True)
    inv_ref = fields.Char('Vendor Reference')
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    notes = fields.Text()
    service_type_id = fields.Many2one(
        'prescription.service.type', 'Service Type', required=True,
        default=lambda self: self.env.ref('prescription.type_service_service_7', raise_if_not_found=False),
    )
    state = fields.Selection([
        ('new', 'New'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='new', string='Stage', group_expand='_expand_states', tracking=True)

    def _get_measure(self):
        self.measure = 0
        for record in self:
            if record.measure_id:
                record.measure = record.measure_id.value

    def _set_measure(self):
        for record in self:
            if not record.measure:
                raise UserError(_('Emptying the measure value of a prescription is not allowed.'))
            measure = self.env['prescription.type.measure'].create({
                'value': record.measure,
                'date': record.date or fields.Date.context_today(record),
                'prescription_id': record.prescription_id.id
            })
            self.measure_id = measure

    @api.model_create_multi
    def create(self, vals_list):
        for data in vals_list:
            if 'measure' in data and not data['measure']:
                # if received value for measure is 0, then remove it from the
                # data as it would result to the creation of a
                # measure log with 0, which is to be avoided
                del data['measure']
        return super(PrescriptionTypeLogServices, self).create(vals_list)

    @api.depends('prescription_id')
    def _compute_prescriber_id(self):
        for service in self:
            service.prescriber_id = service.prescription_id.location_id

    def _expand_states(self, states, domain, order):
        return [key for key, dummy in type(self).state.selection]
