# -*- coding: utf-8 -*-

from email.policy import strict
from odoo import _, api, fields, models, tools
from datetime import timedelta
from datetime import datetime
from odoo.exceptions import ValidationError
import calendar
import io
import xlwt
import base64
from odoo.exceptions import UserError
import uuid
import logging
_logger = logging.getLogger(__name__)
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

PAYMENT_STATE_SELECTION = [
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
]


class Partner(models.Model):
    _inherit = ["multi.company.abstract", "res.partner"]
    _name = 'res.partner'

    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
        index=True,
    )

    info_ids = fields.One2many(
        'res.partner.info', 'partner_id', string="More Info")
    reference = fields.Char('ID Number')
    name = fields.Char(index=True)

    is_practice = fields.Boolean('Practice')
    is_practitioner = fields.Boolean('Practitioner')
    
    practice_ids = fields.One2many(
        comodel_name='podiatry.practice',
        inverse_name='partner_id',
        string="Practices",
    )

    patient_ids = fields.One2many(
        comodel_name='podiatry.patient',
        inverse_name='partner_id',
        string="Patients",
    )

    patient_count = fields.Integer(
        string="Patient Count", store=False,
        compute='_compute_patient_count',
    )

    @api.depends('patient_ids')
    def _compute_patient_count(self):
        for partner in self:
            partner.patient_count = partner.patient_ids
        return

    is_patient = fields.Boolean(
        string="Patient", store=False,
        search='_search_is_patient',
    )

    def _search_is_patient(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('patient_ids', search_operator, False)]

    practitioner_id = fields.Many2one(
        "res.partner",
        string="Main Practitioner",
        domain=[("is_company", "=", False),
                ("practitioner_type", "=", "standalone")],
    )

    other_practitioner_ids = fields.One2many(
        "res.partner",
        "practitioner_id",
        string="Others Positions",
    )

    practitioner_count = fields.Integer(
        string="Practitioner Count", store=False,
        compute='_compute_practitioner_count',
    )

    @api.depends('practitioner_id')
    def _compute_practitioner_count(self):
        for partner in self:
            partner.practitioner_count = partner.practitioner_id
        return

    # is_practitioner = fields.Boolean(
    #     string="Practitioner", store=False,
    #     search='_search_is_practitioner',
    # )

    def _search_is_practitioner(self, operator, value):
        assert operator in ('=', '!=', '<>') and value in (
            True, False), 'Operation not supported'
        if (operator == '=' and value is True) or (operator in ('<>', '!=') and value is False):
            search_operator = '!='
        else:
            search_operator = '='
        return [('practitioner_id', search_operator, False)]

    practitioner_type = fields.Selection(
        [
            ("standalone", "Standalone Practitioner"),
            ("attached", "Attached to existing Practitioner"),
        ],
        compute="_compute_practitioner_type",
        store=True,
        index=True,
        default="standalone",
    )

    @api.depends("practitioner_id")
    def _compute_practitioner_type(self):
        for rec in self:
            rec.practitioner_type = "attached" if rec.practitioner_id else "standalone"

    def _base_practitioner_check_context(self, mode):
        """Remove "search_show_all_positions" for non-search mode.
        Keeping it in context can result in unexpected behaviour (ex: reading
        one2many might return wrong result - i.e with "attached practitioner"
        removed even if it"s directly linked to a company).
        Actually, is easier to override a dictionary value to indicate it
        should be ignored...
        """
        if mode != "search" and "search_show_all_positions" in self.env.context:
            result = self.with_context(
                search_show_all_positions={"is_set": False})
        else:
            result = self
        return result

    @api.model
    def create(self, vals):
        """When creating, use a modified self to alter the context (see
        comment in _base_practitioner_check_context).  Also, we need to ensure
        that the name on an attached practitioner is the same as the name on the
        practitioner it is attached to."""
        modified_self = self._base_practitioner_check_context("create")
        if not vals.get("name") and vals.get("practitioner_id"):
            vals["name"] = modified_self.browse(vals["practitioner_id"]).name
        vals = self._amend_company_id(vals)
        return super(Partner, modified_self).create(vals)

    def read(self, fields=None, load="_classic_read"):
        modified_self = self._base_practitioner_check_context("read")
        return super(Partner, modified_self).read(fields=fields, load=load)

    def write(self, vals):
        modified_self = self._base_practitioner_check_context("write")
        return super(Partner, modified_self).write(vals)

    def unlink(self):
        modified_self = self._base_practitioner_check_context("unlink")
        return super(Partner, modified_self).unlink()

    def _compute_commercial_partner(self):
        """Returns the partner that is considered the commercial
        entity of this partner. The commercial entity holds the master data
        for all commercial fields (see :py:meth:`~_commercial_fields`)"""
        result = super(Partner, self)._compute_commercial_partner()
        for partner in self:
            if partner.practitioner_type == "attached" and not partner.parent_id:
                partner.commercial_partner_id = partner.practitioner_id
        return result
    
    @api.model
    def _commercial_fields(self):
        """Add company_ids to the commercial fields that will be synced with
         childs. Ideal would be that this field is isolated from company field,
         but it involves a lot of development (default value, incoherences
         parent/child...).
        :return: List of field names to be synced.
        """
        fields = super(Partner, self)._commercial_fields()
        fields += ["company_ids"]
        return fields

    @api.model
    def _amend_company_id(self, vals):
        if "company_ids" in vals:
            if not vals["company_ids"]:
                vals["company_id"] = False
            else:
                for item in vals["company_ids"]:
                    if item[0] in (1, 4):
                        vals["company_id"] = item[1]
                    elif item[0] in (2, 3, 5):
                        vals["company_id"] = False
                    elif item[0] == 6:
                        if item[2]:
                            vals["company_id"] = item[2][0]
                        else:  # pragma: no cover
                            vals["company_id"] = False
        elif "company_id" not in vals:
            vals["company_ids"] = False
        return vals

    def _practitioner_fields(self):
        """Returns the list of practitioner fields that are synced from the parent
        when a partner is attached to him."""
        return ["name", "title"]

    def _practitioner_sync_from_parent(self):
        """Handle sync of practitioner fields when a new parent practitioner entity
        is set, as if they were related fields
        """
        self.ensure_one()
        if self.practitioner_id:
            practitioner_fields = self._practitioner_fields()
            sync_vals = self.practitioner_id._update_fields_values(
                practitioner_fields)
            self.write(sync_vals)

    def update_practitioner(self, vals):
        if self.env.context.get("__update_practitioner_lock"):
            return
        practitioner_fields = self._practitioner_fields()
        practitioner_vals = {field: vals[field]
                             for field in practitioner_fields if field in vals}
        if practitioner_vals:
            self.with_context(__update_practitioner_lock=True).write(
                practitioner_vals)

    def _fields_sync(self, update_values):
        """Sync commercial fields and address fields from company and to
        children, practitioner fields from practitioner and to attached practitioner
        after create/update, just as if those were all modeled as
        fields.related to the parent
        """
        self.ensure_one()
        super(Partner, self)._fields_sync(update_values)
        practitioner_fields = self._practitioner_fields()
        # 1. From UPSTREAM: sync from parent practitioner
        if update_values.get("practitioner_id"):
            self._practitioner_sync_from_parent()
        # 2. To DOWNSTREAM: sync practitioner fields to parent or related
        elif any(field in practitioner_fields for field in update_values):
            update_ids = self.other_practitioner_ids.filtered(
                lambda p: not p.is_company)
            if self.practitioner_id:
                update_ids |= self.practitioner_id
            update_ids.update_practitioner(update_values)

    @api.onchange("practitioner_id")
    def _onchange_practitioner_id(self):
        if self.practitioner_id:
            self.name = self.practitioner_id.name

    @api.onchange("practitioner_type")
    def _onchange_practitioner_type(self):
        if self.practitioner_type == "standalone":
            self.practitioner_id = False

    @api.model
    def create_partner_from_ui(self, partner, extraPartner):
        """ create or modify a partner from the point of sale ui.
            partner contains the partner's fields. """
        # image is a dataurl, get the data after the comma
        extraPartner_id = partner.pop('id', False)
        if extraPartner:
            if extraPartner.get('image_1920'):
                extraPartner['image_1920'] = extraPartner['image_1920'].split(',')[
                    1]
            if extraPartner_id:  # Modifying existing extraPartner
                custom_info = self.env['custom.partner.field'].search([])
                for i in custom_info:
                    if i.name in extraPartner.keys():
                        info_data = self.env['res.partner.info'].search(
                            [('partner_id', '=', extraPartner_id), ('name', '=', i.name)])
                        if info_data:
                            info_data.write(
                                {'info_name': extraPartner[i.name], 'partner_id': extraPartner_id})
                        else:
                            self.browse(extraPartner_id).write(
                                {'info_ids': [(0, 0, {'name': i.name, 'info_name': extraPartner[i.name]})]})
            else:
                extraPartner_id = self.create(extraPartner).id

        if partner:
            if partner.get('image_1920'):
                partner['image_1920'] = partner['image_1920'].split(',')[1]
            if extraPartner_id:  # Modifying existing partner

                self.browse(extraPartner_id).write(partner)
            else:
                extraPartner_id = self.create(partner).id
        return extraPartner_id

    @api.model
    def default_start_date(self):
        return datetime.now().date().replace(month=1, day=1)
    
    @api.model
    def default_end_date(self):
        return fields.Date.today()

    start_date = fields.Date('Start Date',default=default_start_date)
    end_date = fields.Date('End Date',default=default_end_date)
    date_filter = fields.Selection([
        ('this_month','This Month'),
        ('last_month','Last Month'),
        ('this_quarter','This Quarter'),
        ('last_quarter','Last Quarter'),
        ('this_year','This Year'),
        ('last_year','Last Year'),
        ('custom','Custom'),
    ])
    
    
    filter_customer_statement_ids = fields.One2many(
        'res.partner.filter.statement', 'partner_id', string='Customer Filtered Statements')
    customer_statement_ids = fields.One2many(
        'customer.statement', 'partner_id', string='Customer Statements')
    customer_zero_to_thiry = fields.Float('0-30')
    customer_thirty_to_sixty = fields.Float('30-60')
    customer_sixty_to_ninety = fields.Float('60-90')
    customer_ninety_plus = fields.Float('90+')
    customer_total = fields.Float('Total')
    dont_send_customer_statement_auto = fields.Boolean("Don't send statement auto ?")
    dont_send_due_customer_statement_auto = fields.Boolean(
        "Don't send Overdue statement auto ?")
    customer_due_statement_ids = fields.One2many(
        'customer.due.statement', 'partner_id', string='Customer Overdue Statements')
    customer_compute_boolean = fields.Boolean(
        'Boolean', compute='_compute_customer_statements')
    company_id = fields.Many2one('res.company', 'Company', index=True)
    # company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    cfs_statement_report_url = fields.Char(compute='_compute_cfs_report_url')
    cust_statement_report_url = fields.Char(compute='_compute_cust_report_url')
    cust_due_statement_report_url = fields.Char(compute='_compute_cust_due_report_url')
    report_token = fields.Char("Access Token")
    portal_statement_url_wp = fields.Char(compute='_compute_statement_portal_url_wp')

    customer_statement_config=fields.Many2many('customer.statement.config',string="Customer Statement Config",readonly=True)

    payment_state = fields.Selection(PAYMENT_STATE_SELECTION, string="Payment Status")

    def _compute_statement_portal_url_wp(self):
        for rec in self:
            rec.portal_statement_url_wp = False
            if rec.company_id.statement_url_in_message:
                base_url = self.env['ir.config_parameter'].sudo(
                ).get_param('web.base.url')
                ticket_url = ''
                if rec.customer_rank > 0:
                    ticket_url = base_url+'/my/customer_statements'
                rec.portal_statement_url_wp = ticket_url

    def _get_token(self):
        """ Get the current record access token """
        if self.report_token:
            return self.report_token
        else:
            report_token = str(uuid.uuid4())
            self.write({'report_token': report_token})
            return report_token

    def get_download_report_url(self):
        url = ''
        if self.id:
            self.ensure_one()
            url = '/download/cfs/' + '%s?access_token=%s' % (
                self.id,
                self._get_token()
            )
        return url
    
    def get_cust_statement_download_report_url(self):
        url = ''
        if self.id:
            self.ensure_one()
            url = '/download/cs/' + '%s?access_token=%s' % (
                self.id,
                self._get_token()
            )
        return url
    
    def get_cust_due_statement_download_report_url(self):
        url = ''
        if self.id:
            self.ensure_one()
            url = '/download/cds/' + '%s?access_token=%s' % (
                self.id,
                self._get_token()
            )
        return url
    
    def _compute_cfs_report_url(self):
        for rec in self:
            rec.cfs_statement_report_url = False
            if rec.company_id.statement_pdf_in_message:
                base_url = self.env['ir.config_parameter'].sudo(
                ).get_param('web.base.url')
                if rec.customer_rank > 0:
                    rec.cfs_statement_report_url = base_url+rec.get_download_report_url()
    
    def _compute_cust_report_url(self):
        for rec in self:
            rec.cust_statement_report_url = False
            if rec.company_id.statement_pdf_in_message:
                base_url = self.env['ir.config_parameter'].sudo(
                ).get_param('web.base.url')
                if rec.customer_rank > 0:
                    rec.cust_statement_report_url = base_url+rec.get_cust_statement_download_report_url()
    
    def _compute_cust_due_report_url(self):
        for rec in self:
            rec.cust_due_statement_report_url = False
            if rec.company_id.statement_pdf_in_message:
                base_url = self.env['ir.config_parameter'].sudo(
                ).get_param('web.base.url')
                if rec.customer_rank > 0:
                    rec.cust_due_statement_report_url = base_url+rec.get_cust_due_statement_download_report_url()
    
    def _get_cfs_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Customer Statement Filter By Date', self.name)
    
    def _get_cs_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Customer Statement', self.name)

    def _get_cds_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Customer Due/Overdue Statement', self.name)
    
    def action_send_filter_customer_whatsapp(self):
        self.ensure_one()
        if not self.mobile:
            raise UserError(_("Partner Mobile Number Not Exist !"))
        template = self.env.ref(
            'podiatry.send_customer_filter_whatsapp_email_template')
        ctx = {
            'default_model': 'res.partner',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_is_customer_statement': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    
    def action_send_customer_whatsapp(self):
        self.ensure_one()
        if not self.mobile:
            raise UserError(_("Partner Mobile Number Not Exist !"))
        template = self.env.ref(
            'podiatry.send_customer_whatsapp_email_template')
        ctx = {
            'default_model': 'res.partner',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_is_customer_statement': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    
    def action_send_due_customer_whatsapp(self):
        self.ensure_one()
        if not self.mobile:
            raise UserError(_("Partner Mobile Number Not Exist !"))
        template = self.env.ref(
            'podiatry.send_customer_due_whatsapp_email_template')
        ctx = {
            'default_model': 'res.partner',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_is_customer_statement': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def update_statement_config_manually_(self):
        view =self.env.ref('podiatry.update_customers_statement_config_wizard')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mass Update Config',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'res_model': 'customer.config.mass.update',
            'view_id':view.id,
            'target': 'new',
            'context':{'default_selected_partner_ids':self.ids},
        }

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.end_date and c.start_date > c.end_date):
            raise ValidationError(_('start date must be less than end date.'))

    def _compute_customer_statements(self):
        for rec in self:
            rec.customer_compute_boolean = False
            if rec.customer_rank > 0:
                rec.customer_statement_ids = False
                rec.customer_due_statement_ids = False
                moves = self.env['account.move'].sudo().search(
                    [('partner_id', '=', rec.id), ('move_type', 'in', ['out_invoice', 'out_refund']), ('state','not in',['draft','cancel'])])
                
                statement_lines = []
                if moves:
                    rec.customer_statement_ids.unlink()
                    
                    for move in moves:
                        statement_vals = {
                            'account': rec.property_account_receivable_id.name,
                            'name': move.name,
                            'currency_id': move.currency_id.id,
                            'customer_invoice_date': move.invoice_date,
                            'customer_due_date': move.invoice_date_due,
                        }
                        if move.move_type == 'out_invoice':
                            statement_vals.update({
                                'customer_amount': move.amount_total,
                                'customer_paid_amount': move.amount_total - move.amount_residual,
                                'customer_balance': move.amount_total - (move.amount_total - move.amount_residual),
                                })
                        elif move.move_type == 'out_refund':
                            statement_vals.update({
                                'customer_amount': move.amount_total - move.amount_residual,
                                'customer_paid_amount':  move.amount_total,
                                'customer_balance': (move.amount_total - move.amount_residual) - move.amount_total
                                })
                        statement_lines.append((0, 0, statement_vals))
                    rec.customer_zero_to_thiry = 0.0
                    rec.customer_thirty_to_sixty = 0.0
                    rec.customer_sixty_to_ninety = 0.0
                    rec.customer_ninety_plus = 0.0
                    today = fields.Date.today()
                    date_before_30 = today - timedelta(days=30)
                    date_before_60 = date_before_30 - timedelta(days=30)
                    date_before_90 = date_before_60 - timedelta(days=30)
                    moves_before_30_days = self.env['account.move'].sudo().search([
                        ('move_type', 'in', ['out_invoice', 'out_refund']),
                        ('partner_id', '=', rec.id),
                        ('invoice_date', '>=', date_before_30),
                        ('invoice_date', '<=', fields.Date.today()),
                        ('state','not in',['draft','cancel'])
                    ])

                    payments_before_30_days = self.env['account.payment'].sudo().search([
                        ('partner_id','=',rec.id),
                        ('state','in',['posted']),
                        ('date', '>=', date_before_30),
                        ('date', '<=', fields.Date.today()),
                        ('partner_type','in',['customer'])])

                    moves_before_60_days = self.env['account.move'].sudo().search([
                        ('move_type', 'in', ['out_invoice', 'out_refund']),
                        ('partner_id', '=', rec.id),
                        ('invoice_date', '>=', date_before_60),
                        ('invoice_date', '<', date_before_30),
                        ('state','not in',['draft','cancel'])
                    ])

                    payments_before_60_days = self.env['account.payment'].sudo().search([
                        ('partner_id','=',rec.id),
                        ('state','in',['posted']),
                        ('date', '>=', date_before_60),
                        ('date', '<', date_before_30),
                        ('partner_type','in',['customer'])])

                    moves_before_90_days = self.env['account.move'].sudo().search([
                        ('move_type', 'in', ['out_invoice', 'out_refund']),
                        ('partner_id', '=', rec.id),
                        ('invoice_date', '>=', date_before_90),
                        ('invoice_date', '<', date_before_60),
                        ('state','not in',['draft','cancel'])
                    ])

                    payments_before_90_days = self.env['account.payment'].sudo().search([
                        ('partner_id','=',rec.id),
                        ('state','in',['posted']),
                        ('date', '>=', date_before_90),
                        ('date', '<', date_before_60),
                        ('partner_type','in',['customer'])])

                    moves_90_plus = self.env['account.move'].sudo().search([
                        ('move_type', 'in', ['out_invoice', 'out_refund']),
                        ('partner_id', '=', rec.id),
                        ('invoice_date', '<', date_before_90),
                        ('state','not in',['draft','cancel'])
                    ])

                    payments_90_plus = self.env['account.payment'].sudo().search([
                        ('partner_id','=',rec.id),
                        ('state','in',['posted']),
                        ('date', '<', date_before_90),
                        ('partner_type','in',['customer'])])

                    if moves_before_30_days or payments_before_30_days:
                        total_paid = 0.0
                        total_amount = 0.0
                        total_balance = 0.0
                        for move_before_30 in moves_before_30_days:
                            if move_before_30.move_type == 'out_invoice':
                                total_amount += move_before_30.amount_total
                                # total_paid += move_before_30.amount_total - move_before_30.amount_residual
                            elif move_before_30.move_type == 'out_refund':
                                total_paid += (move_before_30.amount_total)
                                # total_paid += -(move_before_30.amount_total - move_before_30.amount_residual)
                        
                        for payments_before_30_day in payments_before_30_days:
                            if payments_before_30_day.payment_type == 'inbound':
                                total_paid = total_paid + payments_before_30_day.amount
                            else:
                                total_amount = total_amount + payments_before_30_day.amount

                        total_balance = total_amount - total_paid
                        rec.customer_zero_to_thiry = total_balance
                    if moves_before_60_days or payments_before_60_days:
                        total_paid = 0.0
                        total_amount = 0.0
                        total_balance = 0.0
                        for move_before_60 in moves_before_60_days:
                            if move_before_60.move_type == 'out_invoice':
                                total_amount += move_before_60.amount_total
                                # total_paid += move_before_60.amount_total - move_before_60.amount_residual
                            elif move_before_60.move_type == 'out_refund':
                                total_paid += (move_before_60.amount_total)
                                # total_paid += -(move_before_60.amount_total - move_before_60.amount_residual)

                        for payments_before_60_day in payments_before_60_days:
                            if payments_before_60_day.payment_type == 'inbound':
                                total_paid = total_paid + payments_before_60_day.amount
                            else:
                                total_amount = total_amount + payments_before_60_day.amount
                        
                        total_balance = total_amount - total_paid
                        total_balance = total_amount - total_paid
                        rec.customer_thirty_to_sixty = total_balance
                    if moves_before_90_days or payments_before_90_days:
                        total_paid = 0.0
                        total_amount = 0.0
                        total_balance = 0.0
                        for move_before_90 in moves_before_90_days:
                            if move_before_90.move_type == 'out_invoice':
                                total_amount += move_before_90.amount_total
                                # total_paid += move_before_90.amount_total - move_before_90.amount_residual
                            elif move_before_90.move_type == 'out_refund':
                                total_paid += (move_before_90.amount_total)
                                # total_paid += -(move_before_90.amount_total - move_before_90.amount_residual)
                        
                        for payments_before_90_day in payments_before_90_days:
                            if payments_before_90_day.payment_type == 'inbound':
                                total_paid = total_paid + payments_before_90_day.amount
                            else:
                                total_amount = total_amount + payments_before_90_day.amount

                        total_balance = total_amount - total_paid
                        rec.customer_sixty_to_ninety = total_balance

                    if moves_90_plus or payments_90_plus:
                        total_paid = 0.0
                        total_amount = 0.0
                        total_balance = 0.0
                        for move_90_plus in moves_90_plus:
                            if move_90_plus.move_type == 'out_invoice':
                                total_amount += move_90_plus.amount_total
                                # total_paid += move_90_plus.amount_total - move_90_plus.amount_residual
                            elif move_90_plus.move_type == 'out_refund':
                                total_paid += (move_90_plus.amount_total)
                                # total_paid += -(move_90_plus.amount_total - move_90_plus.amount_residual)

                        for payment_90_plus in payments_90_plus:
                            if payment_90_plus.payment_type == 'inbound':
                                total_paid = total_paid + payment_90_plus.amount
                            else:
                                total_amount = total_amount + payment_90_plus.amount
                            
                        total_balance = total_amount - total_paid
                        rec.customer_ninety_plus = total_balance
                    rec.customer_total = rec.customer_zero_to_thiry + rec.customer_thirty_to_sixty + \
                        rec.customer_sixty_to_ninety + rec.customer_ninety_plus
                
                advanced_payments_inbound = self.env['account.payment'].sudo().search([
                        ('partner_id','=',rec.id),
                        ('state','in',['posted']),
                        ('payment_type','in',['inbound']),
                        ('partner_type','in',['customer'])
                    ])
                if advanced_payments_inbound:
                    for advance_payment in advanced_payments_inbound:
                        total_paid_amount = 0.0
                        if advance_payment.reconciled_invoice_ids:
                            advance_payment_amount = advance_payment.amount
                            for invoice in advance_payment.reconciled_invoice_ids:
                                total_paid_amount+=(invoice.amount_total - invoice.amount_residual)
                            if total_paid_amount < advance_payment_amount:
                                statement_vals = {
                                    'account':
                                    advance_payment.destination_account_id.name,
                                    'name': advance_payment.name,
                                    'currency_id': advance_payment.currency_id.id,
                                    'customer_invoice_date': advance_payment.date,
                                    'customer_amount': 0.0,
                                    'customer_paid_amount': advance_payment.amount - total_paid_amount,
                                    'customer_balance': -(advance_payment.amount - total_paid_amount),
                                }
                                statement_lines.append((0, 0, statement_vals))
                        else:
                            statement_vals = {
                                'account':
                                advance_payment.destination_account_id.name,
                                'name': advance_payment.name,
                                'currency_id': advance_payment.currency_id.id,
                                'customer_invoice_date': advance_payment.date,
                                'customer_amount': 0.0,
                                'customer_paid_amount': advance_payment.amount,
                                'customer_balance': -(advance_payment.amount),
                            }
                            statement_lines.append((0, 0, statement_vals))


                advanced_payments_outbound = self.env['account.payment'].sudo().search([
                    ('partner_id','=',rec.id),
                    ('state','in',['posted']),
                    ('payment_type','in',['outbound']),
                    ('partner_type','in',['customer'])
                ])
                if advanced_payments_outbound:
                    for advance_payment in advanced_payments_outbound:
                        total_paid_amount = 0.0
                        if advance_payment.reconciled_invoice_ids:
                            advance_payment_amount = advance_payment.amount
                            for invoice in advance_payment.reconciled_invoice_ids:
                                total_paid_amount+=(invoice.amount_total - invoice.amount_residual)
                            if total_paid_amount < advance_payment_amount:
                                statement_vals = {
                                    'account':
                                    advance_payment.destination_account_id.name,
                                    'name': advance_payment.name,
                                    'currency_id': advance_payment.currency_id.id,
                                    'customer_invoice_date': advance_payment.date,
                                    'customer_amount': advance_payment.amount - total_paid_amount,
                                    'customer_paid_amount': 0.0,
                                    'customer_balance': advance_payment.amount - total_paid_amount,
                                }
                                statement_lines.append((0, 0, statement_vals))
                        else:
                            statement_vals = {
                                'account':
                                advance_payment.destination_account_id.name,
                                'name': advance_payment.name,
                                'currency_id': advance_payment.currency_id.id,
                                'customer_invoice_date': advance_payment.date,
                                'customer_amount': advance_payment.amount,
                                'customer_paid_amount': 0.0,
                                'customer_balance': advance_payment.amount,
                            }
                            statement_lines.append((0, 0, statement_vals))
                
                rec.customer_statement_ids = statement_lines

                overdue_moves = False
                if self.env.company.display_due_statement == 'due':
                    overdue_moves = moves.filtered(
                        lambda x: x.invoice_date_due and x.invoice_date_due >= fields.Date.today() and x.amount_residual > 0.00)
                elif self.env.company.display_due_statement == 'overdue':
                    overdue_moves = moves.filtered(
                        lambda x: x.invoice_date_due and x.invoice_date_due < fields.Date.today() and x.amount_residual > 0.00)
                elif self.env.company.display_due_statement == 'both':
                    overdue_moves = moves.filtered(
                        lambda x: x.amount_residual > 0.00)
                if overdue_moves:
                    rec.customer_due_statement_ids.unlink()
                    overdue_statement_lines = []
                    for overdue in overdue_moves:
                        overdue_statement_vals = {
                            'account': rec.property_account_receivable_id.name,
                            'currency_id': overdue.currency_id.id,
                            'name': overdue.name,
                            'today': fields.Date.today(),
                            'due_customer_invoice_date': overdue.invoice_date,
                            'due_customer_due_date': overdue.invoice_date_due,
                        }
                        if overdue.move_type == 'out_invoice':
                            overdue_statement_vals.update({
                                'due_customer_amount': overdue.amount_total,
                                'due_customer_paid_amount': overdue.amount_total - overdue.amount_residual,
                                'due_customer_balance': overdue.amount_total - (overdue.amount_total - overdue.amount_residual),
                            })
                        elif overdue.move_type == 'out_refund':
                            overdue_statement_vals.update({
                                'due_customer_amount': (overdue.amount_total - overdue.amount_residual),
                                'due_customer_paid_amount': overdue.amount_total,
                                'due_customer_balance': (overdue.amount_total - overdue.amount_residual) - overdue.amount_total,
                            })
                        overdue_statement_lines.append(
                            (0, 0, overdue_statement_vals))

                    rec.customer_due_statement_ids = overdue_statement_lines

    def send_customer_statement(self):
        for rec in self:
            if rec.customer_rank > 0 and rec.customer_statement_ids:
                template = self.env.ref(
                    'podiatry.customer_statement_mail_template')
                if template:
                    mail = template.sudo().send_mail(rec.id, force_send=True)
                    mail_id = self.env['mail.mail'].sudo().browse(mail)
                    if mail_id:
                        self.env['customer.mail.history'].sudo().create({
                            'name': 'Customer Account Statement',
                            'statement_type': 'customer_statement',
                            'current_date': fields.Datetime.now(),
                            'partner_id': rec.id,
                            'mail_id': mail_id.id,
                            'mail_status': mail_id.state,
                        })

    def send_customer_overdue_statement(self):
        for rec in self:
            if rec.customer_rank > 0 and rec.customer_due_statement_ids:
                template = self.env.ref(
                    'podiatry.customer_due_statement_mail_template')
                if template:
                    mail = template.sudo().send_mail(rec.id, force_send=True)
                    mail_id = self.env['mail.mail'].sudo().browse(mail)
                    if mail_id:
                        self.env['customer.mail.history'].sudo().create({
                            'name': 'Customer Account Overdue Statement',
                            'statement_type': 'customer_overdue_statement',
                            'current_date': fields.Datetime.now(),
                            'partner_id': rec.id,
                            'mail_id': mail_id.id,
                            'mail_status': mail_id.state,
                        })

    def action_print_customer_statement(self):
        return self.env.ref('podiatry.action_report_customer_statement').report_action(self)

    def action_send_customer_statement(self):
        self.ensure_one()
        template = self.env.ref(
            'podiatry.customer_statement_mail_template')
        if template:
            mail = template.sudo().send_mail(self.id, force_send=True)
            mail_id = self.env['mail.mail'].sudo().browse(mail)
            if mail_id:
                self.env['customer.mail.history'].sudo().create({
                    'name': 'Customer Account Statement',
                    'statement_type': 'customer_statement',
                    'current_date': fields.Datetime.now(),
                    'partner_id': self.id,
                    'mail_id': mail_id.id,
                    'mail_status': mail_id.state,
                })

    def action_print_customer_due_statement(self):
        return self.env.ref('podiatry.action_report_customer_due_statement').report_action(self)

    def action_send_customer_due_statement(self):
        self.ensure_one()
        template = self.env.ref(
            'podiatry.customer_due_statement_mail_template')
        if template:
            mail = template.sudo().send_mail(self.id, force_send=True)
            mail_id = self.env['mail.mail'].sudo().browse(mail)
            if mail_id:
                self.env['customer.mail.history'].sudo().create({
                    'name': 'Customer Account Overdue Statement',
                    'statement_type': 'customer_overdue_statement',
                    'current_date': fields.Datetime.now(),
                    'partner_id': self.id,
                    'mail_id': mail_id.id,
                    'mail_status': mail_id.state,
                })

    def action_get_customer_statement(self):
        self.ensure_one()
        today = date.today()
        currQuarter = int((today.month - 1) / 3 + 1)

        if self.date_filter == 'this_month':
            self.start_date = date(today.year, today.month, 1)
            self.end_date  = date(
                today.year, today.month, calendar.mdays[today.month])

        if self.date_filter == 'this_year':
            self.start_date = date(today.year, 1, 1)
            self.end_date = date(today.year, 12, 31)

        if self.date_filter == 'last_month': 
            self.start_date = date(today.year, (today.month-1), 1)
            self.end_date = date(
                today.year, (today.month - 1), calendar.mdays[(today.month-1)])

        if self.date_filter == 'last_year':
            self.start_date = date((today.year-1), 1, 1)
            self.end_date = date((today.year-1), 12, 31)

        if self.date_filter == 'this_quarter':
            self.start_date = datetime(today.year, 3 * currQuarter - 2, 1)
            self.end_date = datetime(today.year, 3 * currQuarter + 1, 1) + timedelta(days=-1)
        
        if self.date_filter == 'last_quarter':

            current_quar_start = datetime(today.year, 3 * currQuarter - 2, 1)

            self.start_date = datetime(today.year, current_quar_start.month, 1) + relativedelta(months=-3)
            self.end_date = current_quar_start + timedelta(days=-1)
            
        if self.customer_rank > 0 and self.start_date and self.end_date:
            
            self.filter_customer_statement_ids.unlink()
            statement_lines = []

            #########
            account_id =  self.property_account_receivable_id.id

            move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', self.id),
                ('date', '<', self.start_date),
                ('account_id','=',account_id),
                ('parent_state','=','posted'),
            ])
            
            balance = sum(move_lines.mapped('debit')) - sum(move_lines.mapped('credit'))
            
            statement_lines.append((0,0,{
                'name' : 'Opening Balance',
                'currency_id': move_lines[0].currency_id.id if move_lines else self.currency_id.id,
                'filter_balance':balance
            }))
            #########


            moves = self.env['account.move'].sudo().search([('partner_id', '=', self.id), ('move_type', 'in', [
                'out_invoice', 'out_refund']), ('invoice_date', '>=', self.start_date), ('invoice_date', '<=', self.end_date),('state','not in',['draft','cancel']),('payment_state','=',self.payment_state)])
            if moves:
                
                for move in moves:
                    statement_vals = {
                        'account': self.property_account_receivable_id.name,
                        'name': move.name,
                        'currency_id': move.currency_id.id,
                        'filter_invoice_date': move.invoice_date,
                        'filter_due_date': move.invoice_date_due,
                    }
                    if move.move_type == 'out_invoice':
                        statement_vals.update({
                            'filter_amount': move.amount_total,
                            'filter_paid_amount': move.amount_total - move.amount_residual,
                            'filter_balance': move.amount_total - (move.amount_total - move.amount_residual)
                        })
                    elif move.move_type == 'out_refund':
                        statement_vals.update({
                            'filter_amount': move.amount_total - move.amount_residual,
                            'filter_paid_amount': move.amount_total,
                            'filter_balance': (move.amount_total - move.amount_residual) - move.amount_total
                        })
                    statement_lines.append((0, 0, statement_vals))

            advanced_payments_inbound = self.env['account.payment'].sudo().search([
                    ('partner_id','=',self.id),
                    ('date', '>=', self.start_date),
                    ('date', '<=', self.end_date),
                    ('state','in',['posted']),
                    ('payment_type','in',['inbound']),
                    ('partner_type','in',['customer'])
                ])
            if advanced_payments_inbound:
                for advance_payment in advanced_payments_inbound:
                    total_paid_amount = 0.0
                    if advance_payment.reconciled_invoice_ids:
                        advance_payment_amount = advance_payment.amount
                        for invoice in advance_payment.reconciled_invoice_ids: 

                            if invoice.invoice_date >= self.start_date and invoice.invoice_date <= self.end_date:
                                
                                total_paid_amount+= (invoice.amount_total - invoice.amount_residual)

                        if total_paid_amount < advance_payment_amount:
                            statement_vals = {
                                'account':
                                advance_payment.destination_account_id.name,
                                'name': advance_payment.name,
                                'currency_id': advance_payment.currency_id.id,
                                'filter_invoice_date': advance_payment.date,
                                'filter_amount': 0.0,
                                'filter_paid_amount': advance_payment.amount - total_paid_amount,
                                'filter_balance': -(advance_payment.amount - total_paid_amount),
                            }
                            statement_lines.append((0, 0, statement_vals))
                    else:
                        statement_vals = {
                            'account':
                            advance_payment.destination_account_id.name,
                            'name': advance_payment.name,
                            'currency_id': advance_payment.currency_id.id,
                            'filter_invoice_date': advance_payment.date,
                            'filter_amount': 0.0,
                            'filter_paid_amount': advance_payment.amount,
                            'filter_balance': -(advance_payment.amount),
                        }
                        statement_lines.append((0, 0, statement_vals))
            
            advanced_payments_outbound = self.env['account.payment'].sudo().search([
                        ('partner_id','=',self.id),
                        ('date', '>=', self.start_date),
                        ('date', '<=', self.end_date),
                        ('state','in',['posted']),
                        ('payment_type','in',['outbound']),
                        ('partner_type','in',['customer'])
                    ])
            if advanced_payments_outbound:
                for advance_payment in advanced_payments_outbound:
                    total_paid_amount = 0.0
                    if advance_payment.reconciled_invoice_ids:
                        advance_payment_amount = advance_payment.amount
                        for invoice in advance_payment.reconciled_invoice_ids: 

                            if invoice.invoice_date >= self.start_date and invoice.invoice_date <= self.end_date:
                                
                                total_paid_amount+= (invoice.amount_total - invoice.amount_residual)

                        if total_paid_amount < advance_payment_amount:
                            statement_vals = {
                                'account':
                                advance_payment.destination_account_id.name,
                                'name': advance_payment.name,
                                'currency_id': advance_payment.currency_id.id,
                                'filter_invoice_date': advance_payment.date,
                                'filter_amount': advance_payment.amount - total_paid_amount,
                                'filter_paid_amount': 0.0,
                                'filter_balance': advance_payment.amount - total_paid_amount,
                            }
                            statement_lines.append((0, 0, statement_vals))
                    else:
                        statement_vals = {
                            'account':
                            advance_payment.destination_account_id.name,
                            'name': advance_payment.name,
                            'currency_id': advance_payment.currency_id.id,
                            'filter_invoice_date': advance_payment.date,
                            'filter_amount': advance_payment.amount,
                            'filter_paid_amount': 0.0,
                            'filter_balance': advance_payment.amount,
                        }
                        statement_lines.append((0, 0, statement_vals))

            self.filter_customer_statement_ids = statement_lines

    def action_print_filter_customer_statement(self):
        return self.env.ref('podiatry.action_report_customer_filtered_statement').report_action(self)

    def action_send_filter_customer_statement(self):
        self.ensure_one()
        template = self.env.ref(
            'podiatry.customer_filter_statement_mail_template')
        if template:
            mail = template.sudo().send_mail(self.id, force_send=True)
            mail_id = self.env['mail.mail'].sudo().browse(mail)
            if mail_id:
                self.env['customer.mail.history'].sudo().create({
                    'name': 'Customer Account Statement by Date',
                    'statement_type': 'customer_statement_filter',
                    'current_date': fields.Datetime.now(),
                    'partner_id': self.id,
                    'mail_id': mail_id.id,
                    'mail_status': mail_id.state,
                })

    def action_view_customer_history(self):
        self.ensure_one()
        return{
            'name': 'Mail Log History',
            'type': 'ir.actions.act_window',
            'res_model': 'customer.mail.history',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'target': 'current',
        }
    
    def action_print_filter_customer_statement_xls(self):
        workbook = xlwt.Workbook()
        heading_format = xlwt.easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;align: vert center;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        normal = xlwt.easyxf(
            'font:bold True;align: horiz center;align: vert center')
        cyan_text = xlwt.easyxf(
            'font:bold True,color aqua;align: horiz center;align: vert center')
        green_text = xlwt.easyxf(
            'font:bold True,color green;align: horiz center;align: vert center'
        )
        red_text = xlwt.easyxf(
            'font:bold True,color red;align: horiz center;align: vert center')
        bold_center = xlwt.easyxf(
            'font:height 225,bold True;pattern: pattern solid,fore_colour gray25;align: horiz center;align: vert center;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        date = xlwt.easyxf(
            'font:height 225,bold True;pattern: pattern solid,fore_colour gray25;align: vert center;align: horiz right;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        totals = xlwt.easyxf(
            'font:height 225,bold True;pattern: pattern solid,fore_colour gray25;align: horiz center;align: vert center;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        worksheet = workbook.add_sheet(u'Customer Statement Filter By Date',
                                       cell_overwrite_ok=True)

        worksheet.row(1).height = 380
        worksheet.row(2).height = 320
        worksheet.row(8).height = 400
        worksheet.col(2).width = 4800
        worksheet.col(3).width = 4800
        worksheet.col(4).width = 5500
        worksheet.col(5).width = 5500
        worksheet.col(6).width = 5500
        worksheet.col(0).width = 5500
        worksheet.col(1).width = 6000
        worksheet.write(1, 0, "Date From", date)
        if self.start_date:
            worksheet.write(1, 1, str(self.start_date), normal)
        worksheet.write(1, 2, "Date To", date)
        if self.end_date:
            worksheet.write(1, 3, str(self.end_date), normal)
        worksheet.write_merge(4, 5, 0, 6, self.name, heading_format)
        worksheet.write(8, 0, "Number", bold_center)
        worksheet.write(8, 1, "Account", bold_center)
        worksheet.write(8, 2, "Date", bold_center)
        worksheet.write(8, 3, "Due Date", bold_center)
        worksheet.write(8, 4, "Total Amount", bold_center)
        worksheet.write(8, 5, "Paid Amount", bold_center)
        worksheet.write(8, 6, "Balance", bold_center)

        total_amount = 0
        total_paid_amount = 0
        total_balance = 0
        k = 9

        if self.filter_customer_statement_ids:
            for i in self.filter_customer_statement_ids:
                for j in i:
                    worksheet.row(k).height = 350
                    if j.filter_amount == j.filter_balance:
                        worksheet.write(k, 0, j.name, cyan_text)
                        worksheet.write(k, 1, j.account, cyan_text)
                        worksheet.write(k, 2, str(j.filter_invoice_date),
                                        cyan_text)
                        if j.filter_due_date:
                            worksheet.write(k, 3, str(j.filter_due_date),
                                            cyan_text)
                        else:
                            worksheet.write(k, 3, '',
                                            cyan_text)
                        worksheet.write(
                            k, 4,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_amount)), cyan_text)
                        worksheet.write(
                            k, 5,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_paid_amount)), cyan_text)
                        worksheet.write(
                            k, 6,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_balance)), cyan_text)
                    elif j.filter_balance == 0:
                        worksheet.write(k, 0, j.name, green_text)
                        worksheet.write(k, 1, j.account, green_text)
                        worksheet.write(k, 2, str(j.filter_invoice_date),
                                        green_text)
                        if j.filter_due_date:
                            worksheet.write(k, 3, str(j.filter_due_date),
                                            green_text)
                        else:
                            worksheet.write(k, 3, '',
                                            green_text)
                        worksheet.write(
                            k, 4,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_amount)), green_text)
                        worksheet.write(
                            k, 5,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_paid_amount)), green_text)
                        worksheet.write(
                            k, 6,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_balance)), green_text)
                    else:
                        worksheet.write(k, 0, j.name, red_text)
                        worksheet.write(k, 1, j.account, red_text)
                        worksheet.write(k, 2, str(j.filter_invoice_date),
                                        red_text)
                        if j.filter_due_date:
                            worksheet.write(k, 3, str(j.filter_due_date),
                                            red_text)
                        else:
                            worksheet.write(k, 3, '',
                                            red_text)
                        worksheet.write(
                            k, 4,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_amount)), red_text)
                        worksheet.write(
                            k, 5,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_paid_amount)), red_text)
                        worksheet.write(
                            k, 6,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.filter_balance)), red_text)
                    k = k + 1
                total_amount = total_amount + j.filter_amount
                total_paid_amount = total_paid_amount + j.filter_paid_amount
                total_balance = total_balance + j.filter_balance
        if self.filter_customer_statement_ids:
            worksheet.write(k, 4,
                            str("{:.2f}".format(total_amount)),
                            totals)
            worksheet.row(k).height = 350
            worksheet.write(k, 5,
                            str("{:.2f}".format(total_paid_amount)),
                            totals)
            worksheet.write(k, 6,
                            str("{:.2f}".format(total_balance)),
                            totals)

        fp = io.BytesIO()
        workbook.save(fp)
        data = base64.encodestring(fp.getvalue())
        IrAttachment = self.env['ir.attachment']
        attachment_vals = {
            "name": "Customer Statement Filter By Date.xls",
            "res_model": "ir.ui.view",
            "type": "binary",
            "datas": data,
            "public": True,
        }
        fp.close()

        attachment = IrAttachment.search(
            [('name', '=', 'Customer Statement Filter By Date'),
             ('type', '=', 'binary'), ('res_model', '=', 'ir.ui.view')],
            limit=1)
        if attachment:
            attachment.write(attachment_vals)
        else:
            attachment = IrAttachment.create(attachment_vals)
        #TODO: make user error here
        if not attachment:
            raise UserError('There is no attachments...')

        url = "/web/content/" + str(attachment.id) + "?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'current',
        }
    
    def action_print_customer_statement_xls(self):
        workbook = xlwt.Workbook()
        heading_format = xlwt.easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;align: vert center;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        normal = xlwt.easyxf(
            'font:bold True;align: horiz center;align: vert center')
        cyan_text = xlwt.easyxf(
            'font:bold True,color aqua;align: horiz center;align: vert center')
        green_text = xlwt.easyxf(
            'font:bold True,color green;align: horiz center;align: vert center'
        )
        red_text = xlwt.easyxf(
            'font:bold True,color red;align: horiz center;align: vert center')
        bold_center = xlwt.easyxf(
            'font:height 225,bold True;pattern: pattern solid,fore_colour gray25;align: horiz center;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        totals = xlwt.easyxf(
            'font:height 225,bold True;pattern: pattern solid,fore_colour gray25;align: horiz center;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        worksheet = workbook.add_sheet(u'Customer Statement',
                                       cell_overwrite_ok=True)

        worksheet.row(5).height = 400
        worksheet.row(12).height = 400
        worksheet.row(13).height = 400
        worksheet.row(10).height = 350
        worksheet.row(11).height = 350
        worksheet.col(2).width = 4800
        worksheet.col(3).width = 4800
        worksheet.col(4).width = 5500
        worksheet.col(5).width = 5500
        worksheet.col(6).width = 5500
        worksheet.col(0).width = 5500
        worksheet.col(1).width = 6000
        worksheet.write_merge(2, 3, 0, 6, self.name, heading_format)
        worksheet.write(5, 0, "Number", bold_center)
        worksheet.write(5, 1, "Account", bold_center)
        worksheet.write(5, 2, "Date", bold_center)
        worksheet.write(5, 3, "Due Date", bold_center)
        worksheet.write(5, 4, "Total Amount", bold_center)
        worksheet.write(5, 5, "Paid Amount", bold_center)
        worksheet.write(5, 6, "Balance", bold_center)

        total_amount = 0
        total_paid_amount = 0
        total_balance = 0
        k = 6

        if self.customer_statement_ids:
            for i in self.customer_statement_ids:
                for j in i:
                    worksheet.row(k).height = 350
                    if j.customer_amount == j.customer_balance:
                        worksheet.write(k, 0, j.name, cyan_text)
                        worksheet.write(k, 1, j.account, cyan_text)
                        worksheet.write(k, 2, str(j.customer_invoice_date),
                                        cyan_text)
                        if j.customer_due_date:
                            worksheet.write(k, 3, str(j.customer_due_date),
                                            cyan_text)
                        else:
                            worksheet.write(k, 3, '',
                                            cyan_text)
                        worksheet.write(
                            k, 4,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_amount)), cyan_text)
                        worksheet.write(
                            k, 5,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_paid_amount)), cyan_text)
                        worksheet.write(
                            k, 6,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_balance)), cyan_text)
                    elif j.customer_balance == 0:
                        worksheet.write(k, 0, j.name, green_text)
                        worksheet.write(k, 1, j.account, green_text)
                        worksheet.write(k, 2, str(j.customer_invoice_date),
                                        green_text)
                        if j.customer_due_date:
                            worksheet.write(k, 3, str(j.customer_due_date),
                                            green_text)
                        else:
                            worksheet.write(k, 3, '',
                                            green_text)
                        worksheet.write(
                            k, 4,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_amount)), green_text)
                        worksheet.write(
                            k, 5,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_paid_amount)), green_text)
                        worksheet.write(
                            k, 6,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_balance)), green_text)
                    else:
                        worksheet.write(k, 0, j.name, red_text)
                        worksheet.write(k, 1, j.account, red_text)
                        worksheet.write(k, 2, str(j.customer_invoice_date),
                                        red_text)
                        if j.customer_due_date:
                            worksheet.write(k, 3, str(j.customer_due_date),
                                            red_text)
                        else:
                            worksheet.write(k, 3, '',
                                            red_text)
                        worksheet.write(
                            k, 4,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_amount)), red_text)
                        worksheet.write(
                            k, 5,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_paid_amount)), red_text)
                        worksheet.write(
                            k, 6,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.customer_balance)), red_text)
                    k = k + 1
                total_amount = total_amount + float("{:.2f}".format(j.customer_amount))
                total_paid_amount = total_paid_amount + float("{:.2f}".format(j.customer_paid_amount))
                total_balance = total_balance + j.customer_balance

        if self.customer_statement_ids:
            worksheet.write(k, 4,
                            str("{:.2f}".format(total_amount)),
                            totals)
            worksheet.row(k).height = 350
            worksheet.write(k, 5,
                            str("{:.2f}".format(total_paid_amount)),
                            totals)
            worksheet.write(k, 6,
                            str("{:.2f}".format(total_balance)),
                            totals)
        worksheet.write(k + 3, 0, 'Gap Between Days', bold_center)
        worksheet.write(k + 3, 1, '0-30(Days)', bold_center)
        worksheet.write(k + 3, 2, '30-60(Days)', bold_center)
        worksheet.write(k + 3, 3, '60-90(Days)', bold_center)
        worksheet.write(k + 3, 4, '90+(Days)', bold_center)
        worksheet.write(k + 3, 5, 'Total', bold_center)
        worksheet.write(k + 4, 0, 'Balance Amount', bold_center)
        if self.customer_statement_ids:
            worksheet.write(
                k + 4, 1,
                str("{:.2f}".format(self.customer_zero_to_thiry)), normal)
            worksheet.write(
                k + 4, 2,
                str("{:.2f}".format(self.customer_thirty_to_sixty)), normal)
            worksheet.write(
                k + 4, 3,
                str("{:.2f}".format(self.customer_sixty_to_ninety)), normal)
            worksheet.write(
                k + 4, 4,
                str("{:.2f}".format(self.customer_ninety_plus)),
                normal)
            worksheet.write(
                k + 4, 5,
                str("{:.2f}".format(self.customer_total)),
                normal)

        fp = io.BytesIO()
        workbook.save(fp)
        data = base64.encodestring(fp.getvalue())
        IrAttachment = self.env['ir.attachment']
        attachment_vals = {
            "name": "Customer Statement.xls",
            "res_model": "ir.ui.view",
            "type": "binary",
            "datas": data,
            "public": True,
        }
        fp.close()

        attachment = IrAttachment.search([('name', '=', 'Customer Statement'),
                                          ('type', '=', 'binary'),
                                          ('res_model', '=', 'ir.ui.view')],
                                         limit=1)
        if attachment:
            attachment.write(attachment_vals)
        else:
            attachment = IrAttachment.create(attachment_vals)
        #TODO: make user error here
        if not attachment:
            raise UserError('There is no attachments...')

        url = "/web/content/" + str(attachment.id) + "?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'current',
        }
    
    def action_print_customer_due_statement_xls(self):
        workbook = xlwt.Workbook()
        heading_format = xlwt.easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;align: vert center;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        red_text = xlwt.easyxf(
            'font:bold True,color red;align: horiz center;align: vert center')
        center_text = xlwt.easyxf(
            'align: horiz center;align: vert center')
        bold_center = xlwt.easyxf(
            'font:height 225,bold True;pattern: pattern solid,fore_colour gray25;align: horiz center;align: vert center;borders: left thin, right thin, bottom thin,top thin,top_color gray40,bottom_color gray40,left_color gray40,right_color gray40'
        )
        date = xlwt.easyxf(
            'font:height 225,bold True;pattern: pattern solid,fore_colour gray25;align: horiz center;borders: left thin, right thin, bottom thin;align: vert center;align: horiz left'
        )
        worksheet = workbook.add_sheet(u'Customer Overdue Statement',
                                       cell_overwrite_ok=True)

        now = datetime.now()
        today_date = now.strftime("%d/%m/%Y %H:%M:%S")

        worksheet.write(1, 0, str(str("Date") + str(": ") + str(today_date)),
                        date)
        worksheet.row(1).height = 350
        worksheet.row(6).height = 350
        worksheet.col(0).width = 8000
        worksheet.col(1).width = 6000
        worksheet.col(2).width = 4800
        worksheet.col(3).width = 4800
        worksheet.col(4).width = 5500
        worksheet.col(5).width = 5500
        worksheet.col(6).width = 5500
        worksheet.row(11).height = 350

        worksheet.write_merge(3, 4, 0, 6, self.name, heading_format)
        worksheet.write(6, 0, "Number", bold_center)
        worksheet.write(6, 1, "Account", bold_center)
        worksheet.write(6, 2, "Date", bold_center)
        worksheet.write(6, 3, "Due Date", bold_center)
        worksheet.write(6, 4, "Total Amount", bold_center)
        worksheet.write(6, 5, "Paid Amount", bold_center)
        worksheet.write(6, 6, "Balance", bold_center)

        total_amount = 0
        total_paid_amount = 0
        total_balance = 0
        k = 7

        if self.customer_due_statement_ids:
            for i in self.customer_due_statement_ids:
                worksheet.row(k).height = 350
                for j in i:
                    if j.due_customer_due_date and j.today and j.due_customer_due_date < j.today: 
                        worksheet.write(k, 0, j.name, red_text)
                        worksheet.write(k, 1, j.account, red_text)
                        worksheet.write(k, 2, str(j.due_customer_invoice_date),
                                        red_text)
                        if j.due_customer_due_date:
                            worksheet.write(k, 3, str(j.due_customer_due_date),
                                            red_text)
                        else:
                            worksheet.write(k, 3, '',
                                            red_text)
                        worksheet.write(
                            k, 4,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.due_customer_amount)), red_text)
                        worksheet.write(
                            k, 5,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.due_customer_paid_amount)), red_text)
                        worksheet.write(
                            k, 6,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.due_customer_balance)), red_text)
                    else:
                        worksheet.write(k, 0, j.name, center_text)
                        worksheet.write(k, 1, j.account, center_text)
                        worksheet.write(k, 2, str(j.due_customer_invoice_date),
                                        center_text)
                        if j.due_customer_due_date:
                            worksheet.write(k, 3, str(j.due_customer_due_date),
                                            center_text)
                        else:
                            worksheet.write(k, 3, '',
                                            center_text)
                        worksheet.write(
                            k, 4,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.due_customer_amount)), center_text)
                        worksheet.write(
                            k, 5,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.due_customer_paid_amount)), center_text)
                        worksheet.write(
                            k, 6,
                            str(i.currency_id.symbol) +
                            str("{:.2f}".format(j.due_customer_balance)), center_text)
                    k = k + 1
                total_amount = total_amount + j.due_customer_amount
                total_paid_amount = total_paid_amount + j.due_customer_paid_amount
                total_balance = total_balance + j.due_customer_balance
        if self.customer_due_statement_ids:
            worksheet.write(k, 4,
                            str("{:.2f}".format(total_amount)),
                            bold_center)
            worksheet.row(k).height = 350
            worksheet.write(k, 5,
                            str("{:.2f}".format(total_paid_amount)),
                            bold_center)
            worksheet.write(k, 6,
                            str("{:.2f}".format(total_balance)),
                            bold_center)

        fp = io.BytesIO()
        workbook.save(fp)

        data = base64.encodestring(fp.getvalue())
        IrAttachment = self.env['ir.attachment']
        attachment_vals = {
            "name": "Customer Overdue Statement.xls",
            "res_model": "ir.ui.view",
            "type": "binary",
            "datas": data,
            "public": True,
        }
        fp.close()

        attachment = IrAttachment.search(
            [('name', '=', 'Customer Overdue Statement'),
             ('type', '=', 'binary'), ('res_model', '=', 'ir.ui.view')],
            limit=1)
        if attachment:
            attachment.write(attachment_vals)
        else:
            attachment = IrAttachment.create(attachment_vals)
        #TODO: make user error here
        if not attachment:
            raise UserError('There is no attachments...')

        url = "/web/content/" + str(attachment.id) + "?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'current',
        }

    @api.model
    def _run_auto_send_customer_statements(self):
        temp=[]
        statement_partners_ids=self.env['customer.statement.config'].sudo().search([])
        if statement_partners_ids:
            for statement in statement_partners_ids:
                for partner in statement.partner_ids:
                    if partner.id not in temp:
                        temp.append(partner.id)
        partner_ids = self.env['res.partner'].sudo().search([('id','not in',temp)])
        for partner in partner_ids:
            try:
                #for customer
                if partner.customer_rank > 0:
                    #for statement
                    if not partner.dont_send_customer_statement_auto:
                        if self.env.company.customer_statement_auto_send and partner.customer_statement_ids:
                            if self.env.company.filter_only_unpaid_and_send_that and not partner.customer_statement_ids.filtered(lambda x:x.filter_balance > 0):
                                return

                            if self.env.company.customer_statement_action == 'daily':
                                if self.env.company.cus_daily_statement_template_id:
                                    mail = self.env.company.cus_daily_statement_template_id.sudo().send_mail(partner.id, force_send=True)
                                    mail_id = self.env['mail.mail'].sudo().browse(mail)
                                    if mail_id and self.env.company.cust_create_log_history:
                                        self.env['customer.mail.history'].sudo().create({
                                            'name': 'Customer Account Statement',
                                            'statement_type': 'customer_statement',
                                            'current_date': fields.Datetime.now(),
                                            'partner_id': partner.id,
                                            'mail_id': mail_id.id,
                                            'mail_status': mail_id.state,
                                        })
                            elif self.env.company.customer_statement_action == 'weekly':
                                today = fields.Date.today().weekday()
                                if int(self.env.company.cust_week_day) == today:
                                    if self.env.company.cust_weekly_statement_template_id:
                                        mail = self.env.company.cust_weekly_statement_template_id.sudo().send_mail(partner.id, force_send=True)
                                        mail_id = self.env['mail.mail'].sudo().browse(
                                            mail)
                                        if mail_id and self.env.company.cust_create_log_history:
                                            self.env['customer.mail.history'].sudo().create({
                                                'name': 'Customer Account Statement',
                                                'statement_type': 'customer_statement',
                                                'current_date': fields.Datetime.now(),
                                                'partner_id': partner.id,
                                                'mail_id': mail_id.id,
                                                'mail_status': mail_id.state,
                                            })
                            elif self.env.company.customer_statement_action == 'monthly':
                                monthly_day = self.env.company.cust_monthly_date
                                today = fields.Date.today()
                                today_date = today.day
                                if self.env.company.cust_monthly_end:
                                    last_day = calendar.monthrange(
                                        today.year, today.month)[1]
                                    if today_date == last_day:
                                        if self.env.company.cust_monthly_template_id:
                                            mail = self.env.company.cust_monthly_template_id.sudo(
                                            ).send_mail(partner.id, force_send=True)
                                            mail_id = self.env['mail.mail'].sudo().browse(
                                                mail)
                                            if mail_id and self.env.company.cust_create_log_history:
                                                self.env['customer.mail.history'].sudo().create({
                                                    'name': 'Customer Account Statement',
                                                    'statement_type': 'customer_statement',
                                                    'current_date': fields.Datetime.now(),
                                                    'partner_id': partner.id,
                                                    'mail_id': mail_id.id,
                                                    'mail_status': mail_id.state,
                                                })
                                else:
                                    if today_date == monthly_day:
                                        if self.env.company.cust_monthly_template_id:
                                            mail = self.env.company.cust_monthly_template_id.sudo(
                                            ).send_mail(partner.id, force_send=True)
                                            mail_id = self.env['mail.mail'].sudo().browse(
                                                mail)
                                            if mail_id and self.env.company.cust_create_log_history:
                                                self.env['customer.mail.history'].sudo().create({
                                                    'name': 'Customer Account Statement',
                                                    'statement_type': 'customer_statement',
                                                    'current_date': fields.Datetime.now(),
                                                    'partner_id': partner.id,
                                                    'mail_id': mail_id.id,
                                                    'mail_status': mail_id.state,
                                                })
                            elif self.env.company.customer_statement_action == 'yearly':
                                today = fields.Date.today()
                                today_date = today.day
                                today_month = today.strftime("%B").lower()
                                if self.env.company.cust_yearly_date == today_date and self.env.company.cust_yearly_month == today_month:
                                    if self.env.company.cust_yearly_template_id:
                                        mail = self.env.company.cust_yearly_template_id.sudo(
                                        ).send_mail(partner.id, force_send=True)
                                        mail_id = self.env['mail.mail'].sudo().browse(
                                            mail)
                                        if mail_id and self.env.company.cust_create_log_history:
                                            self.env['customer.mail.history'].sudo().create({
                                                'name': 'Customer Account Statement',
                                                'statement_type': 'customer_statement',
                                                'current_date': fields.Datetime.now(),
                                                'partner_id': partner.id,
                                                'mail_id': mail_id.id,
                                                'mail_status': mail_id.state,
                                            })
                    #for overdue statement
                    if not partner.dont_send_due_customer_statement_auto:
                        if self.env.company.customer_due_statement_auto_send and partner.customer_due_statement_ids:
                            if self.env.company.filter_only_unpaid_and_send_that and not partner.customer_due_statement_ids.filtered(lambda x:x.filter_balance > 0):
                                return
                                
                            if self.env.company.customer_due_statement_action == 'daily':
                                if self.env.company.cus_due_daily_statement_template_id:
                                    mail = self.env.company.cus_due_daily_statement_template_id.sudo(
                                    ).send_mail(partner.id, force_send=True)
                                    mail_id = self.env['mail.mail'].sudo().browse(
                                        mail)
                                    if mail_id and self.env.company.cust_due_create_log_history:
                                        self.env['customer.mail.history'].sudo().create({
                                            'name': 'Customer Account Overdue Statement',
                                            'statement_type': 'customer_overdue_statement',
                                            'current_date': fields.Datetime.now(),
                                            'partner_id': partner.id,
                                            'mail_id': mail_id.id,
                                            'mail_status': mail_id.state,
                                        })
                            elif self.env.company.customer_due_statement_action == 'weekly':
                                today = fields.Date.today().weekday()
                                if int(self.env.company.cust_due_week_day) == today:
                                    if self.env.company.cust_due_weekly_statement_template_id:
                                        mail = self.env.company.cust_due_weekly_statement_template_id.sudo(
                                        ).send_mail(partner.id, force_send=True)
                                        mail_id = self.env['mail.mail'].sudo().browse(
                                            mail)
                                        if mail_id and self.env.company.cust_due_create_log_history:
                                            self.env['customer.mail.history'].sudo().create({
                                                'name': 'Customer Account Overdue Statement',
                                                'statement_type': 'customer_overdue_statement',
                                                'current_date': fields.Datetime.now(),
                                                'partner_id': partner.id,
                                                'mail_id': mail_id.id,
                                                'mail_status': mail_id.state,
                                            })
                            elif self.env.company.customer_due_statement_action == 'monthly':
                                monthly_day = self.env.company.cust_due_monthly_date
                                today = fields.Date.today()
                                today_date = today.day
                                if self.env.company.cust_due_monthly_end:
                                    last_day = calendar.monthrange(
                                        today.year, today.month)[1]
                                    if today_date == last_day:
                                        if self.env.company.cust_due_monthly_template_id:
                                            mail = self.env.company.cust_due_monthly_template_id.sudo(
                                            ).send_mail(partner.id, force_send=True)
                                            mail_id = self.env['mail.mail'].sudo().browse(
                                                mail)
                                            if mail_id and self.env.company.cust_due_create_log_history:
                                                self.env['customer.mail.history'].sudo().create({
                                                    'name': 'Customer Account Overdue Statement',
                                                    'statement_type': 'customer_overdue_statement',
                                                    'current_date': fields.Datetime.now(),
                                                    'partner_id': partner.id,
                                                    'mail_id': mail_id.id,
                                                    'mail_status': mail_id.state,
                                                })
                                else:
                                    if today_date == monthly_day:
                                        if self.env.company.cust_due_monthly_template_id:
                                            mail = self.env.company.cust_due_monthly_template_id.sudo(
                                            ).send_mail(partner.id, force_send=True)
                                            mail_id = self.env['mail.mail'].sudo().browse(
                                                mail)
                                            if mail_id and self.env.company.cust_due_create_log_history:
                                                self.env['customer.mail.history'].sudo().create({
                                                    'name': 'Customer Account Overdue Statement',
                                                    'statement_type': 'customer_overdue_statement',
                                                    'current_date': fields.Datetime.now(),
                                                    'partner_id': partner.id,
                                                    'mail_id': mail_id.id,
                                                    'mail_status': mail_id.state,
                                                })
     
                            elif self.env.company.customer_due_statement_action == 'yearly':
                                today = fields.Date.today()
                                today_date = today.day
                                today_month = today.strftime("%B").lower()
                                if self.env.company.cust_due_yearly_date == today_date and self.env.company.cust_due_yearly_month == today_month:
                                    if self.env.company.cust_due_yearly_template_id:
                                        mail = self.env.company.cust_due_yearly_template_id.sudo(
                                        ).send_mail(partner.id, force_send=True)
                                        mail_id = self.env['mail.mail'].sudo().browse(
                                            mail)
                                        if mail_id and self.env.company.cust_due_create_log_history:
                                            self.env['customer.mail.history'].sudo().create({
                                                'name': 'Customer Account Overdue Statement',
                                                'statement_type': 'customer_overdue_statement',
                                                'current_date': fields.Datetime.now(),
                                                'partner_id': partner.id,
                                                'mail_id': mail_id.id,
                                                'mail_status': mail_id.state,
                                            })
            except Exception as e:
                _logger.error("%s", e)
