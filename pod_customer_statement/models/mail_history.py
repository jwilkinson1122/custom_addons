# -*- coding: utf-8 -*-


from odoo import models, fields


class PartnerMailHistory(models.Model):
    _name = 'customer.mail.history'
    _description = 'Partner Mail History'

    name = fields.Char('Name')
    statement_type = fields.Selection([
        ('customer_statement_filter', 'Customer Statement By Date'),
        ('customer_statement', 'Customer Statement'),
        ('customer_overdue_statement', 'Customer Overdue Statement'),
    ], string='Statement Type')
    current_date = fields.Datetime('Log Date')
    partner_id = fields.Many2one('res.partner', 'Customer')
    mail_id = fields.Many2one('mail.mail', 'Mail Reference')
    mail_status = fields.Selection([
        ('outgoing', 'Outgoing'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('exception', 'Delivery Failed'),
        ('cancel', 'Cancelled'),
    ], string='Mail Sent Status')
