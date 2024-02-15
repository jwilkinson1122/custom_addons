# -*- coding: utf-8 -*-


from odoo import models, fields, api,_
from datetime import timedelta
from datetime import datetime
import calendar
import logging
_logger = logging.getLogger(__name__)

class CustomerStatementConfig(models.Model):
    _name = 'customer.statement.config'

    name=fields.Char('Title')
    partner_ids=fields.Many2many('res.partner',string="Customer", domain=[('is_company','=', True)])
    customer_statement_auto_send = fields.Boolean(
        'Account Statement Auto Send',readonly=False)
    filter_only_unpaid_and_send_that = fields.Boolean(string = "Filter Only Unpaid, Send nothing if all invoices are paid")
    customer_statement_action = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), (
        'monthly', 'Monthly'), ('yearly', 'Yearly')],
    string='Statement Interval')
    cus_daily_statement_template_id = fields.Many2one(
        'mail.template', string='  Daily Mail Template')
    cust_week_day = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), (
        '3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')],
        string='Week Day', readonly=False)
    cust_weekly_statement_template_id = fields.Many2one(
        'mail.template', string='Weekly Mail Template   ', readonly=False)
    cust_monthly_date = fields.Integer(
        'Monthly  Day', readonly=False, default=1)
    cust_monthly_template_id = fields.Many2one(
        'mail.template', string='Monthly Mail Template', readonly=False)
    cust_yearly_date = fields.Integer(
        ' Yearly day ', readonly=False, default=1)
    cust_monthly_end = fields.Boolean(
        'End of  month', readonly=False)
    cust_yearly_month = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December')
    ],
        string='  Month', readonly=False)
    cust_yearly_template_id = fields.Many2one(
        'mail.template', string='  Yearly Mail Template', readonly=False)
    cust_create_log_history = fields.Boolean(
        'Account Statement Mail Log History',readonly=False)

    
    customer_due_statement_auto_send = fields.Boolean(
        'Account Overdue Statement Auto Send')
    customer_due_statement_action = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), (
        'monthly', 'Monthly'), ('yearly', 'Yearly')], string='Account Overdue Statement Action', readonly=False)
    cus_due_daily_statement_template_id = fields.Many2one(
        'mail.template', string=' Daily Mail Template',readonly=False)
    cust_due_week_day = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), (
        '3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')],
        string='Week Day ', readonly=False)
    cust_due_weekly_statement_template_id = fields.Many2one(
        'mail.template', string='   Weekly Mail Template', readonly=False)
    cust_due_monthly_date = fields.Integer(
        'Monthly Day    ', readonly=False, default=1)
    cust_due_monthly_end = fields.Boolean(
        'End of month', readonly=False)
    cust_due_monthly_template_id = fields.Many2one(
        'mail.template', string='Monthly  Mail Template', readonly=False)
    cust_due_yearly_date = fields.Integer(
        '  Yearly Day     ', readonly=False, default=1)
    cust_due_yearly_month = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December')
    ],
        string='Month', readonly=False)
    cust_due_yearly_template_id = fields.Many2one(
        'mail.template', string=' Yearly Mail Template',readonly=False)
    cust_due_create_log_history = fields.Boolean(
        'Account Overdue Statement Mail Log History',readonly=False)

    @api.onchange('customer_statement_auto_send')
    def onchange_customer_statement_auto_send(self):
        if not self.customer_statement_auto_send:
            self.customer_statement_action = False
            self.cus_daily_statement_template_id = False
            self.cust_week_day = False
            self.cust_weekly_statement_template_id = False
            self.cust_monthly_date = 0
            self.cust_monthly_template_id = False
            self.cust_yearly_date = 0
            self.cust_yearly_month = False
            self.cust_yearly_template_id = False
            self.cust_monthly_end = False

    @api.onchange('customer_due_statement_auto_send')
    def onchange_customer_due_statement_auto_send(self):
        if not self.customer_due_statement_auto_send:
            self.customer_due_statement_action = False
            self.cus_due_daily_statement_template_id = False
            self.cust_due_week_day = False
            self.cust_due_weekly_statement_template_id = False
            self.cust_due_monthly_date = 0
            self.cust_due_monthly_template_id = False
            self.cust_due_yearly_date = 0
            self.cust_due_yearly_month = False
            self.cust_due_yearly_template_id = False
            self.cust_due_monthly_end = False

    # mail history form button
    def mail_history(self):
        search=self.env['customer.mail.history'].search([('partner_id','in',self.partner_ids.ids)]).ids
        return {
            'name': _('Mail Log History'),
            'type': 'ir.actions.act_window',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'customer.mail.history',
            'domain': [('id','in',search)] 
        }
    
    # mass action wizard
    def add_replace_customer_manually_(self):
        view =self.env.ref('pod_customer_statement.update_customers_statement_wizard')
        return {
            'name': 'Mass Update',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'res_model': 'customer.mass.update',
            'view_id':view.id,
            'target': 'new',
            'context':{'default_statement_ids':self.ids},      
        }

    @api.model
    def create(self, vals):
        res = super(CustomerStatementConfig, self).create(vals)
        if res.partner_ids:
            for rec in res.partner_ids:
                rec.customer_statement_config=[(4,res.id)]
        return res

    def write(self, vals):
        res = super(CustomerStatementConfig, self).write(vals)
        if self.partner_ids:
            for k in self.partner_ids:
                k.customer_statement_config=[(4,self.id)]
        return res

    @api.model
    def _run_auto_send_customer_statements_config(self):
        statements_ids=self.env['customer.statement.config'].sudo().search([])
        for statement in statements_ids:
            try:
                for partner in statement.partner_ids:
                    if partner.customer_rank > 0:
                        #for statement
                        if not partner.dont_send_due_customer_statement_auto:
                            if statement.customer_statement_auto_send:
                                if statement.filter_only_unpaid_and_send_that and not partner.customer_statement_ids.filtered(lambda x:x.filter_balance > 0):
                                    return

                                if statement.customer_statement_action == 'daily':
                                    if statement.cus_daily_statement_template_id:
                                        mail = statement.cus_daily_statement_template_id.sudo().send_mail(partner.id, force_send=True)
                                        mail_id = self.env['mail.mail'].sudo().browse(mail)
                                        if mail_id and statement.cust_create_log_history:
                                            self.env['customer.mail.history'].sudo().create({
                                                'name': 'Account Statement',
                                                'statement_type': 'customer_statement',
                                                'current_date': fields.Datetime.now(),
                                                'partner_id': partner.id,
                                                'mail_id': mail_id.id,
                                                'mail_status': mail_id.state,
                                            })
                                elif statement.customer_statement_action == 'weekly':
                                    today = fields.Date.today().weekday()
                                    if int(statement.cust_week_day) == today:
                                        if statement.cust_weekly_statement_template_id:
                                            mail = statement.cust_weekly_statement_template_id.sudo().send_mail(partner.id, force_send=True)
                                            mail_id = self.env['mail.mail'].sudo().browse(
                                                mail)
                                            if mail_id and statement.cust_create_log_history:
                                                self.env['customer.mail.history'].sudo().create({
                                                    'name': 'Account Statement',
                                                    'statement_type': 'customer_statement',
                                                    'current_date': fields.Datetime.now(),
                                                    'partner_id': partner.id,
                                                    'mail_id': mail_id.id,
                                                    'mail_status': mail_id.state,
                                                })
                                elif statement.customer_statement_action == 'monthly':
                                    monthly_day = statement.cust_monthly_date
                                    today = fields.Date.today()
                                    today_date = today.day
                                    if statement.cust_monthly_end:
                                        last_day = calendar.monthrange(
                                            today.year, today.month)[1]
                                        if today_date == last_day:
                                            if statement.cust_monthly_template_id:
                                                mail = statement.cust_monthly_template_id.sudo(
                                                ).send_mail(partner.id, force_send=True)
                                                mail_id = self.env['mail.mail'].sudo().browse(
                                                    mail)
                                                if mail_id and statement.cust_create_log_history:
                                                    self.env['customer.mail.history'].sudo().create({
                                                        'name': 'Account Statement',
                                                        'statement_type': 'customer_statement',
                                                        'current_date': fields.Datetime.now(),
                                                        'partner_id': partner.id,
                                                        'mail_id': mail_id.id,
                                                        'mail_status': mail_id.state,
                                                    })
                                    else:
                                        if today_date == monthly_day:
                                            if statement.cust_monthly_template_id:
                                                mail = statement.cust_monthly_template_id.sudo(
                                                ).send_mail(partner.id, force_send=True)
                                                mail_id = self.env['mail.mail'].sudo().browse(
                                                    mail)
                                                if mail_id and statement.cust_create_log_history:
                                                    self.env['customer.mail.history'].sudo().create({
                                                        'name': 'Account Statement',
                                                        'statement_type': 'customer_statement',
                                                        'current_date': fields.Datetime.now(),
                                                        'partner_id': partner.id,
                                                        'mail_id': mail_id.id,
                                                        'mail_status': mail_id.state,
                                                    })
                                elif statement.customer_statement_action == 'yearly':
                                    today = fields.Date.today()
                                    today_date = today.day
                                    today_month = today.strftime("%B").lower()
                                    if statement.cust_yearly_date == today_date and statement.cust_yearly_month == today_month:
                                        if statement.cust_yearly_template_id:
                                            mail = statement.cust_yearly_template_id.sudo(
                                            ).send_mail(partner.id, force_send=True)
                                            mail_id = self.env['mail.mail'].sudo().browse(
                                                mail)
                                            if mail_id and statement.cust_create_log_history:
                                                self.env['customer.mail.history'].sudo().create({
                                                    'name': 'Account Statement',
                                                    'statement_type': 'customer_statement',
                                                    'current_date': fields.Datetime.now(),
                                                    'partner_id': partner.id,
                                                    'mail_id': mail_id.id,
                                                    'mail_status': mail_id.state,
                                                })
                        #for overdue statement
                        if not partner.dont_send_due_customer_statement_auto:
                            if statement.customer_due_statement_auto_send:

                                    if statement.filter_only_unpaid_and_send_that and not partner.customer_due_statement_ids.filtered(lambda x:x.filter_balance > 0):
                                        return

                                    if statement.customer_due_statement_action == 'daily':
                                        if statement.cus_due_daily_statement_template_id:
                                            mail = statement.cus_due_daily_statement_template_id.sudo(
                                            ).send_mail(partner.id, force_send=True)
                                            mail_id = self.env['mail.mail'].sudo().browse(
                                                mail)
                                            if mail_id and statement.cust_due_create_log_history:
                                                self.env['customer.mail.history'].sudo().create({
                                                    'name': 'Account Overdue Statement',
                                                    'statement_type': 'customer_overdue_statement',
                                                    'current_date': fields.Datetime.now(),
                                                    'partner_id': partner.id,
                                                    'mail_id': mail_id.id,
                                                    'mail_status': mail_id.state,
                                                })
                                    elif statement.customer_due_statement_action == 'weekly':
                                        today = fields.Date.today().weekday()
                                        if int(statement.cust_due_week_day) == today:
                                            if statement.cust_due_weekly_statement_template_id:
                                                mail = statement.cust_due_weekly_statement_template_id.sudo(
                                                ).send_mail(partner.id, force_send=True)
                                                mail_id = self.env['mail.mail'].sudo().browse(
                                                    mail)
                                                if mail_id and statement.cust_due_create_log_history:
                                                    self.env['customer.mail.history'].sudo().create({
                                                        'name': 'Account Overdue Statement',
                                                        'statement_type': 'customer_overdue_statement',
                                                        'current_date': fields.Datetime.now(),
                                                        'partner_id': partner.id,
                                                        'mail_id': mail_id.id,
                                                        'mail_status': mail_id.state,
                                                    })
                                    elif statement.customer_due_statement_action == 'monthly':
                                        monthly_day = statement.cust_due_monthly_date
                                        today = fields.Date.today()
                                        today_date = today.day
                                        if statement.cust_due_monthly_end:
                                            last_day = calendar.monthrange(
                                                today.year, today.month)[1]
                                            if today_date == last_day:
                                                if statement.cust_due_monthly_template_id:
                                                    mail = statement.cust_due_monthly_template_id.sudo(
                                                    ).send_mail(partner.id, force_send=True)
                                                    mail_id = self.env['mail.mail'].sudo().browse(
                                                        mail)
                                                    if mail_id and statement.cust_due_create_log_history:
                                                        self.env['customer.mail.history'].sudo().create({
                                                            'name': 'Account Overdue Statement',
                                                            'statement_type': 'customer_overdue_statement',
                                                            'current_date': fields.Datetime.now(),
                                                            'partner_id': partner.id,
                                                            'mail_id': mail_id.id,
                                                            'mail_status': mail_id.state,
                                                        })
                                        else:
                                            if today_date == monthly_day:
                                                if statement.cust_due_monthly_template_id:
                                                    mail = statement.cust_due_monthly_template_id.sudo(
                                                    ).send_mail(partner.id, force_send=True)
                                                    mail_id = self.env['mail.mail'].sudo().browse(
                                                        mail)
                                                    if mail_id and statement.cust_due_create_log_history:
                                                        self.env['customer.mail.history'].sudo().create({
                                                            'name': 'Account Overdue Statement',
                                                            'statement_type': 'customer_overdue_statement',
                                                            'current_date': fields.Datetime.now(),
                                                            'partner_id': partner.id,
                                                            'mail_id': mail_id.id,
                                                            'mail_status': mail_id.state,
                                                        })
            
                                    elif statement.customer_due_statement_action == 'yearly':
                                        today = fields.Date.today()
                                        today_date = today.day
                                        today_month = today.strftime("%B").lower()
                                        if statement.cust_due_yearly_date == today_date and statement.cust_due_yearly_month == today_month:
                                            if statement.cust_due_yearly_template_id:
                                                mail = statement.cust_due_yearly_template_id.sudo(
                                                ).send_mail(partner.id, force_send=True)
                                                mail_id = self.env['mail.mail'].sudo().browse(
                                                    mail)
                                                if mail_id and statement.cust_due_create_log_history:
                                                    self.env['customer.mail.history'].sudo().create({
                                                        'name': 'Account Overdue Statement',
                                                        'statement_type': 'customer_overdue_statement',
                                                        'current_date': fields.Datetime.now(),
                                                        'partner_id': partner.id,
                                                        'mail_id': mail_id.id,
                                                        'mail_status': mail_id.state,
                                                    })
            except Exception as e:
                _logger.error("%s", e)
