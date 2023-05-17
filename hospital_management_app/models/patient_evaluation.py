# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PatientEvaluation(models.Model):
    # _name = 'hospital.patient.registration'
    _name = 'patient.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Patient Evaluation'

    # Identification Details

    partner_id = fields.Many2one('res.partner', string='Patient')
    father_name = fields.Char(string="Father/Spouse's Name")
    name = fields.Char(string="Name", )
    street = fields.Char(string='Street', )
    street2 = fields.Char(string='Street')
    zip = fields.Char(string='Street')
    city = fields.Char(string='Street')
    registration_no = fields.Char(string='Registration Card')
    disease_type_id = fields.Many2one('condition.type', string='Condition Type',
                                      tracking=True, required=True)
    disease_stage_id = fields.Many2one('condition.stage', string='Condition Stage',
                                       tracking=True)
    date = fields.Datetime(string='Date')
    partner_id = fields.Many2one('res.partner', string='Doctor')
    nurse_id = fields.Many2one('res.partner', string='Nurse')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    state = fields.Selection([('draft', 'draft'), ('evaluated', 'evaluated'), ('invoice', 'Invoice')], default='draft',
                             tracking=True)
    reason = fields.Selection(
        [('pre', 'pre-admission'), ('month', '12-month'), ('acute', 'Acute Change Condition'), ('other', ('other'))],
        tracking=True)
    other_reason = fields.Char('Other Reason')
    bp = fields.Char(string="BP")
    pulse = fields.Char(string="Pulse")
    t = fields.Char(string="T")
    height = fields.Char(string="Height")
    weight = fields.Char(string="Weight")
    primary_diagnosis = fields.Text(string="Primary Diagnosis")
    secondary_diagnosis = fields.Text(string="Secondary Diagnosis")
    is_allergies = fields.Boolean(string='Is Allergies?')
    allergies = fields.Char(string='Allergies')
    diet = fields.Boolean(string='Diet')
    regular = fields.Boolean(string='Regular')
    no_added_salt = fields.Boolean(string='No Added Salt')
    no_sweet = fields.Boolean(string='No Sweet')
    other = fields.Boolean(string='Other')
    other_plan = fields.Char('Other')
    immunization = fields.Boolean(string='Immunization')
    influenza_date = fields.Date(string="Influenza Date")
    basic_fees = fields.Float(string='Basic Fees')
    bed_charge = fields.Float(string='Bed Charge')
    other_fees = fields.Float(string='Other Fees')
    discount = fields.Float(string='Discount Amount')
    total_fees = fields.Float(string='Total Fees', compute='compute_total_charge', store=True)

    @api.depends('basic_fees', 'bed_charge', 'other_fees', 'discount')
    def compute_total_charge(self):
        for rec in self:
            rec.total_fees = rec.basic_fees + rec.bed_charge + rec.other_fees - rec.discount

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
        company_id = self.partner_id.company_id
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
        vals = {
            'name': name,
            'price_unit': self.total_fees,
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
            'company_id': self.partner_id.company_id.id,
        }
        return invoice_vals

    def action_evaluated(self):
        for rec in self:
            rec.state = 'evaluated'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('patient.evaluation') or 'New'
        return super(PatientEvaluation, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            rec.father_name = rec.partner_id.father_name
            rec.street = rec.partner_id.street
            rec.street2 = rec.partner_id.street2
            rec.zip = rec.partner_id.zip
            rec.city = rec.partner_id.city
            rec.registration_no = rec.partner_id.registration_no
            # rec.disease_type_id = rec.partner_id.disease_type_id
            # rec.disease_stage_id = rec.partner_id.disease_stage_id
