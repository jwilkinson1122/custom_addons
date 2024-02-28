# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from psycopg2 import sql

from odoo import tools
from odoo import api, fields, models


class DeviceReport(models.Model):
    _name = "device.custom.cost.report"
    _description = "Device Analysis Report"
    _auto = False
    _order = 'date_start desc'

    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    custom_id = fields.Many2one('device.custom', 'Custom', readonly=True)
    name = fields.Char('Custom Name', readonly=True)
    driver_id = fields.Many2one('res.partner', 'Driver', readonly=True)
    shell_type = fields.Char('Shell', readonly=True)
    date_start = fields.Date('Date', readonly=True)
    custom_type = fields.Selection([('car', 'Car'), ('bike', 'Bike')], readonly=True)

    cost = fields.Float('Cost', readonly=True)
    cost_type = fields.Selection(string='Cost Type', selection=[
        ('contract', 'Contract'),
        ('service', 'Service')
    ], readonly=True)

    def init(self):
        query = """
WITH service_costs AS (
    SELECT
        ve.id AS custom_id,
        ve.company_id AS company_id,
        ve.name AS name,
        ve.driver_id AS driver_id,
        ve.shell_type AS shell_type,
        date(date_trunc('month', d)) AS date_start,
        vem.custom_type as custom_type,
        COALESCE(sum(se.amount), 0) AS
        COST,
        'service' AS cost_type
    FROM
        device_custom ve
    JOIN
        device_custom_model vem ON vem.id = ve.model_id
    CROSS JOIN generate_series((
            SELECT
                min(date)
                FROM device_custom_log_services), CURRENT_DATE + '1 month'::interval, '1 month') d
        LEFT JOIN device_custom_log_services se ON se.custom_id = ve.id
            AND date_trunc('month', se.date) = date_trunc('month', d)
    WHERE
        ve.active AND se.active AND se.state != 'cancelled'
    GROUP BY
        ve.id,
        ve.company_id,
        vem.custom_type,
        ve.name,
        date_start,
        d
    ORDER BY
        ve.id,
        date_start
),
contract_costs AS (
    SELECT
        ve.id AS custom_id,
        ve.company_id AS company_id,
        ve.name AS name,
        ve.driver_id AS driver_id,
        ve.shell_type AS shell_type,
        date(date_trunc('month', d)) AS date_start,
        vem.custom_type as custom_type,
        (COALESCE(sum(co.amount), 0) + COALESCE(sum(cod.cost_generated * extract(day FROM least (date_trunc('month', d) + interval '1 month', cod.expiration_date) - greatest (date_trunc('month', d), cod.start_date))), 0) + COALESCE(sum(com.cost_generated), 0) + COALESCE(sum(coy.cost_generated), 0)) AS
        COST,
        'contract' AS cost_type
    FROM
        device_custom ve
    JOIN
        device_custom_model vem ON vem.id = ve.model_id
    CROSS JOIN generate_series((
            SELECT
                min(acquisition_date)
                FROM device_custom), CURRENT_DATE + '1 month'::interval, '1 month') d
        LEFT JOIN device_custom_log_contract co ON co.custom_id = ve.id
            AND date_trunc('month', co.date) = date_trunc('month', d)
        LEFT JOIN device_custom_log_contract cod ON cod.custom_id = ve.id
            AND date_trunc('month', cod.start_date) <= date_trunc('month', d)
            AND date_trunc('month', cod.expiration_date) >= date_trunc('month', d)
            AND cod.cost_frequency = 'daily'
    LEFT JOIN device_custom_log_contract com ON com.custom_id = ve.id
        AND date_trunc('month', com.start_date) <= date_trunc('month', d)
        AND date_trunc('month', com.expiration_date) >= date_trunc('month', d)
        AND com.cost_frequency = 'monthly'
    LEFT JOIN device_custom_log_contract coy ON coy.custom_id = ve.id
        AND d BETWEEN coy.start_date and coy.expiration_date
        AND date_part('month', coy.date) = date_part('month', d)
        AND coy.cost_frequency = 'yearly'
    WHERE
        ve.active
    GROUP BY
        ve.id,
        ve.company_id,
        vem.custom_type,
        ve.name,
        date_start,
        d
    ORDER BY
        ve.id,
        date_start
)
SELECT row_number() OVER (ORDER BY custom_id ASC) as id,
    company_id,
    custom_id,
    name,
    driver_id,
    shell_type,
    date_start,
    custom_type,
    COST,
    cost_type
FROM (
    SELECT
        company_id,
        custom_id,
        name,
        driver_id,
        shell_type,
        date_start,
        custom_type,
        COST,
        'service' as cost_type
    FROM
        service_costs sc
    UNION ALL (
        SELECT
            company_id,
            custom_id,
            name,
            driver_id,
            shell_type,
            date_start,
            custom_type,
            COST,
            'contract' as cost_type
        FROM
            contract_costs cc)
) c
"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            sql.SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                sql.Identifier(self._table),
                sql.SQL(query)
            ))
