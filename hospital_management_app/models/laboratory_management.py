# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LaboratoryManagement(models.Model):
    _name = 'laboratory.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Laboratory Management'

    # Identification Details

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string='Patient')
    disease_type_id = fields.Many2one('disease.type', string='Disease Type',
                                      tracking=True, required=True)
    disease_stage_id = fields.Many2one('disease.stage', string='Disease Stage',
                                       tracking=True)
    total_fees = fields.Float(string='Total Fees', store=True, compute='compute_total_fees',
                              tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Referring Doctor')
    state = fields.Selection([('draft', 'Draft'), ('process', 'In Process'), ('done', 'Done'), ('invoice', 'Invoice')],
                             default='draft',
                             tracking=True)
    lab_test_ids = fields.Many2many('lab.test.type', 'rel_laboratory_lab_test_type', 'lab_id', 'test_id',
                                    string='Test Type')
    type = fields.Selection(
        [('lab', 'Lab'), ('x_ray', 'X-Ray'), ('pathology', 'Pathology'), ('radiology', 'Radiology')], string='Type')
    x_ray_ids = fields.Many2many('x.ray.type', 'rel_laboratory_x_ray_type', 'lab_id', 'x_ray_id', string='X-Ray Type')
    pathology_ids = fields.Many2many('pathology.type', 'rel_laboratory_pathology_type', 'lab_id', 'pathology_ids',
                                     string='Pathology Type')
    radiology_ids = fields.Many2many('radiology.type', 'rel_laboratory_radiology_type', 'lab_id', 'radiology_ids',
                                     string='Radiology Type')
    line_ids = fields.One2many('laboratory.management.line', 'lab_id', string='Lines')
    report_description = fields.Html('Report Description')
    date = fields.Datetime(string='Date')


    @api.depends('line_ids', 'x_ray_ids', 'type', 'line_ids.fees', 'pathology_ids', 'radiology_ids')
    def compute_total_fees(self):
        total_fees = 0
        for rec in self:
            if rec.type == 'lab':
                for line in rec.line_ids:
                    total_fees += line.fees
            elif rec.type == 'x_ray':
                for line in rec.x_ray_ids:
                    total_fees += line.fees
            elif rec.type == 'pathology':
                for line in rec.pathology_ids:
                    total_fees += line.fees
            elif rec.type == 'radiology':
                for line in rec.radiology_ids:
                    total_fees += line.fees
            else:
                rec.total_fees = 0
            rec.total_fees = total_fees

    def action_process(self):
        for rec in self:
            rec.state = 'process'

    def action_done(self):
        for rec in self:
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

    @api.model
    def create(self, vals):
        if vals['type'] == 'lab':
            vals['name'] = self.env['ir.sequence'].next_by_code('laboratory.management') or 'New'
        elif vals['type'] == 'x_ray':
            vals['name'] = self.env['ir.sequence'].next_by_code('x.ray') or 'New'
        elif vals['type'] == 'pathology':
            vals['name'] = self.env['ir.sequence'].next_by_code('pathology') or 'New'
        elif vals['type'] == 'radiology':
            vals['name'] = self.env['ir.sequence'].next_by_code('radiology') or 'New'
        return super(LaboratoryManagement, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            rec.disease_type_id = rec.partner_id.disease_type_id
            rec.disease_stage_id = rec.partner_id.disease_stage_id


class LaboratoryManagementLine(models.Model):
    _name = 'laboratory.management.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'lab_test_id'
    _description = 'Laboratory Management Line'

    lab_id = fields.Many2one('laboratory.management', string='Laboratory')
    lab_test_id = fields.Many2one('lab.test.type', string='Test type')
    fees = fields.Float(string='Fees', tracking=True)
    min_range = fields.Float(string='Minimum Range', tracking=True)
    max_range = fields.Float(string='Maximum Range', tracking=True)
    uom_id = fields.Many2one('uom.uom', string='Unit')
    result = fields.Float(string='Result')

    @api.onchange('lab_test_id')
    def onchange_lab_test(self):
        for rec in self:
            rec.fees = rec.lab_test_id.fees
            rec.min_range = rec.lab_test_id.min_range
            rec.max_range = rec.lab_test_id.max_range
            rec.uom_id = rec.lab_test_id.uom_id
