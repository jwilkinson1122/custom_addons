# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Technogies @cybrosys(odoo@cybrosys.com)
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


class PodiatryManagerReport(models.Model):
    _name = "report.podiatry.manager"
    _description = "Podiatry Manager Analysis"
    _auto = False

    name = fields.Char(string="Name")
    customer_id = fields.Many2one('res.partner')
    device_id = fields.Many2one('podiatry.device')
    product_brand = fields.Char(string="Product Brand")
    product_color = fields.Char(string="Product Color")
    cost = fields.Float(string="Rent Cost")
    rent_start_date = fields.Date(string="Rent Start Date")
    rent_end_date = fields.Date(string="Rent End Date")
    state = fields.Selection([('draft', 'Draft'), ('running', 'Running'), ('cancel', 'Cancel'),
                              ('checking', 'Checking'), ('done', 'Done')], string="State")
    cost_frequency = fields.Selection([('no', 'No'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'),
                                       ('yearly', 'Yearly')], string="Recurring Cost Frequency")
    total = fields.Float(string="Total(Tools)")
    tools_missing_cost = fields.Float(string="Tools missing cost")
    damage_cost = fields.Float(string="Damage cost")
    damage_cost_sub = fields.Float(string="Damage cost")
    total_cost = fields.Float(string="Total cost")

    _order = 'name desc'

    def _select(self):
        select_str = """
             SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.name as name,
                    t.product_brand as product_brand,
                    t.customer_id as customer_id,
                    t.device_id as device_id,
                    t.product_color as product_color,
                    t.cost as cost,
                    t.rent_start_date as rent_start_date,
                    t.rent_end_date as rent_end_date,
                    t.state as state,
                    t.cost_frequency as cost_frequency,
                    t.total as total,
                    t.tools_missing_cost as tools_missing_cost,
                    t.damage_cost as damage_cost,
                    t.damage_cost_sub as damage_cost_sub,
                    t.total_cost as total_cost
        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    t.id,
                    name,
                    product_brand,
                    customer_id,
                    device_id,
                    product_color,
                    cost,
                    rent_start_date,
                    rent_end_date,
                    state,
                    cost_frequency,
                    total,
                    tools_missing_cost,
                    damage_cost,
                    damage_cost_sub,
                    total_cost
        """
        return group_by_str

    def init(self):
        tools.sql.drop_view_if_exists(self._cr, 'report_podiatry_manager')
        self._cr.execute("""
            CREATE view report_podiatry_manager as
              %s
              FROM product_manager_contract t
                %s
        """ % (self._select(), self._group_by()))
