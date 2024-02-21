# -*- coding: utf-8 -*-


from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_all_prescription_total = fields.Boolean('All Prescription')
    kpi_all_prescription_total_value = fields.Monetary(compute='_compute_kpi_prescription_total_value')

    def _compute_kpi_prescription_total_value(self):
        if not self.env.user.has_group('pod_prescription_team.group_prescription_personnel_all_leads'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))

        self._calculate_company_based_kpi(
            'prescription.report',
            'kpi_all_prescription_total_value',
            date_field='date',
            additional_domain=[('state', 'not in', ['draft', 'cancel', 'sent'])],
            sum_field='price_total',
        )

    def _compute_kpis_actions(self, company, user):
        res = super(Digest, self)._compute_kpis_actions(company, user)
        res['kpi_all_prescription_total'] = 'pod_prescription.report_all_channels_prescription_action&menu_id=%s' % self.env.ref('sale.sale_menu_root').id

        # res['kpi_all_prescription_total'] = 'pod_prescription.report_all_channels_prescription_action&menu_id=%s' % self.env.ref('pod_prescription.prescription_menu_root').id
        return res
