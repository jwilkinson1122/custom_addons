# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from psycopg2 import sql

from odoo import tools
from odoo import api, fields, models


class PodiatryReport(models.Model):
    _name = "podiatry.device.cost.report"
    _description = "Podiatry Analysis Report"
    _auto = False
    _order = 'date_start desc'

    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    device_id = fields.Many2one('podiatry.device', 'Device', readonly=True)
    name = fields.Char('Device Name', readonly=True)
    patient_id = fields.Many2one('res.partner', 'Patient', readonly=True)
    device_type = fields.Char('Fuel', readonly=True)
    date_start = fields.Date('Date', readonly=True)
    device_type = fields.Selection([('device', 'Device'), ('bike', 'Bike')], readonly=True)

    cost = fields.Float('Cost', readonly=True)
    cost_type = fields.Selection(string='Cost Type', selection=[
        ('prescription', 'Prescription'),
        ('service', 'Service')
    ], readonly=True)

    def init(self):
        query = """
WITH service_costs AS (
    SELECT
        ve.id AS device_id,
        ve.company_id AS company_id,
        ve.name AS name,
        ve.patient_id AS patient_id,
        ve.device_type AS device_type,
        date(date_trunc('month', d)) AS date_start,
        vem.device_type as device_type,
        COALESCE(sum(se.amount), 0) AS
        COST,
        'service' AS cost_type
    FROM
        podiatry_device ve
    JOIN
        podiatry_device_model vem ON vem.id = ve.model_id
    CROSS JOIN generate_series((
            SELECT
                min(date)
                FROM podiatry_device_log_services), CURRENT_DATE + '1 month'::interval, '1 month') d
        LEFT JOIN podiatry_device_log_services se ON se.device_id = ve.id
            AND date_trunc('month', se.date) = date_trunc('month', d)
    WHERE
        ve.active AND se.active AND se.state != 'cancelled'
    GROUP BY
        ve.id,
        ve.company_id,
        vem.device_type,
        ve.name,
        date_start,
        d
    ORDER BY
        ve.id,
        date_start
),
prescription_costs AS (
    SELECT
        ve.id AS device_id,
        ve.company_id AS company_id,
        ve.name AS name,
        ve.patient_id AS patient_id,
        ve.device_type AS device_type,
        date(date_trunc('month', d)) AS date_start,
        vem.device_type as device_type,
        (COALESCE(sum(co.amount), 0) + COALESCE(sum(cod.cost_generated * extract(day FROM least (date_trunc('month', d) + interval '1 month', cod.expiration_date) - greatest (date_trunc('month', d), cod.start_date))), 0) + COALESCE(sum(com.cost_generated), 0) + COALESCE(sum(coy.cost_generated), 0)) AS
        COST,
        'prescription' AS cost_type
    FROM
        podiatry_device ve
    JOIN
        podiatry_device_model vem ON vem.id = ve.model_id
    CROSS JOIN generate_series((
            SELECT
                min(acquisition_date)
                FROM podiatry_device), CURRENT_DATE + '1 month'::interval, '1 month') d
        LEFT JOIN podiatry_device_log_prescription co ON co.device_id = ve.id
            AND date_trunc('month', co.date) = date_trunc('month', d)
        LEFT JOIN podiatry_device_log_prescription cod ON cod.device_id = ve.id
            AND date_trunc('month', cod.start_date) <= date_trunc('month', d)
            AND date_trunc('month', cod.expiration_date) >= date_trunc('month', d)
            AND cod.cost_frequency = 'daily'
    LEFT JOIN podiatry_device_log_prescription com ON com.device_id = ve.id
        AND date_trunc('month', com.start_date) <= date_trunc('month', d)
        AND date_trunc('month', com.expiration_date) >= date_trunc('month', d)
        AND com.cost_frequency = 'monthly'
    LEFT JOIN podiatry_device_log_prescription coy ON coy.device_id = ve.id
        AND date_trunc('month', coy.date) = date_trunc('month', d)
        AND date_trunc('month', coy.start_date) <= date_trunc('month', d)
        AND date_trunc('month', coy.expiration_date) >= date_trunc('month', d)
        AND coy.cost_frequency = 'yearly'
    WHERE
        ve.active
    GROUP BY
        ve.id,
        ve.company_id,
        vem.device_type,
        ve.name,
        date_start,
        d
    ORDER BY
        ve.id,
        date_start
)
SELECT row_number() OVER (ORDER BY device_id ASC) as id,
    company_id,
    device_id,
    name,
    patient_id,
    device_type,
    date_start,
    device_type,
    COST,
    cost_type
FROM (
    SELECT
        company_id,
        device_id,
        name,
        patient_id,
        device_type,
        date_start,
        device_type,
        COST,
        'service' as cost_type
    FROM
        service_costs sc
    UNION ALL (
        SELECT
            company_id,
            device_id,
            name,
            patient_id,
            device_type,
            date_start,
            device_type,
            COST,
            'prescription' as cost_type
        FROM
            prescription_costs cc)
) c
"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            sql.SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                sql.Identifier(self._table),
                sql.SQL(query)
            ))
