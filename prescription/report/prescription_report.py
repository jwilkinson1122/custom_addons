# -*- coding: utf-8 -*-

from psycopg2 import sql

from odoo import tools
from odoo import api, fields, models


class PrescriptionReport(models.Model):
    _name = "prescription.type.cost.report"
    _description = "Prescription Analysis Report"
    _auto = False
    _order = 'date_start desc'

    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    prescription_id = fields.Many2one('prescription.type', 'Prescription', readonly=True)
    name = fields.Char('Prescription Name', readonly=True)
    location_id = fields.Many2one('res.partner', 'Practitioner', readonly=True)
    shell_type = fields.Char('Shell', readonly=True)
    date_start = fields.Date('Date', readonly=True)
    prescription_type = fields.Selection([('custom', 'Custom'), ('otc', 'OTC')], readonly=True)

    cost = fields.Float('Cost', readonly=True)
    cost_type = fields.Selection(string='Cost Type', selection=[
        ('prescription', 'Prescription'),
        ('service', 'Adjustment')
    ], readonly=True)

    def init(self):
        query = """
WITH service_costs AS (
    SELECT
        ve.id AS prescription_id,
        ve.company_id AS company_id,
        ve.name AS name,
        ve.location_id AS location_id,
        ve.shell_type AS shell_type,
        date(date_trunc('month', d)) AS date_start,
        vem.prescription_type as prescription_type,
        COALESCE(sum(se.amount), 0) AS
        COST,
        'service' AS cost_type
    FROM
        prescription_type ve
    JOIN
        prescription_type_model vem ON vem.id = ve.model_id
    CROSS JOIN generate_series((
            SELECT
                min(date)
                FROM prescription_type_log_services), CURRENT_DATE + '1 month'::interval, '1 month') d
        LEFT JOIN prescription_type_log_services se ON se.prescription_id = ve.id
            AND date_trunc('month', se.date) = date_trunc('month', d)
    WHERE
        ve.active AND se.active AND se.state != 'cancelled'
    GROUP BY
        ve.id,
        ve.company_id,
        vem.prescription_type,
        ve.name,
        date_start,
        d
    ORDER BY
        ve.id,
        date_start
),
prescription_costs AS (
    SELECT
        ve.id AS prescription_id,
        ve.company_id AS company_id,
        ve.name AS name,
        ve.location_id AS location_id,
        ve.shell_type AS shell_type,
        date(date_trunc('month', d)) AS date_start,
        vem.prescription_type as prescription_type,
        (COALESCE(sum(co.amount), 0) + COALESCE(sum(cod.cost_generated * extract(day FROM least (date_trunc('month', d) + interval '1 month', cod.expiration_date) - greatest (date_trunc('month', d), cod.start_date))), 0) + COALESCE(sum(com.cost_generated), 0) + COALESCE(sum(coy.cost_generated), 0)) AS
        COST,
        'prescription' AS cost_type
    FROM
        prescription_type ve
    JOIN
        prescription_type_model vem ON vem.id = ve.model_id
    CROSS JOIN generate_series((
            SELECT
                min(received_date)
                FROM prescription_type), CURRENT_DATE + '1 month'::interval, '1 month') d
        LEFT JOIN prescription_type_log co ON co.prescription_id = ve.id
            AND date_trunc('month', co.date) = date_trunc('month', d)
        LEFT JOIN prescription_type_log cod ON cod.prescription_id = ve.id
            AND date_trunc('month', cod.start_date) <= date_trunc('month', d)
            AND date_trunc('month', cod.expiration_date) >= date_trunc('month', d)
            AND cod.cost_frequency = 'daily'
    LEFT JOIN prescription_type_log com ON com.prescription_id = ve.id
        AND date_trunc('month', com.start_date) <= date_trunc('month', d)
        AND date_trunc('month', com.expiration_date) >= date_trunc('month', d)
        AND com.cost_frequency = 'monthly'
    LEFT JOIN prescription_type_log coy ON coy.prescription_id = ve.id
        AND d BETWEEN coy.start_date and coy.expiration_date
        AND date_part('month', coy.date) = date_part('month', d)
        AND coy.cost_frequency = 'yearly'
    WHERE
        ve.active
    GROUP BY
        ve.id,
        ve.company_id,
        vem.prescription_type,
        ve.name,
        date_start,
        d
    ORDER BY
        ve.id,
        date_start
)
SELECT row_number() OVER (ORDER BY prescription_id ASC) as id,
    company_id,
    prescription_id,
    name,
    location_id,
    shell_type,
    date_start,
    prescription_type,
    COST,
    cost_type
FROM (
    SELECT
        company_id,
        prescription_id,
        name,
        location_id,
        shell_type,
        date_start,
        prescription_type,
        COST,
        'service' as cost_type
    FROM
        service_costs sc
    UNION ALL (
        SELECT
            company_id,
            prescription_id,
            name,
            location_id,
            shell_type,
            date_start,
            prescription_type,
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
