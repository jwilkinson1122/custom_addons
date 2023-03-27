# -*- coding: utf-8 -*-

from odoo import models, fields, tools


class DifferedCheckHistory(models.Model):
    _name = "report.prescription.order"
    _description = "Prescription Order Analysis"
    _auto = False

    name = fields.Char(string="Label")
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', store=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    # practice_id = fields.Many2one('podiatry.practice', string="Practice")
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address')
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address')
    order_date = fields.Datetime(string="Date")
    user_id = fields.Many2one('res.users', string='Prescription Person')
    total_amount = fields.Float(string='Total')
    currency_id = fields.Many2one("res.currency", string="Currency")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('order', 'Prescription Order'),
        ('process', 'Processing'),
        ('done', 'Done'),
        ('return', 'Returned'),
        ('cancel', 'Cancelled'),
    ], string='Status')

    _order = 'name desc'

    def _select(self):
        select_str = """
             SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.name as name,
                    t.invoice_status as invoice_status,
                    t.partner_id as partner_id,
                    t.partner_invoice_id as partner_invoice_id,
                    t.partner_shipping_id as partner_shipping_id,
                    t.order_date as order_date,
                    t.user_id as user_id,
                    t.total_amount as total_amount,
                    t.currency_id as currency_id,
                    t.state as state
        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    t.id,
                    name,
                    invoice_status,
                    partner_id,
                    partner_invoice_id,
                    partner_shipping_id,
                    order_date,
                    user_id,
                    total_amount,
                    currency_id,
                    state
        """
        return group_by_str

    def init(self):
        tools.sql.drop_view_if_exists(self._cr, 'report_prescription_order')
        self._cr.execute("""
            CREATE view report_prescription_order as
              %s
              FROM prescription_order t
                %s
        """ % (self._select(), self._group_by()))