class CustomPartnerField(models.Model):
    _name = "custom.partner.field"

    name = fields.Char(string="Custom Partner Fields")
    config_id = fields.Many2one("pos.config", string="Pos Config")


class ResPartnerInfo(models.Model):
    _name = "res.partner.info"

    name = fields.Char(string="Extra Info", required=True)
    info_name = fields.Char(string="Info Name")
    partner_id = fields.Many2one("res.partner", string="Partner Info")
    field_id = fields.Many2one("custom.partner.field", string="Custom Filed")

class FilterCustomerStateMent(models.Model):
    _name = 'res.partner.filter.statement'
    _description = 'Filter Customer Statement'

    partner_id = fields.Many2one('res.partner', 'Partner')
    name = fields.Char('Invoice Number')
    currency_id = fields.Many2one('res.currency', 'Currency')
    account = fields.Char('Account')
    filter_invoice_date = fields.Date('Invoice Date')
    filter_due_date = fields.Date('Invoice Due Date')
    filter_amount = fields.Monetary('Total Amount')
    filter_paid_amount = fields.Monetary('Paid Amount')
    filter_balance = fields.Monetary('Balance')

class CustomerStateMent(models.Model):
    _name = 'customer.statement'
    _description = 'Customer Statement'

    partner_id = fields.Many2one('res.partner', 'Partner')
    currency_id = fields.Many2one('res.currency', 'Currency')
    name = fields.Char('Invoice Number')
    account = fields.Char('Account')
    customer_invoice_date = fields.Date('Invoice Date')
    customer_due_date = fields.Date('Invoice Due Date')
    customer_amount = fields.Monetary('Total Amount')
    customer_paid_amount = fields.Monetary('Paid Amount')
    customer_balance = fields.Monetary('Balance')


class CustomerDueStateMent(models.Model):
    _name = 'customer.due.statement'
    _description = 'Customer Due Statement'

    partner_id = fields.Many2one('res.partner', 'Partner')
    name = fields.Char('Invoice Number')
    currency_id = fields.Many2one('res.currency', 'Currency')
    account = fields.Char('Account')
    today = fields.Date('Today')
    due_customer_invoice_date = fields.Date('Invoice Date')
    due_customer_due_date = fields.Date('Invoice Due Date')
    due_customer_amount = fields.Monetary('Total Amount')
    due_customer_paid_amount = fields.Monetary('Paid Amount')
    due_customer_balance = fields.Monetary('Balance')
