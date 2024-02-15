# -*- coding: utf-8 -*-


from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    customer_statement_auto_send = fields.Boolean(
        'Customer Statement Auto Send')
    filter_only_unpaid_and_send_that = fields.Boolean(string = "Filter Only Unpaid, Send nothing if all invoices are paid")
    customer_statement_action = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), (
        'monthly', 'Monthly'), ('yearly', 'Yearly')], string='Customer Statement Action')
    cus_daily_statement_template_id = fields.Many2one(
        'mail.template', string='Daily Mail Template')
    cust_week_day = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), (
        '3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], string=' Week Day')
    cust_weekly_statement_template_id = fields.Many2one(
        'mail.template', string='Weekly Mail Template')
    cust_monthly_date = fields.Integer('Monthly Day', default=1)
    cust_monthly_end = fields.Boolean('End of month')
    cust_monthly_template_id = fields.Many2one(
        'mail.template', string='Monthly Mail Template')
    cust_yearly_date = fields.Integer('Yearly day ', default=1)
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
    ], string='Month')
    
    cust_yearly_template_id = fields.Many2one(
        'mail.template', string='  Yearly Mail Template')
    
    cust_create_log_history = fields.Boolean(
        'Customer Statement Mail Log History')

    customer_due_statement_auto_send = fields.Boolean(
        'Customer Overdue Statement Auto Send')
    customer_due_statement_action = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), (
        'monthly', 'Monthly'), ('yearly', 'Yearly')], string='Customer Overdue Statement Action')
    cus_due_daily_statement_template_id = fields.Many2one(
        'mail.template', string='Daily Mail Template ')
    cust_due_week_day = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), (
        '3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], string='  Week Day ')
    cust_due_weekly_statement_template_id = fields.Many2one(
        'mail.template', string='Weekly Mail Template ')
    cust_due_monthly_date = fields.Integer('Monthly Day ', default=1)
    cust_due_monthly_end = fields.Boolean('End of month ')
    cust_due_monthly_template_id = fields.Many2one(
        'mail.template', string='Monthly Mail Template ')
    cust_due_yearly_date = fields.Integer('Yearly Day ', default=1)
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
    ], string=' Month')

    cust_due_yearly_template_id = fields.Many2one(
        'mail.template', string=' Yearly Mail Template')
    
    cust_due_create_log_history = fields.Boolean(
        'Customer Overdue Statement Mail Log History')

    display_customer_statement = fields.Boolean('Show Customer Statement Menu in portal ?')

    display_due_statement = fields.Selection([
        ('due','Only Due'),
        ('overdue','Only Overdue'),
        ('both','Both')
        ],string='Display Due/Overdue Statements',default='both',required=True)
    
    statement_signature = fields.Boolean("Signature?", default=True)
    display_message_in_chatter = fields.Boolean(
        "Display in Chatter Message?", default=True)
    statement_pdf_in_message = fields.Boolean(
        "Send Report URL in Message?", default=True)
    statement_url_in_message = fields.Boolean("Send Statement URL in Message?", default=True)


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_statement_auto_send = fields.Boolean(
        'Customer Statement Auto Send', related='company_id.customer_statement_auto_send', readonly=False)
    
    filter_only_unpaid_and_send_that = fields.Boolean(string = "Filter Only Unpaid, Send nothing if all invoices are paid",
    related='company_id.filter_only_unpaid_and_send_that',readonly=False)

    customer_statement_action = fields.Selection(
        related='company_id.customer_statement_action', string='Customer Statement Action', readonly=False)
    
    cus_daily_statement_template_id = fields.Many2one(
        'mail.template', string='  Daily Mail Template', related='company_id.cus_daily_statement_template_id', readonly=False)
    
    cust_week_day = fields.Selection(
        string='Week Day', related='company_id.cust_week_day', readonly=False)
    
    cust_weekly_statement_template_id = fields.Many2one(
        'mail.template', string='Weekly Mail Template   ', related='company_id.cust_weekly_statement_template_id', readonly=False)
    
    cust_monthly_date = fields.Integer(
        'Monthly  Day', related='company_id.cust_monthly_date', readonly=False, default=1)
    
    cust_monthly_template_id = fields.Many2one(
        'mail.template', string='Monthly Mail Template', related='company_id.cust_monthly_template_id', readonly=False)
    
    cust_yearly_date = fields.Integer(
        ' Yearly day ', related='company_id.cust_yearly_date', readonly=False, default=1)
    
    cust_monthly_end = fields.Boolean(
        'End of  month', related='company_id.cust_monthly_end', readonly=False)
    
    cust_yearly_month = fields.Selection(
        string='  Month', related='company_id.cust_yearly_month', readonly=False)
    
    cust_yearly_template_id = fields.Many2one(
        'mail.template', string='  Yearly Mail Template', related='company_id.cust_yearly_template_id', readonly=False)
    
    cust_create_log_history = fields.Boolean(
        'Customer Statement Mail Log History', related='company_id.cust_create_log_history', readonly=False)

    cust_due_create_log_history = fields.Boolean(
        'Customer Overdue Statement Mail Log History', related='company_id.cust_due_create_log_history', readonly=False)
    
    # mail_log_history_type = fields.Selection([
    #     ('opt1', 'Statement History'),
    #     ('opt2', 'Overdue Statement History'),
    #     ('opt3', 'Both')
    # ], string='Selection Field')

    # @api.onchange('mail_log_history_type')
    # def _onchange_mail_log_history_type(self):
    #     if self.mail_log_history_type == 'opt1':
    #         self.cust_create_log_history = True
    #         self.cust_due_create_log_history = False
    #     elif self.mail_log_history_type == 'opt2':
    #         self.cust_create_log_history = False
    #         self.cust_due_create_log_history = True
    #     elif self.mail_log_history_type == 'opt3':
    #         self.cust_create_log_history = True
    #         self.cust_due_create_log_history = True

    customer_due_statement_auto_send = fields.Boolean(
        'Customer Overdue Statement Auto Send', related='company_id.customer_due_statement_auto_send', readonly=False)
    
    customer_due_statement_action = fields.Selection(
        related='company_id.customer_due_statement_action', string='Customer Overdue Statement Action', readonly=False)
    
    cus_due_daily_statement_template_id = fields.Many2one(
        'mail.template', string=' Daily Mail Template', related='company_id.cus_due_daily_statement_template_id', readonly=False)
    
    cust_due_week_day = fields.Selection(
        string='Week Day ', related='company_id.cust_due_week_day', readonly=False)
    
    cust_due_weekly_statement_template_id = fields.Many2one(
        'mail.template', string='   Weekly Mail Template', related='company_id.cust_due_weekly_statement_template_id', readonly=False)
    
    cust_due_monthly_date = fields.Integer(
        'Monthly Day    ', related='company_id.cust_due_monthly_date', readonly=False, default=1)
    
    cust_due_monthly_end = fields.Boolean(
        'End of month', related='company_id.cust_due_monthly_end', readonly=False)
    
    cust_due_monthly_template_id = fields.Many2one(
        'mail.template', string='Monthly  Mail Template', related='company_id.cust_due_monthly_template_id', readonly=False)
    
    cust_due_yearly_date = fields.Integer(
        '  Yearly Day     ', related='company_id.cust_due_yearly_date', readonly=False, default=1)
    
    cust_due_yearly_month = fields.Selection(
        string='Month', related='company_id.cust_due_yearly_month', readonly=False)
    
    cust_due_yearly_template_id = fields.Many2one(
        'mail.template', string=' Yearly Mail Template', related='company_id.cust_due_yearly_template_id', readonly=False)
    
    # cust_due_create_log_history = fields.Boolean(
    #     'Customer Overdue Statement Mail Log History', related='company_id.cust_due_create_log_history', readonly=False)

    display_customer_statement = fields.Boolean('Show Customer Statement Menu in portal ?',
        readonly=False,
        related='company_id.display_customer_statement'
    )

    display_due_statement = fields.Selection(
        string='Display Due/Overdue Statements',
        required=True,
        related='company_id.display_due_statement',
        readonly=False
        )
    statement_signature = fields.Boolean("Signature?",related='company_id.statement_signature',readonly=False)
    display_message_in_chatter = fields.Boolean(
        "Display in Chatter Message?",related='company_id.display_message_in_chatter',readonly=False)
    statement_pdf_in_message = fields.Boolean(
        "Send Report URL in Message?",related='company_id.statement_pdf_in_message',readonly=False)
    statement_url_in_message = fields.Boolean("Send Statement URL in Message?",related='company_id.statement_url_in_message',readonly=False)

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
