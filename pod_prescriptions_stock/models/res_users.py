# -*- coding: utf-8 -*-


from odoo import models, fields


class Users(models.Model):
    _inherit = ['res.users']

    property_pod_warehouse_id = fields.Many2one('stock.warehouse', string='Default Warehouse', company_dependent=True, check_company=True)

    def _get_default_pod_warehouse_id(self):
        if self.property_pod_warehouse_id:
            return self.property_pod_warehouse_id
        # !!! Any change to the following search domain should probably
        # be also applied in pod_prescriptions_stock/models/prescriptions_order.py/_init_column.
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['property_pod_warehouse_id']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['property_pod_warehouse_id']
