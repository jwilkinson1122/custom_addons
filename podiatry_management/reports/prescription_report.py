# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Jesni Banu and Nilmar Shereef(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

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
    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address')
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address')
    order_date = fields.Datetime(string="Date")
    prescription_person = fields.Many2one('res.users', string='Prescription Person')
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
                    t.prescription_person as prescription_person,
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
                    prescription_person,
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
