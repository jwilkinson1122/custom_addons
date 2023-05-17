# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AppointmentManagement(models.Model):
    # _name = 'hospital.patient.registration'
    _name = 'appointment.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Appointment Management'

    # Identification Details

    patient_id = fields.Many2one('res.partner', string='Patient')
    father_name = fields.Char(string="Father/Spouse's Name")
    name = fields.Char(string="Name", )
    street = fields.Char(string='Street', )
    street2 = fields.Char(string='Street2')
    zip = fields.Char(string='Zip')
    city = fields.Char(string='City')
    registration_no = fields.Char(string='Registration Card')
    condition_type_id = fields.Many2one('condition.type', string='Condition Type',
                                      tracking=True, required=True)
    condition_stage_id = fields.Many2one('condition.stage', string='Condition Stage',
                                       tracking=True)
    condition_fees = fields.Float(string='Condition Fees Per Visit', tracking=True)
    appointment_date = fields.Datetime(string='Date')
    next_visit = fields.Date(string='Next Visit')
    partner_id = fields.Many2one('res.partner', string='Doctor')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    state = fields.Selection([('new', 'New'), ('complete', 'Complete'), ('invoice', 'Invoice')], default='new',
                             tracking=True)
    doc_type = fields.Selection([('appointment', 'Appointment'), ('treatment', 'Treatment')], string='Type')
    line_ids = fields.One2many('appointment.management.line', 'appointment_id', string="History")
    is_history_created = fields.Boolean(string="Is History Created")

    @api.onchange('condition_type_id')
    def onchange_condition_type_id(self):
        for rec in self:
            rec.condition_fees = rec.condition_type_id.fees

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
            'price_unit': self.condition_fees,
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

    def action_complete(self):
        for rec in self:
            rec.state = 'complete'

    @api.model
    def create(self, vals):
        if vals['doc_type'] == 'appointment':
            vals['name'] = self.env['ir.sequence'].next_by_code('appointment.management') or 'New'
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('treatment.management') or 'New'
        return super(AppointmentManagement, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            rec.father_name = rec.partner_id.father_name
            rec.street = rec.partner_id.street
            rec.street2 = rec.partner_id.street2
            rec.zip = rec.partner_id.zip
            rec.city = rec.partner_id.city
            rec.registration_no = rec.partner_id.registration_no
            # rec.condition_type_id = rec.partner_id.condition_type_id
            # rec.condition_stage_id = rec.partner_id.condition_stage_id
            # rec.condition_fees = rec.partner_id.condition_type_id.fees

    def action_create_history(self):
        for rec in self:
            if rec.doc_type == 'treatment':
                treatment_ids = self.env['appointment.management'].search(
                    [('id', '!=', self.id), ('doc_type', '=', 'treatment'), ('partner_id', '=', self.partner_id.id)])
                if treatment_ids:
                    rec.is_history_created = True
                for treatment_id in treatment_ids:
                    self.env['appointment.management.line'].create({
                        'appointment_id': rec.id,
                        'condition_type_id': treatment_id.condition_type_id.id,
                        'name': treatment_id.name,
                        'condition_stage_id': treatment_id.condition_stage_id.id,
                        'condition_fees': treatment_id.condition_fees,
                        'appointment_date': treatment_id.appointment_date,
                        'partner_id': treatment_id.partner_id.id,
                        'invoice_id': treatment_id.invoice_id.id,
                        'state': treatment_id.state,
                        'doc_type': treatment_id.doc_type,
                    })
            if rec.doc_type == 'appointment':
                appointment_ids = self.env['appointment.management'].search(
                    [('id', '!=', self.id), ('doc_type', '=', 'appointment'), ('partner_id', '=', self.partner_id.id)])

                if appointment_ids:
                    rec.is_history_created = True
                for appointment_id in appointment_ids:
                    self.env['appointment.management.line'].create({
                        'appointment_id': rec.id,
                        'condition_type_id': appointment_id.condition_type_id.id,
                        'name': appointment_id.name,
                        'condition_stage_id': appointment_id.condition_stage_id.id,
                        'condition_fees': appointment_id.condition_fees,
                        'appointment_date': appointment_id.appointment_date,
                        'partner_id': appointment_id.partner_id.id,
                        'invoice_id': appointment_id.invoice_id.id,
                        'state': appointment_id.state,
                        'doc_type': appointment_id.doc_type,
                    })



class AppointmentManagementLine(models.Model):
    _name = 'appointment.management.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Appointment Management Line'

    # Identification Details
    appointment_id = fields.Many2one('appointment.management', string="Appointment")
    name = fields.Char(string="Name")
    condition_type_id = fields.Many2one('condition.type', string='Condition Type',
                                      tracking=True, required=True)
    condition_stage_id = fields.Many2one('condition.stage', string='Condition Stage',
                                       tracking=True)
    condition_fees = fields.Float(string='Condition Fees Per Visit', store=True, related='condition_type_id.fees',
                                tracking=True)
    appointment_date = fields.Datetime(string='Date')
    partner_id = fields.Many2one('res.partner', string='Doctor')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    state = fields.Selection([('new', 'New'), ('complete', 'Complete'), ('invoice', 'Invoice')], default='new',
                             tracking=True)
    doc_type = fields.Selection([('appointment', 'Appointment'), ('treatment', 'Treatment')], string='Type')
