# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PatientProcedures(models.Model):
    _name = 'patient.procedures'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Patient Procedures'

    partner_id = fields.Many2one('res.partner', string='Patient')
    name = fields.Char(string="Name", )
    registration_no = fields.Char(string="Registration No")
    condition_type_id = fields.Many2one('condition.type', string='Condition Type',
                                      tracking=True, required=True)
    condition_stage_id = fields.Many2one('condition.stage', string='Condition Stage',
                                       tracking=True)
    date = fields.Datetime(string='Date')
    employee_id = fields.Many2one('hr.employee', string='Doctor')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    line_ids = fields.One2many('patient.procedures.line', 'procedures_id', string="Lines")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('invoice', 'Invoice')], tracking=True, default='draft')
    total_fees = fields.Float(string="Total Fees", compute='compute_total_fees')

    @api.depends('total_fees')
    def compute_total_fees(self):
        total_fees = 0
        for rec in self:
            for line_id in rec.line_ids:
                total_fees += line_id.fees
            rec.total_fees = total_fees

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('patient.procedures') or 'New'
        return super(PatientProcedures, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            rec.registration_no = rec.partner_id.registration_no
            # rec.condition_type_id = rec.partner_id.condition_type_id
            # rec.condition_stage_id = rec.partner_id.condition_stage_id

    def action_done(self):
        for rec in self:
            for line_id in rec.line_ids:
                if not line_id.end_date:
                    raise ValidationError('Please Enter End Date')
            rec.state = 'done'

    def action_create_invoice(self):
        invoice_vals = self._prepare_invoice()
        account_move = self.env['account.move'].create(invoice_vals)

        if account_move:
            self.invoice_id = account_move
            self.state = 'invoice'
            account_move.action_post()
        form_id = self.env.ref('account.view_move_form').id
        return {'type': 'ir.actions.act_window',
                'name': _('Invoice'),
                'res_model': 'account.move',
                'view_mode': 'form',
                'views': [(form_id, 'form')],
                'domain': [('id', '=', self.invoice_id.id)],
                'res_id': account_move.id
                }

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        company_id = self.employee_id.company_id
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        journal = self.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
        if not journal:
            raise ValidationError(_('Please define an accounting sales journal for the company %s (%s).') % (
                company_id.name, company_id.id))
        name = self.partner_id.name + '-' + self.name
        account_id = self.partner_id.property_account_receivable_id

        partner_id = self.partner_id
        invoice_lines = []
        for line_id in self.line_ids:
            vals = {
                'name': line_id.procedures_type_id.name,
                'price_unit': line_id.fees,
                'quantity': 1,
            }
            invoice_lines.append((0, 0, vals))

        invoice_vals = {
            'move_type': 'out_invoice',
            'invoice_user_id': self.env.user and self.env.user.id,
            'partner_id': partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
            #'journal_id': journal.id,  # company comes from the journal
            'company_id': self.employee_id.company_id.id,
        }
        return invoice_vals


class PatientProceduresLine(models.Model):
    _name = 'patient.procedures.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'procedures_id'
    _description = 'Patient Procedures Line'

    procedures_id = fields.Many2one('patient.procedures', string='Procedure')
    procedures_type_id = fields.Many2one('patient.procedures.type', string='Procedure Type')
    fees = fields.Float(string="Fees")
    start_date = fields.Datetime('Start Date And Time')
    end_date = fields.Datetime('End Date And Time')
    remark = fields.Text('Remark')

    @api.onchange('procedures_type_id')
    def onchange_procedures_type_id(self):
        for rec in self:
            rec.fees = rec.procedures_type_id.fees
