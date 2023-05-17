from odoo import models, fields, api


class Transaction(models.Model):
    _name = 'eclinic.transaction'
    _description = 'Transaction'

    clinic_id = fields.Many2one('clinic', string='Clinic', required=True)
    name = fields.Char(string='Transaction ID', required=True, readonly=True)
    prescription = fields.Text(string='Prescription')

    pharmacist_id = fields.Many2one('eclinic.pharmacist', string='Pharmacist', required=True)
    patient_id = fields.Many2one('eclinic.patient', string='Patient', required=True)

    trx_date = fields.Datetime(string='Transaction Date', default=fields.Date.today())

    total = fields.Float(string='Total', compute='_compute_total')

    transaction_lines = fields.One2many(
        'eclinic.transaction.detail', 
        'transaction_id', 
        string='Transaction Detail'
    )

    @api.depends('transaction_lines.payment_amount')
    def _compute_total(self):
        for record in self:
            record.total = sum(record.transaction_lines.mapped('payment_amount'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('transaction_increment') or 'New'
        return super(Transaction, self).create(vals)       


class TransactionDetail(models.Model):
    _name = 'eclinic.transaction.detail'
    _description = 'Transaction Detail'

    transaction_id = fields.Many2one('eclinic.transaction', string='Transaction')
    medicine_id = fields.Many2one('eclinic.medicine', string='Medicine')
    payment_amount = fields.Float(string='Payment Amount')
